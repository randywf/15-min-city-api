import math
from pprint import pprint


def build_amenity_importance_map(
    amenity_state: dict,
    *,
    min_importance: float,
) -> dict[str, float]:
    """
    Returns: { amenity_name: importance }
    """
    # only enabled categories
    enabled_categories = [
        (cat, cfg)
        for cat, cfg in amenity_state.items()
        if cfg.get("enabled", False)
    ]

    if not enabled_categories:
        return {}

    # normalize rank → importance
    ranks = [cfg["rank"] for _, cfg in enabled_categories]
    min_rank, max_rank = min(ranks), max(ranks)
    span = max(1, max_rank - min_rank)

    importance_map = {}

    for _, cfg in enabled_categories:
        rank = cfg["rank"]
        importance = 1 - ((rank - min_rank) / span)
        importance = max(importance, min_importance)

        for amenity, a_cfg in cfg["amenities"].items():
            if a_cfg.get("enabled", False):
                importance_map[amenity] = importance

    return importance_map

import math


def calculate_score(
    amenities: list[dict],
    amenity_state: dict,
    max_distance: float,
    *,
    min_importance: float = 0.2,
    density_strength: float = 1.5,
) -> float:
    if not amenities or not amenity_state:
        return 0.0

    importance_map = build_amenity_importance_map(
        amenity_state,
        min_importance=min_importance,
    )

    if not importance_map:
        return 0.0

    # group distances per enabled amenity
    grouped: dict[str, list[float]] = {}
    for a in amenities:
        t = a["amenity"]
        if t in importance_map:
            grouped.setdefault(t, []).append(a["distance"])

    raw_score = 0.0
    max_possible = sum(importance_map.values())

    for amenity, importance in importance_map.items():
        if amenity not in grouped:
            continue

        # Step 1: distance decay
        weighted_sum = sum(
            math.exp(-d / max_distance)
            for d in grouped[amenity]
        )

        # Step 2: density saturation
        saturation = 1 - math.exp(
            -weighted_sum / density_strength
        )

        raw_score += importance * saturation

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

    amenity_state = {
        "mobility": {
            "rank": 10,
            "enabled": True,
            "amenities": {
                "parking": {"enabled": True},
            },
        },
        "food_and_drinks": {
            "rank": 50,
            "enabled": True,
            "amenities": {
                "restaurant": {"enabled": True},
                "cafe": {"enabled": True},
                "bar": {"enabled": False},  # disabled
            },
        },
        "education": {
            "rank": 30,
            "enabled": True,
            "amenities": {
                "library": {"enabled": True},
            },
        },
        "health": {
            "rank": 20,
            "enabled": False,  # entire category disabled
            "amenities": {
                "pharmacy": {"enabled": True},
            },
        },
    }
    max_distance = max(a["distance"] for a in amenities)

    print("\nAmenity importance map:")
    pprint(build_amenity_importance_map(amenity_state, min_importance=0.2))

    print("\nInput amenities:")
    pprint(amenities)

    score = calculate_score(
        amenities=amenities,
        amenity_state=amenity_state,
        max_distance=500,
    )

    print(f"\nFinal score: {score}/10\n")

