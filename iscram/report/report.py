import matplotlib.pyplot as plt
import numpy as np


def print_x(x):
    for i in range(len(x)):
        for j in range(len(x[0])):
            print("{}".format(int(x[i,j])), end="")
        print("")


def print_minimal_report(report, sim_params=None):
    print("+"*20 + "Report" + "+"*20)
    print("\u03B1={}, budget={}".format(report["alpha"], report["budget"]))
    print("Objective: {}".format(report["obj"]))
    print("Apx Risk: {}".format(report["apx_risk"]))
    print("Supplier Group Penalty: {}".format(report["s_group_penalty"]))
    print("Supplier Group Counts: {}".format(report["s_g_counts"]))
    print("All Owner Trusts: {}".format(report["chosen_o_trusts"]))
   # print("Chosen Supplier Trusts: {}".format([sim_params["s_p_true"][v] \
    #    for v in sim_params["s_idx_by_c"]]))
   # print("Chosen Component Reliabilities: {}".format(sim_params["c_p_true"]))
    print("Simulation General Failure Risk Results (n={}): \33[92m{}\x1b[0m".format(report["trials"], report["gen_fail"]))
    print("Simulation Owner Failure Risk Results (n={}): \33[92m{}\x1b[0m".format(report["trials"], report["o_fail"]))

    print("+"*46)


def plot_budget_exp_results(budgets, a, objectives, gen_fail, o_fail, output_file):
    
    plt.plot(budgets, objectives,
             "gx",
             linestyle="-",
             label="objective")
    plt.plot(budgets, gen_fail,
             "r+",
             linestyle="-",
             label="general risk")
    plt.plot(budgets, o_fail,
            "bo",
            linestyle="--",
            fillstyle="none",
            label="group risk")

    plt.title("risk after supplier choice, \u03B1={}".format(a))
    plt.xlabel("budget")
    plt.ylabel("risk")
    #plt.ylim([0, .5])
    #plt.legend(loc="upper center", ncol=3, fontsize=10, columnspacing=2, bbox_to_anchor=(0.5, 1.15))
    plt.legend(loc="upper right")
    plt.grid(True)

    plt.savefig("{}_a{}_budget.svg".format(output_file, str(a)))
    #plt.show()


def plot_alpha_exp_results(alphas, objectives, gen_fail, o_fail, output_file):
    plt.plot(alphas, objectives, "gx", linestyle="-", label="objective")
    plt.plot(alphas, gen_fail, "r+", linestyle="-", label="general risk")
    plt.plot(alphas, o_fail, "bo", linestyle="-", label="group risk")


    plt.xlabel("alpha")
    plt.ylabel("risk")
    #plt.ylim([0, .5])
    plt.xscale("log")
    plt.legend(loc="upper center", ncol=3, fontsize=10, columnspacing=2, bbox_to_anchor=(0.5, 1.15))
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("{}_alpha.svg".format(output_file))
    #plt.show()


def plot_single_instance_result(report):


    #
    # component_risks = []
    # trusts = []
    # for i in range(len(self.c_names)):
    #     component_risks.append(np.multiply(self.x, self.risks)[i].sum())
    #     trusts.append(self.s_trusts[rp["chosen_suppliers"][i]])

    fig, ax = plt.subplots(2, 2)
    # plt.title("Results for budget={}, \u03B1={}".format(report["budget"], report["alpha"]))

    x_axis = np.arange(len(report["s_g_counts"]))
    width = .35
    rects = ax[0, 0].bar(x_axis, report["s_g_counts"], width, label="Count")
    ax[0, 0].set_xticks(x_axis)
    ax[0, 0].set_xticklabels(report["o_names"], fontsize=8)
    for tick in ax[0, 0].get_xticklabels():
        tick.set_rotation(45)

    ax[0, 0].set_ylim([0, 5])
    ax[0, 0].set_xlabel("Supplier Groups")
    ax[0, 0].set_ylabel("Components Sourced")

    x_axis_2 = np.arange(len(report["s_names"]))
    rects1 = ax[0, 1].bar(x_axis_2, report["s_counts"], width)

    ax[0, 1].set_xticks(x_axis_2)
    ax[0, 1].set_xticklabels(report["s_names"], fontsize=8)
    for tick in ax[0, 1].get_xticklabels():
        tick.set_rotation(45)
    ax[0, 1].set_xlabel("Suppliers (not including groups)")

    ax[1, 0].bar(["apx_risk", "s_group_penalty", "objective", "sim_risk(n={})".format(report["trials"])],
                 [report["apx_risk"], report["s_group_penalty"], report["obj"], report["gen_fail"]])
    ax[1, 0].set_ylabel("Risk of Security Incident")
    ax[1, 0].set_ylim([0, .5])

    for tick in ax[1, 0].get_xticklabels():
        tick.set_rotation(90)

    #sc_nodes = [s_names[j] for j in rp["chosen_suppliers"]]

    # for k in range(len(self.o_names)):
    #     if rp["supplier_group_count"][k] > 0:
    #         sc_nodes.append(self.o_names[k])
    #
    # s_graph = self.sc_graph.subgraph(sc_nodes)
    #
    # # pos = nx.circular_layout(s_graph)
    # pos = nx.nx_agraph.graphviz_layout(s_graph, prog='dot')
    # # pos = nx.circular_layout(s_graph)
    # # pos = nx.spring_layout(s_graph, k=((len(sc_nodes))**2), pos=pos, iterations=20)
    # nx.draw(s_graph, pos, ax[1, 1], node_size=200, alpha=.5, node_color="cyan", with_labels=True)
    # ax[1, 1].set_xlabel("Supplier Group Relationships")


    fig.tight_layout()
    fig.subplots_adjust(top=0.85)
    plt.savefig("tmp.svg")

    plt.show()

