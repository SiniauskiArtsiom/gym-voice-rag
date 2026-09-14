"""Heuristic router: question -> graph facts.

No LLM involved. Simple keyword matching on Russian queries.
"""
from app.graph import queries as gq

# muscle synonyms (rus -> eng node name)
MUSCLE_MAP = {
    "груд": "Chest",
    "спин": "Back",
    "широч": "Lats",
    "ног": "Quads",
    "квадрицепс": "Quads",
    "бицепс бедра": "Hamstrings",
    "ягодиц": "Glutes",
    "плеч": "Front Delts",
    "дельт": "Front Delts",
    "бицепс": "Biceps",
    "трицепс": "Triceps",
    "пресс": "Core",
    "кор": "Core",
}

INJURY_MAP = {
    "плеч": "Shoulder Pain",
    "колен": "Knee Pain",
    "поясниц": "Lower Back Pain",
    "спин": "Lower Back Pain",
    "локт": "Elbow Pain",
}

EQUIPMENT_MAP = {
    "штан": "Barbell",
    "гантел": "Dumbbell",
    "тренажёр": "Machine",
    "тренажер": "Machine",
    "блок": "Cable",
    "турник": "Pull-Up Bar",
}

EXERCISE_MAP = {
    "жим лёжа": "Bench Press",
    "жим лежа": "Bench Press",
    "жим штанги лёжа": "Bench Press",
    "жим гантелей": "Dumbbell Bench Press",
    "присед": "Squat",
    "приседания": "Squat",
    "становая": "Deadlift",
    "румынская": "Romanian Deadlift",
    "подтягиван": "Pull-Up",
    "тяга штанги": "Barbell Row",
    "тяга в наклоне": "Barbell Row",
    "жим стоя": "Overhead Press",
    "армейский жим": "Overhead Press",
    "махи в стороны": "Lateral Raise",
    "подъём на бицепс": "Barbell Curl",
    "подъем на бицепс": "Barbell Curl",
    "французский жим": "Skull Crusher",
    "разгибания на блоке": "Triceps Pushdown",
}
def _find(text: str, mapping: dict[str, str]) -> str | None:
    text = text.lower()
    for key, value in mapping.items():
        if key in text:
            return value
    return None


def gather_graph_facts(question: str) -> list[str]:
    """Return human-readable facts from the graph based on the question."""
    facts: list[str] = []
    q = question.lower()

    muscle = _find(q, MUSCLE_MAP)
    injury = _find(q, INJURY_MAP)
    equipment = _find(q, EQUIPMENT_MAP)

    # injury-related question
    if injury and ("бол" in q or "травм" in q or "что делать" in q):
        rows = gq.safe_exercises_for_injury(injury)
        names = [r["exercise"] for r in rows[:8]]
        if names:
            facts.append(f"При {injury} избегай упражнений с CONTRAINDICATED_FOR. "
                         f"Безопасные варианты: {', '.join(names)}")
        return facts

    # exercises for muscle
    if muscle:
        if equipment and ("без" in q or "нет" in q):
            rows = gq.exercises_for_muscle_without_equipment(muscle, equipment)
            names = [r["exercise"] for r in rows]
            if names:
                facts.append(
                    f"Упражнения на {muscle} без {equipment}: {', '.join(names)}"
                )
        else:
            rows = gq.exercises_for_muscle(muscle)
            names = [r["exercise"] for r in rows]
            if names:
                facts.append(f"Упражнения на {muscle}: {', '.join(names)}")

    # programs
    if "5x5" in q or "5х5" in q:
        rows = gq.exercises_in_program("5x5")
        names = [r["exercise"] for r in rows]
        if names:
            facts.append(f"Программа 5x5: {', '.join(names)}")
    elif "phul" in q:
        rows = gq.exercises_in_program("PHUL")
        names = [r["exercise"] for r in rows]
        if names:
            facts.append(f"Программа PHUL: {', '.join(names)}")

        # substitutions
    if "замен" in q or "аналог" in q:
        # try russian exercise names first
        target_en = None
        for ru_name, en_name in EXERCISE_MAP.items():
            if ru_name in q:
                target_en = en_name
                break
        # also try direct english match
        if target_en is None:
            for ex in ["Bench Press", "Squat", "Deadlift", "Overhead Press"]:
                if ex.lower() in q:
                    target_en = ex
                    break

        if target_en:
            rows = gq.substitutions_for_exercise(target_en)
            names = [r["substitute"] for r in rows]
            if names:
                facts.append(f"Замены для {target_en}: {', '.join(names)}")

    return facts


if __name__ == "__main__":
    for q in [
        "Какие упражнения на грудь без штанги?",
        "Что делать при боли в плече?",
        "Что входит в программу 5x5?",
        "Чем заменить жим лёжа?",
        "Сколько белка нужно в день?",
    ]:
        print(f"\nQ: {q}")
        for f in gather_graph_facts(q):
            print(f"  -> {f}")
