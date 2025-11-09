solver_registry = dict()


def register_solver(name):
    def add_solver(cls):
        solver_registry[name] = cls()
        return cls
    return add_solver


generator_registry = dict()


def register_generator(name):
    def add_generator(cls):
        generator_registry[name] = cls()
        return cls
    return add_generator
