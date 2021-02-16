from pyomo.environ import *
import numpy as np


def solve_instance(instance):
    print("solving for budget={}, \u03B1={}".format(value(instance.b), value(instance.a)))

    solver = SolverFactory("scipampl")
    results = solver.solve(instance)

    print("solver status: {}".format(results.solver.status))
    print("termination condition: {}".format(results.solver.termination_condition))


def compute_s_group_penalty(x, st_imps, s_groups, o_trusts, N, K):
    weighted_group_involvements = []

    for k in range(K):
        weighted_group_involvement = 0
        for j in s_groups[k]:
            for i in range(N):
                weighted_group_involvement += x[i,j] * st_imps[i]
        weighted_group_involvements.append(weighted_group_involvement)
         

    group_penalties = []

    for k, base in enumerate(weighted_group_involvements):
        group_penalty = (1-o_trusts[k]) * base**2
        group_penalties.append(group_penalty)
    
    return np.sum(group_penalties)


def compute_apx_risk(r, s_trusts, s_to_o_map, o_trusts, st_imps, x, N, M):
    apx_risks = []
    for i in range(N):
        for j in range(M):
            # base: r_i or not s_trusts[j] => sum minus product
            base = (r[i, j] + 1 - s_trusts[j] - (r[i, j] * (1 - s_trusts[j])))
            adjusted = base * st_imps[i]
            chosen = adjusted * x[i,j]
            apx_risks.append(chosen)

    return np.sum(apx_risks)


class ChoiceProblem:
    def __init__(self, loader, system_model):

        # static aspects of the system (cutsets, structural importances)
        self.system_model = system_model

        # cost and risk of each supplier, component combination
        self.costs = loader.load_costs()
        self.risks = loader.load_risks()

        # trust values for each supplier entity
        self.s_trusts = loader.load_s_trusts()
        self.o_trusts = loader.load_o_trusts()

        # list of lists: each list is a group of suppliers referenced by index j
        self.s_groups = loader.load_s_groups()

        # matrix showing which supplier, component combinations are valid
        self.choices = loader.load_choices()

        # number of components
        self.N = self.choices.shape[0]

        # number of suppliers (total)
        self.M = self.choices.shape[1]

        # number of groups
        self.K = len(self.s_groups) 

        # convenience values to avoid trying infeasible or excessive budgets
        self.budget_min = np.sum([np.min(self.costs[i, np.nonzero(self.costs[i])])
                               for i in range(self.N)])
        self.budget_max = np.sum([np.max(self.costs[i])
                               for i in range(self.N)])

        self.loader = loader

        self.model = self.init_abstract_choice_model()


    def init_abstract_choice_model(self):

        birnbaum_st_imps = self.system_model.birnbaum_st_imps

        # create map from a supplier to its owner
        s_to_o_map = []

        for j in range(self.M):
            for k in range(self.K):
                if j in self.s_groups[k]:
                    s_to_o_map.append(k)


        # Pyomo: retrieve and initialize a matrix of risks
        def get_risks(mod, i, j):
            return self.risks[i, j]

        # Pyomo: retrieve and initialize a matrix of costs
        def get_costs(mod, i, j):
            return self.costs[i, j]

        model = AbstractModel()

        # Pyomo: RangeSets useful to initialize parameters
        model.I = RangeSet(0, self.N - 1)
        model.J = RangeSet(0, self.M - 1)

        # Pyomo: Initialize cost and risk matrices
        model.c = Param(model.I, model.J, within=NonNegativeIntegers, initialize=get_costs)
        model.r = Param(model.I, model.J, within=PercentFraction, initialize=get_risks)

        # Pyomo: Declare decision variable
        model.x = Var(model.I, model.J, domain=Boolean, initialize=0)

        # Pyomo: Declare the budget parameter and 'alpha'; 
        ## No value is given here because this is an 'AbstractModel'
        ## For a given set of parameters above, budget & alpha may be varied widely

        model.b = Param(within=NonNegativeIntegers)
        model.a = Param()


        # Pyomo: define constraints
        def one_choice(mod, i):
            return sum([mod.x[i, j] for j in range(self.M)]) == 1

        def valid_choice(mod, i):
            return sum([mod.x[i, j] for j in np.nonzero(self.choices[i])[0]]) == 1

        def budget_constraint(mod):
            return summation(mod.c, mod.x) <= mod.b

        model.OneChoice = Constraint(model.I, rule=one_choice)
        model.ValidChoice = Constraint(model.I, rule=valid_choice)
        model.BudgetConstraint = Constraint(rule=budget_constraint)

        # Pyomo: define objective function as sum of two functions
        def s_group_penalty(mod):
            return compute_s_group_penalty(mod.x, birnbaum_st_imps, self.s_groups,
                                              self.o_trusts, self.N, self.K)

        def apx_risk(mod):
            return compute_apx_risk(mod.r, self.s_trusts, s_to_o_map, self.o_trusts,
                                    birnbaum_st_imps,
                                    mod.x, self.N, self.M)

        def joint_objective(mod):
            return mod.apx_risk + mod.a * mod.s_group_penalty

        model.Objective = Objective(rule=joint_objective, sense=minimize)

        # declare Expressions to access partial results after solution
        model.apx_risk = Expression(rule=apx_risk)
        model.s_group_penalty = Expression(rule=s_group_penalty)


        return model

    def create_instance(self, budget, alpha):
        # given budget, alpha, create a concrete instance of the choice problem
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

        # extract, clean-up solution
        ## solver may only approximate the integer constraint

        x = np.zeros((self.N, self.M))

        for i in range(self.N):
            for j in range(self.M):
                if round(value(instance.x[i, j]), 6) == 1:
                    x[i, j] = 1

        # Check that every component has exactly 1 supplier. 
        for i in range(self.N):
            choice = np.nonzero(x[i])[0]
            if len(choice) != 1:
                raise ValueError("Solver error: constraint not satisfied")

        report["x"] = x

        # Assemble various data useful for diagnostics & reporting
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
