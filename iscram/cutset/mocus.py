import networkx as nx

def valid_for_mocus(graph):
	for node, has_logic in graph.nodes(data=logic_type, default=False):
		if not has_logic:
			return False

	if not(nx.algorithms.tree.is_tree(graph)):
		return False

	return True

def mocus(graph):
	if not valid_for_mocus(graph):
		return None

	