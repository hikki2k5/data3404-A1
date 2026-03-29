"""
Query Engine - REPL for executing queries.
"""

import time
import readline  # just by importing improves input() to support editing and history
from simpledb.main.database_manager import DatabaseManager
from simpledb.parser.query import Query
from simpledb.executor.projection.projection import Projection
from simpledb.executor.limit.limit import Limit
from simpledb.executor.ordering import InMemoryOrderBy
from simpledb.executor.filter.filter import Filter
from simpledb.executor.filter.equals import Equals
from simpledb.executor.filter.range import GreaterThanEquals, GreaterThan, LessThanEquals, LessThan
from simpledb.executor.filter.not_modifier import NotModifier
from simpledb.parser.filter_args import Comparison
from simpledb.executor.join.nested_loop_join import NestedLoopJoin


class QueryEngine:
    """
    Query engine for executing database queries.

    This class parses and executes the query given to the program by the user.
 
    It loops waiting for input (run method), once a command has been entered, it creates a new query and then checks that
    it is valid. If it is, it will execute the query. This involves pipelining the query based on the different components
 
    E.g. in the query SELECT age, name FROM students WHERE age > 10 AND age < 20;
 
    * It will load in the iterator for the students table (AccessIterator rows = table.iterator();)
    * It will then wrap this iterator in a filter for both (age > 10), and another filter for (age < 20)
    * Finally it will project out the columns from this filtered iterator (creating a new TupleDesc to represent them)
    """

    def __init__(self, dbms: DatabaseManager):
        """Initialize the QueryEngine."""
        self.dbms = dbms

    def run(self) -> None:
        """
        Run the query engine's read-eval-print loop (REPL):
         - Loops over input read in from the user, validating the correctness and calling execute on valid queries
         - Exits once "quit" or "exit" is called
         - Shows schema of available tables on command "schema" or "tables"
        """
        print("SimpleDB Query Engine")
        print("Type 'quit' to exit")
        print()
        
        while True:
            try:
                command = input("SQL> ").strip()
                if command.lower() == 'quit' or command.lower() == 'exit':
                    break
                if command.lower() == 'schema' or command.lower() == 'tables':
                    self.dbms.get_catalog().print_schemas()
                    continue
                if not command:
                    continue
                
                self._execute_query(command)
            except KeyboardInterrupt:
                print("\nInterrupted")
            except Exception as e:
                print(f"Error: {e}")

    def _execute_query(self, command: str) -> None:
        """Execute a single query."""
        query = Query.generate_query(command)
        if query is None:
            print("Invalid query syntax")
            return
        
        error = query.validate(self.dbms.get_catalog())
        if error:
            print(f"Query Validation Error: {error}")
            return
        
        start_time = time.time()
        try:
            # Get left table
            left_table = self.dbms.get_heap_file(query.get_table_name())
            left_iterator = left_table.iterator()

            # Handle joins if present
            if query.has_join_arguments():
                join_args = query.get_join_args()
                right_table = self.dbms.get_heap_file(join_args.get_join_table())
                right_iterator = right_table.iterator()
                
                # Use nested loop join by default
                result_iterator = NestedLoopJoin(left_iterator, right_iterator, join_args)
            else:
                result_iterator = left_iterator
            
            # Filter rows according to WHERE clauses
            if query.has_filter_arguments():
                for filter_args in query.get_filter_args():
                    result_iterator = QueryEngine.filter_where(result_iterator, filter_args)

            # Handle the order by clause
            if query.has_orderby_clause():
                result_iterator = InMemoryOrderBy(result_iterator, query.get_orderby_columns())

            # Apply projection if needed
            if query.get_projected_columns():
                result_iterator = Projection(result_iterator, *query.get_projected_columns())
            
            # Add limit operator if needed
            if query.has_limit_clause():
                result_iterator = Limit(result_iterator, query.get_limit())

            # Execute and display results
            row_count = 0
            print()
            for tuple_obj in result_iterator:
                print(tuple_obj.to_row())
                row_count += 1
            
            result_iterator.close()
            
            elapsed = time.time() - start_time
            print(f"\n{row_count} rows retrieved in {elapsed:.3f}s")
            
        except Exception as e:
            print(f"Execution Error: {e}")
            raise

    @staticmethod
    def filter_where(query_iter, filter_args):
        """
        Applies the filter condition described by where_arg to the iterator rows, and returns an iterator over this
        pipelined view.

        You will need to implement the rest of the WHERE clause comparison signs. Currently we can only check if a column
        is equal. Have a look at the signs you need to implement in FilterArgs, and look at the filters that are available
        in Range and NotModifier classes
        """
        schema = query_iter.get_schema()
        # Gets the column name of the where clause
        column = filter_args.get_column()
        # Obtains the where value in the appropriate type to use for filtering (i.e. we need to convert the string
        # "10.9" to a (double)'10.9' so we can compare our records
        value = schema.get_field_type_by_name(column).parse_type(filter_args.get_value())
        # Applies the right where filter
        comparison = filter_args.get_comparison()
        if comparison == Comparison.EQUAL:
            return Filter(query_iter, column, Equals(value))
        elif comparison == Comparison.NOT_EQUAL:
            return Filter(query_iter, column, NotModifier(Equals(value)))
        elif comparison == Comparison.GEQ:
            return Filter(query_iter, column, GreaterThanEquals(value))
        elif comparison == Comparison.GREATER:
            return Filter(query_iter, column, GreaterThan(value))
        elif comparison == Comparison.LEQ:
            return Filter(query_iter, column, LessThanEquals(value))
        elif comparison == Comparison.LESS:
            return Filter(query_iter, column, LessThan(value))
        else:
            return query_iter

