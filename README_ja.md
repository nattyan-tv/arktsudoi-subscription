# dinosaur-stripeconnect
このレポジトリは、Stripeにてサブスクリプションの決済が行われた際に、Discordにてロールの付与を行うためのプログラムのレポジトリです。

# 事前準備
## 必要なもの
- Python 3.6以上 (3.10以上おすすめ)
- StripeのAPIキー ([こちら](https://dashboard.stripe.com/account/apikeys)から取得できます)
- DiscordのBotトークン ([こちら](https://discord.com/developers/applications)から取得できます)

## インストール
1. 必要なライブラリをインストールします。  
   (`pip install -r requirements.txt`)
2. StripeのAPIキーを取得します。  
   [こちら](https://dashboard.stripe.com/account/apikeys)から取得できます。
3. 設定ファイルを作成します。  
    `config.example.json`を`config.json`にコピーして、中身を書き換えます。
4. サーバーを起動します。  
    (`python main.py`)
5. Webhookエンドポイントを追加します。  
    [こちら](https://dashboard.stripe.com/account/webhooks)からWebhookエンドポイントを追加します。  
    デフォルトのエンドポイントは`http://localhost:5500/webhook`です。ポートは`config.json`で変更できます。  
    また、当たり前ですがlocalhostでは動作しないので、適時自身のドメインまたはアドレスに変更してください。

# 設定
`config.json`はサーバーの設定ファイルです。

```json
{
    "DISCORD_TOKEN": "<Discord BOTのTOKEN>",
    "STRIPE_API_KEY": "<sk_...から始まるStripeのAPI KEY>",
    "SERVER_PORT": <サーバーのポート>,
    "DISCORD_GUILD_ID": "<対象サーバーのID>",
    "ROLES": {
        "<prod_...から始まるStripe商品のID>": "<付与したいロールのID>"
    },
    "NOTIFY_WEBHOOK": "<通知用のDiscord Webhook URL>"
}
```
