import string
from typing import Union


def analyze_text(text: str) -> dict[str, Union[int, float]]:
    """
    Анализирует сырой текст и возвращает базовую статистику.

    Приводит текст к нижнему регистру, удаляет знаки препинания,
    разбивает на слова и вычисляет статистические показатели.

    Args:
        text: Сырой текст, который может содержать лишние пробелы,
                знаки препинания и символы разного регистра.

    Returns:
        Словарь со следующими ключами:
            - 'total_words' (int): общее количество слов.
            - 'unique_words' (int): количество уникальных слов.
            - 'avg_word_length' (float): средняя длина слова
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()

    total_words = len(words)
    unique_words = len(set(words))
    avg_word_length = round(sum(len(w) for w in words) / total_words, 2)

    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "avg_word_length": avg_word_length,
    }
