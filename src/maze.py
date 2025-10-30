import networkx as nx
import os
from enum import Enum

class CellType(Enum):
    FREE = 0
    WALL = 1
    
    @staticmethod
    def from_char(char):
        if char == '#':
            return CellType.WALL
        else:
            return CellType.FREE

        
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise Exception(f"cant add Point to {repr(other)}")

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, Point) and \
              self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def get_adjacent(self):
        return [
            Point(self.x, self.y+1),
            Point(self.x, self.y-1),
            Point(self.x+1, self.y),
            Point(self.x-1, self.y),
        ]

        
def validate_maze_from_grid(grid):
    if not set(map(lambda x: len(x), grid)) != 1:
        raise Exception(f"Cannot create Maze from grid: invalid dimensions") 

    if len(grid) % 2 != 1:
        raise Exception("Invalid maze height")
    if len(grid[0]) % 2 != 1:
        raise Exception("Invalid maze width")

    height = len(grid) // 2
    width  = len(grid[0]) // 2

    #Check that all cells are free
    for cell_x in range(height):
        for cell_y in range(width):
            grid_x = cell_x*2+1
            grid_y = cell_y*2+1
            if grid[grid_x][grid_y] != CellType.FREE:
                raise Exception(f"Cell in maze must be free: ({grid_x, grid_y})")

    #Check that around maze wall
    for cell_x in range(height):
        grid_x = cell_x*2+1
        if not grid[grid_x][0] == grid[grid_x][-1] == CellType.WALL:
            raise Exception(f"Maze border must be a wall")
    
    for cell_y in range(width):
        grid_y = cell_y*2+1
        if not grid[0][grid_y] == grid[-1][grid_y] == CellType.WALL:
            raise Exception(f"Maze border must be a wall")
    

class Maze:
    def __init__(self):
        self.height = 0
        self.width  = 0
        self.graph  = nx.Graph()    
    
    def get_adjacent(self, point):
        adjacent = []
        for adjpoint in point.get_adjacent():
            if adjpoint in self.graph:
                adjacent.append(adjpoint)
        return adjacent

    @classmethod
    def from_size(cls, height, width, empty=True):
        maze = cls()
        maze.height = height
        maze.width  = width
        for cell_x in range(maze.height):
            for cell_y in range(maze.width):
                maze.graph.add_node(Point(cell_x, cell_y))

        if not empty:
            return maze

        for point in maze.graph.nodes:
            for adjpoint in maze.get_adjacent(point):
                maze.graph.add_edge(point, adjpoint)

    @classmethod 
    def from_grid(cls, grid):
        validate_maze_from_grid(grid) 
        maze = cls()
        maze.height = len(grid) // 2
        maze.width  = len(grid[0]) // 2
        
        for cell_x in range(maze.height):
            for cell_y in range(maze.width):
                maze.graph.add_node(Point(cell_x, cell_y))

        for point in maze.graph.nodes:
            for adjpoint in maze.get_adjacent(point):
                edge_grid = point + adjpoint
                if grid[edge_grid.x][edge_grid.y] is CellType.FREE:
                    maze.graph.add_edge(point, adjpoint)
        return maze

    @classmethod
    def from_file(cls, path):
        if not os.path.isfile(path):
            raise Exception(f"Invalid path to maze: {path}")
        if not os.access(path, os.R_OK):
            raise Exception(f"File {path} cannot be read")

        grid = []
        with open(path, 'r') as file:
            for line in file.readlines():
                maze_line = list(map(CellType.from_char, list(line.strip())))
                grid.append(maze_line)
        maze = Maze.from_grid(grid)
        return maze

    def __str__(self):
        grid = [['#' for _ in range(self.width * 2 + 1)] for _ in range(self.height * 2 + 1)]

        for point in self.graph.nodes:
            grid[point.x*2+1][point.y*2+1] = ' '

        for edge in self.graph.edges:
            point = edge[0] + edge[1] + Point(1, 1)
            grid[point.x][point.y] = ' '

        return "\n".join(map("".join, grid))

    def __contains__(self, point):
        return point in self.graph                
    
if __name__ == "__main__":
    print(str(Maze.from_file("../tests/cases/4_check_maze_solving/maze.txt")))
    