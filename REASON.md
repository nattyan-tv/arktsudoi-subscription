# REASON
Webhookが送信されると下のようなJSONを返送します。

```json
{
    "status": "success",
    "message": "Role added",
    "code": 500
}
```

`status`部と`message`部と`code`部の3部分に分かれています。

- `status`  
  処理が成功したか失敗したかを表します。  
  `success`か`error`のどちらかが入ります。

- `message`  
  処理の結果を表します。

- `code`  
  処理の結果を表すステータスコードを表します。  
  これは、決してHTTPステータスコードとは関係ありません。

また、全てのステータス及びメッセージはコードを確認すれば分かります。

また、成功か失敗かだけを確認したい場合は、`code`の1桁目を確認してください。  
`0`なら成功、`1`以上なら失敗です。

# コード一覧
## 1xx

これは、`checkout.session`の処理中に送信されるものです。

### 100

status: `success`
message: `Product is not supported`

これは、このサービスがサポートしていない商品が購入された場合に返されます。  
この場合、ロールは操作されません。

## 2xx

これは、`subscription`の処理中に送信されるものです。

### 200

status: `success`
message: `Product is not supported`

これは、このサービスがサポートしていない商品が購入された場合に返されます。  
この場合、ロールは操作されません。

### 201

status: `error`
message: `Customer not found`

これは、サブスクリプションが更新したユーザーの情報が見つからなかった場合に送信されます。

## 3xx

これは、ロール操作で`SKIP`をするときに送信されるものです。

### 300

status: `error`
message: `Action skipped`

これは、ロールが何も操作されなかったことを示します。  
主に、料金が支払われていないが、まだSubscriptionオブジェクトがincompleteのままの状態の場合に送信されます。

## 4xx

これは、ロール操作前のDiscordユーザー取得時に送信されるものです。

### 401

status: `error`
message: `Member not found`

これは、Discordユーザーが見つからなかった場合に送信されます。

## 5xx

これは、ロール操作時に送信されるものです。

### 500

status: `success`
message: `OK`

これは、ロール操作が成功した場合に送信されます。

## 9xx
### 900

status: `success`
message: `Event not supported`

これは、このサービスがサポートしていないイベントが送信された場合に返されます。

### 901

status: `error`
message: `Method not allowed`

これは、このサービスがサポートしていないHTTPメソッドが送信された場合に返されます。  
このサービスのWebhookエンドポイントはPOSTのみをサポートしています。
