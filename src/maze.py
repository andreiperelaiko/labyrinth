import os
from collections.abc import Iterable
from enum import Enum
from itertools import pairwise
from pathlib import Path

import networkx as nx
import numpy as np

import errors


class CellType(Enum):
    """Represent all cell type."""

    FREE = 0
    WALL = 1
    PATH = 2
    START = 3
    END = 4

    @staticmethod
    def from_char(char: str) -> "CellType":
        """Convert string to CellType."""
        if char == "#":
            return CellType.WALL
        return CellType.FREE

    @staticmethod
    def to_char(cell_type: "CellType") -> str:
        """Convert CellType to string."""
        mapping = {
            CellType.FREE: " ",
            CellType.WALL: "#",
            CellType.PATH: ".",
            CellType.START: "X",
            CellType.END: "O",
        }
        return mapping.get(cell_type, "?")


class Point:
    """Representation of cell with coordinate."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise errors.InvalidPointError

    def __sub__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise errors.InvalidPointError

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: "Point") -> bool:
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __lt__(self, other: "Point") -> bool:
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def manhattan_distance(self, other: "Point") -> int:
        """Return manhatten distance with two point."""
        if isinstance(other, Point):
            return abs(self.x - other.x) + abs(self.y - other.y)
        raise errors.InvalidPointError

    def get_adjacent(self) -> list["Point"]:
        """Return adjacent points on the side."""
        return [
            Point(self.x, self.y + 1),
            Point(self.x, self.y - 1),
            Point(self.x + 1, self.y),
            Point(self.x - 1, self.y),
        ]


def validate_grid_cell(height: int, width: int, grid: list | np.ndarray) -> None:
    """Validate cell in grid.

    Check that cell in grid:
        1. All cels are free
        2. Wall are around labyrithm
    """
    for cell_x in range(height):
        for cell_y in range(width):
            grid_x = cell_x * 2 + 1
            grid_y = cell_y * 2 + 1
            if grid[grid_x][grid_y] != CellType.FREE:
                raise errors.InvalidMazeCellError(grid_x, grid_y)

    for cell_x in range(height):
        grid_x = cell_x * 2 + 1
        if not grid[grid_x][0] == grid[grid_x][-1] == CellType.WALL:
            raise errors.InvalidMazeBorderError

    for cell_y in range(width):
        grid_y = cell_y * 2 + 1
        if not grid[0][grid_y] == grid[-1][grid_y] == CellType.WALL:
            raise errors.InvalidMazeBorderError


def validate_grid(grid: list | np.ndarray) -> None:
    """Validate grid.

    Check that:
        1. Grid has 2 dimension with same size
        2. All cells are free
        3. Walls are around labyrithms
    """
    if not {len(x) for x in grid} != {1}:
        raise errors.InvalidMazeDimensionError

    if len(grid) % 2 != 1:
        raise errors.InvalidMazeDimensionError
    if len(grid[0]) % 2 != 1:
        raise errors.InvalidMazeDimensionError

    height = len(grid) // 2
    width = len(grid[0]) // 2

    validate_grid_cell(height, width, grid)


class Maze:
    """Represet a labyrithm."""

    def __init__(self) -> None:
        self.height = 0
        self.width = 0
        self.graph = nx.Graph()

    def get_adjacent(self, point: Point) -> list[Point]:
        """Return adjacent points in labirythm."""
        return [adjpoint for adjpoint in point.get_adjacent() if adjpoint in self.graph]

    def get_neighbors(self, point: Point) -> Iterable[Point]:
        """Return connnected points."""
        return self.graph.neighbors(point)

    @classmethod
    def from_size(cls, height: int, width: int, *, empty: bool = True) -> "Maze":
        """Create empty/filled labyrithm from size."""
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
    def from_grid(cls, grid: list | np.ndarray) -> "Maze":
        """Create labyrithm from grid."""
        validate_grid(grid)
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
    def from_file(cls, path: str) -> "Maze":
        """Load labyrithm from file."""
        path_obj = Path(path)
        if not path_obj.is_file() or not os.access(path, os.R_OK):
            raise errors.InvalidMazePathError(path)

        grid = []
        with path_obj.open() as file:
            for line in file:
                maze_line = list(map(CellType.from_char, list(line.strip())))
                grid.append(maze_line)
        return Maze.from_grid(grid)

    def save(self, path: str, *, with_edges: bool = True) -> None:
        """Save labyrithm in file."""
        path_obj = Path(path)
        with path_obj.open("w") as file:
            file.write(self._grid_to_str(self.to_grid(with_edges=with_edges)) + "\n")

    def save_solution(
        self, solution: list, path: str, *, with_edges: bool = True
    ) -> None:
        """Save solution of labyrithm in file."""
        path_obj = Path(path)
        with path_obj.open("w") as file:
            file.write(self.display_path(solution, with_edges=with_edges) + "\n")

    def _to_grid(self) -> np.ndarray:
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

    def _display_path(self, path: list[Point]) -> np.ndarray:
        grid = self._to_grid()

        for point in path:
            grid_x = point.x * 2 + 1
            grid_y = point.y * 2 + 1
            grid[grid_x][grid_y] = CellType.PATH

        for edge in pairwise(path):
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

    def to_grid(self, *, with_edges: bool = True) -> np.ndarray:
        """Represent maze as grid."""
        grid = self._to_grid()
        if not with_edges:
            grid = grid[1::2, 1::2]
        return grid

    def _grid_to_str(self, grid: list | np.ndarray) -> str:
        result = ["".join(map(CellType.to_char, line)) for line in grid]
        return "\n".join(result)

    def display_path(self, path: list[Point], *, with_edges: bool = True) -> str:
        """Display maze path as string."""
        grid = self._display_path(path)
        if not with_edges:
            grid = grid[1::2, 1::2]
        return self._grid_to_str(grid)

    def __str__(self) -> str:
        grid = self.to_grid()
        return self._grid_to_str(grid)

    def __contains__(self, point: Point) -> bool:
        return point in self.graph
