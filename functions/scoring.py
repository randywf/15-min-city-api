import math

def calculate_score(
    amenities: list[dict],
    priority_order: list[str],
    max_distance: float,
    min_importance: float = 0.2,
    type_cap_multiplier: float = 1.0,  # 1.0 = max equals importance
) -> float:
    if not amenities or not priority_order:
        return 0.0

    priority_index = {
        amenity: i for i, amenity in enumerate(priority_order)
    }

    # Group distances by amenity type
    grouped = {}
    for a in amenities:
        t = a["amenity"]
        if t in priority_index:
            grouped.setdefault(t, []).append(a["distance"])

    raw_score = 0.0
    max_possible = 0.0

    for t, idx in priority_index.items():
        importance = 1 - (idx / max(1, len(priority_order) - 1))
        importance = max(importance, min_importance)
        max_possible += importance

        if t not in grouped:
            continue

        type_score = 0.0
        for d in grouped[t]:
            distance_weight = math.exp(-d / max_distance)
            type_score += importance * distance_weight

        # 🔒 Cap contribution per type
        raw_score += min(type_score, importance * type_cap_multiplier)

    normalized = (raw_score / max_possible) * 10
    return round(min(10.0, normalized), 2)

if __name__ == "__main__":
    # --- test data (similar to your real output) ---
    amenities = [
        {"amenity": "restaurant", "distance": 140.0},
        {"amenity": "cafe", "distance": 120.0},
        {"amenity": "bar", "distance": 170.0},
        {"amenity": "pharmacy", "distance": 150.0},
        {"amenity": "library", "distance": 125.0},
        {"amenity": "parking", "distance": 100.0},
        {"amenity": "parking", "distance": 100.0},
        {"amenity": "pharmacy", "distance": 190.0},
    ]

    priority_order = [
        "restaurant",
        "cafe",
        "bar",
        "pharmacy",
        "library",
    ]

    max_distance = max(a["distance"] for a in amenities)

    score = calculate_score(
        amenities=amenities,
        priority_order=priority_order,
        max_distance=max_distance,
    )

    print("=== SCORE TEST ===")
    print(f"Priority order: {priority_order}")
    print(f"Max distance: {max_distance:.1f} m\n")

    for a in amenities:
        print(f"- {a['amenity']:10s} @ {a['distance']:6.1f} m")

    print("\nFinal score:", score)
