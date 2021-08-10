import discord
from discord.ext import commands

import io
import traceback
import utils

async def on_command_error(ctx: commands.Context, exception: Exception):
    if isinstance(exception, commands.CommandInvokeError):
        if isinstance(exception.original, discord.Forbidden):
            try: await ctx.send(f'Permissions error: `{exception}`', delete_after=10)
            except discord.Forbidden: pass
            return
        await notify_devs(ctx, exception.original)
    elif isinstance(exception, commands.CheckFailure):
        await ctx.send("You can't do that. " + str(exception), delete_after=10)
    elif isinstance(exception, commands.CommandNotFound):
        pass
    elif isinstance(exception, commands.ConversionError):
        await ctx.send(f"Expected a {exception.converter.__name__}", delete_after=10)
    elif isinstance(exception, commands.BadArgument):
        await ctx.send(''.join(exception.args) or 'Bad argument. No further information was specified.', delete_after=10)
    elif isinstance(exception, commands.UserInputError):
        if hasattr(exception, "message") and exception.message:
            await ctx.send(exception.message, delete_after=10)
        else:
            await ctx.send('Error: {}'.format(' '.join(exception.args)), delete_after=10)
    elif isinstance(exception, commands.CommandOnCooldown):
        await utils.temporary_reaction(ctx, '🛑', exception.retry_after)
    else:
        await notify_devs(ctx, exception)

async def notify_devs(ctx, exception):
    bot = ctx.bot

    info = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
    bot.logger.error('Unhandled command exception - {}'.format(''.join(info)))
    errorfile = discord.File(io.StringIO(''.join(info)), 'traceback.txt')

    cmd = ctx.command
    cog = ctx.cog

    if cmd is None or cog is None:
        await ctx.send(f'{exception}, something happened, one of the devs should check the logs.', file=errorfile)
        return

    devids = []
    if hasattr(cmd.callback, 'devids'):
        cmd_devids = cmd.callback.devids
        devids += [cmd_devids] if isinstance(cmd_devids, int) else cmd_devids
    if hasattr(cog, 'devids'):
        cog_devids = cog.devids
        devids += [cog_devids] if isinstance(cog_devids, int) else cog_devids
    
    devids = set(devids)

    if len(devids) == 0:
        await ctx.send(f'{exception}. btw the creator of this command is a coward.', file=errorfile)
        return

    devs = []
    for devid in devids:
        dev = await bot.fetch_user(devid)
        if dev is not None: devs.append(dev.name)
    
    if devs:
        insert = "one of " if len(devs) > 1 else ""
        await ctx.send(f'{exception}. You should probably inform {insert}{", ".join(devs)}.', file=errorfile)
    else:
        await ctx.send(f'{exception}, but I couldn\'t find the creator of this command.', file=errorfile)

def setup(bot):
    bot.add_listener(on_command_error)