import random
import h5py


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


def hdf5_read_recursive(group):
    data = []

    for key in group.keys():
        item = group[key]

        if isinstance(item, h5py.Group):
            data.append(hdf5_read_recursive(item))
        else:
            data.append(item[()])

    return data

def hdf5_write_recursive(group, data):
    for n, item in enumerate(data):
        if isinstance(item, list):
            subgroup = group.create_group(str(n))
            hdf5_write_recursive(subgroup, item)
        else:
            group.create_dataset(str(n), data=item)
