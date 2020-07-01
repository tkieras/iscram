import json
from iscram.shared.named_data import NamedData

def dict_to_NamedData(d):
	return NamedData(name=d["name"], data=d["data"])


class DataLoader:
	def __init__(self, path):
		self.path = path + "/"

	def load_comp_graph_adj_list(self):
		with open(self.path + "comp_graph_adj_list.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))

	def load_comp_graph_default_risks(self):
		with open(self.path + "comp_graph_default_risks.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))
	def load_comp_graph_logic_dict(self):
		with open(self.path + "comp_graph_logic_dict.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))
	def load_supp_graph_adj_list(self):
		with open(self.path + "supp_graph_adj_list.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))
	def load_supp_graph_s_trusts(self):
		with open(self.path + "supp_graph_s_trusts.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))
	def load_supp_graph_costs(self):
		with open(self.path + "supp_graph_costs.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))
	def load_supp_graph_risks(self):
		with open(self.path + "supp_graph_risks.json", "r") as fp:
			return dict_to_NamedData(json.load(fp))

