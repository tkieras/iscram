from iscram.domain.model import SystemGraph, DataValidationError


def provide_p_unknown_data(sg: SystemGraph):
    base = {n: 0.5 for n in sg.nodes}
    base["indicator"] = 0.0
    return base


def provide_p_direct_from_data(sg: SystemGraph, data, error_on_missing_node=False):
    base = {n: 0.0 for n in sg.nodes}
    try:
        for node in base:
            if node in data["nodes"] and "risk" in data["nodes"][node]:
                base[node] = data["nodes"][node]["risk"]
            elif error_on_missing_node:
                raise DataValidationError("Data missing for node: {}".format(node))
    except KeyError:
        if error_on_missing_node:
            raise DataValidationError("Invalid data provided.")

    return base


def provide_p_attribute_heuristic(sg: SystemGraph, data):
    base = {n: 0.0 for n in sg.nodes}

    return base