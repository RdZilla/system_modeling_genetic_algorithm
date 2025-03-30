import json
import csv

import matplotlib.pyplot as plt

from api.utils.custom_logger import RESULT_KEY


def save_results_to_csv(results, filename="results/fitness_results.csv", only_best_result=False):
    """Сохранение результатов в CSV файл"""
    if only_best_result:
        result_data = results.get(RESULT_KEY)

        results = {}
        if result_data:
            results[RESULT_KEY] = result_data

    if not results:
        return "Невозможно выгрузить данные"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Process", "Generation", "Min Fitness", "Max Fitness", "Avg Fitness", "Timestamp"])

        for process, data in results.items():
            for entry in data:
                writer.writerow([
                    process,
                    entry.get("generation"),
                    entry.get("min_fitness"),
                    entry.get("max_fitness"),
                    entry.get("avg_fitness"),
                    entry.get("timestamp")
                ])


def plot_results(results, filename="results/fitness_plot.png", only_best_result=False):
    """Построение графика изменения значений фитнес-функции"""
    plt.figure(figsize=(10, 5))

    if only_best_result:
        result_data = results.get(RESULT_KEY)

        results = {}
        if result_data:
            results[RESULT_KEY] = result_data

    if not results:
        return "Невозможно выгрузить данные"

    for process, data in results.items():
        generations = [entry.get("generation") for entry in data]
        min_fitness = [entry.get("min_fitness") for entry in data]
        max_fitness = [entry.get("max_fitness") for entry in data]
        avg_fitness = [entry.get("avg_fitness") for entry in data]

        plt.plot(generations, min_fitness, marker='o', linestyle='-', label=f'{process} Min Fitness')
        plt.plot(generations, max_fitness, marker='o', linestyle='-', label=f'{process} Max Fitness')
        plt.plot(generations, avg_fitness, marker='o', linestyle='-', label=f'{process} Avg Fitness')

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness Evolution Over Generations")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.show()
