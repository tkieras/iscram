from typing import Dict

import jsons

from iscram.domain.model import SystemGraph


def dump_system_graph_json(sg: SystemGraph):
    return jsons.dump(sg)


def load_system_graph_json(input_dict: Dict) -> SystemGraph:
    return jsons.load(input_dict, SystemGraph)


def dump_system_graph_json_str(sg: SystemGraph):
    return jsons.dumps(sg)


def load_system_graph_json_str(input_str: str) -> SystemGraph:
    return jsons.loads(input_str, SystemGraph)
