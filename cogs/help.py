import discord
from discord.ext import commands

import itertools
from utils import Dev, PuzzlebotCog

class PBHelp(commands.MinimalHelpCommand):
    # Special semantics
    # To declare a category that encompasses multiple cogs,
    # set the class of the cog to NessieCog (from utils), 
    # and set cat to the specified category
    # (See bottom of this script for example)

    # Category consists of all cogs with the same cat as well as
    # the cog that shares the same name as the category (if it
    # exists)
    def __init__(self):
        super().__init__(command_attrs={
            "help": """\
                This help message

                (Help, I'm stuck in a Discord bot!)
            """
        })

    async def command_callback(self, ctx, *, command=None):
        """|coro|

        The actual implementation of the help command.

        It is not recommended to override this method (oh well!) and instead change
        the behaviour through the methods that actually get dispatched.

        - :meth:`send_bot_help`
        - :meth:`send_nesscat_help`*
        - :meth:`send_group_help`
        - :meth:`send_command_help`
        - :meth:`get_destination`
        - :meth:`command_not_found`
        - :meth:`subcommand_not_found`
        - :meth:`send_error_message`
        - :meth:`on_help_command_error`
        - :meth:`prepare_help_command`
        """
        await self.prepare_help_command(ctx, command)
        bot: commands.Bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        maybe_coro = discord.utils.maybe_coroutine

        # Check for command first
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            # category check
            cat_match = next((c for c in self.all_cats if c.lower() == command.lower()), None)

            if cat_match:
                return await self.send_nesscat_help(cat_match)

            string = await maybe_coro(self.command_not_found, self.remove_mentions(keys[0]))
            return await self.send_error_message(string)

        # Subcommand check
        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)
    
    async def send_pages(self):
        """A helper utility to send the page output from :attr:`paginator` to the destination."""
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(page, allowed_mentions=discord.AllowedMentions.none())

    async def send_bot_help(self, mapping):
        # force Misc at the end, sort rest by alphabetical
        cats = sorted(self.all_cats, key=lambda k: (k == "Misc", k))

        self.paginator.add_line("**Categories:**")
        width = max([len(cat) for cat in cats]) + 2
        
        for left, right in zip(cats[0::2], cats[1::2]):
            self.paginator.add_line(f"`{left}`{' ' * int(2.3 * (width-len(left)))}`{right}`")
        if len(cats) % 2 == 1:
            self.paginator.add_line(f"`{cats[-1]}`")
        self.paginator.add_line()

        self.add_ending_note()
        self.add_disclaimer()
        await self.send_pages()

    async def send_nesscat_help(self, cat):
        cogs = self.cat_cogs(cat)
        cmds = [*itertools.chain.from_iterable(cog.get_commands() for cog in cogs)]

        # if cog is one command, just redirect to there
        if len(cmds) == 1: 
            if isinstance(cmds[0], commands.Group):
                return await self.send_group_help(cmds[0])
            else:
                return await self.send_command_help(cmds[0])

        self.paginator.add_line(f"**{cat} commands:**", empty=True)
        
        #self.add_desc(cog)
        await self.add_subcommand_list(sorted(cmds, key=lambda c: c.name))

        self.add_ending_note()
        await self.send_pages()

    async def send_group_help(self, group):
        self.add_command_heading(group)
        
        self.add_desc(group)
        
        self.paginator.add_line("**Usage:**")

        # main signature
        self.add_command_signatures(group)
        self.paginator.add_line()
        # subcommands (sort by insertion)
        await self.add_subcommand_list(list(dict.fromkeys(group.all_commands.values())))

        self.add_command_aliases(group)
        
        self.paginator.close_page()
        await self.send_pages()

    async def send_command_help(self, command):
        self.add_command_heading(command)
        self.add_desc(command)

        self.paginator.add_line("**Usage:**")
        # signature
        self.add_command_signatures(command)
        self.paginator.add_line()

        self.add_command_aliases(command)
        
        self.paginator.close_page()
        await self.send_pages()

    ## UTILITY COMMANDS ##
    def add_command_heading(self, command):
        parent = command.full_parent_name
        full_cmd = command.name if not parent else parent + ' ' + command.name
        self.paginator.add_line(f"Help for `{self.clean_prefix}{full_cmd}`:", empty=True)

    def add_desc(self, c):
        desc = None
        if hasattr(c, "help"): desc = c.help
        elif hasattr(c, "description"): desc = c.description

        if desc:
            try:
                self.paginator.add_line(desc.strip(), empty=True)
            except RuntimeError:
                for line in desc.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()
    
    def get_command_aliases(self, command):
        aliases = []

        for alias in command.aliases:
                parent = command.full_parent_name
                full_cmd = alias if not parent else parent + ' ' + alias
                aliases.append(f"`{self.clean_prefix}{full_cmd}`")

        return aliases

    def add_command_aliases(self, command):
        aliases = self.get_command_aliases(command)
        if aliases:
            self.paginator.add_line("**Aliases:** {}".format(', '.join(aliases)), empty=True)

    async def can_run(self, command):
        try:
            return await command.can_run(self.context)
        except commands.CommandError:
            return False

    async def add_can_run(self, command):
        if not (await self.can_run(command)):
            self.paginator.add_line("*You cannot run this command.*")

    def add_subcommand_formatting(self, command, italicized=False, cell=0):
        ctext = f"{self.clean_prefix}{command}".ljust(cell)
        fmt = '`{0}` {1}' if command.short_doc else '`{}`'
        if italicized: fmt = f"*{fmt}*"
        self.paginator.add_line(fmt.format(ctext, command.short_doc))

    def get_nesscmd_signatures(self, command) -> "list[tuple[str, str]]":
        cleanse_sig = lambda s: s.strip().replace(" [_]", "")
        if hasattr(command.callback, "signatures"):
            cmd = f"{self.clean_prefix}{command.qualified_name}"

            sigs = []
            for sig in command.callback.signatures:
                info = ""
                if not isinstance(sig, str): sig, info = sig
                sigs.append((
                    cleanse_sig(f"{cmd}{f' {sig}'}"), # signature
                    info.strip() # any shortbox info
                ))
            
            return sigs
        
        else: 
            return [(cleanse_sig(super().get_command_signature(command)), "")]
    
    def add_command_signatures(self, command):
        sigs = self.get_nesscmd_signatures(command)

        #maxlen = max(len(sig if isinstance(sig, str) else sig[0]) for sig in sigs)
        for tpl in sigs:
            sig, info = tpl
            self.paginator.add_line(f"`{sig}` {info}")

    def add_disclaimer(self):
        disc = f'To contribute to the bot, submit a PR at the github repo.\n\n'
        self.paginator.add_line(disc)

    def get_ending_note(self):
        return '`{0}{1} <command>` for in-depth help for a command\n' \
               '`{0}{1} <category>` for commands in a category\n' \
               .format(self.clean_prefix, self.invoked_with)
    
    def add_ending_note(self):
        note = self.get_ending_note()
        if note:
            self.paginator.add_line(note)

    def command_not_found(self, string):
        return f'{string}??? No command called "{string}" found.'

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f'{string}??? Command "{command.qualified_name}" has no subcommand named {string}'
        return f'{string}??? Command "{command.qualified_name}" has no subcommands.'

    @property
    def all_cats(self):
        return set(self.cat_name(cog) for cog in self.context.bot.cogs.values())
    
    def cat_name(self, cog):
        """
        Get the cog name which is normally cog.qualified_name
        """
        if hasattr(cog, "nesscat"): return cog.nesscat
        return cog.qualified_name

    def cat_cogs(self, cat):
        return tuple(cog for cog in self.context.bot.cogs.values() if self.cat_name(cog) == cat)

    async def add_subcommand_list(self, cmds):
        if len(cmds) > 0:
            maxlen = max(len(str(cmd)) + 1 for cmd in cmds)
            for command in cmds:
                self.add_subcommand_formatting(command, False, maxlen)
            self.paginator.add_line()

class Help(PuzzlebotCog, cat="Utils"):
    def __init__(self):
        self.devids = []

def setup(bot):
    helpcog = Help()
    bot.add_cog(helpcog)
    bot.help_command = PBHelp()
    bot.help_command.cog = helpcog
