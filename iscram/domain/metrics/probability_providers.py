from iscram.domain.model import SystemGraph, DataValidationError


def provide_p_unknown_data(sg: SystemGraph):
    base = {n: 0.5 for n in sg.nodes}
    base["indicator"] = 0.0
    return base


def provide_p_direct_from_data(sg: SystemGraph, data, error_on_missing_node=False):
    base = {n: 0.0 for n in sg.nodes}
    # First set risk equal to value in node data
    try:
        for node in base:
            if node in data["nodes"] and "risk" in data["nodes"][node]:
                base[node] = data["nodes"][node]["risk"]
            elif error_on_missing_node:
                raise DataValidationError("Data missing for node: {}".format(node))
    except KeyError:
        if error_on_missing_node:
            raise DataValidationError("Invalid data provided.")

    # If a value exists in edge data then overwrite any previous risk
    node_suppliers = {}
    for edge in sg.edges:
        if "potential" in edge.tags:
            continue
        if edge.src in sg.suppliers and edge.dst in sg.components:
            node_suppliers[edge.dst] = edge.src

    for edge in data.get("edges", []):
        if edge["src"] == node_suppliers.get(edge["dst"]):
            base[edge["dst"]] = edge.get("risk", base[edge["dst"]])

    return base


def provide_p_attribute_heuristic(sg: SystemGraph, data):
    base = {n: 0.0 for n in sg.nodes}

    return base