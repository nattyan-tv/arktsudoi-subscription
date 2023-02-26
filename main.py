import sanic
import json

from async_stripe import stripe

import clientmodel
import configmodel

CONFIG = configmodel.Config(**json.load(open("config.json", "r")))

app = sanic.Sanic(f"dinosaur-stripeconnect")
stripe.api_key = CONFIG.STRIPE_API_KEY
client = clientmodel.Client(CONFIG.DISCORD_TOKEN, CONFIG.DISCORD_GUILD_ID)

checkout_history = []

@app.post("/webhook")
async def webhook(request):
    data = request.json["data"]["object"]
    if data["id"] in checkout_history:
        return # Skip if already processed
    else:
        checkout_history.append(data["id"])
    if data["mode"] != "subscription":
        return sanic.response.json({"status": "success", "message": "Not a subscription", "code": 0})
    user = data["custom_fields"][0]["text"]["value"] # ちゃんと入れてくれてればユーザー名になっているはず。
    subscription = await stripe.Subscription.retrieve(data["subscription"])
    product = subscription["items"]["data"][0]["price"]["product"] # Product ID
    username, discriminator = "#".join(user.split("#")[:-1]), user.split("#")[-1]
    member = await client.fetch_member(username, discriminator)
    if not member:
        return sanic.response.json({"status": "error", "message": "Member not found", "code": 1})
    member_id = member["user"]["id"]
    if product not in CONFIG.ROLES:
        return sanic.response.json({"status": "success", "message": "Product not supported", "code": 0})
    role_id = CONFIG.ROLES[product]
    result = await client.add_role(member_id, role_id)
    if result:
        return sanic.response.json({"status": "success", "message": "OK", "code": 0})
    else:
        return sanic.response.json({"status": "error", "message": "Failed to add role", "code": 2})

if __name__ == "__main__":
    print("dinosaur-stripeconnect")
    print(f"The webhook url is 'http://localhost:{CONFIG.SERVER_PORT}/webhook' (localrun)")
    app.run("0.0.0.0", CONFIG.SERVER_PORT)
