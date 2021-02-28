from typing import FrozenSet, List, Set, Dict
from collections import defaultdict

from iscram.domain.model import SystemGraph
from iscram.domain.metrics.graph_functions import (
    prep_for_mocus, get_tree_boolean_function_lambda,
    enumerate_all_combinations
)


class MOCUSError(RuntimeError):
    pass


def find_minimal_cutsets(sg: SystemGraph, ignore_suppliers=True) -> FrozenSet[FrozenSet[str]]:
    return mocus(sg, ignore_suppliers)


def mocus(sg: SystemGraph, ignore_suppliers=True) -> FrozenSet[FrozenSet[str]]:
    """ Something should be said to note that the input graph differs from
        a traditional fault-tree. Specifically, all nodes here are both events and logic gates.
        So strictly this is a MOCUS-like algorithm.
    """
    # Risk metrics are undefined when multiple suppliers of a component are included.
    # Therefore, mocus should not be called in such cases.

    if not ignore_suppliers:
        pass
        ## replace this check with a similar check
        ### that asserts only one supplier is a risk_src for a given component
        # offering_counter = Counter(map(lambda of: of.component_id, sg.offerings))
        # if any(map(lambda cm: offering_counter[cm] > 1, offering_counter.elements())):
        #     raise MOCUSError

    graph, logic = prep_for_mocus(sg, ignore_suppliers)

    working_result = [{"indicator"}]
    recursive_mocus("indicator", graph, logic, working_result)
    # The indicator should be removed from the cutsets since it is not a component or supplier
    working_result.remove({"indicator"})

    working_result = minimize_cutsets([frozenset(cutset) for cutset in working_result])

    return remove_fictive_gate_cutsets(working_result)


def recursive_mocus(n: str, graph: Dict, logic: Dict, cutsets: List[Set]) -> None:
    children = graph.get(n, None)
    if not children or len(children) == 0:
        return

    # pseudocode for MOCUS
    # let n be current working node
    # let c be predecessors(children) of n

    # if n is "and" then
    #   for each cutset including n
    #   add additional cutset without n but with c instead
    # if n is "or" then
    #   for each cutset including n
    #   for each child C in c
    # add additional cutset without n but with C instead

    n_involved = filter(lambda x: n in x, cutsets)
    tmp = []

    if logic[n] == "and":
        for cutset in n_involved:
            new_cutset = cutset - {n}
            new_cutset.update(children)
            tmp.append(new_cutset)
        cutsets.extend(tmp)
    elif logic[n] == "or":
        for cutset in n_involved:
            for child in children:
                new_cutset = cutset - {n}
                new_cutset.add(child)
                tmp.append(new_cutset)
        cutsets.extend(tmp)

    for child in children:
        recursive_mocus(child, graph, logic, cutsets)

#
# def explore_non_basic_event_effects():
#     from collections import defaultdict
#     logic = defaultdict(lambda: "and")
#     main_gates = ["1-m", "2-m", "3-m", "4-m"]
#     dep_gates = ["1-d", "2-d", "3-d", "4-d"]
#     for m in main_gates:
#         logic[m] = "or"
#
#     graph = {
#         "i" : ["1-m"],
#         "1-m" : ["1-b", "1-s", "1-d"],
#         "2-m" : ["2-b", "2-s", "2-d"],
#         "3-m" : ["3-b", "3-s", "3-d"],
#         "4-m" : ["4-b", "4-s", "4-d"],
#         "1-d" : ["2-m", "3-m"],
#         "2-d" : ["4-m"],
#         "3-d" : ["4-m"],
#         "1-s" : ["x"],
#         "2-s" : ["x"],
#         "3-s" : ["x"],
#         "4-s" : ["x"]
#     }
#     cutsets = [{"i"}]
#
#     recursive_mocus("i", graph, logic, cutsets)
#
#     cutsets.remove({"i"})
#     return cutsets


def brute_force_find_cutsets(sg: SystemGraph) -> FrozenSet[FrozenSet[str]]:
    """ This is brute force and infeasible for even moderate graphs,
    but useful to check methods on small examples """

    graph, logic = prep_for_mocus(sg, ignore_suppliers=True)
    indicator_fn = get_tree_boolean_function_lambda("indicator", graph, logic)

    component_ids = {c.identifier for c in sg.components}

    temporary_results = []
    x_template = defaultdict(lambda: False)
    x_template.update({n: False for n in component_ids})
    x_template["indicator"] = False  # indicator, always false manually

    for true_nodes in enumerate_all_combinations(component_ids):
        true_nodes = frozenset(true_nodes)
        test_x = x_template.copy()
        for n in true_nodes:
            test_x[n] = True

        if indicator_fn(test_x):
            temporary_results.append(true_nodes)

    return minimize_cutsets(temporary_results)


def minimize_cutsets(cutsets: List[FrozenSet]) -> FrozenSet[FrozenSet[str]]:
    sorted_temp_results = sorted(cutsets, key=lambda r: len(r))
    try:
        result = [sorted_temp_results[0]]
    except IndexError:
        return frozenset()

    for possible in sorted_temp_results[1:]:
        minimal = True
        for saved in result:
            if saved < possible:
                minimal = False
                break

        if minimal:
            result.append(possible)

    return frozenset(result)


def is_fictive(node):
    return node[0] == "@"


def remove_fictive_gate_cutsets(cutsets):
    def no_fictive(cutset):
        return not any([is_fictive(node) for node in cutset])

    return frozenset(list(filter(no_fictive, cutsets)))


## TODO: supplier only cutsets; combine with supplier-excluded cutsets
# old code that does some of that below

# import csv
# import pprint
# def load_named_cutsets():
#     named_cutsets = []
#     with open("named_cutsets.csv", "r") as infile:
#         reader = csv.reader(infile)
#         for line in reader:
#             named_cutsets.append(line)
#     return named_cutsets
#
#
# def binary_to_fill_val(val, i, components, suppliers):
#     if val % 2:
#             return suppliers[i]
#     else:
#             return components[i]
#
# def binary_combine(components, suppliers):
#     if len(components) != len(suppliers):
#         return None
#     results = []
#     for i in range(2**len(components)):
#         comb = []
#         idx = 0
#         while idx < len(components):
#             comb.append(binary_to_fill_val(i, idx, \
#                 components, suppliers))
#             idx += 1
#             i = i >> 1
#         results.append(comb)
#     return results
#
#
# def combine_with_suppliers(components):
#     combinations = set()
#     suppliers = ["s_{}".format(c) for c in components]
#
#     comb_res = binary_combine(components,suppliers)
#     for r in comb_res:
#         combinations.add(tuple(r))
#     return combinations
#
# def match(cut, subset, sub):
#     cutset = set(cut)
#     subset = set(subset)
#     newcut = set()
#     if subset.issubset(cutset):
#         newcut = cutset - subset
#         newcut.add(sub)
#         return tuple(newcut)
#     elif cutset.issubset(subset):
#         newcut.add(sub)
#         return tuple(newcut)
#     else:
#         return None
#
#
# allcuts = load_named_cutsets()
#
# new_cutsets = set()
# for i in range(len(allcuts)):
#     new_cutsets = new_cutsets.union(combine_with_suppliers(allcuts[i]))
#
# #pprint.pprint(new_cutsets)
#
# owner_dict = {
#     "o1" : ["imu", "maps"],
#     "o2" : ["accel_act", "brake_act"],
#     "o3" : ["v2v", "radar"]
# }
# def add_owners(owner_dict, new_cutsets):
#     new_new_new_cutsets = set(new_cutsets)
#
#     for oname, ochildren in owner_dict.items():
#         subsets = combine_with_suppliers(ochildren)
#         new_new_cutsets = set()
#         for newcut in new_new_new_cutsets:
#             found = False
#             for subset in subsets:
#                 res = match(newcut, subset, oname)
#                 if res is not None:
#                     new_new_cutsets.add(res)
#                     if not found:
#                         new_new_cutsets.add(tuple(newcut))
#                     found = True
#             if not found:
#                 new_new_cutsets.add(tuple(newcut))
#         new_new_new_cutsets = new_new_new_cutsets.union(new_new_cutsets)
#
#     return new_new_new_cutsets
#
# final_cutsets = add_owners(owner_dict, new_cutsets)
# pprint.pprint(final_cutsets)
# print(len(final_cutsets))
#
# with open("exploded_cutsets.csv", "w") as of:
#     writer = csv.writer(of)
#     for cutset in final_cutsets:
#         writer.writerow(cutset)
#
