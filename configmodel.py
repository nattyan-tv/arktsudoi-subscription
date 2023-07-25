class Config:
    def __init__(self, DISCORD_TOKEN, STRIPE_API_KEY, DISCORD_GUILD_ID, SERVER_PORT, ROLES, NOTIFY_WEBHOOK):
        self.DISCORD_TOKEN: str = DISCORD_TOKEN
        if STRIPE_API_KEY[:3] != "sk_":
            raise ValueError("Invalid Stripe API Key (Stripe API Key must start with 'sk_')")
        self.LIVE: bool = False
        if STRIPE_API_KEY[:8] == "sk_live_":
            self.LIVE: bool = True
        self.STRIPE_API_KEY: str = STRIPE_API_KEY
        self.DISCORD_GUILD_ID: str | int = DISCORD_GUILD_ID
        self.SERVER_PORT: int = SERVER_PORT
        self.ROLES: dict[str, str] = ROLES
        self.NOTIFY_WEBHOOK: str = NOTIFY_WEBHOOK

