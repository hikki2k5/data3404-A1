# AuctionDB performance evaluation files for SimpleDB

This is a small AuctionDB dataset that can be used for performance evaluation of different parts of SimpleDB.

## Usage
Execute from the root directory of SimpleDBL

```
python -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_test.db
```

or for one of the provided auctiondbs with a certain SIZE (small, large):

```
python -B -m tests.performance.auctiondb -d tests/performance/data3404_auctiondb_[SIZE].db
```

This loads the corresponding database file and provides the AuctionDB schema, on which then an
SQL command can be executed. 

### Performance Evaluations How-To
**For performance evaluation,** run same query on different database sizes at least 3 times and log execution time, page accesses and buffer hits. Report on averages of those values over the number of executions.

### Command Line Options
```
usage: import_csv.py [-h] [-d FILNAME] [-b SIZE] -f FILENAME [-e CHAR] [-t NAME] [-s TYPES] [-i]
options:
  -h, --help            show this help message and exit
  -d, --dbfile FILNAME  name of database file
  -b, --buffer SIZE     number of buffer frames
  -f, --file FILENAME   file name of CSV file to import [REQUIRED]
  -e, --delimiter CHAR  delimiter of CSV data; default ','
  -t, --tablename NAME  name of the table to load
  -s, --schema TYPES    list of types for row schema; all string by default; supported TYPES: str, int, float, bool
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
> **Important:** Make sure your code base is using your new storage layer when you run the csv importer, and/or change in the ```import_csv.py``` in line 72 the ```import_table = dbms.get_heap_file(args.tablename)``` call to use the proper storage file class.

Example: To create an experiment database for the 1000 bids scale:

```
python -B -m tests.performance.import_csv -f tests/performance/raw_data/bids1000.csv  -d data3404_auctiondb_experiment.db -t Bids  -s int,int,int,int,float,float,str
python -B -m tests.performance.import_csv -f tests/performance/raw_data/users1000.csv -d data3404_auctiondb_experiment.db -t Users -s int,str,str,str,str,str,int,float,str,int
python -B -m tests.performance.import_csv -f tests/performance/raw_data/items1000.csv -d data3404_auctiondb_experiment.db -t Items -s int,str,str,float,int,float,float,int,float,str,str,int,int
python -B -m tests.performance.import_csv -f tests/performance/raw_data/regions.csv   -d data3404_auctiondb_experiment.db -t Regions  -s int,str
python -B -m tests.performance.import_csv -f tests/performance/raw_data/categories.csv -d data3404_auctiondb_experiment.db -t Categories -s int,str
```
