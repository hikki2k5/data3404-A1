"""
Query parser for database queries.
"""

import re
from typing import List, Tuple as PyTuple
from simpledb.parser.join_args import JoinArgs


class Query:
    """Represents a database query."""

    def __init__(self, table_name: str, projected_columns: List[str], join_args: JoinArgs = None):
        """Initialize a Query."""
        self.table_name = table_name
        self.projected_columns = projected_columns
        self.join_args = join_args

    def get_projected_columns(self) -> List[str]:
        """Get the columns to project from the query."""
        return self.projected_columns

    def get_table_name(self) -> str:
        """Get the table name from the query."""
        return self.table_name

    def has_join_arguments(self) -> bool:
        """Check if the query has join arguments."""
        return self.join_args is not None

    def get_join_args(self) -> JoinArgs:
        """Get the join arguments."""
        return self.join_args

    def validate(self, catalog) -> str:
        """Validate the query against the database schema."""
        schema = catalog.read_schema(self.table_name)
        if schema is None:
            return f"Invalid Schema: {self.table_name}"
            
        schema_columns = schema.get_column_names()
        
        if not self.has_join_arguments():
            # Single table query
            for column in self.projected_columns:
                if column not in schema_columns:
                    return f"Invalid Column: {column}"
            return None
        
        # Join query
        join_schema = catalog.read_schema(self.join_args.get_join_table())
        if join_schema is None:
            return f"Invalid Join-Table {self.join_args.get_join_table()}"
        
        join_schema_columns = join_schema.get_column_names()
        
        for column in self.projected_columns:
            in_left = column in schema_columns
            in_right = column in join_schema_columns
            
            if not in_left and not in_right:
                return f"Invalid Join Column: {column}"
            if in_left and in_right:
                return f"Ambiguous Join Column: {column}"
        
        if self.join_args.get_left_column() not in schema_columns:
            return "Join condition columns cannot be found in the schema"
        if self.join_args.get_right_column() not in join_schema_columns:
            return "Join condition columns cannot be found in the schema"
        
        left_type = schema.get_field_type_by_name(self.join_args.get_left_column())
        right_type = join_schema.get_field_type_by_name(self.join_args.get_right_column())
        
        if left_type != right_type:
            return "Join columns are of a different type"
        
        return None


    @staticmethod
    def generate_query(command: str):
        """Parse a query from a string."""
        pattern = r"SELECT ([\w, ]+)\s+FROM (\w+)(\s+JOIN (\w+)\s+ON (\w+)\s*=\s*(\w+))?;?"
        match = re.match(pattern, command.strip(), re.IGNORECASE)
        
        if not match:
            return None
        
        table_name = match.group(2)
        projected_columns = [col.strip().lower() for col in match.group(1).split(',')]
        
        join_args = None
        if match.group(3):  # Has JOIN
            join_args = JoinArgs(match.group(4), match.group(5).lower(), match.group(6).lower())
        
        return Query(table_name, projected_columns, join_args)

    def __str__(self) -> str:
        """String representation."""
        result = f"Running a query on: {self.table_name} projecting over columns: {self.projected_columns}"
        if self.has_join_arguments():
            result += f" joining {self.join_args}"
        return result
