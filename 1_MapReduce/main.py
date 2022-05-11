import re
import sys
import pathlib
from black_list import black_list


def main(paths: list[str]):
    top_count = 20
    file_paths = list()

    for path in paths:
        file_paths += get_file_paths(path)

    map_res = list()

    for path in file_paths:
        map_res += [*map_fn(path)]

    shuffle_res = shuffle_fn(map_res)
    reduce_res = reduce_fn(shuffle_res)

    print(f'Топ {top_count} словосочетаний')
    print()
    for k, v in sorted(
        reduce_res.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_count]:
        print(f'{k}: {v}')


def get_file_paths(path: str) -> list[str]:
    entries = pathlib.Path(path)
    paths = list()
    for entry in entries.iterdir():
        if entry.is_dir():
            paths += get_file_paths(str(entry))
        if entry.is_file():
            paths.append(str(entry))
    return paths


def map_fn(path: str):
    first_word, second_word = None, None
    with open(path, encoding='utf8') as f:
        for word in re.split(r'[^\w]+', f.read().lower()):
            first_word, second_word = second_word, word if word not in black_list else None

            if first_word and second_word:
                yield f'{first_word} {second_word}', 1


def shuffle_fn(items: list[tuple[str, int]]) -> dict[str, list[int]]:
    res = dict()
    for k, v in items:
        if k not in res:
            res[k] = list()
        res[k].append(v)
    return res


def reduce_fn(items: dict[str, list[int]]) -> dict[str, int]:
    return {
        k: sum(v)
        for k, v in items.items()
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Скрипт требует один и более параметров: путь до файла.')
        exit(1)
    main(sys.argv[1:])
