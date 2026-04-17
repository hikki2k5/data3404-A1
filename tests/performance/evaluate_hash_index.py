"""Automated evaluation helper for comparing AuctionDB query behaviour."""

# genAI acknowledgement:
# genAI was used only for light support in drafting benchmark-helper structure.
# The evaluation workflow, chosen metrics, measurement corrections, and final
# tested script were determined and refined by the team.

from __future__ import annotations

import argparse
import time
from statistics import mean
from typing import Dict, List

from simpledb.executor.query_planner import QueryPlanner
from simpledb.main.database_constants import DatabaseConstants
from simpledb.main.database_manager import DatabaseManager
from simpledb.parser.query import Query
from tests.performance.auctiondb import load_auctiondb_schema, rebuild_default_hash_indexes


DEFAULT_BENCHMARK_QUERIES = [
    "SELECT * FROM Regions WHERE rid = 3;",
    "SELECT * FROM Categories WHERE cid = 2;",
    "SELECT * FROM Items WHERE category = 5;",
    "SELECT * FROM Bids WHERE item_id = 100;",
]


def run_query_once(dbfile: str, query_text: str, buffer_frames: int, rebuild_hash_indexes: bool, bucket_count: int) -> Dict[str, object]:
    """Run one query in a fresh DBMS session and return execution metrics."""
    dbms = DatabaseManager(dbfile, buffer_frames)
    try:
        load_auctiondb_schema(dbms)
        if rebuild_hash_indexes:
            rebuild_default_hash_indexes(dbms, bucket_count=bucket_count)

        planner = QueryPlanner(dbms)
        buffer_manager = dbms.get_buffer_manager()
        # Measure the query itself, not one-time setup such as schema load or index rebuild.
        buffer_manager.page_accesses = 0
        buffer_manager.cache_hits = 0
        query = Query.generate_query(query_text)
        if query is None:
            raise ValueError(f"Could not parse query: {query_text}")
        validation_error = query.validate(dbms.get_catalog())
        if validation_error is not None:
            raise ValueError(validation_error)

        logical_plan = planner.create_logical_plan(query)
        start = time.perf_counter()
        result_iterator = planner.create_execution_plan(logical_plan)
        try:
            row_count = sum(1 for _ in result_iterator)
        finally:
            result_iterator.close()
        elapsed = time.perf_counter() - start

        details = planner.get_last_execution_details()
        return {
            "query": query_text,
            "rows": row_count,
            "time_seconds": elapsed,
            "page_accesses": buffer_manager.get_page_accesses(),
            "buffer_hits": buffer_manager.get_cache_hits(),
            "plan_name": details.plan_name,
            "index_name": details.index_name,
            "tuples_examined": details.tuples_examined,
            "reason": details.reason,
        }
    finally:
        dbms.close()


def format_metric(value: float) -> str:
    """Format a numeric metric for compact report output."""
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def main() -> None:
    """Run repeated AuctionDB benchmarks and print averaged metrics."""
    argparser = argparse.ArgumentParser(description="AuctionDB benchmark helper for hash-index evaluation")
    argparser.add_argument("-d", "--dbfile", metavar="FILNAME", help="database file to benchmark", default=DatabaseConstants.DEFAULT_DB_NAME, type=str)
    argparser.add_argument("-b", "--buffer", metavar="SIZE", help="number of buffer frames", default=DatabaseConstants.MAX_BUFFER_FRAMES, type=int)
    argparser.add_argument("-r", "--repeats", metavar="COUNT", help="number of repeated runs per query", default=3, type=int)
    argparser.add_argument("--rebuild-hash-indexes", help="rebuild the default AuctionDB hash indexes before each benchmark run", action="store_true")
    argparser.add_argument("--hash-index-buckets", metavar="COUNT", help="bucket count to use if rebuilding default AuctionDB hash indexes", default=128, type=int)
    argparser.add_argument("-q", "--query", action="append", help="query to benchmark; can be supplied multiple times")
    args = argparser.parse_args()

    queries = args.query if args.query else DEFAULT_BENCHMARK_QUERIES

    print("=" * 72)
    print("AuctionDB Hash Index Evaluation")
    print("=" * 72)
    print(f"Database file: {args.dbfile}")
    print(f"Repeats per query: {args.repeats}")
    print(f"Rebuild hash indexes: {args.rebuild_hash_indexes}")
    print()

    for query_text in queries:
        runs = [
            run_query_once(
                args.dbfile,
                query_text,
                args.buffer,
                args.rebuild_hash_indexes,
                args.hash_index_buckets,
            )
            for _ in range(args.repeats)
        ]

        avg_time = mean(run["time_seconds"] for run in runs)
        avg_accesses = mean(run["page_accesses"] for run in runs)
        avg_hits = mean(run["buffer_hits"] for run in runs)
        avg_examined = mean(run["tuples_examined"] for run in runs)
        first = runs[0]

        print("-" * 72)
        print(f"Query: {query_text}")
        print(f"Plan: {first['plan_name']}" + (f" on {first['index_name']}" if first["index_name"] else ""))
        if first["reason"]:
            print(f"Reason: {first['reason']}")
        print(f"Rows returned: {first['rows']}")
        print(f"Average time (s): {format_metric(avg_time)}")
        print(f"Average page accesses: {format_metric(avg_accesses)}")
        print(f"Average buffer hits: {format_metric(avg_hits)}")
        print(f"Average tuples examined: {format_metric(avg_examined)}")
        print()


if __name__ == "__main__":
    main()
