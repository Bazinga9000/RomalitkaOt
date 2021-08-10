import traceback
import logging
import os
import sys

import discord

from discord.ext import commands
from ruamel.yaml import YAML
from pathlib import Path

class Bot(commands.Bot):
    def __init__(self, command_prefix='[', *args, **kwargs):
        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        self.yaml = YAML(typ='safe')
        with open('config/config.yml') as conf_file:
            self.config = self.yaml.load(conf_file)

        if 'command_prefix' in self.config:
            command_prefix = self.config['command_prefix']

        am = discord.AllowedMentions(everyone=False, replied_user=False, roles=False)
        #intents = discord.Intents.all()
        #super().__init__(command_prefix=command_prefix, allowed_mentions=am, intents=intents, *args, **kwargs)
        super().__init__(command_prefix=command_prefix, allowed_mentions=am, *args, **kwargs)

    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        info = traceback.format_exception(*info, chain=False)
        self.logger.error('Unhandled exception - {}'.format(''.join(info)))

    async def on_ready(self):
        self.logger.info(f'Connected to Discord')
        self.logger.info(f'Guilds  : {len(self.guilds)}')
        self.logger.info(f'Channels: {len(list(self.get_all_channels()))}')

    def load_module(self, module: str):
        """
        Loads a module
        """
        try:
            self.load_extension(module)
        except Exception as e:
            self.logger.exception(f'Failed to load module {module}:')
            print()
            self.logger.exception(e)
            print()
        else:
            self.logger.info(f'Loaded module {module}.')

    def load_dir(self, directory: str):
        """
        Loads all modules in a directory
        """
        path = Path(directory)
        if not path.is_dir(): 
            self.logger.info(f"Directory {directory} does not exist, skipping")
            return

        modules = [f"{directory}.{p.stem}" for p in path.iterdir() if p.suffix == ".py"]
        for m in modules:
            self.load_module(m)

    def run(self, token):
        self.load_dir("core")
        self.load_dir("cogs")

        self.logger.info(f'Loaded {len(self.cogs)} cogs')
        super().run(token)

if __name__ == '__main__':
    bot = Bot()
    token = open(bot.config['token_file'], 'r').read().split('\n')[0]
    bot.run(token)
