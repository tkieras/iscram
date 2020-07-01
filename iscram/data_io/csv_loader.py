import csv
import numpy as np


class DataLoader:
    def __init__(self, path):
        self.path = path + "/"

    def load_c_names(self):
        c_names = []
        with open(self.path + "c_names.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                c_names.append(line[0])
        return sorted(c_names)

    def load_named_cutsets(self):
        named_cutsets = []
        with open(self.path + "named_cutsets.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                named_cutsets.append(line)
        return named_cutsets

    def load_s_names(self):
        s_names = []
        with open(self.path + "s_names.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                s_names.append(line[0])
        return s_names

    def load_costs(self):
        return np.genfromtxt(self.path + "costs.csv", delimiter=",", dtype=np.int16)

    def load_risks(self):
        return np.genfromtxt(self.path + "risks.csv", delimiter=",")

    def load_s_trusts(self):
        return np.genfromtxt(self.path + "s_trusts.csv", delimiter=",")

    def load_choices(self):
        return np.genfromtxt(self.path + "choices.csv", delimiter=",")

    def load_s_groups(self):
        s_groups = []
        with open(self.path + "s_groups.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                group = [int(member) for member in line]
                s_groups.append(group)
        return s_groups

    def load_o_trusts(self):
        o_trusts = []
        with open(self.path + "o_trusts.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                o_trusts.append(float(line[0]))
        return o_trusts

    def load_o_names(self):
        o_names = []
        with open(self.path + "o_names.csv", "r") as infile:
            reader = csv.reader(infile)
            for line in reader:
                o_names.append(line[0])
        return o_names

