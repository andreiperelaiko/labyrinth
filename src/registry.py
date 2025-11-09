from collections.abc import Callable

solver_registry = {}


def register_solver(name: str) -> Callable:
    """Register labyrinths solver."""

    def add_solver(cls: type) -> type:
        solver_registry[name] = cls()
        return cls

    return add_solver


generator_registry = {}


def register_generator(name: str) -> Callable:
    """Register labyrinths generator."""

    def add_generator(cls: type) -> type:
        generator_registry[name] = cls()
        return cls

    return add_generator
