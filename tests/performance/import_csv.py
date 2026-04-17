"""
Simple CSV file importer for USyd SimpleDB Database System.

Example usage:
python -B -m tests.performance.import_csv -f tests/performance/raw_data/users1000.csv -d data3404_auctiondb_small.db -t Users -s int,str,str,str,str,str,int,float,str,int
"""

from simpledb.main.database_manager import DatabaseManager
from simpledb.main.database_constants import DatabaseConstants
from simpledb.executor.query_engine import QueryEngine
from simpledb.main.catalog.tuple_desc import TupleDesc
import argparse
from pathlib import Path
import csv


def main():
    """Process command-line argument"""
    argparser = argparse.ArgumentParser(description="SimpleDB CSV Importer")
    argparser.add_argument("-d", "--dbfile",   metavar="FILNAME",  help="name of database file",   default=DatabaseConstants.DEFAULT_DB_NAME,   type=str)
    argparser.add_argument("-b", "--buffer",   metavar="SIZE",     help="number of buffer frames", default=DatabaseConstants.MAX_BUFFER_FRAMES, type=int)
    argparser.add_argument("-f", "--file",     metavar="FILENAME", help="file name of CSV file to import [REQUIRED]", default=None, type=str, required=True)
    argparser.add_argument("-e", "--delimiter",metavar="CHAR",     help="delimiter of CSV data; default ','", default=',', type=str)
    argparser.add_argument("-t", "--tablename",metavar="NAME",     help="name of the table to load", default=None,type=str)
    argparser.add_argument("-s", "--schema",   metavar="TYPES",    help="list of types for row schema; all string by default; supported TYPES: str, int, float, bool", default=None, type=str)
    argparser.add_argument("-i", "--interactive",                  help="flag whether interactive SQL command line should be opened after import", action='store_true')
    args = argparser.parse_args()

    # Open the file to import and get the schema from the header line
    try:
      with open(args.file, "r") as csvfile:
        csvdata = csv.reader(csvfile, delimiter=args.delimiter)

        # check which table name to use for import
        if args.tablename is None:
            args.tablename = Path(args.file).stem.capitalize()
        print("Importing csv data into table: ", args.tablename)

        """Run the importer"""
        try:
            dbms = DatabaseManager(args.dbfile, args.buffer)
        except Exception as e:
            print(f"Error initializing DBMS: {e}")
            return  
    
        # Create schema for imported data
        fieldnames = csvdata.__next__() # read header line of CSV file
        print(fieldnames)
        if not args.schema:
            typelist = []
            for f in fieldnames:
                typelist.append("str")
        else:
            typelist = args.schema.split(",")

        import_schema = TupleDesc()
        for i in range(len(fieldnames)):
            print(fieldnames[i], ": ", typelist[i])
            if typelist[i]=="str":
                import_schema.add_string(fieldnames[i])
            elif typelist[i]=="int":
                import_schema.add_integer(fieldnames[i])
            elif typelist[i]=="float":
                import_schema.add_double(fieldnames[i])
            elif typelist[i]=="bool":
                import_schema.add_boolean(fieldnames[i])
        dbms.get_catalog().add_schema(import_schema, args.tablename)
    
        # By default we load into a heap file.
        # NOTE: If you want to import data into an own storage implementation, 
        #       you need to use the correct get_XYZ(tablename) call here.
        import_table = dbms.get_heap_file(args.tablename)

        # Insert rows (only if db file without data yet)
        if import_table.is_empty():
            with import_table.inserter() as inserter:
                rowcount = 0
                for row in csvdata:
                    # csv reads everything as strings; convert to types as specified in row schema
                    for i in range(len(typelist)):
                        if typelist[i]=="str": # just ensure string is not longer than currently supported by SimpleDB
                            if fieldnames[i] == "email": # HACK: special handling of email to keep domain at end of email addr
                                row[i] = row[i][-DatabaseConstants.MAX_STRING_LENGTH:]
                            else:
                                row[i] = row[i][:DatabaseConstants.MAX_STRING_LENGTH]
                        elif typelist[i]=="int":
                            row[i] = int(row[i])
                        elif typelist[i]=="float":
                            row[i] = float(row[i])
                        elif typelist[i]=="bool":
                            row[i] = bool(row[i])
                    # print(row)
                    inserter.insert(row)
                    rowcount += 1
            print(f"\nimported {rowcount} rows into table {args.tablename}\n")
        else:
            print("Table already exists - nothing loaded.")    

        # If interactive mode, run query engine
        if args.interactive:
            query_engine = QueryEngine(dbms)
            query_engine.run()
    
        # Flush dirty pages
        dbms.get_buffer_manager().flush_dirty()

    except OSError:
      print("Could not open/read csv file:", args.file)

if __name__ == "__main__":
    main()
