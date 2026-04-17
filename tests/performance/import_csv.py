"""
Simple CSV file importer for USyd SimpleDB Database System.

Example usage:
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/users1000.csv -d data3404_auctiondb_small.db -t Users -s int,str,str,str,str,str,int,float,str,int

Option 4 usage:
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/bids1000.csv -d data3404_auctiondb_indexed.db -t Bids -s int,int,int,int,float,float,str --hash-index-columns user_id,item_id
"""

# genAI acknowledgement:
# genAI gave limited support for initial drafting of helper structure.
# The Option 4 integration for AuctionDB import, hash-index creation flow,
# robustness fixes, and final tested behaviour were implemented and improved
# by the team.

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable, List

from simpledb.executor.query_engine import QueryEngine
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.database_constants import DatabaseConstants
from simpledb.main.database_manager import DatabaseManager


SUPPORTED_TYPES = {"str", "int", "float", "bool"}


def parse_type_list(schema_arg: str | None, fieldnames: List[str]) -> List[str]:
    """Parse or infer a list of CSV field types."""
    if schema_arg is None:
        return ["str"] * len(fieldnames)

    typelist = [type_name.strip() for type_name in schema_arg.split(",")]
    if len(typelist) != len(fieldnames):
        raise ValueError("Number of schema types must match number of CSV columns")
    invalid = [type_name for type_name in typelist if type_name not in SUPPORTED_TYPES]
    if invalid:
        raise ValueError(f"Unsupported schema type(s): {', '.join(invalid)}")
    return typelist


def build_schema(fieldnames: List[str], typelist: List[str]) -> TupleDesc:
    """Create a TupleDesc from CSV header names and parsed type names."""
    import_schema = TupleDesc()
    for field_name, type_name in zip(fieldnames, typelist):
        if type_name == "str":
            import_schema.add_string(field_name)
        elif type_name == "int":
            import_schema.add_integer(field_name)
        elif type_name == "float":
            import_schema.add_double(field_name)
        elif type_name == "bool":
            import_schema.add_boolean(field_name)
    return import_schema


def convert_csv_row(row: List[str], fieldnames: List[str], typelist: List[str]) -> List[object]:
    """Convert one CSV row from strings into the requested SimpleDB field types."""
    converted = list(row)
    for index, type_name in enumerate(typelist):
        if type_name == "str":
            if fieldnames[index] == "email":
                converted[index] = converted[index][-DatabaseConstants.MAX_STRING_LENGTH:]
            else:
                converted[index] = converted[index][:DatabaseConstants.MAX_STRING_LENGTH]
        elif type_name == "int":
            converted[index] = int(converted[index])
        elif type_name == "float":
            converted[index] = float(converted[index])
        elif type_name == "bool":
            converted[index] = converted[index].strip().lower() == "true"
    return converted


def parse_index_columns(index_columns_arg: str | None) -> List[str]:
    """Parse a comma-separated list of columns that should receive hash indexes."""
    if not index_columns_arg:
        return []
    return [column.strip().lower() for column in index_columns_arg.split(",") if column.strip()]


def create_requested_hash_indexes(
    dbms: DatabaseManager,
    table_name: str,
    index_columns: Iterable[str],
    bucket_count: int,
) -> List[str]:
    """Create hash indexes for the requested columns and return their names."""
    created_indexes: List[str] = []
    for column_name in index_columns:
        index_name = f"{table_name}_{column_name}_hash_idx"
        dbms.create_hash_index(table_name, column_name, index_name=index_name, bucket_count=bucket_count)
        created_indexes.append(index_name)
    return created_indexes


def import_csv(args) -> None:
    """Import one CSV file into a SimpleDB table and optionally create hash indexes."""
    try:
        with open(args.file, "r", newline="", encoding="utf-8-sig") as csvfile:
            csvdata = csv.reader(csvfile, delimiter=args.delimiter)

            if args.tablename is None:
                args.tablename = Path(args.file).stem.capitalize()
            print("Importing csv data into table:", args.tablename)

            try:
                dbms = DatabaseManager(args.dbfile, args.buffer)
            except Exception as e:
                print(f"Error initializing DBMS: {e}")
                return

            fieldnames = [field_name.lstrip("\ufeff") for field_name in next(csvdata)]
            typelist = parse_type_list(args.schema, fieldnames)

            print(fieldnames)
            for field_name, type_name in zip(fieldnames, typelist):
                print(field_name, ": ", type_name)

            import_schema = build_schema(fieldnames, typelist)
            dbms.get_catalog().add_schema(import_schema, args.tablename)

            # For Option 4 we still load base table rows into the table,
            # then build integrated hash indexes over selected columns.
            import_table = dbms.get_heap_file(args.tablename)

            if import_table.is_empty():
                with import_table.inserter() as inserter:
                    rowcount = 0
                    for row in csvdata:
                        inserter.insert(convert_csv_row(row, fieldnames, typelist))
                        rowcount += 1
                print(f"\nImported {rowcount} rows into table {args.tablename}\n")
            else:
                print("Table already exists - nothing loaded.")

            index_columns = parse_index_columns(args.hash_index_columns)
            if index_columns:
                created_indexes = create_requested_hash_indexes(
                    dbms,
                    args.tablename,
                    index_columns,
                    args.hash_index_buckets,
                )
                print("Created hash indexes:")
                for index_name in created_indexes:
                    print(f"  - {index_name}")
                print()

            if args.interactive:
                QueryEngine(dbms).run()

            dbms.get_buffer_manager().flush_dirty()
            dbms.close()

    except OSError:
        print("Could not open/read csv file:", args.file)
    except ValueError as error:
        print(f"Import Error: {error}")


def main():
    """Process command-line arguments and import CSV data into SimpleDB."""
    argparser = argparse.ArgumentParser(description="SimpleDB CSV Importer")
    argparser.add_argument("-d", "--dbfile", metavar="FILNAME", help="name of database file", default=DatabaseConstants.DEFAULT_DB_NAME, type=str)
    argparser.add_argument("-b", "--buffer", metavar="SIZE", help="number of buffer frames", default=DatabaseConstants.MAX_BUFFER_FRAMES, type=int)
    argparser.add_argument("-f", "--file", metavar="FILENAME", help="file name of CSV file to import [REQUIRED]", default=None, type=str, required=True)
    argparser.add_argument("-e", "--delimiter", metavar="CHAR", help="delimiter of CSV data; default ','", default=",", type=str)
    argparser.add_argument("-t", "--tablename", metavar="NAME", help="name of the table to load", default=None, type=str)
    argparser.add_argument("-s", "--schema", metavar="TYPES", help="list of types for row schema; supported TYPES: str, int, float, bool", default=None, type=str)
    argparser.add_argument("--hash-index-columns", metavar="COLS", help="comma-separated columns that should receive integrated hash indexes after import", default=None, type=str)
    argparser.add_argument("--hash-index-buckets", metavar="COUNT", help="number of buckets to use for created hash indexes", default=64, type=int)
    argparser.add_argument("-i", "--interactive", help="flag whether interactive SQL command line should be opened after import", action="store_true")
    args = argparser.parse_args()
    import_csv(args)


if __name__ == "__main__":
    main()
