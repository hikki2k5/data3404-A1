"""
Query Engine - REPL for executing queries.
"""

import time
from simpledb.main.database_manager import DatabaseManager
from simpledb.parser.query import Query
from simpledb.executor.projection.projection import Projection
from simpledb.executor.join.nested_loop_join import NestedLoopJoin
from simpledb.executor.join.block_nested_loop_join import BlockNestedLoopJoin
from simpledb.executor.join.sort_merge_join import SortMergeJoin


class QueryEngine:
    """Query engine for executing database queries."""

    def __init__(self, dbms: DatabaseManager):
        """Initialize the QueryEngine."""
        self.dbms = dbms

    def run(self) -> None:
        """Run the query engine REPL (read-eval-print loop)."""
        print("SimpleDB Query Engine")
        print("Type 'quit' to exit")
        print()
        
        while True:
            try:
                command = input("SQL> ").strip()
                if command.lower() == 'quit':
                    break
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
        
        error = query.validate(self.dbms)
        if error:
            print(f"Validation Error: {error}")
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
            
            # Apply projection if needed
            if query.get_projected_columns():
                result_iterator = Projection(result_iterator, *query.get_projected_columns())
            
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
