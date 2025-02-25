import json
import csv

import matplotlib.pyplot as plt


def save_results_json(results, filename="results/output.json"):
    """Сохранение результатов в JSON"""
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)


def save_results_csv(results, filename="results/output.csv"):
    """Сохранение результатов в CSV"""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Generation", "Best Fitness"])
        for gen, fitness in results.items():
            writer.writerow([gen, fitness])


def plot_results(results, filename="results/fitness_plot.png"):
    """Построение графика изменения лучшего значения фитнес-функции"""
    generations = list(results.keys())
    fitness_values = list(results.values())

    plt.figure(figsize=(10, 5))
    plt.plot(generations, fitness_values, marker='o', linestyle='-', color='b', label='Best Fitness')
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness Evolution Over Generations")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.show()
