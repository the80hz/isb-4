import functools
import multiprocessing as mp
import time
from typing import Dict
import logging
import argparse
import json

from tqdm import tqdm

from funcs import charting, luna, compute_hash

logging.basicConfig(filename='app.log', level=logging.INFO)


def choose_pool() -> int:
    """Функция выбора кол-ва ядер"""
    pool_size = int(input("Выберите кол-во потоков: "))
    return pool_size


def find_card(pool_size: int, setting: Dict[str, any]):
    """Функция поиска карты

    Args:
        pool_size (int): количество потоков
        setting (dict): настройки
    """
    compute_hash_partial = functools.partial(compute_hash, CONFIG=setting)
    start = time.time()
    logging.info("Инициализация всех карт")
    cards = []

    for i in tqdm(range(0, 1000000), unit="card"):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)

    with mp.Pool(pool_size) as p:
        logging.info("Сверяем хеш карт")
        progress_bar = tqdm(total=len(cards), unit="card", ncols=80)
        results = []
        for result in p.imap_unordered(compute_hash_partial, cards):
            results.append(result)
            progress_bar.update()
        progress_bar.close()

    for result, card in zip(results, cards):
        if result:
            success(start, card)
            p.terminate()
            break
    else:
        logging.info("Карта не найдена")


def success(start: float, result: int):
    """Функция обновляет прогресс бар и выводит информацию о карте и времени поиска

    Args:
        start (float): время начала поиска
        result (int): результат
    """
    end = time.time() - start
    result_text = f'Расшифрованный номер: {str(result)[0:4]} {str(result)[4:8]} ' \
                  f'{str(result)[8:12]} {str(result)[12:]}\n'
    result_text += f'Проверка на алгоритм Луна: {luna(result)}\n'
    result_text += f'Время: {end:.2f} секунд'
    logging.info(result_text)
    logging.info("\t Карта найдена")


def show_graph(setting: Dict[str, any]):
    """Функция отрисовки графика"""
    cards = []
    compute_hash_partial = functools.partial(compute_hash, CONFIG=setting)
    logging.info("Инициализация всех карт")

    for i in tqdm(range(0, 1000000), unit="card"):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)

    max_cpu_count = mp.cpu_count()
    logging.info(f"Подождите идет процесс оценки времени с 1-{max_cpu_count} core")

    values = []
    for cpu in tqdm(range(1, max_cpu_count), unit="core"):
        start = time.time()

        with mp.Pool(cpu) as p:
            results = []
            for result in p.imap_unordered(compute_hash_partial, cards):
                results.append(result)
            for result, card in zip(results, cards):
                if result:
                    end = time.time() - start
                    values.append((cpu, end))
                    p.terminate()
                    break
    charting(values)
    logging.info("График готов")


def main():
    parser = argparse.ArgumentParser(description='Поиск номера банковской карты')
    parser.add_argument('-s', '--settings', type=str, help='Путь к файлу настроек')
    parser.add_argument('-g', '--graph', action='store_true', help='Построить график')
    parser.add_argument('-f', '--find_card', type=int, help='Поиск карты с указанным кол-вом потоков')

    args = parser.parse_args()
    with open(args.settings, 'r') as json_file:
        setting = json.load(json_file)

    if args.graph:
        show_graph(setting)
    elif args.find_card:
        find_card(args.find_card, setting)


if __name__ == "__main__":
    main()
