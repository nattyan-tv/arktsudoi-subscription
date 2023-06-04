class Config:
    def __init__(self, DISCORD_TOKEN, STRIPE_API_KEY, DISCORD_GUILD_ID, SERVER_PORT, ROLES, NOTIFY_WEBHOOK):
        self.DISCORD_TOKEN = DISCORD_TOKEN
        if STRIPE_API_KEY[:3] != "sk_":
            raise ValueError("Invalid Stripe API Key (Stripe API Key must start with 'sk_')")
        self.LIVE = False
        if STRIPE_API_KEY[:8] == "sk_live_":
            self.LIVE = True
        self.STRIPE_API_KEY = STRIPE_API_KEY
        self.DISCORD_GUILD_ID = DISCORD_GUILD_ID
        self.SERVER_PORT = SERVER_PORT
        self.ROLES = ROLES
        self.NOTIFY_WEBHOOK = NOTIFY_WEBHOOK

