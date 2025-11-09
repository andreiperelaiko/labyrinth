class InvalidGridError(Exception):
    """Base invalid maze in grid error."""


class InvalidMazeBorderError(InvalidGridError):
    """Raised when grid border is not a wall."""

    def __init__(self, message: str = "Maze border must be a wall") -> None:
        super().__init__(message)


class InvalidMazeCellError(InvalidGridError):
    """Raised when maze cell is not free."""

    def __init__(self, cell_x: int, cell_y: int) -> None:
        super().__init__(f"Maze cell at ({cell_x}, {cell_y}) must be a wall")


class InvalidMazeDimensionError(InvalidGridError):
    """Raised when dimension in maze are not equal."""


class InvalidMazePathError(Exception):
    """Raised when file with maze is unavailable."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Invalid path to maze: {path}")


class InvalidPointError(Exception):
    """Errors with Point."""
