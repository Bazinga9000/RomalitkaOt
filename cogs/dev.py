import discord
from discord.ext import commands

import asyncio
import importlib
import utils
import subprocess
import sys

from utils import Dev

DELETE_THRESHOLD = 3

class Developer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.devid = [Dev.HANSS314]
        #self.dthresh = bot.config['delete_react_threshold']

    @commands.Cog.listener('on_raw_reaction_add')
    async def check_delete(self, payload):
        pemoji = payload.emoji
        if pemoji.name != '❌': return
        chan = self.bot.get_channel(payload.channel_id)
        message = await chan.fetch_message(payload.message_id)
        for reac in message.reactions:
            if reac.emoji == pemoji.name and reac.count >= DELETE_THRESHOLD and \
                    message.author.id == self.bot.user.id and not reac.me:
                await message.delete()
                return

    @commands.command(aliases=['git_pull'])
    async def update(self, ctx, *, ext=None):
        '''Updates the bot from git'''

        await ctx.send(':warning: Warning! Pulling from git!')

        if sys.platform == 'win32':
            process = subprocess.run('git pull', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.stdout, process.stderr
        else:
            process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE,
                                                           stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
        stdout = stdout.decode().splitlines()
        stdout = '\n'.join('+ ' + i for i in stdout)
        stderr = stderr.decode().splitlines()
        stderr = '\n'.join('- ' + i for i in stderr)

        await ctx.send('`Git` response: ```diff\n{}\n{}```'.format(stdout, stderr))
        if ext:
            await self.reload(ctx, ext=ext)

    @commands.group(invoke_without_command=True)
    async def reload(self, ctx, *, ext):
        """
        Reloads an extension
        """
        logger = self.bot.logger

        if "." not in ext: ext = "cogs." + ext
        logger.info("Reloading %s", ext)
        try:
            ctx.bot.reload_extension(ext)
        except commands.ExtensionNotLoaded:
            await self.load(ctx, ext=ext)
        except Exception as e:
            await ctx.send(f'Failed to load: `{ext}`\n```py\n{e}\n```')
            logger.error("Error while reloading %s", ext, exc_info=e)
        else:
            logger.info("Reloaded %s!", ext)
            print()
            await ctx.send(f'\N{OK HAND SIGN} Reloaded extension `{ext}` successfully')

    @commands.command()
    async def load(self, ctx, *, ext):
        """
        Loads an extension
        """
        logger = self.bot.logger

        if "." not in ext: ext = "cogs." + ext
        logger.info("Loading %s", ext)
        try:
            ctx.bot.load_extension(ext)
        except Exception as e:
            await ctx.send(f'Failed to load: `{ext}`\n```py\n{e}\n```')
            logger.error("Error while loading %s", ext, exc_info=e)
        else:            
            logger.info("Loaded %s!", ext)
            print()
            await ctx.send(f'\N{OK HAND SIGN} **Loaded** extension `{ext}` successfully')

    @commands.command()
    async def unload(self, ctx, *, ext):
        """
        Unloads an extension
        """
        logger = self.bot.logger

        if "." not in ext: ext = "cogs." + ext
        logger.info("Unloading %s", ext)
        try:
            ctx.bot.unload_extension(ext)
        except Exception as e:
            await ctx.send(f'Failed to unload: `{ext}`\n```py\n{e}\n```')
            logger.error("Error while unloading %s", ext, exc_info=e)
        else:
            logger.info("Unloaded %s!", ext)
            print()
            await ctx.send(f'\N{OK HAND SIGN} **Unloaded** extension `{ext}` successfully')

    @reload.command(name='all', invoke_without_command=True)
    async def reload_all(self, ctx):
        """
        Reloads all extensions
        """

        logger = self.bot.logger
        
        importlib.reload(sys.modules["utils"])
        logger.info("Reloading all extensions")
        for ext in ctx.bot.extensions.copy():
            try:
                logger.info("Reloading %s", ext)
                ctx.bot.reload_extension(ext)
                logger.info("Reloaded %s!", ext)
            except Exception as e:
                await ctx.send(f'Failed to load `{ext}`:\n```py\n{e}\n```')
                logger.error("Error while reloading %s", ext, exc_info=e)

        await ctx.send(f'\N{OK HAND SIGN} Reloaded {len(ctx.bot.extensions)} extensions successfully')
    
    @reload.command(name='config')
    async def reload_cfg(self, ctx):
        """
        Reloads the config, useful for updating config values (does not update token or command prefix)
        """

        logger = self.bot.logger
        
        logger.info("Reloading config")
        with open('config/config.yml') as conf_file:
            self.config = self.yaml.load(conf_file)
        logger.info("Reloaded config!")
        await ctx.send(f'\N{OK HAND SIGN} **Reloaded** config successfully')


    @commands.command()
    @utils.cmd_props(authors=[])
    async def version(self, ctx):
        """
        Get Python & d.py version
        """
        lines = (
            f"Python {sys.version}",
            "",
            f"discord.py version: {discord.__version__}"
        )

        await ctx.send("\n".join(lines))
    
def setup(bot):
    bot.add_cog(Developer(bot))
