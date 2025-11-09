from enum import Enum
import networkx as nx
import numpy as np
import os


class CellType(Enum):
    FREE = 0
    WALL = 1
    PATH = 2
    START = 3
    END = 4

    @staticmethod
    def from_char(char):
        if char == "#":
            return CellType.WALL
        else:
            return CellType.FREE

    @staticmethod
    def to_char(cell_type):
        mapping = {
            CellType.FREE: " ",
            CellType.WALL: "#",
            CellType.PATH: ".",
            CellType.START: "X",
            CellType.END: "O",
        }
        return mapping.get(cell_type, "?")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise Exception(f"cant add Point to {repr(other)}")

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise Exception(f"cant add Point to {repr(other)}")

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def manhattan_distance(self, other):
        if isinstance(other, Point):
            return abs(self.x - other.x) + abs(self.y - other.y)
        raise Exception(f"cant add Point to {repr(other)}")

    def get_adjacent(self):
        return [
            Point(self.x, self.y + 1),
            Point(self.x, self.y - 1),
            Point(self.x + 1, self.y),
            Point(self.x - 1, self.y),
        ]


def validate_maze_from_grid(grid):
    if not set(map(lambda x: len(x), grid)) != 1:
        raise Exception(f"Cannot create Maze from grid: invalid dimensions")

    if len(grid) % 2 != 1:
        raise Exception("Invalid maze height")
    if len(grid[0]) % 2 != 1:
        raise Exception("Invalid maze width")

    height = len(grid) // 2
    width = len(grid[0]) // 2

    # Check that all cells are free
    for cell_x in range(height):
        for cell_y in range(width):
            grid_x = cell_x * 2 + 1
            grid_y = cell_y * 2 + 1
            if grid[grid_x][grid_y] != CellType.FREE:
                raise Exception(f"Cell in maze must be free: ({grid_x, grid_y})")

    # Check that around maze wall
    for cell_x in range(height):
        grid_x = cell_x * 2 + 1
        if not grid[grid_x][0] == grid[grid_x][-1] == CellType.WALL:
            raise Exception(f"Maze border must be a wall")

    for cell_y in range(width):
        grid_y = cell_y * 2 + 1
        if not grid[0][grid_y] == grid[-1][grid_y] == CellType.WALL:
            raise Exception(f"Maze border must be a wall")


class Maze:
    def __init__(self):
        self.height = 0
        self.width = 0
        self.graph = nx.Graph()

    def get_adjacent(self, point):
        adjacent = []
        for adjpoint in point.get_adjacent():
            if adjpoint in self.graph:
                adjacent.append(adjpoint)
        return adjacent

    def get_neighbors(self, point):
        return self.graph.neighbors(point)

    @classmethod
    def from_size(cls, height, width, empty=True):
        maze = cls()
        maze.height = height
        maze.width = width
        for cell_x in range(maze.height):
            for cell_y in range(maze.width):
                maze.graph.add_node(Point(cell_x, cell_y))

        if not empty:
            return maze

        for point in maze.graph.nodes:
            for adjpoint in maze.get_adjacent(point):
                maze.graph.add_edge(point, adjpoint)
        return maze

    @classmethod
    def from_grid(cls, grid):
        validate_maze_from_grid(grid)
        maze = cls()
        maze.height = len(grid) // 2
        maze.width = len(grid[0]) // 2

        for cell_x in range(maze.height):
            for cell_y in range(maze.width):
                maze.graph.add_node(Point(cell_x, cell_y))

        for point in maze.graph.nodes:
            for adjpoint in maze.get_adjacent(point):
                edge_grid = point + adjpoint + Point(1, 1)
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
        with open(path, "r") as file:
            for line in file.readlines():
                maze_line = list(map(CellType.from_char, list(line.strip())))
                grid.append(maze_line)
        maze = Maze.from_grid(grid)
        return maze

    def save(self, path, with_edges=True):
        with open(path, "w") as file:
            file.write(self._grid_to_str(self.to_grid(with_edges=with_edges)) + "\n")

    def save_solution(self, solution: list, path: str, with_edges=True):
        with open(path, "w") as file:
            file.write(self.display_path(solution, with_edges=with_edges) + "\n")

    def _to_grid(self):
        grid_height = self.height * 2 + 1
        grid_width = self.width * 2 + 1
        grid = np.full((grid_height, grid_width), CellType.WALL, dtype=object)

        for point in self.graph.nodes:
            grid_x = point.x * 2 + 1
            grid_y = point.y * 2 + 1
            grid[grid_x][grid_y] = CellType.FREE

        for edge in self.graph.edges:
            grid_x = edge[0].x + edge[1].x + 1
            grid_y = edge[0].y + edge[1].y + 1
            grid[grid_x][grid_y] = CellType.FREE

        return grid

    def _display_path(self, path):
        grid = self._to_grid()

        for point in path:
            grid_x = point.x * 2 + 1
            grid_y = point.y * 2 + 1
            grid[grid_x][grid_y] = CellType.PATH

        for edge in zip(path, path[1:]):
            grid_x = edge[0].x + edge[1].x + 1
            grid_y = edge[0].y + edge[1].y + 1
            grid[grid_x][grid_y] = CellType.PATH

        grid_start_point_x = path[0].x * 2 + 1
        grid_start_point_y = path[0].y * 2 + 1
        grid[grid_start_point_x][grid_start_point_y] = CellType.START

        grid_end_point_x = path[-1].x * 2 + 1
        grid_end_point_y = path[-1].y * 2 + 1
        grid[grid_end_point_x][grid_end_point_y] = CellType.END

        return grid

    def to_grid(self, with_edges=True):
        grid = self._to_grid()
        if not with_edges:
            grid = grid[1::2, 1::2]
        return grid

    def _grid_to_str(self, grid):
        result = []
        for line in grid:
            result.append("".join(list(map(CellType.to_char, line))))
        return "\n".join(result)

    def display_path(self, path, with_edges=True):
        # TODO: add check to valid path
        grid = self._display_path(path)
        if not with_edges:
            grid = grid[1::2, 1::2]
        return self._grid_to_str(grid)

    def __str__(self):
        grid = self.to_grid()
        return self._grid_to_str(grid)

    def __contains__(self, point):
        return point in self.graph
