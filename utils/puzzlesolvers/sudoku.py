"""
Sudoku solver. Based on the GRILOPS example.
"""

from z3 import Distinct
import grilops
from grilops.geometry import Point
import math
from . import utils

def solve(grid, symboltable):
    givens = [utils.line_to_symtable(i, symboltable) for i in grid.splitlines()]
    grid_length = len(givens)
    box_length = int(math.sqrt(grid_length))

    sym = grilops.make_number_range_symbol_set(1, grid_length)

    sg = grilops.SymbolGrid(grilops.get_square_lattice(grid_length), sym)

    for y, given_row in enumerate(givens):
        for x, given in enumerate(given_row):
            if given != 0:
                sg.solver.add(sg.cell_is(Point(y, x), sym[given]))

    for y in range(grid_length):
        sg.solver.add(Distinct(*[sg.grid[Point(y, x)] for x in range(grid_length)]))

    for x in range(grid_length):
        sg.solver.add(Distinct(*[sg.grid[Point(y, x)] for y in range(grid_length)]))

    for z in range(grid_length):
        top = (z // box_length) * box_length
        left = (z % box_length) * box_length
        cells = [sg.grid[Point(y, x)] for y in range(top, top + box_length) for x in range(left, left + box_length)]
        sg.solver.add(Distinct(*cells))

    return sg