"""
AuctionDB Client for the SimpleDB Database System.

Execute with:
python3 -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_test.db
or
python3 -B -m tests.performance.auctiondb -d data3404_auctiondb_indexed.db --rebuild-hash-indexes

Careful: already on small database, join queries can run quite long...
         Always start with data3404_auctiondb_test.db first.
"""

from __future__ import annotations

import argparse
from typing import List

from simpledb.executor.query_engine import QueryEngine
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.database_constants import DatabaseConstants
from simpledb.main.database_manager import DatabaseManager


DEFAULT_AUCTIONDB_INDEX_SPECS = {
    "Bids": ["user_id", "item_id"],
    "Users": ["uid", "region"],
    "Items": ["seller", "category"],
    "Regions": ["rid"],
    "Categories": ["cid"],
}


def load_auctiondb_schema(dbms: DatabaseManager) -> None:
    """Register the AuctionDB schema in the in-memory catalog."""
    catalog = dbms.get_catalog()
    catalog.add_schema(
        TupleDesc()
        .add_integer("uid")
        .add_string("first_name")
        .add_string("last_name")
        .add_string("nick_name")
        .add_string("password")
        .add_string("email")
        .add_integer("rating")
        .add_double("balance")
        .add_string("creation_date")
        .add_integer("region"),
        "Users",
    )

    catalog.add_schema(
        TupleDesc()
        .add_integer("iid")
        .add_string("name")
        .add_string("description")
        .add_double("initial_price")
        .add_integer("quantity")
        .add_double("reserve_price")
        .add_double("buy_now")
        .add_integer("nb_of_bids")
        .add_double("max_bid")
        .add_string("start_date")
        .add_string("end_date")
        .add_integer("seller")
        .add_integer("category"),
        "Items",
    )

    catalog.add_schema(
        TupleDesc()
        .add_integer("bid_id")
        .add_integer("user_id")
        .add_integer("item_id")
        .add_integer("qty")
        .add_double("bid")
        .add_double("max_bid")
        .add_string("date"),
        "Bids",
    )

    catalog.add_schema(
        TupleDesc().add_integer("rid").add_string("region_name"),
        "Regions",
    )

    catalog.add_schema(
        TupleDesc().add_integer("cid").add_string("name"),
        "Categories",
    )


def rebuild_default_hash_indexes(dbms: DatabaseManager, bucket_count: int = 128) -> List[str]:
    """Recreate the default AuctionDB hash indexes inside the current DBMS session."""
    created_indexes: List[str] = []
    for table_name, columns in DEFAULT_AUCTIONDB_INDEX_SPECS.items():
        for column_name in columns:
            index_name = f"{table_name}_{column_name}_hash_idx"
            dbms.create_hash_index(table_name, column_name, index_name=index_name, bucket_count=bucket_count)
            created_indexes.append(index_name)
    return created_indexes


def main():
    """Run the AuctionDB interactive client."""
    argparser = argparse.ArgumentParser(description="SimpleDB demo - AuctionDB schema")
    argparser.add_argument("-d", "--dbfile", metavar="FILNAME", help="name of database file", default=DatabaseConstants.DEFAULT_DB_NAME, type=str)
    argparser.add_argument("-b", "--buffer", metavar="SIZE", help="number of buffer frames", default=DatabaseConstants.MAX_BUFFER_FRAMES, type=int)
    argparser.add_argument("--rebuild-hash-indexes", help="rebuild the default AuctionDB hash indexes after loading the schema", action="store_true")
    argparser.add_argument("--hash-index-buckets", metavar="COUNT", help="bucket count to use when rebuilding default AuctionDB hash indexes", default=128, type=int)
    args = argparser.parse_args()

    try:
        dbms = DatabaseManager(args.dbfile, args.buffer)
    except Exception as e:
        print(f"Error initializing DBMS: {e}")
        return

    load_auctiondb_schema(dbms)

    if args.rebuild_hash_indexes:
        rebuilt = rebuild_default_hash_indexes(dbms, bucket_count=args.hash_index_buckets)
        print("Rebuilt AuctionDB hash indexes:")
        for index_name in rebuilt:
            print(f"  - {index_name}")
        print()

    query_engine = QueryEngine(dbms)
    query_engine.run()

    buf_io = dbms.get_buffer_manager().get_page_accesses()
    buf_hits = dbms.get_buffer_manager().get_cache_hits()
    print(f"** Buffer Manager: {buf_io} page accesses, {buf_hits} cache hits")

    dbms.get_buffer_manager().flush_dirty()


if __name__ == "__main__":
    main()
