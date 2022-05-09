from dataclasses import dataclass
from collections import defaultdict
from helpers import (
    shrink_string,
    iterate_files_paths,
    split_string_to_words,
)
from black_list import black_list


@dataclass
class Document:
    document_id: str
    data: str
    word_weight: dict[str, float]


class TopNHeap:

    def __init__(
        self,
        n: int,
        key=lambda x: x
    ) -> None:
        self.n = n
        self.stored = 0
        self.data: list = [None] * (n+1)
        self.key = key

    def add(self, value):
        position = self.stored
        self.data[position] = value
        while (
            position > 0
            and self.key(self.data[position]) > self.key(self.data[position//2])
        ):
            self.data[position], self.data[position//2] = self.data[position//2], self.data[position]  # noqa
            position //= 2
        self.stored = min(self.stored + 1, self.n)

    def to_list(self):
        return sorted(self.data[:self.stored], key=self.key, reverse=True)


class InvertedIndex():

    def __init__(self) -> None:
        self.word_entries: dict[str, set[str]] = defaultdict(set)
        self.documents: dict[str, Document] = dict()

    def add_documents(self, path: str):
        for file_path in iterate_files_paths(path):
            with open(file_path, encoding='utf8') as f:
                data = f.read()

            document = Document(
                document_id=file_path,
                data=data,
                word_weight=defaultdict(lambda: 0)
            )
            words = split_string_to_words(data)
            words = [*filter(lambda w: w not in black_list, words)]

            for word in words:
                self.word_entries[word].add(document.document_id)

                document.word_weight[word] += 1. / len(words)

            self.documents[document.document_id] = document

    def search(self, query: str, n: int = 5) -> list[tuple[str, float]]:
        query_words = split_string_to_words(query)

        documents = set()
        for word in query_words:
            documents |= self.word_entries[word]

        result = TopNHeap(n=n, key=lambda x: x[1])
        for document_id in documents:
            weight = sum(
                self.documents[document_id].word_weight[word]
                for word in query_words
            )
            result.add((document_id, weight))
        return result.to_list()


def main():
    index = InvertedIndex()
    index.add_documents('data')

    queries = [
        'Что приготовить на новый год?',
        'Что лучше: евро или доллар?',
        'Почему вороны не любят меня?',
        'Отдых в Мавритании. Дешево',
    ]

    for query in queries:
        print(query)
        for doc, weight in index.search(query, n=5):
            print(f'{shrink_string(doc, 40):40} {weight:2.5f}')
        print()


if __name__ == '__main__':
    main()
