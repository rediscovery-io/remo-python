import json


def print_pretty(res):
    print(json.dumps(res, indent=2, sort_keys=True))
