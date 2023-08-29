import random


def gen_random_tree(elements_min: int, elements_max: int, value_min: int, value_max: int, max_sublevel: int = 0):
    '''Функция генерирующая набор вложенных списков с рандомными данными'''

    arr = []

    for _ in range(random.randint(elements_min, elements_max)):

        if max_sublevel > 0 and random.randint(1, 4) == 2:
            arr.append(gen_random_tree(elements_min, elements_max, value_min, value_max, max_sublevel - 1))
        else:
            value = random.randint(value_min, value_max)
            if random.randint(1, 4) == 2: value *= -1
            arr.append(value)

    return arr