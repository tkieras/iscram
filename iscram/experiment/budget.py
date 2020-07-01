import numpy as np
from iscram.data_io import csv_loader 
from iscram.core_model import system_model as model
from iscram.core_model import choice_problem as problem
from iscram.analysis import simulate as sim
from iscram.report import report as rpt



def budget_experiment(args):
    problem_data = csv_loader.DataLoader(args.input)
    system_model = model.SystemModel(problem_data)
    choice_problem = problem.ChoiceProblem(problem_data, system_model)

    alpha = args.alpha
    trials = args.trials
    budgets = list(range(choice_problem.budget_min, choice_problem.budget_max, args.step))
    
    objectives = []
    gen_fails = []
    o_fails = []
    reports = []

    for budget in budgets:
        
        instance = choice_problem.create_instance(budget, alpha)
        problem.solve_instance(instance)
        report = choice_problem.process_solver_results(instance)

        sim_result_list = sim.simulate(choice_problem, system_model, report, args.threads, args.trials)

        ## BELOW: VARIOUS REPORT ##

        gen_fail_list = [sim_result_list[i][0] for i in range(len(sim_result_list))]
        o_fail_list = [sim_result_list[i][1] for i in range(len(sim_result_list))]

        gen_fail = np.average(gen_fail_list)
        o_fail = np.average(o_fail_list)

        report["budget"] = budget
        report["alpha"] = alpha
        report["trials"] = trials
        report["gen_fail"] = gen_fail
        report["o_fail"] = o_fail
        reports.append(report)
        objectives.append(report["obj"])
        gen_fails.append(gen_fail)
        o_fails.append(o_fail)
        rpt.print_minimal_report(report)


    if len(budgets) == 1:
        rpt.plot_single_instance_result(report)
    else:
        rpt.plot_budget_exp_results(budgets, alpha, objectives, gen_fails, o_fails, args.output)


    print("Experiment completed")
