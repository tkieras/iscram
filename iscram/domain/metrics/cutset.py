from typing import FrozenSet, List, Set, Dict
from collections import Counter

from iscram.domain.model import SystemGraph
from iscram.domain.metrics.graph_functions import (
    convert_system_graph_to_tree, TreeError, get_tree_boolean_function_lambda,
    enumerate_all_combinations
)


class MOCUSError(RuntimeError):
    pass


def find_minimal_cutsets(sg: SystemGraph, ignore_suppliers=True) -> FrozenSet[FrozenSet[int]]:
    return mocus(sg, ignore_suppliers)


def mocus(sg: SystemGraph, ignore_suppliers=True) -> FrozenSet[FrozenSet[int]]:
    """ Something should be said to note that the input graph differs from
        a traditional fault-tree. Specifically, all nodes here are both events and logic gates.
        So strictly this is a MOCUS-like algorithm.
    """
    # Risk metrics are undefined when multiple suppliers of a component are included.
    # Therefore, mocus should not be called in such cases.
    if not ignore_suppliers:
        offering_counter = Counter(map(lambda of: of.component_id, sg.offerings))
        if any(map(lambda cm: offering_counter[cm] > 1, offering_counter.elements())):
            raise MOCUSError

    # Currently only trees are supported for MOCUS
    try:
        graph, logic = convert_system_graph_to_tree(sg, ignore_suppliers)
    except TreeError:
        raise MOCUSError

    working_result = [{-1}]

    recursive_mocus(-1, graph, logic, working_result)

    # The indicator should be removed from the cutsets since it is not a component or supplier
    working_result.remove({-1})

    final_result = frozenset([frozenset(cutset) for cutset in working_result])

    return final_result


def recursive_mocus(n: int, graph: Dict, logic: Dict, cutsets: List[Set]) -> None:
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


def brute_force_find_cutsets(sg: SystemGraph) -> FrozenSet[FrozenSet[int]]:
    """ This is brute force and infeasible for even moderate graphs,
    but useful to check methods on small examples """

    graph, logic = convert_system_graph_to_tree(sg, ignore_suppliers=True)
    indicator_fn = get_tree_boolean_function_lambda(-1, graph, logic)

    component_ids = {c.identifier for c in sg.components}

    temporary_results = []
    x_template = {n: False for n in component_ids}
    x_template[-1] = False  # indicator, always false manually

    for true_nodes in enumerate_all_combinations(component_ids):
        true_nodes = frozenset(true_nodes)
        test_x = x_template.copy()
        for n in true_nodes:
            test_x[n] = True

        if indicator_fn(test_x):
            temporary_results.append(true_nodes)

    sorted_temp_results = sorted(temporary_results, key=lambda r: len(r))
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
