import sys
import time
from types import ModuleType
import builtins
import dataclasses
from enum import Enum
from importlib import import_module
import math
import random
from typing import *

import pygame as pg

class Game:
    level: ModuleType

    screen: pg.Surface | pg.SurfaceType
    clock: pg.time.Clock
    time: float
    lest_time: float
    delta_time: float
    run_time: float


    def new_game(self, level: str, supress=False):
        """
        Create a new game level.
        Supress == True: the NewGame exception.
        """

