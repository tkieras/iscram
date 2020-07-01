import numpy as np
from tabulate import tabulate
import csv

# Cost parameters

COST_SIGMA_MIN = 5
COST_SIGMA_MAX = 1
COST_SIGMA = .9

# Risk parameters
# If this flag is false, RISK_FIXED_VAL is used instead of random
RISK_RAND = True
RISK_FIXED_VAL = 0.00
#RISK_MAX = .07
#RISK_MIN = .01
RISK_SIGMA = .01
RISK_MU = .02
RISK_COST_CORRELATION = 1.0

# Trust parameters
# If these flags are false, *_TRUST_FIXED_VAL is used instead of random
S_TRUST_RAND = True
O_TRUST_RAND = True
S_TRUST_FIXED_VAL = 1.0
O_TRUST_FIXED_VAL = .98
S_TRUST_MU = .98
S_O_TRUST_RATIO = 1.0
O_TRUST_MU = S_TRUST_MU * S_O_TRUST_RATIO
S_TRUST_SIGMA = .01
O_TRUST_SIGMA = .01

# Z malicious owners are penalized to introduce variation
NUM_MALICIOUS_OWNERS = 2
MALICIOUS_OWNER_PENALTY = .80

# Significant figures for rounding functions
SIG_FIG_RISK = 6
SIG_FIG_TRUST = 6

# General assumption: numerical index of a component corresponds
# to its location in the alphabetically sorted list of components
COMPONENTS = sorted(["accel_act",
                     "act_engine",
                     "brake_act",
                     "camera",
                     "geo_fusion",
                     "gps",
                     "imu",
                     "lidar",
                     "maps",
                     "radar",
                     "sensor_fusion",
                     "steer_act",
                     "ultrasound",
                     "v2i",
                     "v2v"])
COST_BASE = [50, 50, 50, 100, 250,
             30, 30, 350, 75, 25,
             275, 25, 75, 100, 150]

N = len(COMPONENTS)
S_PER_C = 3
M = N * S_PER_C
K = N // 3


def init_choices():
    choices = np.zeros((N, M))

    suppliers_shuffled = (np.arange(M))
    np.random.shuffle(suppliers_shuffled)

    choice_list = []
    idx = 0
    for i in range(N):
        choice_list.append(suppliers_shuffled[idx:idx + S_PER_C])
        idx += S_PER_C

    for i in range(N):
        for j in choice_list[i]:
            choices[i, j] = 1

    for i in range(N):
        assert (np.sum(choices[i, :]) == S_PER_C)

    return choices


def init_costs():
    costs = np.zeros((N, M))

    for i in range(N):
        mu = COST_BASE[i]
        sigma_percent = np.random.random()
        sigma_percent = sigma_percent * (COST_SIGMA_MAX - COST_SIGMA_MIN)
        sigma_percent += COST_SIGMA_MIN
        sigma = COST_BASE[i] * COST_SIGMA
       # sigma = COST_SIGMA
        component_costs = np.random.normal(mu, sigma, M)
        for j in range(M):
            costs[i, j] = abs(int(component_costs[j]))
            if costs[i, j] == 0:
                costs[i, j] = mu
    return costs


def init_risks(costs):
    risks = np.zeros((N, M))

    for i in range(N):
        mu = RISK_MU
        for j in range(M):
            #risks[i, j] = (1 - costs[i, j] / COST_BASE[i])
            cost_ratio = costs[i, j] / COST_BASE[i]
            #diff = risks[i, j] * mu
            #risks[i, j] = abs(mu + diff)
            risks[i, j] = mu * cost_ratio
            if np.random.random() > RISK_COST_CORRELATION:
                risks[i, j] = np.random.normal(mu, RISK_SIGMA)
            risks[i, j] = round(risks[i, j], SIG_FIG_RISK)
           # if risks[i, j] <= 0:
            #    risks[i, j] = mu
            assert(risks[i, j] > 0)
            if not RISK_RAND:
                risks[i, j] = RISK_FIXED_VAL
    return risks


def eliminate_invalid_options(valid_choices, risks, costs):
    for i in range(N):
        for j in range(M):
            if valid_choices[i, j] == 0:
                risks[i, j] = 0.0
                costs[i, j] = 0


def init_trusts():
    if S_TRUST_RAND:
        s_trusts = np.random.normal(S_TRUST_MU, S_TRUST_SIGMA, M)
    else:
        s_trusts = [S_TRUST_FIXED_VAL] * M

    if O_TRUST_RAND:
        o_trusts_fill = np.random.normal(O_TRUST_MU, O_TRUST_SIGMA, K)
        for k in range(K):
            if o_trusts_fill[k] >= 1.0:
                o_trusts_fill[k] = O_TRUST_MU
            o_trusts_fill[k] = round(o_trusts_fill[k], SIG_FIG_TRUST)
    else:
        o_trusts_fill = [O_TRUST_FIXED_VAL] * K

    for j in range(M):
        if s_trusts[j] > 1.0:
            s_trusts[j] = S_TRUST_MU
        s_trusts[j] = round(s_trusts[j], SIG_FIG_TRUST)

    # Ensure "shadow owners" (self-owners) always have trust=1.0
    o_trusts = [1.0] * M
    for k in range(K):
        o_trusts[k] = o_trusts_fill[k]

    for z in range(NUM_MALICIOUS_OWNERS):
        o_trusts[z] *= MALICIOUS_OWNER_PENALTY

    return s_trusts, o_trusts


def init_s_groups():
    s_groups = []
    shuffled_suppliers = np.arange(M)
    np.random.shuffle(shuffled_suppliers)

    idx = 0
    group_size = ((M - 1) // K) - 2

    for k in range(K):
        s_groups.append(
            shuffled_suppliers[idx:idx + group_size])
        idx += group_size

    for j in range(idx, M):
        s_groups.append([shuffled_suppliers[j]])

    return s_groups


def init_names():
    s_names = []
    for i in range(M):
        s_names.append("S{}".format(i))

    o_names = ["None"] * M
    for k in range(K):
        o_names[k] = "O{}".format(k)

    return s_names, o_names


def print_data(choices, costs, risks,
               s_trusts, o_trusts, groups,
               s_names, o_names):
    print("Valid Choices:")
    print(tabulate(choices))
    print("Costs:")
    print(tabulate(costs))

    max_cost = np.sum([np.max(costs[i, :]) for i in range(N)])

    min_cost = np.sum([np.min(costs[i, np.nonzero(costs[i])])
                       for i in range(N)])

    print("Cost Max: {}".format(max_cost))
    print("Cost Min: {}".format(min_cost))
    print("Risks:")
    print(tabulate(risks))

    print("Supplier Trusts:")
    print(tabulate((s_trusts,)))
    print("Owner Trusts:")
    print(tabulate((o_trusts,)))

    print("Supplier Groups:")
    print(tabulate(groups))

    print("Supplier and Owner Names:")
    print(s_names)
    print(o_names)


def write_data(choices, costs, risks,
               s_trusts, o_trusts, s_groups,
               s_names, o_names):
    with open("choices.csv", "w") as of:
        writer = csv.writer(of)
        writer.writerows(choices)

    with open("costs.csv", "w") as of:
        writer = csv.writer(of)
        writer.writerows(costs)

    with open("risks.csv", "w") as of:
        writer = csv.writer(of)
        writer.writerows(risks)

    with open("s_trusts.csv", "w") as of:
        writer = csv.writer(of)
        for trust in s_trusts:
            writer.writerow([trust])

    with open("o_trusts.csv", "w") as of:
        writer = csv.writer(of)
        for trust in o_trusts:
            writer.writerow([trust])

    with open("s_groups.csv", "w") as of:
        writer = csv.writer(of)
        for grp in s_groups:
            writer.writerows([grp])

    with open("s_names.csv", "w") as of:
        writer = csv.writer(of)
        for name in s_names:
            writer.writerow([name])

    with open("o_names.csv", "w") as of:
        writer = csv.writer(of)
        for name in o_names:
            writer.writerow([name])

    with open("c_names.csv", "w") as of:
        writer = csv.writer(of)
        for component in COMPONENTS:
            writer.writerow([component])


def main():
    np.random.seed(None)

    choices = init_choices()
    costs = init_costs()
    risks = init_risks(costs)
    eliminate_invalid_options(choices, risks, costs)

    s_trusts, o_trusts = init_trusts()

    s_groups = init_s_groups()
    s_names, o_names = init_names()

    print_data(choices, costs, risks,
               s_trusts, o_trusts, s_groups,
               s_names, o_names)

    write_data(choices, costs, risks,
               s_trusts, o_trusts, s_groups,
               s_names, o_names)


if __name__ == "__main__":
    main()
