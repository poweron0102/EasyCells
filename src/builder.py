import os

start_functions: dict[str, str] = {}  # {Level: Function}
update_functions: dict[str, str] = {}  # {Level: Function}


with open('main.py', 'w') as main:
    with open('main.py') as game:
        main.write(game.read())
        main.write('\n')

    levels = os.listdir("Levels")

    for level in levels:
        if not level.endswith('.py'):
            continue

        with open(f'Levels/{level}') as level_file:
            for line in level_file:
                striped = line.strip()

                if striped.startswith("from EasyCells import *"):
                    continue
                if striped.startswith("def init(game: Game):"):
                    start_functions[level] = striped


                main.write(line)
            main.write('\n')
