import argparse
import os
import re


class GeneratorSubparser:
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--algorithm", choices=["dfs", "prim"],
                            help="Type of generating algorithm")
        parser.add_argument("--width", type=int, help="Width of labyrinths")
        parser.add_argument("--height", type=int, help="Height of labyrinths")
        parser.add_argument("--output", type=str, help="Path to save labyrinth")
        return parser


class SolverSubparser:
    @staticmethod
    def _file(path):
        if not os.path.isfile(path):
            raise Exception(f"File {path} does not exist")
        if not os.access(path, os.R_OK):
            raise Exception(f"File {path} cannot be read")
        return path

    @staticmethod
    def _point(point):
        pattern = re.compile(r'^[0-9]+,[0-9]+$')
        if not pattern.fullmatch(point):
            raise Exception(
                f"Invalid point format: {point}, expected format: x,y"
            )
        return tuple(map(int, point.split(',')))

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--algorithm", choices=["astar", "dijkstra"],
                            help="Type of solving algorithm")
        parser.add_argument("--file", type=SolverSubparser._file,
                            help="File with labyrinth description")
        parser.add_argument("--start", type=SolverSubparser._point,
                            help="Starting point of the route")
        parser.add_argument("--end", type=SolverSubparser._point,
                            help="Finish point of the route")
        return parser


def main():
    parser = argparse.ArgumentParser(
        prog="maze-app",
        description="Maze generator and solver CLI application.",
        add_help=False
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-V", "--version", action="version", version="1.0.0", help="Print version information and exit.")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND", help="Type of task")

    subparsers.add_parser(
        "generate",
        help="Generate a maze with specified algorithm and dimensions.",
        parents=[GeneratorSubparser.create_parser()],
    )
    subparsers.add_parser(
        "solve",
        help="Solve a maze with specified algorithm and points.",
        parents=[SolverSubparser.create_parser()],
    )
    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(0)
    print(args)


if __name__ == "__main__":
    main()
