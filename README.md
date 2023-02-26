# dinosaur-stripeconnect
Stripe Connect integration for Dinosaur

# Installation
1. Install requirements  
  (`pip install -r requirements.txt`)
2. Create a Stripe API key.  
  You can do this by going to [here](https://dashboard.stripe.com/account/apikeys).
3. Create configuration file.  
  Copy `config.example.json` to `config.json` and fill in the values.
4. Run the server.  
  (`python main.py`)
5. Add the webhook endpoint.  
  Go to [here](https://dashboard.stripe.com/account/webhooks) and add the webhook endpoint.  
  The endpoint is `http://localhost:5500/webhook` if you are running the server locally.  
  Port can be changed in `config.json`.

# Config

`config.json` is the configuration file for the server.

key|description
---|---
`PRODUCTION`|Set to `true` if you are running the server in production.
`DISCORD_TOKEN`|Discord bot token.
`STRIPE_API_KEY`|Stripe API key.
`SERVER_PORT`|Port to run the server on.
