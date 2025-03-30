import json
import csv

import matplotlib.pyplot as plt

from api.utils.custom_logger import RESULT_KEY


def save_results_csv(results, filename="results/output.csv"):
    """Сохранение результатов в CSV"""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Generation", "Best Fitness"])
        for gen, fitness in results.items():
            writer.writerow([gen, fitness])


def plot_results(results, filename="results/fitness_plot.png", only_result=False):
    """Построение графика изменения значений фитнес-функции"""
    plt.figure(figsize=(10, 5))

    if only_result:
        result_data = results.get(RESULT_KEY)

        results = []
        if result_data:
            results[RESULT_KEY] = result_data

    if not results:
        return "Невозможно выгрузить данные"

    for process, data in results.items():
        generations = [entry["generation"] for entry in data]
        min_fitness = [entry["min_fitness"] for entry in data]
        max_fitness = [entry["max_fitness"] for entry in data]
        avg_fitness = [entry["avg_fitness"] for entry in data]

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
