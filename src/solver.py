from abc import ABC, abstractmethod
from maze import Point
from queue import PriorityQueue
from registry import register_solver
from typing import List
import argparse


class Solver(ABC):
    @abstractmethod
    def solve(self, maze, start_point, end_point) -> List[int]:
        pass

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        def point_validation(point_str):
            try:
                x, y = map(int, point_str.split(","))
                return Point(x, y)
            except Exception as e:
                raise Exception(
                    f'Invalid point format: "{point_str}", expected format: x,y'
                )

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
    def solve(self, maze, start_point, end_point):
        self.maze = maze
        self.start_point = start_point
        self.end_point = end_point
        self.dist = dict()
        self.prev = dict()
        for point in self.maze.graph.nodes():
            self.dist[point] = self.maze.graph.number_of_nodes()
        self.astar()
        return self.restore_path()

    def heuristics(self, point):
        return self.end_point.manhattan_distance(point)

    def astar(self):
        q = PriorityQueue()
        self.dist[self.start_point] = 0
        self.prev[self.start_point] = self.start_point
        q.put((0, self.start_point))
        while not q.empty():
            priority, current = q.get()
            for adj_point in self.maze.get_neighbors(current):
                if self.dist[adj_point] > self.dist[current] + 1:
                    self.dist[adj_point] = self.dist[current] + 1
                    self.prev[adj_point] = current
                    q.put(
                        (self.dist[adj_point] + self.heuristics(adj_point), adj_point)
                    )

    def restore_path(self):
        path = [self.end_point]
        while path[-1] != self.start_point:
            path.append(self.prev[path[-1]])
        return path


@register_solver("astar")
class DijkstraSolver(AstarSolver):
    def heuristics(self, point):
        return 0


if __name__ == "__main__":
    import generator
    from maze import *

    generator = generator.PrimGenerator()
    maze = generator.generate(10, 10)
    solver = AstarSolver()
    path = solver.solve(maze, Point(0, 0), Point(9, 9))
    print(maze.display_path(path))
