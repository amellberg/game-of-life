# A Python implementation of Game of Life using curses.
# The main idea is to iterate over every living cell, going through each of
# the nine neighboring points to see how many of these are cells, and how many
# cells that each such neighboring point have living next to it. To not waste
# time recomputing this data for points that have already been looked at, we
# keep a cache around. Since new cells can spawn only in the neighboring
# vicinity of living cells, we are sure to capture the occurrence of new life
# without traversing the entire world grid.
#    All living cells are tracked by a hash table ('cells', a Python dict),
# mapping their coordinates (represented by Point:s) to the cell objects. The
# program uses a cache ('proc') to keep track of points investigated before,
# implemented as a hash table, with keys being just the points and a boolean
# value indicating whether the point is a cell or not (this value is just a
# convenience, saving only a constant lookup time to 'cells'; the real reason
# for keeping a cache, as already pointed out, is to prevent having to rescan
# all neighboring points of a point, counting how many of them are cells).
#    There is a certain ugliness to the design of the program in that the
# counting of cell neighbors for all living cells is done as part of the
# check_neighbors function, while the counting of cell neighbors for empty
# points is separated out into num_cell_neighbors. One alternative that would
# result in a better design but most likely a slower execution would be to
# make two passes over all neighbor points of a cell: one counting how many of
# these points are cells, and one for processing each such point (which
# involves determining how many of the neighbors of the point are cells). This
# latter alternative would make use of num_cell_neighbors in both passes. I
# decided to keep my original design, and also not to spend more time looking
# for better implementations. The program already seems fast enough.

import curses
from collections import namedtuple
from time import sleep

# An arbitrary point with integer coordinates
Point = namedtuple("Point", ["x", "y"])

# Represents an alive cell; has a position (of type Point) and a generation
# number (a nonnegative integer)
Cell = namedtuple("Cell", ["pos", "gen"])

dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
rows = 0
cols = 0

def align_point(point):
    return Point(point.x % (cols - 1), point.y % (rows - 1))

def num_cell_neighbors(point, cells):
    n = 0
    for d in dirs:
        np = align_point(Point(*tuple(map(lambda x, y: x + y, point, d))))
        n += 1 if np in cells else 0
    return n

def check_neighbors(cell, cells, proc):
    n = 0        # Number of neighboring points of cell that already are cells
    births = []  # Neighboring points of cell that will become cells

    for d in dirs:  # Check each neighbor point
        np = align_point(Point(*tuple(map(lambda x, y: x + y, cell.pos, d))))
        if np in proc:
            n += 1 if proc[np] else 0
        else:  # Point hasn't been investigated before
            is_cell = False
            if np in cells:
                n += 1
                is_cell = True
            elif num_cell_neighbors(np, cells) == 3:
                births.append(np)
            proc[np] = is_cell
    return n, births

def compute_life(cells, gen):
    proc = {}  # Points looked at during this cycle; key=Point, value=bool
    cells_next = {}

    for cell in cells.values():
        n, births = check_neighbors(cell, cells, proc)
        if n in {2, 3}:
            cells_next[cell.pos] = cell
        for pos in births:
            cells_next[pos] = Cell(pos, gen + 1)

    return cells_next

def main(stdscr):
    global rows
    global cols
    rows = curses.LINES
    cols = curses.COLS
    origo = Point(int(cols / 2), int(rows / 2))
    gen = 0  # Generation number

    seed = [(-1,0), (0,0), (0,-1), (0,1), (1,1)]  # R-Pentomino; really cool
    #seed = [(-4,0), (-3,0), (0,0), (1,0), (2,0), (-1,-1), (-3,-2)]  # Acorn
    #seed = [(-40,15),(-40,14),(-40,13)]
    seed_t = [Point(origo.x + x, origo.y - y) for (x, y) in seed]
    cells = {Point(*p): Cell(Point(*p), gen) for p in seed_t}
    #cells = compute_life(cells, gen)

    win = curses.newwin(rows, cols)
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    while True:
        win.clear()
        for cell in cells.values():
            win.addch(cell.pos.y, cell.pos.x, curses.ACS_DIAMOND,
                    curses.color_pair(cell.gen % 7 + 1))
        win.refresh()
        cells = compute_life(cells, gen)
        gen += 1
        sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
