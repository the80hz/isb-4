import sys
import time
import re
import json
import multiprocessing as mp
import functools
from funcs import charting, luna, compute_hash


def choose_pool():
    """Функция выбора кол-ва ядер
    """
    pool_size = int(input("Выберите кол-во потоков: "))
    return pool_size


def find_card(pool_size, setting):
    """Функция поиска карты

    Args:
        pool_size (int): количество потоков
        setting (dict): настройки
    """
    compute_hash_partial = functools.partial(compute_hash, CONFIG=setting)
    start = time.time()
    print("\tИнициализация всех карт")
    progress = 0
    cards = []
    for i in range(0, 1000000):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)
            progress = int((i + 1) * 50 / 10 ** 6)
            print("Progress: {}/100".format(progress))
    print("")

    with mp.Pool(pool_size) as p:
        print("Сверяем хэшы карт")
        progress = 67
        print("Progress: {}/100".format(progress))
        results = p.map(compute_hash_partial, cards)
    for result, card in zip(results, cards):
        progress = 85
        print("Progress: {}/100".format(progress))
        if result:
            success(start, card)
            p.terminate()
            break
    else:
        print("Карта не найдена")
        progress = 0
        print("Progress: {}/100".format(progress))


def success(start, result):
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


def show_graph(setting):
    """Функция отрисовки графика
    """
    cards = []
    compute_hash_partial = functools.partial(compute_hash, CONFIG=setting)
    print("Инициализация всех карт")
    for i in range(0, 1000000):
        mid = str(i).zfill(6)
        for j in range(len(setting["bins"])):
            card = (setting["bins"][j] + mid + setting["last_number"])
            cards.append(card)
    values = []
    for cpu in range(1, mp.cpu_count() + 1):
        start = time.time()
        print(f"Подождите идет процес оценки времени с {cpu} core")
        with mp.Pool(cpu) as p:
            results = p.map(compute_hash_partial, cards)
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
