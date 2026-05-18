"""Command-line interface."""

from __future__ import annotations

import argparse

from syren_tuner import __version__
from syren_tuner.worker import run_worker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="syren-tuner")
    parser.add_argument("--version", action="version", version=f"syren-tuner {__version__}")
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("worker", help="Run the Studio JSONL worker")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "worker":
        return run_worker()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

