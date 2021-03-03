import argparse
from pprint import pprint

from iscram.adapters.repository import FakeRepository
from iscram.adapters.json import load_system_graph_json_str, dump_system_graph_json

from iscram.service_layer.services import (
    get_risk, get_birnbaum_importances, get_birnbaum_structural_importances
)


def parse_args():
    parser = argparse.ArgumentParser("ISCRAM: A Supply Chain Risk Assessment and Mitigation Tool")
    parser.add_argument('-i', '--input', required=True,
                        help="Path to json file specifying a system graph.")

    return parser.parse_args()


def main():
    args = parse_args()

    repo = FakeRepository()

    with open(args.input) as infile:
        sg = load_system_graph_json_str(infile.read())

    print("*** System Graph ***")
    pprint(dump_system_graph_json(sg))

    print("\n\n*** Birnbaum Structural Importances ***")
    pprint(get_birnbaum_structural_importances(sg, repo))

    print("\n\n*** Birnbaum Importances ***")
    pprint(get_birnbaum_importances(sg, repo))

    print("\n\n*** Risk ***")
    pprint(get_risk(sg, repo))


if __name__ == "__main__":
    main()
