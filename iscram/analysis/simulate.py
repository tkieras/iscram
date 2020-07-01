import numpy as np
from multiprocessing import Pool

def simulate(choice_problem, system_model, report, threads, trials):
    pool = Pool(threads)

    params = setup_simulation(choice_problem, system_model, report)
    sims = [Simulator(trials // threads, params) for _ in range(threads)]
    sim_workers = [pool.apply_async(sims[i].run) for i in range(threads)]
    sim_result_list = [worker.get() for worker in sim_workers]

    return sim_result_list

def setup_simulation(choice_problem, system_model, report):
    sim_params = {}
    c_risks = np.sum(np.multiply(report["x"], choice_problem.risks), axis=1)
    sim_params["N"] = choice_problem.N
    sim_params["K"] = choice_problem.K

    sim_params["c_p_true"] = np.array([1 - v for v in c_risks])
    sim_params["s_idx_by_c"] = [np.nonzero(report["x"][i])[0][0] for i in range(choice_problem.N)]
    sim_params["s_p_true"] = choice_problem.s_trusts
    sim_params["o_p_true"] = choice_problem.o_trusts
    sim_params["s_groups"] = choice_problem.s_groups
    sim_params["cutset_masks"] = system_model.cutset_masks

    return sim_params


class Simulator:
    def __init__(self, trials, params):
        self.trials = trials
        self.params = params
        self.s_groups = params["s_groups"]
        self.s_idx_by_c = params["s_idx_by_c"]
        self.cutset_masks = params["cutset_masks"]

    def sim_o_to_s(self, o, s, s_groups):
        for k in range(len(s_groups)):
            for j in s_groups[k]:
                s[j] = s[j] & o[k]
        return s

    def sim_s_to_c(self, s, c, s_idx_by_c):
        for i in range(len(c)):
            s_idx = s_idx_by_c[i]
            c[i] = c[i] & s[s_idx]
        return c

    def sim_c_to_sys(self, c, cutset_masks):
        for m in cutset_masks:
            if np.sum(np.logical_and(c, m) != c) == 0:
                return False
        return True

    def filter_chosen_owner_state(self, o, s_groups, s_idx_by_c):
        chosen_o_state = []
        for k in range(len(s_groups)):
            chosen = False
            for j in s_groups[k]:
                if j in s_idx_by_c:
                    chosen = True
            if chosen:
                chosen_o_state.append(o[k])
        return chosen_o_state

    def count_chosen_owner_state(self, o, s_groups, s_idx_by_c):
            chosen_o_state = []
            for k in range(len(s_groups)):
                for j in s_groups[k]:
                    if j in s_idx_by_c:
                        chosen_o_state.append(o[k])
            return chosen_o_state

    def run(self):
        np.random.seed(None)
        system_states_any_cause = []
        system_states_owner_only = []

        # ab = []
        # b = []

        for trial in range(self.trials):
            c_state = np.random.binomial(1, self.params["c_p_true"])
            s_state = np.random.binomial(1, self.params["s_p_true"])
            o_state = np.random.binomial(1, self.params["o_p_true"])

            s_state = self.sim_o_to_s(o_state, s_state, self.params["s_groups"])
            c_state = self.sim_s_to_c(s_state, c_state, self.params["s_idx_by_c"])
            sys_state = self.sim_c_to_sys(c_state, self.params["cutset_masks"])
            system_states_any_cause.append(sys_state)

            # repeat test but with perfect s and c states
            p_s_state = np.ones(len(s_state), dtype=int)
            p_c_state = np.ones(len(c_state), dtype=int)

            p_s_state = self.sim_o_to_s(o_state, p_s_state, self.params["s_groups"])
            p_c_state = self.sim_s_to_c(p_s_state, p_c_state, self.params["s_idx_by_c"])
            p_sys_state = self.sim_c_to_sys(p_c_state, self.params["cutset_masks"])

            system_states_owner_only.append(p_sys_state)

            # chosen_owner_state = self.filter_chosen_owner_state(o_state, self.params["s_groups"], self.params["s_idx_by_c"])
            # ab.append(sys_state and not np.all(chosen_owner_state))
            # b.append(not np.all(chosen_owner_state))



        avg_system_risk = 1 - (np.average(system_states_any_cause))       
        avg_o_failures = 1 - np.average(system_states_owner_only)
        #print(avg_o_failures)
        #total_o_failures = sum(o_failures)

    
        # tmp = 1-(np.average(ab) / np.average(b))
       
        # if avg_o_failures == 0 or avg_system_risk == 0:
        #     sys_o_ratio = 0
        # else:
        #     sys_o_ratio =  avg_o_failures / avg_system_risk

        return avg_system_risk, avg_o_failures 


if __name__ == "__main__":
    params = {
        "s_groups" : [[3,4], [1, 2], [0], []], "s_idx_by_c": [0,1,2,3,4], "cutset_masks" : [[0,1,1,1,1]],
        "c_p_true" : [1,1,1,1,1],
        "s_p_true" : [1,1,1,1,1],
        "o_p_true" : [1, 1, .5, 1, 1, 1,]
    }
    sim = Simulator(10, params)
    #print(sim.filter_chosen_owner_state([0,1,0,1,1], [[3,4], [1,2], [0]], [0,3,2]))
    print(sim.run())
