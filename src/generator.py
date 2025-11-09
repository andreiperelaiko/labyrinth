import argparse
import random
from abc import ABC, abstractmethod

from maze import Maze, Point
from registry import register_generator


class Generator(ABC):
    """Base class for labyrinths generation."""

    @abstractmethod
    def generate(self, height: int, width: int) -> Maze:
        """Generate a labyrinth of the specific size."""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create parser for generators."""
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-a",
            "--algorithm",
            choices=["dfs", "prim"],
            help="Type of generating algorithm",
        )
        parser.add_argument("-w", "--width", type=int, help="Width of labyrinths")
        parser.add_argument("--height", type=int, help="Height of labyrinths")
        parser.add_argument("-o", "--output", type=str, help="Path to save labyrinth")
        return parser


@register_generator("dfs")
class DfsGenerator(Generator):
    """Labyrinths generator based on dfs algorithm."""

    def generate(self, height: int, width: int) -> Maze:
        """Generate labyrinths by dfs algorithm."""
        self.maze = Maze.from_size(height, width, empty=False)
        self.visited = set()
        self.start_point = random.choice(list(self.maze.graph.nodes()))
        self.dfs(self.start_point)
        return self.maze

    def dfs(self, cur_point: Point) -> None:
        """Implement of dfs algorithm."""
        self.visited.add(cur_point)
        adj_points = self.maze.get_adjacent(cur_point)
        for nxt_point in random.sample(adj_points, len(adj_points)):
            if nxt_point not in self.visited:
                self.maze.graph.add_edge(cur_point, nxt_point)
                self.dfs(nxt_point)


@register_generator("prim")
class PrimGenerator(Generator):
    """Labyrinths generator based on prim algorithm."""

    def generate(self, height: int, width: int) -> Maze:
        """Generate labyrinths by prim algorithm."""
        self.maze = Maze.from_size(height, width, empty=False)
        self.visited = set()
        self.boundary_edges = set()
        start_point = random.choice(list(self.maze.graph.nodes()))
        self.visited.add(start_point)
        for adj_point in self.maze.get_adjacent(start_point):
            self.boundary_edges.add((start_point, adj_point))
        self.prim()
        return self.maze

    def process_edge(self, edge: tuple[Point, Point]) -> None:
        """Check if the given edge is on the boundary and process it.

        If the edge connects a visited point to an unvisited one, the new point
        is added to the maze graph and marked as visit
        Check if the given edge is on the boundary and process it.
        """
        point_from, point_to = edge
        if point_to not in self.visited:
            self.maze.graph.add_edge(point_from, point_to)
            self.visited.add(point_to)
            for adj_point in self.maze.get_adjacent(point_to):
                self.boundary_edges.add((point_to, adj_point))

    def prim(self) -> None:
        """Process and add all boundary edges."""
        while self.boundary_edges:
            edge = random.choice(list(self.boundary_edges))
            self.boundary_edges.discard(edge)
            self.process_edge(edge)
