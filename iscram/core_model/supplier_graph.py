import networkx as nx
from iscram.shared.named_data import NamedData
from iscram.shared import validate_params

class SupplierGraph():
	def __init__(self, adj_list, s_trusts, risks, costs):
		self.graph = nx.DiGraph()

		if not self.validate_input(adj_list.data, s_trusts.data, risks.data, costs.data):
			raise RuntimeError("Invalid or inconsistent input to SupplierGraph constructor.")

		for key, value in s_trusts.data.items():
			self.graph.add_node(key, trust=value)

		for src, adj in adj_list.data.items():
			for dst in adj:
				if dst in s_trusts.data.keys():
					self.graph.add_edge(src, dst)

		for src, adj in risks.data.items():
			for dst in adj.keys():
				r = risks.data[src][dst]
				c = costs.data[src][dst]
				self.graph.add_edge(src, dst, risk=r, cost=c)

		self.deps = [adj_list, s_trusts, risks, costs]
		self.name = self.create_name()

	def validate_input(self, adj_list, s_trusts, risks, costs):
		try:
			for key, value in s_trusts.items():
				assert(validate_params.validate_risk(value))

			for src, adj in adj_list.items():
				s_trusts[src]
				for dst in adj:
					if dst not in s_trusts.keys():
						risks[src][dst]


			for src, adj in risks.items():
				for dst in adj.keys():
					assert(validate_params.validate_risk(risks[src][dst]))
					assert(validate_params.validate_cost(costs[src][dst]))


			return True
		except (AssertionError, KeyError):
			return False

	def create_name(self):
		return ".".join([dep.name for dep in self.deps])

	def __str__(self):
		return self.name


if __name__=="__main__":

	adj_list = NamedData("s01", {"supplier1" : ["component1"], "supplier2" : ["supplier1"], "supplier2" : ["component2"] })
	s_trusts = NamedData("st01", {"supplier1" : 0.8, "supplier2" : 0.98})
	risks = NamedData("r01", {"supplier1" : {"component1" : 0.01}, "supplier2": {"component2": 0.1}})
	costs = NamedData("c01", {"supplier1" : {"component1" : 10}, "supplier2" : {"component2" : 5}})

	supp_graph = SupplierGraph(adj_list, s_trusts, risks, costs)
	print(supp_graph)