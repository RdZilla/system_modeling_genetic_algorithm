from core.selection.roulette_wheel_selection import roulette_wheel_selection
from core.selection.tournament_selection import tournament_selection


def adaptive_selection(self):
    """Динамическая адаптация стратегии селекции по мере развития поколений."""
    _ru_function_name = "Адаптивная селекция"

    generation = self.generation
    max_generations = self.max_generations

    if generation < max_generations / 2:
        # Турнирная селекция на ранних стадиях
        return tournament_selection(self)
    else:
        # Рулеточная селекция на более поздних стадиях
        return roulette_wheel_selection(self)