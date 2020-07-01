import networkx as nx

ALLOW_MISSING_SUPPLIERS = False
ALLOW_EXCESS_COMPONENTS = False

class SystemGraph():
	def __init__(self, comp_graph, supp_graph=None):
		self.comp_graph = comp_graph
		self.supp_graph = supp_graph
		self.graph = self.comp_graph.graph

		if not self.validate_input(comp_graph, supp_graph):
			raise RuntimeError("Invalid or inconsistent input to SystemGraph constructor.")

		if self.supp_graph is not None:
			self.graph = nx.compose(self.graph, self.supp_graph.graph)

		self.name = self.create_name()


	def validate_input(self):
		try:
			if not ALLOW_MISSING_SUPPLIERS:
				for comp in self.comp_graph.graph.nodes:
					self.supp_graph.graph[comp]

			if not ALLOW_EXCESS_COMPONENTS:
				for (src, dst, dst_is_comp) in self.supp_graph.graph.edges.data('risk', default=False):
					if dst_is_comp:
						self.comp_graph.graph[dst]

			return True
		except KeyError:
			return False

	def create_name(self):
		name = self.comp_graph.name
		if self.supp_graph is not None:
			name = ".".join([name, self.supp_graph.name])
		return name

	def __str__(self):
		return name