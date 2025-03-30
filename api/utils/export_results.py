import json
import csv

import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


def best_result_json(results, filename="results/fitness_plot.png"):
    result_data = results.get(RESULT_KEY)

    results = {}
    if result_data:
        results[RESULT_KEY] = result_data

    if not results:
        return "Невозможно выгрузить данные"

    with open(filename, "w") as json_file:
        json.dump(results, json_file, indent=4)


def save_results_to_pdf(results, filename="results/fitness_results.pdf"):
    """Сохранение результатов в PDF файл"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y_position = height - 40

    c.setFont("Helvetica", 12)
    c.drawString(30, y_position, "Fitness Results")
    y_position -= 20

    for process, data in results.items():
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30, y_position, f"Process: {process}")
        y_position -= 15
        c.setFont("Helvetica", 9)
        c.drawString(30, y_position, "Generation | Min Fitness | Max Fitness | Avg Fitness | Timestamp")
        y_position -= 15

        for entry in data:
            row = f"{entry.get('generation')} | {entry.get('min_fitness')} | {entry.get('max_fitness')} | {entry.get('avg_fitness')} | {entry.get('timestamp')}"
            c.drawString(30, y_position, row)
            y_position -= 15
            if y_position < 40:
                c.showPage()
                y_position = height - 40

    c.save()
