from abc import ABC
from queue import PriorityQueue

#TODO: raise error when maze in unsolvable

class Solver(ABC):
    def solve(self, maze, start_point, end_point):
        pass

class DijkstraSolver(Solver):
    def solve(self, maze, start_point, end_point):
        self.maze = maze
        self.start_point = start_point
        self.end_point = end_point
        self.dist = dict()
        self.prev = dict()
        for point in self.maze.graph.nodes():
            self.dist[point] = self.maze.graph.number_of_nodes()
        self.dijkstra()
        return self.restore_path()
    
    def heuristics(self, point):
        return 0
    
    def dijkstra(self):
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
                    q.put((self.dist[adj_point] + self.heuristics(adj_point), adj_point))

    def restore_path(self):
        path = [self.end_point]
        while path[-1] != self.start_point:
            path.append(self.prev[path[-1]])
        return path

class AstarSolver(DijkstraSolver):
    def heuristics(self, point): 
        return self.end_point.manhattan_distance(point)

if __name__ == "__main__":
    import generator 
    from maze import *
    generator = generator.PrimGenerator()
    maze = generator.generate(10, 10)
    solver = AstarSolver()
    path = solver.solve(maze, Point(0, 0), Point(9, 9))
    print(maze.display_path(path))
