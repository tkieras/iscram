import random

from iscram.domain.model import (
    SystemGraph, Component, RiskRelation, Indicator
)
from iscram.adapters.json import dump_system_graph_json_str


def gen_random_tree(n, save=False):
    def rand_logic():
        return random.choice(["and", "or"])

    def rand_risk():
        return random.uniform(0.001, 0.1)

    def rand_cost():
        return random.randint(0, 100)

    unused = ["x"+str(i) for i in range(1, n)]
    random.shuffle(unused)

    used = ["indicator"]
    nodes = {"indicator"}
    edges = set()

    while unused:
        child = unused.pop(0)
        parent = random.choice(used)
        nodes.add(child)
        edges.add((child, parent))
        used.append(child)

    nodes.remove("indicator")
    ind_edges = list(filter(lambda e: e[1] == "indicator", edges))
    for edge in ind_edges:
        edges.remove(edge)

    indicator = Indicator(rand_logic(), frozenset([RiskRelation(*edge) for edge in ind_edges]))

    components = frozenset([Component(node, rand_logic(), rand_risk(), rand_cost()) for node in nodes])

    deps = frozenset([RiskRelation(*edge) for edge in edges])

    sg = SystemGraph("rand_tree", components, frozenset(), deps, frozenset(), indicator)

    if save:
        with open("random_tree_{}.json".format(n), "w") as outfile:
            outfile.write(dump_system_graph_json_str(sg))

    return sg


if __name__ == "__main__":
    gen_random_tree(50, True)