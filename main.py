import asyncio
import aiofiles
import sanic
import json
import enum

import sys

from async_stripe import stripe

import clientmodel
import configmodel
import notification

CONFIG = configmodel.Config(**json.load(open("config.json", "r")))

stripe.api_key = CONFIG.STRIPE_API_KEY

async def write_userdata(data) -> None:
    async with aiofiles.open("userdata", "w") as f:
        await f.write(json.dumps(data))

async def read_userdata() -> dict[str, str]:
    try:
        with open("userdata", "r") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        with open("userdata", "w") as f:
            f.write("{}")
        return {}

event_history = []

class ActionType(enum.Enum):
    ADD = 1
    REMOVE = 2
    ADDITIONAL_REMOVE = 3
    SKIP = 4

app = sanic.Sanic(f"dinosaur-stripeconnect-{'LIVE' if CONFIG.LIVE else 'TEST'}")

client = clientmodel.Client(CONFIG.DISCORD_TOKEN, CONFIG.DISCORD_GUILD_ID)
notify = notification.DiscordNotification(CONFIG.NOTIFY_WEBHOOK)


@app.route("/webhook", methods=["GET", "DELETE", "HEAD", "OPTIONS", "PATCH", "PUT", "POST"])
async def webhook(request: sanic.Request):
    if request.method != "POST":
        return sanic.response.json({"status": "error", "message": "Method not allowed", "code": 901})

    if request.json["id"] in event_history:
        return sanic.response.json({"status": "success", "message": "Event already processed (Duplicate or Resend)", "code": 100})
    else:
        event_history.append(request.json["id"])

    data = request.json["data"]["object"]
    userdata = await read_userdata()

    actions = []

    # print(data)
    # if data["id"] in checkout_history:
    #     return # Skip if already processed
    # else:
    #     checkout_history.append(data["id"])

    if request.json["type"] == "customer.subscription.deleted":
        print("Subscription Deleted Event")
        if data["customer"] not in userdata:
            return sanic.response.json({"status": "error", "message": "Customer not found", "code": 201})
        user = userdata[data["customer"]]

        username, discriminator = "#".join(user.split("#")[:-1]), user.split("#")[-1]
        member = await client.fetch_member(username, discriminator)
        if not member:
            return sanic.response.json({"status": "error", "message": "Member not found", "code": 401})
        member_id = member["user"]["id"] # 1234567890123

        embeds = []

        for item in data["items"]["data"]:
            product = item["plan"]["product"] # prod_...

            if product not in CONFIG.ROLES:
                continue


            role_id = CONFIG.ROLES[product] # 1234567890123
            actions.append({
                "action": ActionType.REMOVE,
                "role_id": role_id,
            })

            embed = notification.DiscordEmbed()
            embed.set_title("サブスクリプションが削除されました。")
            embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
            embed.set_color(0xff0000)
            embed.add_field("ステータス", "サブスクリプションが削除されました。\n`customer.subscription.deleted`", True)
            embed.add_field("ロール状態", "削除されました。", True)
            embed.add_field("対象ロール", f"<@&{role_id}>", True)
            embed.set_footer("DinosaurStripeConnect")
            embeds.append(embed)

        await notify.send(embed=embeds)

    elif request.json["type"] == "checkout.session.completed":
        print("Checkout Session Event")
        # Checkout Session Event
        user = data["custom_fields"][0]["text"]["value"] # Discord#0000
        customer = data["customer"] # cus_...
        userdata[customer] = user
        asyncio.ensure_future(write_userdata(userdata))
        subscription = await stripe.Subscription.retrieve(data["subscription"]) # Subscription Object

        product = subscription["items"]["data"][0]["plan"]["product"] # prod_...

        username, discriminator = "#".join(user.split("#")[:-1]), user.split("#")[-1]
        member = await client.fetch_member(username, discriminator)
        if not member:
            return sanic.response.json({"status": "error", "message": "Member not found", "code": 401})
        member_id = member["user"]["id"] # 1234567890123

        if product not in CONFIG.ROLES:
            return sanic.response.json({"status": "success", "message": "Product is not supported", "code": 100})
        role_id = CONFIG.ROLES[product] # 1234567890123

        status = subscription["status"]

        match status:
            case "trialing":
                action = ActionType.ADD
                embed = notification.DiscordEmbed()
                embed.set_title("トライアルが開始されました！")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0x00ff00)
                embed.add_field("ステータス", "トライアル中\n`checkout.session.completed`/`trialing`", True)
                embed.add_field("ロール状態", "付与されました。（期限が切れるとロールは削除されます。）", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "active":
                action = ActionType.ADD
                embed = notification.DiscordEmbed()
                embed.set_title("サブスクリプションが開始されました！")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0x00ff00)
                embed.add_field("ステータス", "サブスクリプションアクティブ\n`checkout.session.completed`/`active`", True)
                embed.add_field("ロール状態", "付与されました。（期限が切れるとロールは削除されます。）", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "incomplete":
                action = ActionType.SKIP
                embed = notification.DiscordEmbed()
                embed.set_title("支払いを待機しています。")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0xffff00)
                embed.add_field("ステータス", "購入を試みたが支払いは完了していない\n`checkout.session.completed`/`incomplete`", True)
                embed.add_field("ロール状態", "操作は行われません。", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "incomplete_expired":
                action = ActionType.REMOVE
                embed = notification.DiscordEmbed()
                embed.set_title("支払いに失敗しました")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0xff0000)
                embed.add_field("ステータス", "購入を試みたが支払いに失敗\n`checkout.session.completed`/`incomplete_expired`", True)
                embed.add_field("ロール状態", "削除されました。", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "past_due":
                action = ActionType.REMOVE
                embed = notification.DiscordEmbed()
                embed.set_title("自動決済に失敗しました")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0xff0000)
                embed.add_field("ステータス", "自動決済に失敗（Stripeのリトライルールに基づき再度支払いを試みる場合があります）\n`checkout.session.completed`/`past_due`", True)
                embed.add_field("ロール状態", "削除されました。", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "canceled":
                action = ActionType.REMOVE
                embed = notification.DiscordEmbed()
                embed.set_title("支払いがキャンセルされました。")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0xff0000)
                embed.add_field("ステータス", "支払いキャンセル\n`checkout.session.completed`/`canceled`", True)
                embed.add_field("ロール状態", "削除されました。", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)
            case "unpaid":
                action = ActionType.REMOVE
                embed = notification.DiscordEmbed()
                embed.set_title("支払いは行われませんでした。")
                embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                embed.set_color(0xff0000)
                embed.add_field("ステータス", "支払いは行われませんでした。\n`checkout.session.completed`/`unpaid`", True)
                embed.add_field("ロール状態", "削除されました。", True)
                embed.add_field("対象ロール", f"<@&{role_id}>", True)
                embed.set_footer("DinosaurStripeConnect")
                await notify.send(embed=embed)

        actions.append({
            "action": action,
            "role_id": role_id,
        })

    elif request.json["type"] == "customer.subscription.updated":
        print("Subscription Update Event")
        # Subscription Update Event

        if data["customer"] not in userdata:
            return sanic.response.json({"status": "error", "message": "Customer not found", "code": 201})
        user = userdata[data["customer"]]

        username, discriminator = "#".join(user.split("#")[:-1]), user.split("#")[-1]
        member = await client.fetch_member(username, discriminator)
        if not member:
            return sanic.response.json({"status": "error", "message": "Member not found", "code": 401})
        member_id = member["user"]["id"] # 1234567890123

        if "previous_attributes" in request.json["data"]:
            if "items" in request.json["data"]["previous_attributes"]:
                print("Previous attributes found")
                for item in request.json["data"]["previous_attributes"]["items"]["data"]:
                    # previous_product = request.json["data"]["previous_attributes"]["items"]["data"][0]["plan"]["product"] # prod_...
                    product = item["plan"]["product"] # prod_...
                    if product in CONFIG.ROLES:
                        role_id = CONFIG.ROLES[product] # 1234567890123
                        await client.del_roles(member_id, role_id)

        embeds = []

        for item in data["items"]["data"]:
            product = item["plan"]["product"]

            if product not in CONFIG.ROLES:
                continue

            role_id = CONFIG.ROLES[product] # 1234567890123
            status = data["status"]
            action = None

            match status:
                case "trialing":
                    action = ActionType.ADD
                    embed = notification.DiscordEmbed()
                    embed.set_title("トライアルが開始されました！")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0x00ff00)
                    embed.add_field("ステータス", "トライアル中\n`customer.subscription.updated`/`trialing`", True)
                    embed.add_field("ロール状態", "付与されました。（期限が切れるとロールは削除されます。）", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "active":
                    action = ActionType.ADD
                    embed = notification.DiscordEmbed()
                    embed.set_title("サブスクリプションが開始されました！")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0x00ff00)
                    embed.add_field("ステータス", "サブスクリプションアクティブ\n`customer.subscription.updated`/`active`", True)
                    embed.add_field("ロール状態", "付与されました。（期限が切れるとロールは削除されます。）", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "incomplete":
                    action = ActionType.SKIP
                    embed = notification.DiscordEmbed()
                    embed.set_title("支払いを待機しています。")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0xffff00)
                    embed.add_field("ステータス", "購入を試みたが支払いは完了していない\n`customer.subscription.updated`/`incomplete`", True)
                    embed.add_field("ロール状態", "操作は行われません。", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "incomplete_expired":
                    action = ActionType.REMOVE
                    embed = notification.DiscordEmbed()
                    embed.set_title("支払いに失敗しました")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0xff0000)
                    embed.add_field("ステータス", "購入を試みたが支払いに失敗\n`customer.subscription.updated`/`incomplete_expired`", True)
                    embed.add_field("ロール状態", "削除されました。", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "past_due":
                    action = ActionType.REMOVE
                    embed = notification.DiscordEmbed()
                    embed.set_title("自動決済に失敗しました")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0xff0000)
                    embed.add_field("ステータス", "自動決済に失敗（Stripeのリトライルールに基づき再度支払いを試みる場合があります）\n`customer.subscription.updated`/`past_due`", True)
                    embed.add_field("ロール状態", "削除されました。", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "canceled":
                    action = ActionType.REMOVE
                    embed = notification.DiscordEmbed()
                    embed.set_title("支払いがキャンセルされました。")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0xff0000)
                    embed.add_field("ステータス", "支払いキャンセル\n`customer.subscription.updated`/`canceled`", True)
                    embed.add_field("ロール状態", "削除されました。", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)
                case "unpaid":
                    action = ActionType.REMOVE
                    embed = notification.DiscordEmbed()
                    embed.set_title("支払いは行われませんでした。")
                    embed.set_description(f"ユーザー: {user}（<@{member_id}>）\nプラン: {product}")
                    embed.set_color(0xff0000)
                    embed.add_field("ステータス", "支払いは行われませんでした。\n`customer.subscription.updated`/`unpaid`", True)
                    embed.add_field("ロール状態", "削除されました。", True)
                    embed.add_field("対象ロール", f"<@&{role_id}>", True)
                    embed.set_footer("DinosaurStripeConnect")
                    embeds.append(embed)

            actions.append({
                "action": action,
                "role_id": role_id,
            })
            await notify.send(embed=embeds)

    else:
        return sanic.response.json({"status": "success", "message": "Event not supported", "code": 900})

    await client.add_roles(member_id, [action["role_id"] for action in actions if action["action"] == ActionType.ADD])
    await client.del_roles(member_id, [action["role_id"] for action in actions if action["action"] == ActionType.REMOVE])

    return sanic.response.json({"status": "success", "message": "OK", "code": 500})

@app.listener("after_server_start")
async def after_server_start(app, loop):
    print("Server started")



    #subscription = await stripe.Subscription.retrieve(data["subscription"])
    #product = subscription["items"]["data"][0]["price"]["product"] # Product ID
    #username, discriminator = "#".join(user.split("#")[:-1]), user.split("#")[-1]
    #member = await client.fetch_member(username, discriminator)
    #if not member:
    #    return sanic.response.json({"status": "error", "message": "Member not found", "code": 1})
    #member_id = member["user"]["id"]
    #if product not in CONFIG.ROLES:
    #    return sanic.response.json({"status": "success", "message": "Product not supported", "code": 0})
    #role_id = CONFIG.ROLES[product]
    #result = await client.add_role(member_id, role_id)
    #if result:
    #    return sanic.response.json({"status": "success", "message": "OK", "code": 0})
    #else:
    #    return sanic.response.json({"status": "error", "message": "Failed to add role", "code": 2})

def main():
    print("dinosaur-stripeconnect")
    if CONFIG.LIVE:
        print("""\
########## ATTENTION! ##########
You are running this in LIVE mode.
################################""")
    print(f"The webhook url is 'http://localhost:{CONFIG.SERVER_PORT}/webhook' (localrun)")

    app.run("0.0.0.0", CONFIG.SERVER_PORT)

if __name__ == "__main__":
    main()
