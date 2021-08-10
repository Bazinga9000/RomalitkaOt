import discord
import math
import sys
import io
from discord.ext import commands
from contextlib import redirect_stdout

from importlib import reload
import utils.puzzlesolvers as solvers

def is_square(n):
    return math.sqrt(n) == int(math.sqrt(n))

def strip_grid(grid):
    if grid.startswith("```\n"):
        grid = grid[4:]
    elif grid.startswith("```"):
        grid = grid[3:]

    if grid.endswith("\n```"):
        grid = grid[:-4]
    elif grid.endswith("```"):
        grid = grid[:-3]

    return grid

def get_symboltable(grid, blank):
    grid = grid.replace("\n","")
    return [blank] + list(set(grid.replace(blank, "")))

def print_solved_grid_from_symboltable(sg, symboltable):
    def hook_function(point, n):
        return symboltable[n]

    return solvers.utils.print_to_string(sg, hook_function)


class LogicPuzzles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sudoku(self, ctx, blank, *, grid):
        if len(blank) != 1:
            return await ctx.send("E: The blank symbol must be a single character.")

        grid = strip_grid(grid)

        symboltable = get_symboltable(grid, blank)

        sg = solvers.sudoku.solve(grid, symboltable)

        if sg.solve():
            first_grid = print_solved_grid_from_symboltable(sg, symboltable)
            out = "\n```\n"
            out += first_grid
            out += "\n```"

            if sg.is_unique():
                return await ctx.send("**Unique Solution:**" + out)

            else:
                second_grid = print_solved_grid_from_symboltable(sg, symboltable)
                out += "\n```\n" + second_grid + "\n```"
                return await ctx.send("**Multiple Solutions:**" + out)
        else:
            return await ctx.send("**No solution.**")


def setup(bot):
    reload(solvers)
    bot.add_cog(LogicPuzzles(bot))
