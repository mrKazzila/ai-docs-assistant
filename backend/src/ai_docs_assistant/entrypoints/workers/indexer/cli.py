import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize documentation vector index",
    )

    parser.add_argument(
        "--no-recreate",
        action="store_true",
        help="Do not recreate Qdrant collection before indexing",
    )

    return parser.parse_args()
