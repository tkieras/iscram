import networkx as nx
from iscram.shared import validate_params
from iscram.shared.named_data import NamedData

class ComponentGraph():
	def __init__(self, adj_list, logic_dict, default_risks):
		self.graph = nx.DiGraph()

		if not self.validate_input(adj_list.data, logic_dict.data, default_risks.data):
			raise RuntimeError("Invalid or inconsistent input to ComponentGraph constructor.")

		for key in logic_dict.data.keys():
			self.graph.add_node(key, logic=logic_dict.data[key], default_risk=default_risks.data[key])

		for src, adj in adj_list.data.items():
			for dst in adj:
				self.graph.add_edge(src, dst)

		self.deps = [adj_list, logic_dict, default_risks] # not sure if we need to keep these references
		self.name = self.create_name()

	def validate_input(self, adj_list, logic_dict, default_risks):
		try:

			for key, value in logic_dict.items():
				assert(validate_params.validate_logic(value))
				r = default_risks[key]
				assert(validate_params.validate_risk(r))

			for src, adj in adj_list.items():
				logic_dict[src]
				for dst in adj:
					logic_dict[dst]

			return True

		except (KeyError, AssertionError):
			return False

	def create_name(self):
		return ".".join([dep.name for dep in self.deps])

	def __str__(self):
		return self.name


	
