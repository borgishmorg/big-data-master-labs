import re
import math
import json
import requests
import traceback
from collections import defaultdict
from dataclasses import dataclass
from bs4 import BeautifulSoup


def main():
    n = 10
    alpha = 0.15
    host = 'https://felenasoft.com'
    # save_site_data(host, start_path='/ru/')
    site_data = load_site_data(host)

    ranks: dict[str, float] = defaultdict(lambda: 0.)

    for data in site_data:
        rank = get_static_rank(data)
        ranks[data.path] += rank
        for link in data.links:
            ranks[link] += rank / len(data.links)

    for data in site_data:
        ranks[data.path] = (1-alpha)*ranks[data.path] + alpha / len(site_data)

    print(f'Top {n}:')
    for path, rank in sorted(
        ranks.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:n]:
        print(f'{rank:6.3f} {path}')
    print()
    print(f'Last {n}:')
    for path, rank in sorted(
        ranks.items(),
        key=lambda x: x[1],
        reverse=False,
    )[:n]:
        print(f'{rank:6.3f} {path}')


def save_site_data(host: str, start_path: str = '/'):
    data = dict()
    founded = {start_path}
    to_check = [start_path]

    with requests.Session() as session:
        while to_check:
            suffix = to_check.pop()
            link = f'{host}{suffix}'

            print(f'({len(founded) - len(to_check) - 1}/{len(founded)}) {link}')

            try:
                result = session.get(link)
                soup = BeautifulSoup(result.content.decode('utf8'), "lxml")
                links = set()

                for next_link in soup.findAll('a'):
                    ref = next_link.get('href') or ''
                    ref = ref.split('#')[0]
                    if ref.startswith('/') and ref.endswith('/'):
                        links.add(ref)
                        if ref not in founded:
                            founded.add(ref)
                            to_check.append(ref)

                data[suffix] = {
                    'links': list(links),
                    'text': result.content.decode('utf8')
                }
            except Exception:
                traceback.print_exc()

    with open(re.sub(r'[^\w]', '_', host) + '.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


@dataclass
class SiteData:
    path: str
    links: list[str]
    text: str


def load_site_data(host: str) -> list[SiteData]:
    with open(re.sub(r'[^\w]', '_', host) + '.json', 'r', encoding='utf8') as f:
        raw_data = json.load(f)
    return [
        SiteData(
            path=path,
            **data
        )
        for path, data in raw_data.items()
    ]


tags_rank = {
    '<h1': 100,
    '<h2': 75,
    '<h3': 50,
    '<p': 10,
}


def get_static_rank(data: SiteData) -> float:
    rank = 500. / math.sqrt(len(data.path))

    for tag, tag_rank in tags_rank.items():
        rank += data.text.count(tag) * tag_rank

    return rank


if __name__ == '__main__':
    main()
