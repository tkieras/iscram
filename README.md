# ISCRAM: Supply Chain Risk Analysis and Mitigation Tool

The ISCRAM tool performs risk modeling for supply chain security risks, given a specified system, risk and trust values for system entities. The tool includes also a decision support function that recommends optimal risk mitigating choices among available suppliers, subject to budget constraints. For documentation, please refer to the papers describing the modeling approach implemented here:
- T. Kieras, M.J. Farooq, Q. Zhu. RIoTS: Risk Analysis of IoT Supply Chain Threats. IEEE 6th World Forum on the Internet of Things, 2020. <https://arxiv.org/abs/1911.12862>
- T. Kieras, M.J. Farooq, Q. Zhu. Modeling and Assessment of IoT Supply Chain Security Risks: The Role of Structural and Parametric Uncertainties. IEEE Security & Privacy CReSCT Workshop, 2020. <https://arxiv.org/abs/2003.12363>

The included Python code is used to implement the above models and run case studies. A broader range of usage will be supported by future versions.

## Installation

The project requires Python v.3+.

Python dependencies for ISCRAM are as follows:
- networkx
- numpy
- pyomo
- matplotlib

In addition, the optimization uses [SCIP](https://scipopt.org/). In order to run ISCRAM, the binary of ```scipampl``` must be on your system PATH. Instructions for installing scip & scipampl vary by platform.

```
git clone https://github.com/tkieras/iscram
cd iscram
export PYTHONPATH=PYTHONPATH:$(pwd)
cd iscram
```

## Usage

A problem is specified currently by a folder of csv files that contain the various parameters needed to specify a problem. A set of seven cases are included in the ```data``` folder.

To run an experiment that optimizes for a range of budgets, use the budget experiment flag:

```
python main.py -i ../data/case7 -t 10000 -s 10 -o ../output -a .1 -e budget -T 4
```

To run an experiment that fixes the budget and uses a preselected range of alpha hyperparameters, use the alpha experiment flag:

```
python main.py -i ../data/case7 -t 10000 -s 10 -o ../output -a .1 -e alpha -T 4
```

For additional usage notes, you may also run:
```
python main.py --help
```

Results are currently in the form of charts that detail the simulated risk resulting from optimization at each budget or alpha step. Detailed information from each step is displayed via STDOUT.
