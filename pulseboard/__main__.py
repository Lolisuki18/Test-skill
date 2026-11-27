"""CLI entry point for PulseBoard (`python -m pulseboard`)."""

from __future__ import annotations

import argparse

from .server import run_server
from .storage import apply_migrations, seed_default_users


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PulseBoard issue tracker")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--db", default="pulseboard.db")
    parser.add_argument("--seed", action="store_true", help="Seed default admin and member users")
    parser.add_argument("--migrate-only", action="store_true", help="Apply migrations and exit")
    args = parser.parse_args(argv)

    version = apply_migrations(args.db)
    if args.seed:
        seed_default_users(args.db)
    if args.migrate_only:
        print(f"Migrated {args.db} to schema_version={version}")
        return 0
    run_server(host=args.host, port=args.port, db_path=args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
