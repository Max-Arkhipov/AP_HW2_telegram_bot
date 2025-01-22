# Утилитарные функции (например, парсинг)
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(STORAGE_FILE):
    """Загрузка данных из файла JSON."""
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_data(STORAGE_FILE, data):
    """Сохранение данных в файл JSON."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def create_combined_progress_chart(water_logged, water_norm, calories_logged, calories_norm, file_path):
    """
    Создаёт объединённую кольцевую диаграмму с прогрессом по воде и калориям.

    :param water_logged: Выпитое количество воды.
    :param water_norm: Норма воды.
    :param calories_logged: Потреблённые калории.
    :param calories_norm: Норма калорий.
    :param file_path: Путь для сохранения изображения.
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    # Данные для воды
    water_values = [water_logged, max(0, water_norm - water_logged)]
    water_colors = ["#4CAF50", "#D3D3D3"]

    # Данные для калорий
    calories_values = [calories_logged, max(0, calories_norm - calories_logged)]
    calories_colors = ["#FF5733", "#D3D3D3"]

    # Внешнее кольцо - калории
    wedges_calories, texts_calories, autotexts_calories = ax.pie(
        calories_values,
        radius=1,
        colors=calories_colors,
        startangle=90,
        wedgeprops=dict(width=0.3, edgecolor="white"),
        autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
        pctdistance=0.85,
    )

    # Внутреннее кольцо - вода
    wedges_water, texts_water, autotexts_water = ax.pie(
        water_values,
        radius=0.7,
        colors=water_colors,
        startangle=90,
        wedgeprops=dict(width=0.3, edgecolor="white"),
        autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
        pctdistance=0.80,
    )

    # Настройки стилей подписей
    for autotext in autotexts_calories:
        autotext.set_color("white")
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")
    for autotext in autotexts_water:
        autotext.set_color("white")
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")

    # Добавляем аннотации для кругов
    ax.text(0, 1.1, "Калории", color="#FF5733", fontsize=14, fontweight="bold", ha="center")
    ax.text(0, 0.2, "Вода", color="#4CAF50", fontsize=14, fontweight="bold", ha="center")

    # Настройки графика
    ax.set(aspect="equal")
    ax.set_title("Ваш прогресс: Вода и Калории", fontsize=16)

    # Сохранение изображения
    plt.savefig(file_path)
    plt.close(fig)

