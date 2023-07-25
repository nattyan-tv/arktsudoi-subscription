import asyncio
import aiohttp
import logging

class Client:
    """Discord API Client for dinosaur-stripeconnect"""
    def __init__(self, token: str, guild_id: int | str, api_version: int | None = None) -> None:
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
                print("Add Role (Discord API)", resp.status)
                if resp.status == 204:
                    return True
                else:
                    return False

    async def add_roles(self, member_id: str | int, role_ids: str | int | list[str] | list[int], reason: str = "Subscription with Stripe is now active. (dinosaur-stripeconnect)"):
        if isinstance(role_ids, str) or isinstance(role_ids, int):
            role_ids: list[str] | list[int] = [role_ids] # type: ignore
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
                logging.info("Del Role (Discord API)", resp.status)
                if resp.status == 204:
                    return True
                else:
                    return False

    async def del_roles(self, member_id: str | int, role_ids: str | int | list[str] | list[int], reason: str = "Subscription with Stripe has been deactivated. (dinosaur-stripeconnect)"):
        if isinstance(role_ids, str) or isinstance(role_ids, int):
            role_ids: list[str] | list[int] = [role_ids] # type: ignore
        for role_id in role_ids:
            await self._del_role(member_id, role_id, reason=reason)
            await asyncio.sleep(1)

    async def fetch_member(self, user_id: str | int) -> dict | None:
        """Fetch a Guid Member Object from the Discord API"""
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{self._api_url}/guilds/{self.guild_id}/members/{user_id}", headers={"Authorization": self._authorization}) as resp:
                logging.info("Get Guild Member (Discord API)", resp.status)
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None
