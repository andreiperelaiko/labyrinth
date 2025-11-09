from abc import ABC, abstractmethod
from maze import Maze
from registry import register_generator
import argparse
import random


class Generator(ABC):
    @abstractmethod
    def generate(self, height, width) -> Maze:
        pass

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-a", "--algorithm", choices=["dfs", "prim"],
                            help="Type of generating algorithm")
        parser.add_argument("-w", "--width", type=int,
                            help="Width of labyrinths")
        parser.add_argument("--height", type=int, help="Height of labyrinths")
        parser.add_argument("-o", "--output", type=str,
                            help="Path to save labyrinth")
        return parser


@register_generator("dfs")
class DfsGenerator(Generator):
    def generate(self, height, width) -> Maze:
        self.maze = Maze.from_size(height, width, empty=False)
        self.visited = set()
        self.start_point = random.choice(list(self.maze.graph.nodes()))
        self.dfs(self.start_point)
        return self.maze

    def dfs(self, cur_point):
        self.visited.add(cur_point)
        adj_points = self.maze.get_adjacent(cur_point)
        for nxt_point in random.sample(adj_points, len(adj_points)):
            if nxt_point not in self.visited:
                self.maze.graph.add_edge(cur_point, nxt_point)
                self.dfs(nxt_point)


@register_generator("prim")
class PrimGenerator(Generator):
    def generate(self, height, width):
        self.maze = Maze.from_size(height, width, empty=False)
        self.visited = set()
        self.boundary_edges = set()
        start_point = random.choice(list(self.maze.graph.nodes()))
        self.visited.add(start_point)
        for adj_point in self.maze.get_adjacent(start_point):
            self.boundary_edges.add((start_point, adj_point))
        self.prim()
        return self.maze

    def process_edge(self, edge):
        point_from, point_to = edge
        if point_to not in self.visited:
            self.maze.graph.add_edge(point_from, point_to)
            self.visited.add(point_to)
            for adj_point in self.maze.get_adjacent(point_to):
                self.boundary_edges.add((point_to, adj_point))

    def prim(self):
        while self.boundary_edges:
            edge = random.choice(list(self.boundary_edges))
            self.boundary_edges.discard(edge)
            self.process_edge(edge)
