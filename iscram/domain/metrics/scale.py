from typing import Dict


def scale_proportionally(data: Dict):
    total = sum(data.values())

    if total == 0:
        return data
    else:
        return {k: (v/total) for k, v in data.items()}


def scale_min_max(data: Dict):
    min_v= min(data.values())
    max_v = max(data.values())

    if (max_v - min_v) == 0:
        return data
    else:
        return {k: ((v-min_v) / (max_v-min_v)) for k, v in data.items()}


def apply_scaling(interim_results, scaling_method):
    if scaling_method == "PROPORTIONAL":
        return scale_proportionally(interim_results)
    elif scaling_method == "MIN_MAX":
        return scale_min_max(interim_results)
    else:
        return interim_results
