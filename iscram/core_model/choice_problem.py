from pyomo.environ import *
import numpy as np
import math


def solve_instance(instance):
    print("solving for budget={}, \u03B1={}".format(value(instance.b), value(instance.a)))

    solver = SolverFactory("scipampl")
    results = solver.solve(instance)
    # solver = SolverFactory("mindtpy")
    # results = solver.solve(instance, mip_solver="glpk", nlp_solver="ipopt")

    # solver = SolverFactory("glpk")
    # results = solver.solve(instance)
    print("solver status: {}".format(results.solver.status))
    print("termination condition: {}".format(results.solver.termination_condition))


def compute_s_group_penalty(x, st_imps, s_groups, o_trusts, N, K):
    s_g_counts = [sum([(x[i, j]) * st_imps[i] * 10 for i in range(N)
                       for j in s_groups[k]])
                  for k in range(K)]
    weight = lambda v, k: v**2 * (1- o_trusts[k]) * 10
    
    penalty = sum([weight(v, k) for k, v in enumerate(s_g_counts)])
    return penalty


def compute_apx_risk(r, s_trusts, s_to_o_map, o_trusts, st_imps, x, N, M):
    return sum([(r[i, j] + 1 - s_trusts[j]
                 - (r[i, j] * (1 - s_trusts[j])))
                * st_imps[i]
                * x[i, j]
                for j in range(M)
                for i in range(N)])


class ChoiceProblem:
    def __init__(self, loader, system_model):
        self.system_model = system_model
        self.costs = loader.load_costs()
        self.risks = loader.load_risks()
        self.s_trusts = loader.load_s_trusts()
        self.o_trusts = loader.load_o_trusts()
        self.s_groups = loader.load_s_groups()
        self.choices = loader.load_choices()
        self.N = self.choices.shape[0]
        self.M = self.choices.shape[1]
        self.K = len(self.s_groups)
        self.model = self.init_abstract_choice_model()

        self.budget_min = sum([np.min(self.costs[i, np.nonzero(self.costs[i])])
                               for i in range(self.N)])
        self.budget_max = sum([np.max(self.costs[i])
                               for i in range(self.N)])

        self.loader = loader

    def init_abstract_choice_model(self):
        birnbaum_st_imps = self.system_model.birnbaum_st_imps
        s_to_o_map = []
        for j in range(self.M):
            for k in range(self.K):
                if j in self.s_groups[k]:
                    s_to_o_map.append(k)

        def get_risks(mod, i, j):
            return self.risks[i, j]

        def get_costs(mod, i, j):
            return self.costs[i, j]

        model = AbstractModel()
        model.I = RangeSet(0, self.N - 1)
        model.J = RangeSet(0, self.M - 1)

        model.c = Param(model.I, model.J, within=NonNegativeIntegers, initialize=get_costs)
        model.r = Param(model.I, model.J, within=PercentFraction, initialize=get_risks)
        model.x = Var(model.I, model.J, domain=Boolean, initialize=0)

        model.b = Param(within=NonNegativeIntegers)
        model.a = Param()

        def one_choice(mod, i):
            return sum([mod.x[i, j] for j in range(self.M)]) == 1

        def valid_choice(mod, i):
            return sum([mod.x[i, j] for j in np.nonzero(self.choices[i])[0]]) == 1

        def budget_constraint(mod):
            return summation(mod.c, mod.x) <= mod.b

        def s_group_penalty(mod):
            penalty = compute_s_group_penalty(mod.x, birnbaum_st_imps, self.s_groups,
                                              self.o_trusts, self.N, self.K)
            return penalty * mod.a

        def apx_risk(mod):
            return compute_apx_risk(mod.r, self.s_trusts, s_to_o_map, self.o_trusts,
                                    birnbaum_st_imps,
                                    mod.x, self.N, self.M)

        def joint_objective(mod):
            return mod.apx_risk + mod.s_group_penalty

        model.OneChoice = Constraint(model.I, rule=one_choice)
        model.ValidChoice = Constraint(model.I, rule=valid_choice)
        model.BudgetConstraint = Constraint(rule=budget_constraint)
        model.apx_risk = Expression(rule=apx_risk)
        model.s_group_penalty = Expression(rule=s_group_penalty)
        model.Objective = Objective(rule=joint_objective, sense=minimize)

        return model

    def create_instance(self, budget, alpha):
        data = {
            None: {
                "b": {None: budget},
                "a": {None: alpha}
            }
        }
        instance = self.model.create_instance(data)
        return instance

    def process_solver_results(self, instance):
        report = {
            "obj": value(instance.Objective),
            "apx_risk": value(instance.apx_risk),
            "s_group_penalty": value(instance.s_group_penalty)
        }

        x = np.zeros((self.N, self.M))

        for i in range(self.N):
            for j in range(self.M):
                if round(value(instance.x[i, j]), 6) == 1:
                    x[i, j] = 1

        for i in range(self.N):
            choice = np.nonzero(x[i])[0]
            if len(choice) != 1:
                raise ValueError("Solver error: constraint not satisfied")

        report["x"] = x

        all_s_g_counts = [sum([(x[i, j]) for i in range(self.N)
                  for j in self.s_groups[k]])
             for k in range(self.K)]

        all_o_names = self.loader.load_o_names()
        all_s_names = self.loader.load_s_names()
        all_s_counts = [sum([x[i, j] for i in range(self.N)])
             for j in range(self.M)]

        report["s_g_counts"] = all_s_g_counts
        report["o_names"] = all_o_names
        report["chosen_o_trusts"] = self.o_trusts

        report["s_names"] = []
        report["s_counts"] = []
        for j in range(self.M):
            if all_s_counts[j] > 0:
                report["s_names"].append(all_s_names[j])
                report["s_counts"].append(all_s_counts[j])

        return report
