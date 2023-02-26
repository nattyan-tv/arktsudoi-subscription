import aiohttp

class Client:
    def __init__(self, token: str, guild_id: int) -> None:
        self.token = token
        self.guild_id = guild_id

    async def add_role(self, member_id: int, role_id: int, reason: str = "Subscriptions were settled by Stripe. (dinosaur-stripeconnect)"):
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
            "X-Audit-Log-Reason": reason
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.put(f"https://discord.com/api/guilds/{self.guild_id}/members/{member_id}/roles/{role_id}", headers=headers) as resp:
                if resp.status == 204:
                    return True
                else:
                    return False

    async def _fetch_members(self, member_name: str) -> list | bool:
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        query = {
            "query": member_name,
            "limit": 1000
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://discord.com/api/guilds/{self.guild_id}/members/search", headers=headers, params=query) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return False

    async def fetch_member(self, member_name: str, discriminator: str) -> dict | bool:
        members = await self._fetch_members(member_name)
        if not members:
            return False
        for member in members:
            if member["user"]["discriminator"] == discriminator:
                return member
        return False
