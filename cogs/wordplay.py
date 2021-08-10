import json
from discord.ext import commands
import discord
import random
import regex
import io
import requests
import string

# display names of databases
database_display_names = {
    "words": "Words",
    "pokemon": "Pokémon",
    "magic": "Magic Card"
}

# aliases from terms to fields
aliases = {
    # common
    "word": "w",
    "length": "l",
    "len": "l",
    "scrabblescore": "s",
    "scrabble": "s",
    "anagram": "a",
    "bank": "b",
    "unique": "b",
    "re": "regex",

    # wp corpus
    "frequency": "f",
    "freq": "f",

    # pokemon
    "health": "hp",
    "attack": "atk",
    "defense": "def",
    "spattack": "spatk",
    "sp_attack": "spatk",
    "specialattack": "spatk",
    "special_attack": "spatk",
    "sp_atk": "spatk",
    "specialatk": "spatk",
    "special_atk": "spatk",
    "spdefense": "spdef",
    "sp_defense": "spdef",
    "specialdefense": "spdef",
    "special_defense": "spdef",
    "sp_def": "spdef",
    "specialdef": "spdef",
    "special_def": "spdef",
    "speed": "spd",
    "gen": "generation",
    "shape_sci": "shape_awesome",
    "shape_scientific": "shape_awesome",
    "type": "types",

    # magic
    "manacost": "mana_cost",
    "convertedmanacost": "cmc",
    "converted_mana_cost": "cmc",
    "manavalue": "cmc",
    "mv": "cmc"

}
# Mappings from fields in user commands to internal database names

# Fields that actually exist in databases
direct_fields = [
    "w", "l", "s", "a", "b",  # common to all databases
    "f",  # wikipedia corpus (words)

    "height", "weight", "exp", "hp", "atk", "def", "spatk", "spdef", "spd", "types", "species",
    "generation", "region", "prev_evo", "next_evo", "color", "shape", "shape_awesome", "habitat", "capture_rate",
    "base_happiness", "is_legendary", "is_mythical", "genus", "dex", "regional_dex",  # pokemon

    "full_name", "color_identity", "colors", "cmc", "mana_cost", "types", "supertypes",
    "subtypes", "layout", "side", "has_variable_power", "power", "has_variable_toughness", "toughness",
    "has_variable_loyalty", "loyalty", "hand", "life", "keywords", "legal_in", "restricted_in",
    "banned_in", "not_legal_in", "leadershipskills", "reserved_list", "printings"  # magic
]

# dictionary containing the various functions that compare your given parameter against the value in the database
direct_query_lambdas = {
    "=": lambda field, arg: lambda x: x[field] is not None and x[field] == arg,
    "!=": lambda field, arg: lambda x: x[field] is not None and x[field] != arg,
    ">": lambda field, arg: lambda x: x[field] is not None and x[field] > arg,
    ">=": lambda field, arg: lambda x: x[field] is not None and x[field] >= arg,
    "<": lambda field, arg: lambda x: x[field] is not None and x[field] < arg,
    "<=": lambda field, arg: lambda x: x[field] is not None and x[field] <= arg,
    "|>": lambda field, arg: lambda x: x[field] is not None and x[field] in arg,
    "<|": lambda field, arg: lambda x: x[field] is not None and arg in x[field],
    "!|>": lambda field, arg: lambda x: x[field] is not None and x[field] not in arg,
    "!<|": lambda field, arg: lambda x: x[field] is not None and arg not in x[field],
    "<|>": lambda field, arg: lambda x: x[field] is not None and x[field] in arg or arg in x[field],
    "!<|>": lambda field, arg: lambda x: x[field] is not None and x[field] not in arg and arg not in x[field],
    "?": lambda field, arg: lambda x: x[field] is not None,
    "!?": lambda field, arg: lambda x: x[field] is None
}

# what different comparators are allowed for a given field/query
ALL_COMPARATORS = ["=", "!=", ">", ">=", "<", "<=", "|>", "<|", "!|>", "!<|", "<|>", "!<|>", "?", "!?"]
FULL_INT_COMPARISON = ["=", "!=", ">", ">=", "<", "<=", "?", "!?"]
FULL_STRING_COMPARISON = FULL_INT_COMPARISON + ["|>", "<|", "!|>", "!<|", "<|>", "!<|>", "?", "!?"]
EQUALITY_ONLY = ["=", "!=", "?", "!?"]
BINARY_FUNCTION = ["=", "!="]
COLON_ONLY = [":"]

valid_comparators = {
    # common fields
    "w": FULL_STRING_COMPARISON,
    "l": FULL_INT_COMPARISON,
    "s": FULL_INT_COMPARISON,
    "a": EQUALITY_ONLY,  # comparison between anagram strings makes no sense because each string is an equiv. class
    "b": EQUALITY_ONLY,  # see above

    # words
    "f": FULL_INT_COMPARISON,

    # pokemon
    "height": FULL_INT_COMPARISON,
    "weight": FULL_INT_COMPARISON,
    "exp": FULL_INT_COMPARISON,
    "hp": FULL_INT_COMPARISON,
    "atk": FULL_INT_COMPARISON,
    "def": FULL_INT_COMPARISON,
    "spatk": FULL_INT_COMPARISON,
    "spdef": FULL_INT_COMPARISON,
    "spd": FULL_INT_COMPARISON,
    "types": FULL_STRING_COMPARISON,
    "species": FULL_STRING_COMPARISON,
    "generation": FULL_INT_COMPARISON,
    "region": FULL_INT_COMPARISON,
    "prev_evo": FULL_STRING_COMPARISON,
    "next_evo": FULL_STRING_COMPARISON,
    "color": FULL_STRING_COMPARISON,
    "shape": FULL_STRING_COMPARISON,
    "shape_awesome": FULL_STRING_COMPARISON,
    "habitat": FULL_STRING_COMPARISON,
    "capture_rate": FULL_INT_COMPARISON,
    "base_happiness": FULL_INT_COMPARISON,
    "is_legendary": EQUALITY_ONLY,
    "is_mythical": EQUALITY_ONLY,
    "genus": FULL_STRING_COMPARISON,
    "dex": FULL_INT_COMPARISON,
    "regional_dex": FULL_INT_COMPARISON,

    # magic
    "full_name": FULL_STRING_COMPARISON,
    "color_identity": FULL_STRING_COMPARISON,
    "colors": FULL_STRING_COMPARISON,
    "cmc": FULL_INT_COMPARISON,
    "mana_cost": FULL_STRING_COMPARISON,
    # types already present in pokemon
    "supertypes": FULL_STRING_COMPARISON,
    "subtypes": FULL_STRING_COMPARISON,
    "layout": FULL_STRING_COMPARISON,
    "side": FULL_STRING_COMPARISON,
    "has_variable_power": EQUALITY_ONLY,
    "power": FULL_INT_COMPARISON,
    "has_variable_toughness": EQUALITY_ONLY,
    "toughness": FULL_INT_COMPARISON,
    "has_variable_loyalty": EQUALITY_ONLY,
    "loyalty": FULL_INT_COMPARISON,
    "hand": FULL_INT_COMPARISON,
    "life": FULL_INT_COMPARISON,
    "keywords": FULL_STRING_COMPARISON,
    "legal_in": FULL_STRING_COMPARISON,
    "restricted_in": FULL_STRING_COMPARISON,
    "banned_in": FULL_STRING_COMPARISON,
    "not_legal_in": FULL_STRING_COMPARISON,
    "leadershipskills": FULL_STRING_COMPARISON,
    "reserved_list": EQUALITY_ONLY,
    "printings": FULL_STRING_COMPARISON,

    # the special queries are all here, at the end of this dictionary
    "subanagram": COLON_ONLY,
    "superanagram": COLON_ONLY,
    "transdelete": COLON_ONLY,
    "transadd": COLON_ONLY,
    "subbank": COLON_ONLY,
    "superbank": COLON_ONLY,
    "delete": COLON_ONLY,
    "add": COLON_ONLY,
    "change": COLON_ONLY,
    "regex": BINARY_FUNCTION
}

# those fields which are integers
INTEGER_FIELDS = [
    "l", "s",  # common
    "f",  # words

    "height", "weight", "exp", "hp", "atk", "def", "spatk", "spdef", "spd", "generation",
    "capture_rate", "base_happiness", "dex", "regional_dex",  # pokemon

    "cmc", "power", "toughness", "loyalty", "hand", "life", # magic
]

# display names for fields in 'get
DISPLAY_NAMES = {
    # common fields
    "w": "Word",
    "l": "Length",
    "s": "Scrabble Score",
    "a": "Sorted Alphabetically",
    "b": "Unique Letters",

    # words
    "f": "Frequency on Wikipedia",

    # pokemon
    "height": "Height",
    "weight": "Weight",
    "exp": "Base EXP Gained",
    "hp": "HP",
    "atk": "Attack",
    "def": "Defense",
    "spatk": "Special Attack",
    "spdef": "Special Defense",
    "spd": "Speed",
    "types": "Type",
    "species": "Species",
    "generation": "Gen. of Origin",
    "region": "Region of Origin",
    "prev_evo": "Prev. Evolution",
    "next_evo": "Next Evolution",
    "color": "Color",
    "shape": "Shape",
    "shape_awesome": "Shape (Sci.)",
    "habitat": "Habitat",
    "capture_rate": "Capture Rate",
    "base_happiness": "Base Happiness",
    "is_legendary": "Is Legendary?",
    "is_mythical": "Is Mythical?",
    "genus": "Genus",
    "dex": "National Dex No.",
    "regional_dex": "Regional Dex No.",

    # magic
    "full_name": "Full Name",
    "color_identity": "Color Identity",
    "colors": "Colors",
    "cmc": "Converted Mana Cost",
    "mana_cost": "Mana Cost",
    # types already present in pokemon
    "supertypes": "Supertypes",
    "subtypes": "Subtypes",
    "layout": "Card Layout",
    "side": "MFC Side",
    "has_variable_power": "Variable Power?",
    "power": "Power",
    "has_variable_toughness": "Variable Toughness?",
    "toughness": "Toughness",
    "has_variable_loyalty": "Variable Loyalty?",
    "loyalty": "Loyalty",
    "hand": "Hand Modifier",
    "life": "Life Modifier",
    "keywords": "Keywords",
    "legal_in": "Legal Formats",
    "restricted_in": "Restricted Formats",
    "banned_in": "Banned Formats",
    "not_legal_in": "Illegal Formats",
    "leadershipskills": "Commander Legal Formats",
    "reserved_list": "Reserved?",
    "printings": "Sets Printed In"
}

SPECIAL_REGEX_TOKENS = {
    "\\P": "(he|li|be|ne|na|mg|al|si|cl|ar|ca|sc|ti|cr|mn|fe|co|ni|cu|zn|ga|ge|as|se|br|kr|rb|sr|zr|nb|mo|tc|ru|rh|pd"
           "|ag|cd|in|sn|sb|te|xe|cs|ba|la|ce|pr|nd|pm|sm|eu|gd|tb|dy|ho|er|tm|yb|lu|hf|ta|re|os|ir|pt|au|hg|tl|pb|bi"
           "|po|at|rn|fr|ra|ac|th|pa|np|pu|am|cm|bk|cf|es|fm|md|no|lr|rf|db|sg|bh|hs|mt|ds|rg|cn|nh|fl|mc|lv|ts|og|h|b"
           "|c|n|o|f|p|s|k|v|y|i|w|u)"  # match an element on the periodic table
}


def to_anagram(string):
    return "".join(sorted(string))


def to_unique_bank(string):
    return "".join(sorted("".join(set(string))))


def split_query(query):
    for comp in sorted(ALL_COMPARATORS, key=lambda x: len(x), reverse=True):
        parted = query.partition(comp)
        if parted != (query, "", ""):
            return parted


def query_to_function(query):
    args = split_query(query)
    if args is None:
        raise ValueError(f"Invalid query: {query}")
    given_field_query = args[0]
    field_query, comparator, argument = args
    if field_query in aliases:
        field_query = aliases[field_query]

    if field_query not in valid_comparators.keys():
        raise ValueError(f"Error: Unknown search criteria `{field_query}` in query `{query}`")

    if comparator not in valid_comparators[field_query]:
        raise ValueError(
            f"Error: `{comparator}` cannot be used when when searching for `{given_field_query}` in query `{query}`.")

    if field_query in direct_fields:
        if field_query == "a":
            argument = to_anagram(argument)
        elif field_query == "b":
            argument = to_unique_bank(argument)

        if field_query in INTEGER_FIELDS:
            try:
                argument = int(argument)
            except:
                raise ValueError(f"Error: Unable to coerce argument `{argument}` to integer in query `{query}`")

        return direct_query_lambdas[comparator](field_query, argument)

    elif field_query == "regex":
        pattern = argument
        for token, replacement in SPECIAL_REGEX_TOKENS.items():
            pattern = pattern.replace(token, replacement)

        if comparator == "=":
            return lambda x: regex.match(pattern, x["w"]) is not None
        elif comparator == "!=":
            return lambda x: regex.match(pattern, x["w"]) is None
        else:
            # This should never happen!
            raise ValueError(f"This message should never appear, ping bazinga if it does.")


class Wordplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.databases = {}
        self.database_lengths = {}
        self.database_list = ["words", "pokemon", "magic"]
        for db in self.database_list:
            with open(f"assets/data/{db}.json") as f:
                data = json.load(f)
                self.databases[db] = data
                self.database_lengths[db] = len(data)
            print(f"[WORDPLAY] Loaded the {db} database.")

    @commands.command()
    async def get(self, ctx, database, word):
        '''
        Get the data on a single word.
        '''
        if database not in self.database_list:
            return await ctx.send(
                f"Error: `{database}` is not a valid database. The valid databases are `{', '.join(self.database_list)}`.")

        try:
            data = self.databases[database][word]
        except KeyError:
            return await ctx.send(f"Error: `{word}` was not found in the `{database}` database.")

        color = random.randint(0, 0xffffff)
        num_fields = 0
        nones = []
        embed = discord.Embed(title=f"{database_display_names[database]} Query", color=color)
        for field in data:
            if DISPLAY_NAMES[field] is not None:
                if data[field] is not None:
                    embed.add_field(name=DISPLAY_NAMES[field], value=data[field], inline=True)
                    num_fields += 1
                    if (num_fields % 25) == 0:
                        await ctx.send(embed=embed)
                        embed = discord.Embed(title="", color=color)
                else:
                    nones.append(DISPLAY_NAMES[field])
        if (num_fields % 25) != 0: await ctx.send(embed=embed)

        if len(nones) != 0:
            nones = [f"`{i}`" for i in nones]
            await ctx.send("Empty Fields: " + ", ".join(nones) + ".")

    @commands.command()
    async def query(self, ctx, database, *queries):
        '''
        Query the databases to find words fitting some pattern.

        Full documentation can be found here: [THIS WILL EXIST SOON]
        '''
        if database not in self.database_list:
            return await ctx.send(
                f"Error: `{database}` is not a valid database. The valid databases are `{', '.join(self.database_list)}`.")

        try:
            qfunctions = [query_to_function(q) for q in queries]
        except ValueError as e:
            return await ctx.send(e)

        hits = []
        num_hits = 0

        for word in self.databases[database].values():
            if all(qf(word) for qf in qfunctions):
                num_hits += 1
                hits.append(word["w"])

        if len(hits) == 0:
            return await ctx.send("**No results.**")

        hits_string = "{0:,}".format(num_hits)
        r = "Result" if num_hits == 1 else "Results"
        database_percentage = 100 * num_hits / self.database_lengths[database]
        db_perc_string = "%.4g" % database_percentage
        return await ctx.send(
            f"**{hits_string} {r} ({db_perc_string}% of Database)**",
            file=discord.File(io.StringIO('\n'.join(hits)), 'results.txt')
        )

    @commands.command(aliases=["rot","ceasar"])
    async def caesar(self, ctx, *, text):
        '''
        Produces all caesar shifts of a given piece of text.
        '''
        def rot(l, n):
            if l in string.ascii_lowercase:
                return chr(ord("a") + ((ord(l) - ord("a") + n + 26) % 26))
            elif l in string.ascii_uppercase:
                return chr(ord("A") + ((ord(l) - ord("A") + n + 26) % 26))
            else:
                return l
        out = "```\n"
        for shift in range(26):
            if len(out) > 1800:
                out += "```"
                await ctx.send(out)
                out = "```\n"
            newtext = "".join(rot(char, shift) for char in text)
            out += f"{('+' + str(shift)).rjust(3)}: {newtext}\n"
        out += "```"
        await ctx.send(out)

def setup(bot):
    bot.add_cog(Wordplay(bot))
