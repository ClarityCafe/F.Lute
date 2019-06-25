from discord import TextChannel, Message, Reaction, Member

from bot.bot import MusicBot
from bot.structures.config import Config


def event(emote: str):
    def decorator(func):
        func.listen_emote = emote
        return func

    return decorator


def event_class(cls):
    cls.events = {}
    for attr in cls.__dict__.values():
        if hasattr(attr, "listen_emote"):
            cls.events[attr.listen_emote] = attr
    return cls


class MenuContext:
    # Handles events on messages based on emotes

    id = ""
    message: str = "<placeholder>"
    msg_object: Message = None

    def __init__(self, channel: TextChannel, bot: MusicBot):
        self.channel = channel
        self.bot = bot

    async def set_message(self, msg: str):
        self.message = f"**{self.id}**```{msg}```"
        await self.msg_object.edit(content=self.message)

    async def pull_from_channel(self):
        async for message in self.channel.history():
            if message.author.id == self.bot.bot_id and message.content.startswith(f"**{self.id}**"):
                self.msg_object = message
                break

    async def setup(self):
        await self.pull_from_channel()

        if self.msg_object is None:
            self.msg_object = await self.channel.send(self.message)
        else:
            await self.load()

        for emote in self.events:
            await self.msg_object.add_reaction(emote)

    async def load(self):
        pass

    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if not isinstance(user, Member) or user.bot or reaction.message.id != self.msg_object.id:
            return  # Ignore DMs and Bots and other channels

        await reaction.remove(user)

        if reaction.emoji in self.events:
            await self.events[reaction.emoji](self)
