from typing import Dict, List, Tuple

import pyomo.environ as pyo

from iscram.domain.model import SystemGraph, Edge
from iscram.domain.metrics.importance import birnbaum_structural_importance


class OptimizationError(Exception):
    def __init__(self, message):
        self.message = message


class SupplierChoiceProblem:
    def __init__(self, sg: SystemGraph, data: Dict):
        """ Parameters extracted/computed from SystemGraph and data:
                   - N int: number of components in system
                   - M int: number of suppliers in system
                   - NxM matrix of floats: component_risks
                   - NxM matrix of floats: component_costs
                   - Nx1 vector of floats: component_importances
                   - NxM matrix of booleans: valid_choices pairings of supplier/component
                   - Mx1 vector of floats: supplier risks
                   - K int: number of supplier groups in system
                   - KxM matrix of booleans: membership of suppliers in groups
                   - Kx1 vector of float: group risks
               """

        all_suppliers = set(sg.suppliers)
        supplier_groups_raw = sg.supplier_groups

        if len(all_suppliers) == 0 or len(supplier_groups_raw) == 0:
            raise OptimizationError("No suppliers found.")

        self.N = len(sg.components)
        self.M = len(all_suppliers)
        self.K = len(supplier_groups_raw)
        self.component_risks = [[0 for _ in range(self.M)] for _ in range(self.N)]
        self.component_costs = [[0 for _ in range(self.M)] for _ in range(self.N)]
        self.potential_suppliers = [[0 for _ in range(self.M)] for _ in range(self.N)]
        self.component_importances = [False for _ in range(self.N)]
        self.supplier_risks = [0 for _ in range(self.M)]
        self.supplier_groups = [[False for _ in range(self.M)] for _ in range(self.K)]
        self.group_risks = [0 for _ in range(self.K)]
        component_index_map = {cname: idx for idx, cname in enumerate(sorted(sg.components))}
        supplier_index_map = {sname: idx for idx, sname in enumerate(sorted(all_suppliers))}
        group_index_map = {gname: idx for idx, gname in enumerate(sorted(supplier_groups_raw.keys()))}
        pre_existing_suppliers = {}  # map component name to supplier name

        # begin with any supplier/component information in the system graph already
        for edge in sg.edges:
            if edge.src in all_suppliers and edge.dst in sg.components:
                pre_existing_suppliers[edge.dst] = edge.src
                i = component_index_map[edge.dst]
                j = supplier_index_map[edge.src]
                self.potential_suppliers[i][j] = True

        # extract risk values which are given in node data.
        for nodeId, nodeData in data.get("nodes", {}).items():
            if nodeId in sg.components:
                i = component_index_map[nodeId]
                supplier_of_i = pre_existing_suppliers.get(nodeId, None)
                save = nodeData.get("risk", 0)
                if supplier_of_i is not None:
                    j = supplier_index_map[supplier_of_i]
                    self.component_risks[i][j] = save
                else:
                    # This should not generally be used, but if a node has no supplier it may still contribute risk.
                    self.component_risks[i] = [save] * self.M
            elif nodeId in all_suppliers:
                self.supplier_risks[supplier_index_map[nodeId]] = nodeData.get("risk", 0.0)
                if group_index_map.get(nodeId):
                    self.group_risks[group_index_map.get(nodeId)] = nodeData.get("risk", 0.0)

        # extract risk and cost values if given in data-edges for valid pairings
        for edgeDict in data.get("edges", []):
            if edgeDict["src"] in all_suppliers and edgeDict["dst"] in sg.components:
                i = component_index_map[edgeDict["dst"]]
                j = supplier_index_map[edgeDict["src"]]
                self.component_risks[i][j] = edgeDict.get("risk", 0.0)
                self.component_costs[i][j] = edgeDict.get("cost", 0.0)
                self.potential_suppliers[i][j] = True

        # save indices for use after optimization
        self.map_index_component = invert_dict(component_index_map)
        self.map_index_supplier = invert_dict(supplier_index_map)
        self.map_index_group = invert_dict(group_index_map)

        # load supplier groups into matrix
        for root, group in supplier_groups_raw.items():
            k = group_index_map[root]
            self.supplier_groups[k] = [True if self.map_index_supplier[m] in group else False for m in range(0, self.M)]

        # load component importances
        all_importances = birnbaum_structural_importance(sg, bdd_with_root=sg.get_bdd_with_root())
        for i in range(0, self.N):
            self.component_importances[i] = all_importances[self.map_index_component[i]]

        self.model = self.make_pyomo_model()

    def make_pyomo_model(self):
        # Pyomo: retrieve and initialize a matrix of risks
        def get_risks(mod, i, j):
            return self.component_risks[i][j]

        # Pyomo: retrieve and initialize a matrix of costs
        def get_costs(mod, i, j):
            return self.component_costs[i][j]

        model = pyo.AbstractModel()

        # Pyomo: RangeSets useful to initialize parameters
        model.I = pyo.RangeSet(0, self.N - 1)
        model.J = pyo.RangeSet(0, self.M - 1)

        # Pyomo: Initialize cost and risk matrices
        model.c = pyo.Param(model.I, model.J, within=pyo.NonNegativeIntegers, initialize=get_costs)
        model.r = pyo.Param(model.I, model.J, within=pyo.PercentFraction, initialize=get_risks)

        # Pyomo: Declare decision variable
        model.x = pyo.Var(model.I, model.J, domain=pyo.Boolean, initialize=0)

        # Pyomo: Declare the budget parameter and 'alpha';
        model.b = pyo.Param(within=pyo.NonNegativeIntegers)
        model.a = pyo.Param()

        # Pyomo: define constraints
        def one_choice(mod, i):
            return sum([mod.x[i, j] for j in range(self.M)]) == 1

        def valid_choice(mod, i):
            return sum([mod.x[i, j] * self.potential_suppliers[i][j] for j in range(self.M)]) == 1
            #return sum([mod.x[i, j] for j in np.nonzero(self.potential_suppliers[i])[0]]) == 1

        def budget_constraint(mod):
            return pyo.summation(mod.c, mod.x) <= mod.b

        model.OneChoice = pyo.Constraint(model.I, rule=one_choice)
        model.ValidChoice = pyo.Constraint(model.I, rule=valid_choice)
        model.BudgetConstraint = pyo.Constraint(rule=budget_constraint)

        # Pyomo: define objective function as sum of two functions
        def s_group_penalty(mod):
            return compute_s_group_penalty(mod.x,
                                           self.component_importances,
                                           self.supplier_groups,
                                           self.group_risks,
                                           self.N,
                                           self.K)

        def apx_risk(mod):
            return compute_apx_risk(mod.r,
                                    self.supplier_risks,
                                    self.component_importances,
                                    mod.x,
                                    self.N,
                                    self.M)

        def joint_objective(mod):
            return mod.apx_risk + mod.a * mod.s_group_penalty

        model.Objective = pyo.Objective(rule=joint_objective, sense=pyo.minimize)

        # Pyomo: these Expressions are used to access data after solving
        model.apx_risk = pyo.Expression(rule=apx_risk)
        model.s_group_penalty = pyo.Expression(rule=s_group_penalty)

        return model

    def solve(self, params: Dict) -> Tuple[List[Edge], Dict]:
        if "budget" not in params or "alpha" not in params:
            raise ValueError("Missing budget or alpha parameter for optimization.")

        data = {
            None: {
                "b": {None: params["budget"]},
                "a": {None: params["alpha"]}
            }
        }

        instance = self.model.create_instance(data)

        ## Fastest: SCIP, but (current) difficulties automating install
        # solver = pyo.SolverFactory("scipampl")
        # results = solver.solve(instance)

        ## Alternate, but slow: Mindtpy with GLPK & IPOPT
        # solver = pyo.SolverFactory("mindtpy")
        # results = solver.solve(instance, mip_solver='glpk', nlp_solver='ipopt')

        ## Middle-ground, but accessible installation
        solver = pyo.SolverFactory("couenne")
        results = solver.solve(instance)

        metadata = {
            "solver_status": str(results.solver.status),
            "termination_condition": str(results.solver.termination_condition),
            "objective": pyo.value(instance.Objective),
            "risk_importance_heuristic": pyo.value(instance.apx_risk),
            "supplier_group_heuristic": pyo.value(instance.s_group_penalty)
        }

        if metadata["termination_condition"] != "optimal":
            raise OptimizationError("Infeasible budget constraint.")
        if metadata["solver_status"] != "ok":
            raise OptimizationError("Could not solve under given constraints.")

        edge_results = []
        for i in range(self.N):
            for j in range(self.M):
                if round(pyo.value(instance.x[i, j]), 6) == 1:
                    edge_results.append(Edge(src=self.map_index_supplier[j], dst=self.map_index_component[i]))

        return edge_results, metadata


def compute_s_group_penalty(x, component_importances, supplier_groups, group_risks, N, K):
    group_penalty = 0
    for k in range(K):
        score = 0
        for j in supplier_groups[k]:
            for i in range(N):
                score += x[i, j] * component_importances[i]
        group_penalty += (group_risks[k] * score) ** 2
    return group_penalty


def compute_apx_risk(r, supplier_risks, component_importances, x, N, M):
    apx_risk = 0
    for i in range(N):
        for j in range(M):
            score = r[i, j] + supplier_risks[j] - (r[i, j] * supplier_risks[j])
            apx_risk += score * component_importances[i] * x[i, j]
    return apx_risk


def invert_dict(input_dict):
    return {v: k for k, v in input_dict.items()}
