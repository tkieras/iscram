import random
import json
from typing import Dict
from iscram.domain.model import SystemGraph


def gen_random_tree(n, save=False, generate_data=True) -> (SystemGraph, Dict):
    def rand_logic():
        return random.choice(["and", "or"])

    def rand_risk():
        return random.uniform(0.001, 0.1)

    def rand_cost():
        return random.randint(0, 100)

    unused = ["x"+str(i) for i in range(1, n)]
    random.shuffle(unused)

    used = ["indicator"]
    nodes = {"indicator": {"tags": ["indicator"], "logic": {"component": rand_logic()}}}
    edges = []

    while unused:
        child_id = unused.pop(0)
        parent_id = random.choice(used)
        nodes[child_id] = {"tags": ["component"], "logic": {"component": rand_logic()}}
        edges.append({"src": child_id, "dst": parent_id})
        used.append(child_id)

    sg_dict = {
        "nodes": nodes,
        "edges": edges
    }

    data_dict = None
    if generate_data:
        data_dict = {
            node: {"risk": rand_risk()} for node in nodes.keys()
        }
        data_dict["indicator"]["risk"] = 0

    if save:
        filename = "rand_system_graph_tree_{}".format(n)
        with open(filename+".json", "w") as outfile:
            json.dump(sg_dict, outfile, indent=4)
        if data_dict is not None:
            with open(filename+"_data.json", "w") as outfile:
                json.dump(data_dict, outfile, indent=4)

    return SystemGraph(**sg_dict), data_dict


if __name__ == "__main__":
    gen_random_tree(500, True, True)