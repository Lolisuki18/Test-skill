"""CLI entry point for Vault (`python -m vault`)."""

from __future__ import annotations

import argparse

from .server import run_server
from .storage import apply_migrations, seed_users


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vault bookmark manager")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8095)
    parser.add_argument("--db", default="vault.db")
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--migrate-only", action="store_true")
    args = parser.parse_args(argv)

    ver = apply_migrations(args.db)
    if args.seed:
        seed_users(args.db)
    if args.migrate_only:
        print(f"Migrated {args.db} to schema_version={ver}")
        return 0
    run_server(host=args.host, port=args.port, db_path=args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
