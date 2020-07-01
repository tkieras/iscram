import numpy as np
import csv

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


sys_prefix = ""

valid_choices = np.genfromtxt(sys_prefix+"valid_choices.csv", delimiter=",")

supplier_groups = []

with open(sys_prefix+"supplier_groups.csv", "r") as infile:
    reader = csv.reader(infile)
    for line in reader:
        group = [int(member) for member in line]
        supplier_groups.append(group)

supplier_count = np.sum(valid_choices, axis=0)
group_counts = [np.sum([supplier_count[j] for j in grp]) for grp in supplier_groups]
plt.bar(range(len(group_counts)), group_counts)
plt.xticks(np.arange(len(supplier_groups)))
plt.xlabel("Supplier Group")
plt.ylabel("Components Offered")
#plt.imshow(valid_choices)
plt.show()

