import argparse
from abc import ABC, abstractmethod
from queue import PriorityQueue

from maze import Maze, Point
from registry import register_solver


class ParserError(Exception):
    """Base exception for solver-related errors."""


class Solver(ABC):
    """Base class for labyrinths solvers."""

    @abstractmethod
    def solve(self, maze: Maze, start_point: Point, end_point: Point) -> list[Point]:
        """Find path in maze from start_point to end_point."""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Initialize parser for solvers."""

        def point_validation(point_str: str) -> Point:
            try:
                x, y = map(int, point_str.split(","))
                return Point(x, y)
            except Exception as e:
                msg = f'Invalid point format: "{point_str}", expected format: x,y'
                raise ParserError(msg) from e

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "--algorithm",
            choices=["astar", "dijkstra"],
            help="Type of solving algorithm",
        )
        parser.add_argument("--file", type=str, help="File with labyrinth description")
        parser.add_argument("--output", type=str, help="File with labyrinth solution")
        parser.add_argument(
            "--start", type=point_validation, help="Starting point of the route"
        )
        parser.add_argument(
            "--end", type=point_validation, help="Finish point of the route"
        )
        return parser


@register_solver("dijkstra")
class AstarSolver(Solver):
    """Labyrinths solver based on A* (astart) algorithm."""

    def solve(self, maze: Maze, start_point: Point, end_point: Point) -> list[Point]:
        """Find path in labyrinths from start_point to end_point.

        For each visited point save the privous point.
        """
        self.maze = maze
        self.start_point = start_point
        self.end_point = end_point
        self.dist = {}
        self.prev = {}
        for point in self.maze.graph.nodes():
            self.dist[point] = self.maze.graph.number_of_nodes()
        self.astar()
        return self.restore_path()

    def heuristics(self, point: Point) -> int:
        """Evaluate heuristic with manhattan distance."""
        return self.end_point.manhattan_distance(point)

    def astar(self) -> None:
        """Perform A* pathfinding algorithm.

        Uses a priority queue to iteratively expand the lowest-cost node.
        """
        q = PriorityQueue()
        self.dist[self.start_point] = 0
        self.prev[self.start_point] = self.start_point
        q.put((0, self.start_point))
        while not q.empty():
            _, current = q.get()
            for adj_point in self.maze.get_neighbors(current):
                if self.dist[adj_point] > self.dist[current] + 1:
                    self.dist[adj_point] = self.dist[current] + 1
                    self.prev[adj_point] = current
                    q.put(
                        (self.dist[adj_point] + self.heuristics(adj_point), adj_point)
                    )

    def restore_path(self) -> list[Point]:
        """Restore path after filling self.prev by astar."""
        path = [self.end_point]
        while path[-1] != self.start_point:
            path.append(self.prev[path[-1]])
        return path


@register_solver("astar")
class DijkstraSolver(AstarSolver):
    """Labyrinth solver implementing Dijkstra's algorithm.

    This class is implemented as a special case of the A* algorithm,
    where the heuristic function always returns zero. As a result,
    pathfinding is equivalent to the classical Dijkstra algorithm.
    """

    def heuristics(self, _point: Point) -> int:
        """Djikstra heuristic is always zero."""
        return 0
