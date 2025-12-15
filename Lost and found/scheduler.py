import traceback
from typing import Generator, Callable

from .NewGame import NewGame
from .Game import Game

# Implementação do Scheduler com prioridades
class Scheduler:
    """
    Manages scheduled events, functions, and generators, executing them at the appropriate time
    and in order of priority.
    """
    instance: 'Scheduler' = None

    def __init__(self, game: Game):
        """
        Initializes the Scheduler.
        """
        self.game = game

        # --- Data structures for scheduled items ---

        # Generators (list-based)
        self._generators: list[Generator] = []
        self._generators_times: list[float] = []
        self._generators_priorities: list[int] = []

        # Generators (dictionary-based)
        self._generators_dict: dict[any, Generator] = {}
        self._generators_dict_times: dict[any, float] = {}
        self._generators_dict_priorities: dict[any, int] = {}

        # Functions (list-based)
        self._times: list[float] = []
        self._functions: list[Callable] = []
        self._priorities: list[int] = []

        # Functions (dictionary-based)
        self._times_dict: dict[any, float] = {}
        self._functions_dict: dict[any, Callable] = {}
        self._priorities_dict: dict[any, int] = {}

        if not Scheduler.instance:
            Scheduler.instance = self

    def update(self):
        """
        Updates the scheduler, running all due functions and generators for the current frame.
        Items are processed in order of priority (lower number first), then by scheduled time.
        """
        current_time = self.game.run_time

        # --- Process list-based functions ---
        ready_functions = []
        for index, t in enumerate(self._times):
            if t < current_time:
                # Collect all due functions with their priority, time, and original index
                ready_functions.append((self._priorities[index], t, self._functions[index], index))

        # Sort by priority, then by time
        ready_functions.sort()

        indices_to_remove = []
        for _priority, _time, function, index in ready_functions:
            try:
                function()
            except (KeyboardInterrupt, SystemExit, NewGame) as e:
                raise e
            except Exception as e:
                print(f"Error in scheduled function {function}:\n    {e}")
                traceback.print_exc()
            indices_to_remove.append(index)

        # Remove executed functions from lists, in reverse order to avoid index shifting issues
        for index in sorted(indices_to_remove, reverse=True):
            self._times.pop(index)
            self._functions.pop(index)
            self._priorities.pop(index)

        # --- Process dictionary-based functions ---
        ready_dict_functions = []
        for key, t in list(self._times_dict.items()):
            if t < current_time:
                # Collect all due functions with their priority, time, and key
                ready_dict_functions.append((self._priorities_dict[key], t, self._functions_dict[key], key))

        ready_dict_functions.sort()

        for _priority, _time, function, key in ready_dict_functions:
            try:
                function()
            except (KeyboardInterrupt, SystemExit, NewGame) as e:
                raise e
            except Exception as e:
                print(f"Error in scheduled dict function {function} (key: {key}):\n    {e}")
                traceback.print_exc()
            # Remove directly after execution
            self._times_dict.pop(key)
            self._functions_dict.pop(key)
            self._priorities_dict.pop(key)

        # --- Process list-based generators ---
        ready_generators = []
        for index, t in enumerate(self._generators_times):
            if t < current_time:
                ready_generators.append((self._generators_priorities[index], t, self._generators[index], index))

        ready_generators.sort()

        indices_to_remove_gen = []
        for _priority, _time, generator, index in ready_generators:
            try:
                next_time = next(generator)
                # If the generator yields None, treat it as a delay of 0 (run next frame).
                delay = next_time if next_time is not None else 0
                self._generators_times[index] = current_time + delay
            except StopIteration:
                # Generator is finished, mark for removal
                indices_to_remove_gen.append(index)
            except (KeyboardInterrupt, SystemExit, NewGame) as e:
                raise e
            except Exception as e:
                print(f"Error in generator {generator}:\n    {e}")
                traceback.print_exc()
                indices_to_remove_gen.append(index)

        for index in sorted(indices_to_remove_gen, reverse=True):
            self._generators.pop(index)
            self._generators_times.pop(index)
            self._generators_priorities.pop(index)

        # --- Process dictionary-based generators ---
        ready_dict_generators = []
        for key, t in list(self._generators_dict_times.items()):
            if t < current_time:
                ready_dict_generators.append(
                    (self._generators_dict_priorities[key], t, self._generators_dict[key], key))

        ready_dict_generators.sort()

        for _priority, _time, generator, key in ready_dict_generators:
            try:
                next_time = next(generator)
                delay = next_time if next_time is not None else 0
                self._generators_dict_times[key] = current_time + delay
            except StopIteration:
                # Generator is finished, remove it
                self._generators_dict.pop(key)
                self._generators_dict_times.pop(key)
                self._generators_dict_priorities.pop(key)
            except (KeyboardInterrupt, SystemExit, NewGame) as e:
                raise e
            except Exception as e:
                print(f"Error in dict generator {generator} (key: {key}):\n    {e}")
                traceback.print_exc()
                # Remove problematic generator
                if key in self._generators_dict:
                    self._generators_dict.pop(key)
                    self._generators_dict_times.pop(key)
                    self._generators_dict_priorities.pop(key)

    def add(self, time: float, function: Callable, priority: int = 50):
        self._times.append(self.game.run_time + time)
        self._functions.append(function)
        self._priorities.append(priority)

    def remove(self, function: Callable):
        index = self._functions.index(function)
        self._times.pop(index)
        self._functions.pop(index)
        self._priorities.pop(index)

    def add_dict(self, key, time: float, function: Callable, priority: int = 50):
        self._times_dict[key] = self.game.run_time + time
        self._functions_dict[key] = function
        self._priorities_dict[key] = priority

    def remove_dict(self, key):
        self._times_dict.pop(key)
        self._functions_dict.pop(key)
        self._priorities_dict.pop(key)

    def add_generator(self, generator: Generator, time: float = 0, priority: int = 50):
        self._generators.append(generator)
        self._generators_times.append(self.game.run_time + time)
        self._generators_priorities.append(priority)

    def remove_generator(self, generator: Generator):
        index = self._generators.index(generator)
        self._generators.pop(index)
        self._generators_times.pop(index)
        self._generators_priorities.pop(index)

    def add_dict_generator(self, key, generator: Generator, time: float = 0, priority: int = 50):
        self._generators_dict[key] = generator
        self._generators_dict_times[key] = self.game.run_time + time
        self._generators_dict_priorities[key] = priority

    def remove_dict_generator(self, key):
        try:
            self._generators_dict.pop(key)
            self._generators_dict_times.pop(key)
            self._generators_dict_priorities.pop(key)
        except KeyError:
            pass

    def change_time_dict_generator(self, key, time: float):
        self._generators_dict_times[key] = self.game.run_time + time

    def change_time_generator(self, generator: Generator, time: float):
        index = self._generators.index(generator)
        self._generators_times[index] = self.game.run_time + time

    def change_time_dict(self, key, time: float):
        self._times_dict[key] = self.game.run_time + time

    def change_time(self, function: Callable, time: float):
        index = self._functions.index(function)
        self._times[index] = self.game.run_time + time

    def clear(self):
        self._times.clear()
        self._functions.clear()
        self._priorities.clear()

        self._times_dict.clear()
        self._functions_dict.clear()
        self._priorities_dict.clear()

        self._generators.clear()
        self._generators_times.clear()
        self._generators_priorities.clear()

        self._generators_dict.clear()
        self._generators_dict_times.clear()
        self._generators_dict_priorities.clear()


class Tick:
    def __init__(self, time: float):
        self.time = time
        self.on = True

    def turn_off(self):
        self.on = False

    def turn_on(self):
        self.on = True

    def reset(self):
        self.on = False
        Scheduler.instance.add(self.time, self.turn_on)

    def __call__(self) -> bool:
        if self.on:
            self.on = False
            Scheduler.instance.add(self.time, self.turn_on)
            return True
        return False
