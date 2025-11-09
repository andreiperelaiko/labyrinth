from generator import Generator
from maze import Maze
from registry import generator_registry, solver_registry
from solver import Solver
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="maze-app",
        description="Maze generator and solver CLI application.",
        add_help=False
    )
    parser.add_argument("-h", "--help", action="help",
                        help="Show this help message and exit.")
    parser.add_argument("-V", "--version", action="version",
                        version="1.0.0", help="Print version information and exit.")
    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", help="Type of task")

    subparsers.add_parser(
        "generate",
        help="Generate a maze with specified algorithm and dimensions.",
        parents=[Generator.create_parser()],
    )
    subparsers.add_parser(
        "solve",
        help="Solve a maze with specified algorithm and points.",
        parents=[Solver.create_parser()],
    )
    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        return

    if args.command == "generate":
        generator = generator_registry[args.algorithm]
        maze = generator.generate(args.height, args.width)
        maze.save(args.output)
    elif args.command == "solve":
        solver = solver_registry[args.algorithm]
        maze = Maze.from_file(args.file)
        solution = solver.solve(maze, args.start, args.end)
        maze.save_solution(solution, args.output)
    else:
        print(f"{args.command} is not a command")


if __name__ == "__main__":
    main()
