import csv
import pprint
def load_named_cutsets():
    named_cutsets = []
    with open("named_cutsets.csv", "r") as infile:
        reader = csv.reader(infile)
        for line in reader:
            named_cutsets.append(line)
    return named_cutsets


def binary_to_fill_val(val, i, components, suppliers):
    if val % 2:
            return suppliers[i]
    else:
            return components[i]

def binary_combine(components, suppliers):
    if len(components) != len(suppliers):
        return None
    results = []
    for i in range(2**len(components)):
        comb = []
        idx = 0
        while idx < len(components):
            comb.append(binary_to_fill_val(i, idx, \
                components, suppliers))
            idx += 1
            i = i >> 1
        results.append(comb)
    return results


def combine_with_suppliers(components):
    combinations = set()
    suppliers = ["s_{}".format(c) for c in components]

    comb_res = binary_combine(components,suppliers)
    for r in comb_res:
        combinations.add(tuple(r))
    return combinations

def match(cut, subset, sub):
    cutset = set(cut)
    subset = set(subset)
    newcut = set()
    if subset.issubset(cutset):
        newcut = cutset - subset
        newcut.add(sub)
        return tuple(newcut)
    elif cutset.issubset(subset):
        newcut.add(sub)
        return tuple(newcut)
    else:
        return None


allcuts = load_named_cutsets()

new_cutsets = set()
for i in range(len(allcuts)):
    new_cutsets = new_cutsets.union(combine_with_suppliers(allcuts[i]))

#pprint.pprint(new_cutsets)

owner_dict = {
    "o1" : ["imu", "maps"],
    "o2" : ["accel_act", "brake_act"],
    "o3" : ["v2v", "radar"]
}
def add_owners(owner_dict, new_cutsets):
    new_new_new_cutsets = set(new_cutsets)

    for oname, ochildren in owner_dict.items():
        subsets = combine_with_suppliers(ochildren)
        new_new_cutsets = set()
        for newcut in new_new_new_cutsets:
            found = False
            for subset in subsets:
                res = match(newcut, subset, oname)
                if res is not None:
                    new_new_cutsets.add(res)
                    if not found:
                        new_new_cutsets.add(tuple(newcut))
                    found = True
            if not found:
                new_new_cutsets.add(tuple(newcut))
        new_new_new_cutsets = new_new_new_cutsets.union(new_new_cutsets)

    return new_new_new_cutsets

final_cutsets = add_owners(owner_dict, new_cutsets)
pprint.pprint(final_cutsets)
print(len(final_cutsets))

with open("exploded_cutsets.csv", "w") as of:
    writer = csv.writer(of)
    for cutset in final_cutsets:
        writer.writerow(cutset)

