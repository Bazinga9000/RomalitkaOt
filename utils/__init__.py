import discord
from discord.ext import commands

import asyncio
from asyncio import sleep
from io import BytesIO, StringIO
from typing import Optional

class Dev:
    """
    Enums of Dev user IDs
    """
    BAZINGA_9000 = 137001076284063744
    HANSS314 = 240995021208289280
    SOM1SEZHI = 152933723543830529

def cmd_props(**kwargs):
    """
    Decorator attaches properties onto the command callback, so that additional data can be added for Nessie use.
    authors (list[int]): mark authors of command
    signatures (list[str | tuple(str, str)]): overrides default signature
    """
    authors = kwargs.pop("authors", None)
    def decorator(o):
        fn = o
        if isinstance(o, commands.Command):
            fn = o.callback
            
        if authors: fn.devids = authors
        fn.__dict__.update(kwargs)
        return o
    return decorator

async def temporary_reaction(ctx: commands.Context, emoji, secs):
    """
    Reaction that shows up for a temporary amount of time
    """
    await ctx.message.add_reaction(emoji)
    await sleep(secs)
    await ctx.message.remove_reaction(emoji, ctx.bot.user)

async def multireaction(bot: commands.Bot, msg: discord.Message, emojis: "list[discord.Emoji | discord.PartialEmoji | str]", *, allowed_users: "list[int]" = None, check = None, timeout = None) -> "tuple[Optional[discord.Reaction], Optional[discord.User]]":
    """
    Multiple reactions that record the first clicked reaction of the reactions (This is based off which reaction a user adds to)
    """

    def c(rxn, user):
        return rxn not in emojis \
           and user != bot.user \
           and (user.id in allowed_users if allowed_users else True) \
           and rxn.message == msg \
           and (check(rxn, user) if callable(check) else True)

    already_emoji: "list[discord.Emoji]" = [r.emoji for r in msg.reactions]
    for emoji in emojis:
        if emoji not in already_emoji:
            await msg.add_reaction(emoji)

    try:
        result = await bot.wait_for("reaction_add", check=c, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return (None, None)

async def get_reply(ctx):
    """
    Return the reply message if the ctx message is replying to some message,
    otherwise return None
    """
    reference = ctx.message.reference
    if reference is not None:
        if reference.cached_message is not None:
            return reference.cached_message
        elif reference.message_id is not None:
            channel = ctx.bot.get_channel(reference.channel_id)
            return await channel.fetch_message(reference.message_id)

def im2file(im, filename, format="PNG", *, spoiler=False, **im_params) -> discord.File:
    file = BytesIO()
    im.save(file, format, **im_params)
    file.seek(0)
    return discord.File(file, filename=filename, spoiler=spoiler)

class OneOf:
    def casenorm(self, s):
        return s.lower() if self.ci else s

    def __init__(self, *allowed, case_insensitive=True):
        self.allowed = allowed
        self.ci = case_insensitive
        self.map = lambda a: a

    def __call__(self, arg):
        for k in self.allowed:
            if self.casenorm(k) == self.casenorm(arg): return self.map(k)

        formatting = ', '.join(f"`{k}`" for k in self.allowed)
        raise commands.BadArgument(f"Argument is not one of {formatting}")
    
    @classmethod
    def enum(cls, enum, case_insensitive=True):
        allowed = enum._member_map_.keys()
        o = cls(*allowed, case_insensitive=case_insensitive)
        o.map = lambda a: enum[a]
        
        return o

async def send_long(ctx, msg, warn=""):
    """
    Sends a message, or a file if msg is too long
    """
    if len(msg) <= 2000:
        return await ctx.send(msg)
        
    outfile = discord.File(StringIO(msg), 'output.txt')
    await ctx.send(warn, file=outfile)

class PuzzlebotCogMeta(commands.CogMeta):
    def __new__(cls, clsname, bases, attrs, **kwargs):
        if "cat" in kwargs: attrs["nesscat"] = kwargs.pop("cat")
        return super(PuzzlebotCogMeta, cls).__new__(cls, clsname, bases, attrs, **kwargs)

class PuzzlebotCog(commands.Cog, metaclass=PuzzlebotCogMeta):
    pass