"""Seed Neo4j graph with strength-training domain.

Nodes:
  Muscle, Equipment, Injury, Program, Exercise

Relationships:
  (Exercise)-[:TARGETS]->(Muscle)
  (Exercise)-[:REQUIRES]->(Equipment)
  (Exercise)-[:CONTRAINDICATED_FOR]->(Injury)
  (Exercise)-[:PART_OF]->(Program)
  (Exercise)-[:SUBSTITUTED_BY]->(Exercise)
"""
from app.graph.neo4j_client import run_query, wipe_all

MUSCLES = [
    "Chest",
    "Upper Chest",
    "Back",
    "Lats",
    "Lower Back",
    "Quads",
    "Hamstrings",
    "Glutes",
    "Front Delts",
    "Side Delts",
    "Rear Delts",
    "Biceps",
    "Triceps",
    "Forearms",
    "Core",
]

EQUIPMENT = [
    "Barbell",
    "Dumbbell",
    "Machine",
    "Bodyweight",
    "Cable",
    "Pull-Up Bar",
    "Bench",
    "Rack",
]

INJURIES = ["Shoulder Pain", "Knee Pain", "Lower Back Pain", "Elbow Pain"]

PROGRAMS = ["5x5", "PHUL", "Full Body"]

# Each exercise: name, targets (muscles), requires (equipment),
# contraindicated (injuries), programs, substituted_by
EXERCISES = [
    {
        "name": "Bench Press",
        "targets": ["Chest", "Front Delts", "Triceps"],
        "requires": ["Barbell", "Bench"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["5x5", "PHUL", "Full Body"],
        "substituted_by": ["Dumbbell Bench Press", "Push-Up"],
    },
    {
        "name": "Dumbbell Bench Press",
        "targets": ["Chest", "Front Delts", "Triceps"],
        "requires": ["Dumbbell", "Bench"],
        "contraindicated": [],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": ["Push-Up"],
    },
    {
        "name": "Push-Up",
        "targets": ["Chest", "Triceps", "Core"],
        "requires": ["Bodyweight"],
        "contraindicated": [],
        "programs": ["Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Incline Dumbbell Press",
        "targets": ["Upper Chest", "Front Delts"],
        "requires": ["Dumbbell", "Bench"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Cable Crossover",
        "targets": ["Chest"],
        "requires": ["Cable"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Squat",
        "targets": ["Quads", "Glutes", "Core"],
        "requires": ["Barbell", "Rack"],
        "contraindicated": ["Knee Pain", "Lower Back Pain"],
        "programs": ["5x5", "PHUL", "Full Body"],
        "substituted_by": ["Leg Press"],
    },
    {
        "name": "Leg Press",
        "targets": ["Quads", "Glutes"],
        "requires": ["Machine"],
        "contraindicated": [],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Romanian Deadlift",
        "targets": ["Hamstrings", "Glutes", "Lower Back"],
        "requires": ["Barbell"],
        "contraindicated": ["Lower Back Pain"],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": ["Leg Curl"],
    },
    {
        "name": "Leg Curl",
        "targets": ["Hamstrings"],
        "requires": ["Machine"],
        "contraindicated": [],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Deadlift",
        "targets": ["Back", "Hamstrings", "Glutes", "Lower Back"],
        "requires": ["Barbell"],
        "contraindicated": ["Lower Back Pain"],
        "programs": ["5x5", "PHUL"],
        "substituted_by": ["Romanian Deadlift"],
    },
    {
        "name": "Pull-Up",
        "targets": ["Lats", "Back", "Biceps"],
        "requires": ["Pull-Up Bar", "Bodyweight"],
        "contraindicated": ["Elbow Pain"],
        "programs": ["PHUL"],
        "substituted_by": ["Lat Pulldown"],
    },
    {
        "name": "Lat Pulldown",
        "targets": ["Lats", "Back"],
        "requires": ["Machine"],
        "contraindicated": [],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Barbell Row",
        "targets": ["Back", "Lats", "Biceps"],
        "requires": ["Barbell"],
        "contraindicated": ["Lower Back Pain"],
        "programs": ["5x5", "PHUL", "Full Body"],
        "substituted_by": ["Dumbbell Row"],
    },
    {
        "name": "Dumbbell Row",
        "targets": ["Back", "Lats"],
        "requires": ["Dumbbell", "Bench"],
        "contraindicated": [],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Overhead Press",
        "targets": ["Front Delts", "Side Delts", "Triceps"],
        "requires": ["Barbell"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["5x5", "PHUL", "Full Body"],
        "substituted_by": ["Dumbbell Shoulder Press"],
    },
    {
        "name": "Dumbbell Shoulder Press",
        "targets": ["Front Delts", "Side Delts", "Triceps"],
        "requires": ["Dumbbell"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Lateral Raise",
        "targets": ["Side Delts"],
        "requires": ["Dumbbell"],
        "contraindicated": ["Shoulder Pain"],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Face Pull",
        "targets": ["Rear Delts", "Back"],
        "requires": ["Cable"],
        "contraindicated": [],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Barbell Curl",
        "targets": ["Biceps", "Forearms"],
        "requires": ["Barbell"],
        "contraindicated": ["Elbow Pain"],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": ["Dumbbell Curl"],
    },
    {
        "name": "Dumbbell Curl",
        "targets": ["Biceps", "Forearms"],
        "requires": ["Dumbbell"],
        "contraindicated": [],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Hammer Curl",
        "targets": ["Biceps", "Forearms"],
        "requires": ["Dumbbell"],
        "contraindicated": [],
        "programs": ["PHUL"],
        "substituted_by": [],
    },
    {
        "name": "Triceps Pushdown",
        "targets": ["Triceps"],
        "requires": ["Cable"],
        "contraindicated": [],
        "programs": ["PHUL", "Full Body"],
        "substituted_by": [],
    },
    {
        "name": "Skull Crusher",
        "targets": ["Triceps"],
        "requires": ["Barbell", "Bench"],
        "contraindicated": ["Elbow Pain"],
        "programs": ["PHUL"],
        "substituted_by": ["Triceps Pushdown"],
    },
    {
        "name": "Dips",
        "targets": ["Triceps", "Chest"],
        "requires": ["Bodyweight"],
        "contraindicated": ["Shoulder Pain", "Elbow Pain"],
        "programs": ["PHUL"],
        "substituted_by": ["Triceps Pushdown"],
    },
    {
        "name": "Plank",
        "targets": ["Core"],
        "requires": ["Bodyweight"],
        "contraindicated": [],
        "programs": ["Full Body"],
        "substituted_by": [],
    },
]


def _seed_simple(label: str, names: list[str]) -> None:
    for name in names:
        run_query(f"MERGE (n:{label} {{name: $name}})", {"name": name})


def seed_nodes() -> None:
    _seed_simple("Muscle", MUSCLES)
    _seed_simple("Equipment", EQUIPMENT)
    _seed_simple("Injury", INJURIES)
    _seed_simple("Program", PROGRAMS)
    for ex in EXERCISES:
        run_query("MERGE (e:Exercise {name: $name})", {"name": ex["name"]})


def seed_relationships() -> None:
    for ex in EXERCISES:
        name = ex["name"]
        for m in ex["targets"]:
            run_query(
                """
                MATCH (e:Exercise {name: $ex}), (m:Muscle {name: $m})
                MERGE (e)-[:TARGETS]->(m)
                """,
                {"ex": name, "m": m},
            )
        for eq in ex["requires"]:
            run_query(
                """
                MATCH (e:Exercise {name: $ex}), (eq:Equipment {name: $eq})
                MERGE (e)-[:REQUIRES]->(eq)
                """,
                {"ex": name, "eq": eq},
            )
        for inj in ex["contraindicated"]:
            run_query(
                """
                MATCH (e:Exercise {name: $ex}), (i:Injury {name: $inj})
                MERGE (e)-[:CONTRAINDICATED_FOR]->(i)
                """,
                {"ex": name, "inj": inj},
            )
        for p in ex["programs"]:
            run_query(
                """
                MATCH (e:Exercise {name: $ex}), (p:Program {name: $p})
                MERGE (e)-[:PART_OF]->(p)
                """,
                {"ex": name, "p": p},
            )
        for sub in ex["substituted_by"]:
            run_query(
                """
                MATCH (e:Exercise {name: $ex}), (s:Exercise {name: $sub})
                MERGE (e)-[:SUBSTITUTED_BY]->(s)
                """,
                {"ex": name, "sub": sub},
            )


def main() -> None:
    print("Wiping existing graph...")
    wipe_all()

    print("Seeding nodes...")
    seed_nodes()

    print("Seeding relationships...")
    seed_relationships()

    print("\nCounts:")
    counts = run_query(
        """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(*) AS count
        ORDER BY label
        """
    )
    for row in counts:
        print(f"  {row['label']}: {row['count']}")

    rel_counts = run_query(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(*) AS count
        ORDER BY type
        """
    )
    print("\nRelationships:")
    for row in rel_counts:
        print(f"  {row['type']}: {row['count']}")


if __name__ == "__main__":
    main()
