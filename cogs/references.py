from discord.ext import commands
import discord
import glob

class References(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_image(self, ctx, filename, message=""):
        with open(f"assets/refs/{filename}", "rb") as f:
            await ctx.send(message, file=discord.File(f))

    @commands.command()
    async def braille(self, ctx):
        '''
        Display a reference for Braille.
        '''
        return await self.send_image(ctx, "braille.png")

    @commands.command()
    async def morebraille(self, ctx):
        '''
        Display an even bigger reference for Braille.
        '''
        return await self.send_image(ctx, "morebraille.png")

    @commands.command()
    async def pigpen(self, ctx):
        '''
        Display a reference for the Pigpen Cipher.
        '''
        return await self.send_image(ctx, "pigpen.png")

    @commands.command(aliases=["asl"])
    async def sign(self, ctx):
        '''
        Display a reference for American Sign Language.
        '''
        return await self.send_image(ctx, "asl.png")

    @commands.command()
    async def semaphore(self, ctx):
        '''
        Display a reference for Flag Semaphore.
        '''
        return await self.send_image(ctx, "semaphore.png")

    @commands.command(aliases=["aminoacids"])
    async def amino(self, ctx):
        '''
        Display a reference for Amino Acid Codes.
        '''
        return await self.send_image(ctx, "amino.png")

    @commands.command()
    async def greek(self, ctx):
        '''
        Display a reference for the Greek Alphabet.
        '''
        return await self.send_image(ctx, "greek.png")

    @commands.command()
    async def hebrew(self, ctx):
        '''
        Display a reference for the Hebrew Alphabet.
        '''
        return await self.send_image(ctx, "hebrew.png")

    @commands.command(aliases=["kana"])
    async def japanese(self, ctx):
        """
        Display a reference for Japanese Kana.
        """
        await self.send_image(ctx, "hiragana.png")
        return await self.send_image(ctx, "katakana.png")

    @commands.command()
    async def moon(self, ctx):
        """
        Display a reference for Moon Script.
        """
        return await self.send_image(ctx, "moon.png")

    @commands.command(aliases=["morse_code"])
    async def morse(self, ctx):
        """
        Display a reference for Morse Code.
        """
        return await self.send_image(ctx, "morse_code.png")

    @commands.command()
    async def nato(self, ctx):
        """
        Display a reference for the NATO Phonetic Alphabet.
        """
        return await self.send_image(ctx, "nato.png")

    @commands.command(aliases=["color_codes", "colorcodes"])
    async def resistor(self, ctx):
        """
        Display a reference for Resistor Color Codes.
        """
        return await self.send_image(ctx, "resistor.png")

    @commands.command()
    async def scrabble(self, ctx, language="english"):
        """
        Display a reference for Scrabble (in various languages).
        """
        if language == "list":
            filenames = glob.glob("assets/refs/scrabble/*.png")
            outputs = [i.replace("assets/refs/scrabble/","")[:-4] for i in filenames]
            return await ctx.send(f"```\n{' '.join(sorted(outputs))}\n```")
        try:
            return await self.send_image(ctx, f"scrabble/{language}.png")
        except:
            return await ctx.send(f"Invalid langauge {language}.")

    @commands.command()
    async def dvorak(self, ctx):
        """
        Display a reference for the Dvorak Keyboard Layout.
        """
        return await self.send_image(ctx, "dvorak.png")

    @commands.command()
    async def colemak(self, ctx):
        """
        Display a reference for the Colemak Keyboard Layout.
        """
        return await self.send_image(ctx, "colemak.png")

    @commands.command()
    async def workman(self, ctx):
        """
        Display a reference for the Workman Keyboard Layout.
        """
        return await self.send_image(ctx, "workman.png")

    @commands.command()
    async def spacecadet(self, ctx):
        """
        Display a reference for the Space Cadet Keyboard Layout.
        """
        return await self.send_image(ctx, "spacecadet.png", message="The bottom right symbol is the front-of-key symbol.")

    @commands.command()
    async def ascii(self, ctx):
        """
        Display a reference for the ASCII Character Set.
        """
        return await self.send_image(ctx, "ascii.png")

    @commands.command()
    async def binary(self, ctx):
        """
        Display a reference for the Binary Alphabet.
        """
        return await self.send_image(ctx, "binary.jpeg")

def setup(bot):
    bot.add_cog(References(bot))
