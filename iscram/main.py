# import argparse
# import os
# from experiment import budget, alpha
#
# def parse_args():
#     parser = argparse.ArgumentParser("ISCRAM: A Supply Chain Risk Assessment and Mitigation Tool")
#     parser.add_argument('-i', '--input', required=True,
#         help="Path to a directory containing csv files specifying the problem.")
#     parser.add_argument('-t', '--trials', required=True, type=int,
#         help="Number of trials for simulation of post-optimization risk.")
#     parser.add_argument('-s', '--step', required=True, type=int,
#         help="For budget experiments, the amount to increment the budget at each iteration.")
#     parser.add_argument('-o', '--output', required=True,
#         help="Path to a directory where ouput files will be saved.")
#     parser.add_argument('-a', '--alpha', required=True, type=float,
#         help="For budget experiment, the value of the alpha hyperparameter to use.")
#     parser.add_argument('-e', '--experiment', required=False, choices=["budget", "alpha"], default="budget",
#         help="Specify whether to run budget experiment or alpha experiment.")
#     parser.add_argument('-T', '--threads', required=False, default=4, type=int,
#         help="Number of threads to use for simulation of post-optimization risk.")
#     args = parser.parse_args()
#
#     if not os.path.isdir(args.input):
#         print("Input path invalid.")
#         return None
#
#     return args
#
# def main():
#
#     args = parse_args()
#
#     if not args:
#         return
#
#     if args.experiment == "budget":
#         budget.budget_experiment(args)
#     elif args.experiment == "alpha":
#         alpha.alpha_experiment(args, 1700)
#
#
# if __name__ == "__main__":
#     main()
