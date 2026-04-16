"""
AuctionDB Client for the SimpleDB Database System.

Execute with:
python -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_test.db
or
python -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_[SIZE].db

Careful: already on small database, join queries can run quite long...
         Always start with data3404_auctiondb_test.db first.
"""

from simpledb.main.database_manager import DatabaseManager
from simpledb.main.database_constants import DatabaseConstants
from simpledb.executor.query_engine import QueryEngine
from simpledb.main.catalog.tuple_desc import TupleDesc
import argparse


def main():
    """Process command-line argument"""
    argparser = argparse.ArgumentParser(description="SimpleDB demo - AuctionDB schema")
    argparser.add_argument("-d", "--dbfile", metavar="FILNAME", help="name of database file",   default=DatabaseConstants.DEFAULT_DB_NAME,   type=str)
    argparser.add_argument("-b", "--buffer", metavar="SIZE", help="number of buffer frames", default=DatabaseConstants.MAX_BUFFER_FRAMES, type=int)
    args = argparser.parse_args()

    """Run SimpleDB engine."""
    try:
        dbms = DatabaseManager(args.dbfile, args.buffer)
    except Exception as e:
        print(f"Error initializing DBMS: {e}")
        return  
    
    # Create schema for table Users
    catalog = dbms.get_catalog()
    catalog.add_schema(TupleDesc().add_integer("uid")\
                                  .add_string("first_name")\
                                  .add_string("last_name")\
                                  .add_string("nick_name")\
                                  .add_string("password")\
                                  .add_string("email")\
                                  .add_integer("rating")\
                                  .add_double("balance")\
                                  .add_string("creation_date")\
                                  .add_integer("region")\
                      , "Users")
    
    # Create schema for table Items
    catalog.add_schema(TupleDesc().add_integer("iid")\
                                  .add_string("name")\
                                  .add_string("description")\
                                  .add_double("initial_price")\
                                  .add_integer("quantity")\
                                  .add_double("reserve_price")\
                                  .add_double("buy_now")\
                                  .add_integer("nb_of_bids")\
                                  .add_double("max_bid")\
                                  .add_string("start_date")\
                                  .add_string("end_date")\
                                  .add_integer("seller")\
                                  .add_integer("category")\
                      , "Items")

    # Create schema for table Bids
    catalog.add_schema(TupleDesc().add_integer("bid_id")\
                                  .add_integer("user_id")\
                                  .add_integer("item_id")\
                                  .add_integer("qty")\
                                  .add_double("bid")\
                                  .add_double("max_bid")\
                                  .add_string("date")\
                      , "Bids")
        
    # Create schema for table Regions
    catalog.add_schema(TupleDesc().add_integer("rid")\
                                  .add_string("region_name")\
                      , "Regions")

    # Create schema for table Categories
    catalog.add_schema(TupleDesc().add_integer("cid")\
                                  .add_string("name")\
                      , "Categories")
        
    # Run query engine
    query_engine = QueryEngine(dbms)
    query_engine.run()
    
    # print some buffer statistics
    buf_io   = dbms.get_buffer_manager().get_page_accesses()
    buf_hits = dbms.get_buffer_manager().get_cache_hits()
    print(f"** Buffer Manager: {buf_io} page accesses, {buf_hits} cache hits")

    # Flush dirty pages
    dbms.get_buffer_manager().flush_dirty()


if __name__ == "__main__":
    main()
