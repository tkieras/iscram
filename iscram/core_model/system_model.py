import numpy as np


def phi(cutset_masks, state_vector):
    cutvals = []
    for m in cutset_masks:
        m = np.array(m)
        relevant_components = np.where(m == 0)[0]
        cutval = np.prod([state_vector[c] for c in relevant_components])
        cutvals.append(1-cutval)

    return 1 - np.prod(cutvals)

def compute_birnbaum_st_imps(cutset_masks, N):
    birnbaum_st_imps = np.zeros(N)
    state_vector = [0.5] * N

    for i in range(N):
        state_vector[i] = 1.0
        phi_1 = phi(cutset_masks, state_vector)
        state_vector[i] = 0.0
        phi_0 = phi(cutset_masks, state_vector)
        birnbaum_st_imps[i] = phi_1 - phi_0
        state_vector[i] = 0.5

    return birnbaum_st_imps



class SystemModel:
    def __init__(self, loader):
        self.c_names = loader.load_c_names()
        self.N = len(self.c_names)
        self.named_cutsets = loader.load_named_cutsets()
        self.cutset_masks = self.create_cutset_masks()
        self.birnbaum_st_imps = compute_birnbaum_st_imps(self.cutset_masks, self.N)

    def create_cutset_masks(self):
        indexed_cutsets = [list(map(lambda c: self.c_names.index(c), cutset)) for cutset in self.named_cutsets]
        cutset_masks = []

        for cut in indexed_cutsets:
            mask = [1] * self.N
            for v in cut:
                mask[v] = 0
            cutset_masks.append(mask)

        if len(cutset_masks) == 0:
            cutset_masks.append([1] * self.N)

        return cutset_masks

    