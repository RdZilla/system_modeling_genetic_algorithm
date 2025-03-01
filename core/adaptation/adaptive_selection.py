from core.selection.roulette_wheel_selection import roulette_wheel_selection
from core.selection.tournament_selection import tournament_selection


def adaptive_selection(population, fitness, generation, max_generations):
    """Динамическая адаптация стратегии селекции по мере развития поколений."""
    if generation < max_generations / 2:
        # Турнирная селекция на ранних стадиях
        return tournament_selection(population, fitness)
    else:
        # Рулеточная селекция на более поздних стадиях
        return roulette_wheel_selection(population, fitness)