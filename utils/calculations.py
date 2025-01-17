# Логика расчёта воды и калорий

def calculate_water_norm(weight, activity_minutes, temperature):
    """
    Рассчитывает дневную норму воды в мл.

    :param weight: Вес пользователя в кг.
    :param activity_minutes: Уровень активности пользователя в минутах.
    :param temperature: Температура воздуха в градусах Цельсия.
    :return: Норма воды в мл.
    """
    # Базовая норма воды
    water_norm = weight * 30  # мл на кг веса

    # Добавляем воду за активность
    water_norm += (activity_minutes // 15) * 250  # +500 мл за каждые 30 минут активности

    # Добавляем воду за жаркую погоду
    if temperature > 25:
        water_norm += 500  # Умеренная жара
        if temperature > 30:
            water_norm += 500  # Очень жаркая погода

    return water_norm


def calculate_calories_norm(weight, height, age, gender, activity):
    """
    Рассчитывает дневную норму калорий с учетом пола, веса, роста, возраста и уровня активности.

    :param weight: Вес пользователя в кг.
    :param height: Рост пользователя в см.
    :param age: Возраст пользователя в годах.
    :param gender: Пол пользователя ("male" или "female").
    :param activity: Уровень активности в минутах.
    :return: Норма калорий в ккал.
    """
    # Рассчитаем уровень активности
    activity_level = activity

    min_af = 1.2  # Минимальный коэффициент для сидячего образа жизни
    max_af = 1.9  # Максимальный коэффициент для очень высокой активности
    activity_level = min_af + (activity / 480) * (max_af - min_af)

    # Рассчитываем базовый метаболизм (BMR)
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Пол должен быть 'male' или 'female'.")

    # Умножаем на коэффициент активности
    daily_calories = bmr * activity_level

    return round(daily_calories, 2)