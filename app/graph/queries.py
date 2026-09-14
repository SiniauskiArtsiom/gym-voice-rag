"""High-level graph queries for the assistant."""
from app.graph.neo4j_client import run_query


def exercises_for_muscle(muscle: str) -> list[dict]:
    """All exercises targeting a given muscle."""
    return run_query(
        """
        MATCH (e:Exercise)-[:TARGETS]->(m:Muscle {name: $muscle})
        RETURN e.name AS exercise
        ORDER BY e.name
        """,
        {"muscle": muscle},
    )


def exercises_for_muscle_without_equipment(
    muscle: str, equipment: str
) -> list[dict]:
    """Exercises targeting muscle that don't require the given equipment."""
    return run_query(
        """
        MATCH (e:Exercise)-[:TARGETS]->(m:Muscle {name: $muscle})
        WHERE NOT (e)-[:REQUIRES]->(:Equipment {name: $equipment})
        RETURN e.name AS exercise
        ORDER BY e.name
        """,
        {"muscle": muscle, "equipment": equipment},
    )


def safe_exercises_for_injury(injury: str) -> list[dict]:
    """Exercises that are NOT contraindicated for the given injury."""
    return run_query(
        """
        MATCH (e:Exercise)
        WHERE NOT (e)-[:CONTRAINDICATED_FOR]->(:Injury {name: $injury})
        RETURN e.name AS exercise
        ORDER BY e.name
        LIMIT 20
        """,
        {"injury": injury},
    )


def substitutions_for_exercise(exercise: str) -> list[dict]:
    """Get all substitutes for an exercise, recursively."""
    return run_query(
        """
        MATCH (e:Exercise {name: $exercise})-[:SUBSTITUTED_BY]->(s:Exercise)
        RETURN s.name AS substitute
        ORDER BY s.name
        """,
        {"exercise": exercise},
    )


def exercises_in_program(program: str) -> list[dict]:
    """All exercises belonging to a program."""
    return run_query(
        """
        MATCH (e:Exercise)-[:PART_OF]->(p:Program {name: $program})
        RETURN e.name AS exercise
        ORDER BY e.name
        """,
        {"program": program},
    )


def muscles_for_exercise(exercise: str) -> list[dict]:
    """Which muscles an exercise targets."""
    return run_query(
        """
        MATCH (e:Exercise {name: $exercise})-[:TARGETS]->(m:Muscle)
        RETURN m.name AS muscle
        ORDER BY m.name
        """,
        {"exercise": exercise},
    )


if __name__ == "__main__":
    print("Exercises for Chest:")
    for r in exercises_for_muscle("Chest"):
        print(" ", r["exercise"])

    print("\nChest without Barbell:")
    for r in exercises_for_muscle_without_equipment("Chest", "Barbell"):
        print(" ", r["exercise"])

    print("\nSubstitutes for Bench Press:")
    for r in substitutions_for_exercise("Bench Press"):
        print(" ", r["substitute"])

    print("\nExercises in 5x5:")
    for r in exercises_in_program("5x5"):
        print(" ", r["exercise"])

    print("\nMuscles for Squat:")
    for r in muscles_for_exercise("Squat"):
        print(" ", r["muscle"])
