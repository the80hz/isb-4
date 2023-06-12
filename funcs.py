import matplotlib.pyplot as plt
import hashlib
import logging
from typing import List, Tuple

logging.basicConfig(filename="log.log", level=logging.INFO)


def charting(results: List[Tuple[int, float]]):
    """
    Функция для рисования графика

    Args:
        results (list): Список результатов (пары значений ядер и времени выполнения)
    """
    cores, times = zip(*results)
    plt.bar(cores, times, align='center', alpha=0.5)
    plt.title('Время выполнения от количества ядер')
    plt.xlabel('Количество ядер')
    plt.ylabel('Время выполнения (с)')
    plt.show()


def luhn(card: int) -> bool:
    """Функция проверки номера карты алгоритмом Луна

    Args:
        card (int): номер карты

    Returns:
        bool: результат проверки
    """
    logging.info(f"Запущен алгоритм Луна с картой {card}")
    card = str(card)
    card = card[::-1]
    card = list(card)
    for i in range(1, len(card), 2):
        card[i] = str(int(card[i]) * 2)
        if int(card[i]) >= 10:
            num = int(card[i])
            card[i] = str(num % 10)
            num //= 10
            card[i] = str(int(card[i]) + num % 10)
    summ = 0
    for i in range(len(card)):
        summ += int(card[i])
    if summ % 10 == 0:
        logging.info("Номер карты является корректным")
        return True
    else:
        logging.error("Номер карты не является корректным")
        return False


def compute_hash(card: int, parameters: dict) -> bool:
    """
    Функция делает проверку хэша по номеру карты

    Args:
        card (int): номер карты
        parameters (dict): настройки

    Returns:
        bool: True, если проверка пройдена, и False в противном случае
    """
    card_str = str(card)
    hash_object = hashlib.blake2s()
    hash_object.update(card_str.encode('utf-8'))
    hash_object.hexdigest()

    return parameters["hash"] == hash_object.hexdigest()
