from discord.ext import commands
import discord
import io
import utils.wordplay_apis as ext

class Externals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def onelook(self, ctx, query, max_results=100):
        '''
        Search OneLook for a word or phrase
        '''
        out = ext.onelook(query, max_results)
        url = out[0]
        num_results = len(out[1])
        results = "\n".join(f"{i[0]}\t[{i[1]}]" for i in out[1])
        await ctx.send(
            f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''}**\n" +
            url,
            file=discord.File(io.StringIO(results), 'results.txt')
        )

    @commands.command()
    async def nutrimatic(self, ctx, query, max_results=100):
        '''
        Search Nutrimatic for a word or phrase
        '''
        out = ext.nutrimatic(query, max_results)
        url = out[0]
        num_results = len(out[1])
        results = "\n".join(out[1])
        await ctx.send(
            f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''}**\n" +
            url,
            file=discord.File(io.StringIO(results), 'results.txt')
        )

    @commands.command()
    async def qat(self, ctx, query, max_results=100):
        '''
        Search Qat for a word or phrase
        '''
        out = ext.qat(query, max_results)
        url = out[0]
        await ctx.send(url)
        for results in out[1].items():
            length = results[0]
            num_results = len(results[1])
            results = "\n".join(results[1])
            await ctx.send(
                f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''} of length {length}**\n",
                file=discord.File(io.StringIO(results), 'results.txt')
            )

    @commands.command(aliases=["ww","regex"])
    async def wordsword(self, ctx, query, dictionary="standard", case_sensitive=False):
        '''
        Search WordsWord for a word or phrase
        '''
        out = ext.regex(query, dictionary, case_sensitive)
        url = out[0]
        num_results = len(out[1])
        results = "\n".join(out[1])
        await ctx.send(
            f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''}**\n" +
            url,
            file=discord.File(io.StringIO(results), 'results.txt')
        )

    @commands.command()
    async def synonyms(self, ctx, *, query):
        '''
        Search Merriam Webster for synonyms of a word or phrase
        '''
        out = ext.synonyms(query)
        num_results = len(out)
        results = "\n".join(out)
        await ctx.send(
            f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''}**\n",
            file=discord.File(io.StringIO(results), 'results.txt')
        )

    @commands.command()
    async def antonyms(self, ctx, *, query):
        '''
        Search Merriam Webster for antonyms of a word or phrase
        '''
        out = ext.antonyms(query)
        num_results = len(out)
        results = "\n".join(out)
        await ctx.send(
            f"**{num_results if num_results != 0 else 'No'} Result{'s' if num_results != 1 else ''}**\n",
            file=discord.File(io.StringIO(results), 'results.txt')
        )

    @commands.command(aliases=["wa"])
    async def wolframalpha(self, ctx, *, query):
        '''
        Run something through Wolfram Alpha
        '''
        out = ext.wolfram_alpha(query)
        results = "".join(out)
        await ctx.send(
            results
        )

    @commands.command(aliases=["break_vigenere"])
    async def breakvigenere(self, ctx, *, query):
        '''
        Attempt to break a vigenere cipher.
        '''
        out = ext.solve_vigenere(query)
        await ctx.send(
            f"Key: `{out[0]}`\nPlaintext: `{out[1]}`"
        )
def setup(bot):
    bot.add_cog(Externals(bot))
