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

def calculate_workout(workout_type, duration):
    """
    Рассчитывает калории и воду в зависимости от типа тренировки и длительности.

    :param workout_type: Тип тренировки.
    :param duration: Длительность тренировки в минутах.
    :return: Кортеж (сожженные калории, дополнительные мл воды).
    """
    workout_data = {
        "бег": {"calories_per_minute": 10, "water_per_30_min": 200},
        "плавание": {"calories_per_minute": 8, "water_per_30_min": 250},
        "йога": {"calories_per_minute": 3, "water_per_30_min": 100},
        "велосипед": {"calories_per_minute": 7, "water_per_30_min": 150},
        "силовая тренировка": {"calories_per_minute": 6, "water_per_30_min": 200},
        "ходьба": {"calories_per_minute": 4, "water_per_30_min": 100},
        "Сноуборд": {"calories_per_minute": 8, "water_per_30_min": 200},

    }

    workout = workout_data.get(workout_type.lower())
    if not workout:
        return None, None

    calories = workout["calories_per_minute"] * duration
    additional_water = (duration / 30) * workout["water_per_30_min"]
    return calories, additional_water
