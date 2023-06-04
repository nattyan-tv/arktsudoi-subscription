import sanic
import asyncio
import aiohttp

class Client:
    def __init__(self, token: str, guild_id: int | str, api_version: int | None = None) -> None:
        """Initialize the client"""
        # self.app = app
        self.token = token # Discord Bot Token
        self.guild_id = str(guild_id) # Discord Guild ID
        self._content_type = "application/json" # HTTP Request Content-Type
        self._authorization = f"Bot {self.token}" # HTTP Request Authorization
        self._base_url = "https://discord.com/api" # Discord API Base URL
        self.api_version: int | None = api_version # Discord API Version
        self._api_url = f"{self._base_url}/v{self.api_version}" if self.api_version else self._base_url # Discord API URL

    async def _add_role(self, member_id: str | int, role_id: str | int, reason: str = "Subscription with Stripe is now active. (dinosaur-stripeconnect)"):
        headers = {
            "Authorization": self._authorization,
            "Content-Type": self._content_type,
            "X-Audit-Log-Reason": reason
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.put(f"{self._api_url}/guilds/{self.guild_id}/members/{member_id}/roles/{role_id}", headers=headers) as resp:
                print(resp.status)
                if resp.status == 204:
                    return True
                else:
                    return False

    async def add_roles(self, member_id: str | int, role_ids: str | int | list[str] | list[int], reason: str = "Subscription with Stripe is now active. (dinosaur-stripeconnect)"):
        if isinstance(role_ids, str) or isinstance(role_ids, int):
            role_ids = [role_ids]
        for role_id in role_ids:
            await self._add_role(member_id, role_id, reason=reason)
            await asyncio.sleep(1)

    async def _del_role(self, member_id: str | int, role_id: str | int, reason: str = "Subscription with Stripe has been deactivated. (dinosaur-stripeconnect)"):
        headers = {
            "Authorization": self._authorization,
            "Content-Type": self._content_type,
            "X-Audit-Log-Reason": reason
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.delete(f"{self._api_url}/guilds/{self.guild_id}/members/{member_id}/roles/{role_id}", headers=headers) as resp:
                print(resp.status)
                if resp.status == 204:
                    return True
                else:
                    return False

    async def del_roles(self, member_id: str | int, role_ids: str | int | list[str] | list[int], reason: str = "Subscription with Stripe has been deactivated. (dinosaur-stripeconnect)"):
        if isinstance(role_ids, str) or isinstance(role_ids, int):
            role_ids = [role_ids]
        for role_id in role_ids:
            await self._del_role(member_id, role_id, reason=reason)
            await asyncio.sleep(1)

    async def _fetch_members(self, member_name: str) -> list | bool:
        headers = {
            "Authorization": self._authorization,
            "Content-Type": self._content_type
        }
        query = {
            "query": member_name,
            "limit": 1000
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{self._api_url}/guilds/{self.guild_id}/members/search", headers=headers, params=query) as resp:
                print(resp.status)
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
