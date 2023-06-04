import aiohttp
import asyncio

class DiscordEmbed:
    title: str | None = None
    description: str | None = None
    url: str | None = None
    timestamp: str | None = None
    color: int = 0x000000
    footer: dict[str, str] = {}
    image: dict[str, str] = {}
    thumbnail: dict[str, str] = {}
    author: dict[str, str] = {}
    fields: list[dict[str, str | bool]] = []

    def set_title(self, title: str):
        self.title = title

    def set_description(self, description: str):
        self.description = description

    def set_url(self, url: str):
        self.url = url

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp

    def set_color(self, color: int):
        self.color = color

    def set_footer(self, text: str, icon_url: str | None = None):
        self.footer = {
            "text": text,
            "icon_url": icon_url
        }

    def set_image(self, url: str):
        self.image = {
            "url": url
        }

    def set_thumbnail(self, url: str):
        self.thumbnail = {
            "url": url
        }

    def set_author(self, name: str, url: str, icon_url: str):
        self.author = {
            "name": name,
            "url": url,
            "icon_url": icon_url
        }

    def add_field(self, name: str, value: str, inline: bool = False):
        self.fields.append({
            "name": name,
            "value": value,
            "inline": inline
        })

    def get_embed(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "timestamp": self.timestamp,
            "color": self.color,
            "footer": self.footer,
            "image": self.image,
            "thumbnail": self.thumbnail,
            "author": self.author,
            "fields": self.fields
        }

class DiscordNotification:
    def __init__(
            self,
            webhook_url: str,
            username: str = "DinosaurStripeConnect",
            avatar_url: str = "",
            loop: asyncio.AbstractEventLoop | None = None
        ):
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url

    def get_content(self, message: str | None = None, embed: list[DiscordEmbed] | None = None):
        if embed:
            return {
                "username": self.username,
                "avatar_url": self.avatar_url,
                "content": message,
                "embeds": [e.get_embed() for e in embed]
            }
        else:
            return {
                "username": self.username,
                "avatar_url": self.avatar_url,
                "content": message
            }

    async def send(self, message: str | None = None, embed: DiscordEmbed | list[DiscordEmbed] | None = None):
        if isinstance(embed, DiscordEmbed):
            embed = [embed]
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=self.get_content(message, embed))
