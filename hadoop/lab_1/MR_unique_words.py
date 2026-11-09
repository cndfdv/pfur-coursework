# Вариант 7 - слова, которые встречаются в тексте ровно один раз

import json
from string import punctuation

from mrjob.job import MRJob
from mrjob.protocol import TextValueProtocol
from mrjob.step import MRStep


class MRUniqueWordsByLength(MRJob):
    # чтобы вывод был обычным текстом с табами, а не JSON
    OUTPUT_PROTOCOL = TextValueProtocol

    def steps(self):
        return [
            MRStep(mapper=self.mapper_words, reducer=self.reducer_only_unique),
            # маппер на втором шаге не нужен, mrjob сам передаст данные из первого редьюсера
            MRStep(reducer=self.reducer_group_by_length),
        ]

    # шаг 1: частота слов, оставляем только те, что встретились один раз

    def mapper_words(self, _, line):
        # "--" в тексте стоит между словами, поэтому меняем на пробел
        for token in line.lower().replace("--", " ").split():
            word = token.strip(punctuation)  # убираем знаки по краям слова
            if word:
                yield word, 1

    def reducer_only_unique(self, word, counts):
        total = 0
        for count in counts:
            total += count
            if total > 1:
                return  # слово уже не уникальное, дальше считать незачем
        yield len(word), word

    # шаг 2: группируем уникальные слова по длине

    def reducer_group_by_length(self, length, words):
        count = 0
        group = []
        for word in words:
            count += 1
            group.append(word)
        group.sort()
        yield None, f"{length}\t{count}\t{json.dumps(group, ensure_ascii=False)}"


if __name__ == "__main__":
    MRUniqueWordsByLength.run()
