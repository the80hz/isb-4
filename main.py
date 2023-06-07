import sys
import time
import re
import json
import multiprocessing as mp
import functools
from tqdm import tqdm
from typing import Dict
from funcs import charting, luna, compute_hash


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
    print("Инициализация всех карт")
    progress = 0
    cards = []

    for i in tqdm(range(0, 1000000), unit="card"):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)

    with mp.Pool(pool_size) as p:
        print("Сверяем хэшы карт")
        progress_bar = tqdm(total=len(cards), unit="card", ncols=80)
        progress_bar.set_description("Progress")
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
        print("Карта не найдена")


def success(start: float, result: int):
    """Функция обновляет прогресс бар и выводит информацию о карте и времени поиска

    Args:
        start (float): время начала поиска
        result (int): результат
    """
    end = time.time() - start
    result_text = f'Расшифрованный номер: {str(result)[0:4]} {str(result)[4:8]} {str(result)[8:12]} {str(result)[12:]}\n'
    result_text += f'Проверка на алгоритм Луна: {luna(result)}\n'
    result_text += f'Время: {end:.2f} секунд'
    print(result_text)
    print("\t Карта найдена")


def show_graph(setting: Dict[str, any]):
    """Функция отрисовки графика"""
    cards = []
    compute_hash_partial = functools.partial(compute_hash, CONFIG=setting)
    print("Инициализация всех карт")
    for i in tqdm(range(0, 1000000), unit="card"):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)

    print(f"Подождите идет процес оценки времени с 1-{mp.cpu_count() + 1} core\n")

    values = []
    for cpu in tqdm(range(1, mp.cpu_count() + 1), unit="core"):
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
    print("График готов")


def main():
    with open("settings.json") as json_file:
        setting = json.load(json_file)

    print('Поиск номера банковской карты')
    while True:
        print("\nВыберите действие:")
        print("1. Найти карту")
        print("2. Построить график")
        print("3. Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            pool_size = choose_pool()
            find_card(pool_size, setting)
        elif choice == "2":
            show_graph(setting)
        elif choice == "3":
            sys.exit(0)
        else:
            print("Неверный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    main()
