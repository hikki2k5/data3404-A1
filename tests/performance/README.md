# AuctionDB performance evaluation files for SimpleDB

This is a small AuctionDB dataset that can be used for performance evaluation of different parts of SimpleDB.

## Usage
Execute from the root directory of SimpleDB:

```bash
python3 -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_test.db
```

or for one of the provided auctiondbs with a certain SIZE (small, large):

```bash
python3 -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_[SIZE].db
```

If you want to reopen an indexed AuctionDB created for Option 4 and make the planner rebuild the default in-memory hash indexes in that session, run:

```bash
python3 -B -m tests.performance.auctiondb -d data3404_auctiondb_indexed.db --rebuild-hash-indexes
```

This loads the corresponding database file and provides the AuctionDB schema, on which then an
SQL command can be executed. 

### Performance Evaluations How-To
**For performance evaluation,** run same query on different database sizes at least 3 times and log execution time, page accesses and buffer hits. Report on averages of those values over the number of executions.

### Command Line Options
```text
usage: import_csv.py [-h] [-d FILNAME] [-b SIZE] -f FILENAME [-e CHAR] [-t NAME] [-s TYPES] [--hash-index-columns COLS] [--hash-index-buckets COUNT] [-i]
options:
  -h, --help            show this help message and exit
  -d, --dbfile FILNAME  name of database file
  -b, --buffer SIZE     number of buffer frames
  -f, --file FILENAME   file name of CSV file to import [REQUIRED]
  -e, --delimiter CHAR  delimiter of CSV data; default ','
  -t, --tablename NAME  name of the table to load
  -s, --schema TYPES    list of types for row schema; all string by default; supported TYPES: str, int, float, bool
  --hash-index-columns COLS
                        comma-separated columns that should receive integrated hash indexes after import
  --hash-index-buckets COUNT
                        number of buckets to use for created hash indexes
  -i, --interactive     flag whether interactive SQL command line should be opened after import
```

## AuctionDB Data Scales
**Test dataset:** _data3404_auctiondb_test.db_<br> 
48 kB with 100 bids and corresponding users, stems, regions and categories

**Small dataset:** _data3404_auctiondb_small.db_<br>
427 kB with 1000 bids and corresponding users, stems, regions and categories

**Large dataset:** _data3404_auctiondb_large.db_<br>
2.0 MB with 5000 bids and corresponding users, stems, regions and categories

## AuctionDB Database Creation: ```import_csv.py```
The provided databases come with the auctiondb data pre-loaded in five tables stored in HeapFiles.

If you want to evaluate an own storage container, you can create an own database manually using the provided csv importer and the raw data from CSV files.

### Step 1: Unzip raw data
In command line, navigate to folder ```tests/performance/raw_data/``` and unpack the ```auctiondb_csvfiles.zip``` archive there (be careful to not create an additional sub-directory; CSV files should reside directly in raw_data/).

### Step 2: Import CSV files of same size into new SimpleDB database

Decide on a new database name, say  ```data3404_auctiondb_experiment.db``` 

Decide which data size to load; there are files with 100 (test), 1000 (small), 5000 (large) and 10000 (XL) bids and corresponding user, item, region and categoiry data.

> [!NOTE]
> **Option 4 note:** The importer now supports integrated hash-index creation directly via `--hash-index-columns`. This allows you to import the AuctionDB tables and build your Option 4 indexes immediately after loading each table.

Example: To create an experiment database for the 1000 bids scale:

```bash
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/bids1000.csv  -d data3404_auctiondb_experiment.db -t Bids  -s int,int,int,int,float,float,str
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/users1000.csv -d data3404_auctiondb_experiment.db -t Users -s int,str,str,str,str,str,int,float,str,int
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/items1000.csv -d data3404_auctiondb_experiment.db -t Items -s int,str,str,float,int,float,float,int,float,str,str,int,int
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/regions.csv   -d data3404_auctiondb_experiment.db -t Regions  -s int,str
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/categories.csv -d data3404_auctiondb_experiment.db -t Categories -s int,str
```

Example for Option 4 with integrated hash indexes:

```bash
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/bids1000.csv  -d data3404_auctiondb_indexed.db -t Bids  -s int,int,int,int,float,float,str --hash-index-columns user_id,item_id --hash-index-buckets 128
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/users1000.csv -d data3404_auctiondb_indexed.db -t Users -s int,str,str,str,str,str,int,float,str,int --hash-index-columns uid,region --hash-index-buckets 128
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/items1000.csv -d data3404_auctiondb_indexed.db -t Items -s int,str,str,float,int,float,float,int,float,str,str,int,int --hash-index-columns seller,category --hash-index-buckets 128
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/regions.csv   -d data3404_auctiondb_indexed.db -t Regions  -s int,str --hash-index-columns rid
python3 -B -m tests.performance.import_csv -f tests/performance/raw_data/categories.csv -d data3404_auctiondb_indexed.db -t Categories -s int,str --hash-index-columns cid
```

## Automated Evaluation Helper

To collect averaged metrics for report tables, use:

```bash
python3 -B -m tests.performance.evaluate_hash_index -d data3404_auctiondb_indexed.db --rebuild-hash-indexes -r 3
```

This prints, for each benchmark query:
- chosen plan
- rows returned
- average execution time
- average page accesses
- average buffer hits
- average tuples examined
