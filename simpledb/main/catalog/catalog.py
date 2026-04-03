"""Catalog for storing schemas and index metadata."""

from typing import Dict, Optional
from simpledb.main.catalog.tuple_desc import TupleDesc


class Catalog:
    """Stores the schemas for the database."""
    """Currently just stores the Schema in-memory, does not write it to disk"""

    def __init__(self):
        """Initialize the Catalog."""
        self.schemas: Dict[str, TupleDesc] = {}
        self.indexes: Dict[str, Dict[str, object]] = {}

    @staticmethod
    def _normalise_name(name: str) -> str:
        return name.lower()

    def add_schema(self, schema: TupleDesc, name: str) -> None:
        """Store a schema definition in the Catalog."""
        normalised = self._normalise_name(name)
        if normalised in self.schemas:
            raise RuntimeError("Schema Already Exists")
        self.schemas[normalised] = schema
        self.indexes.setdefault(normalised, {})

    def read_schema(self, name: str) -> TupleDesc:
        """Get the schema associated with the given name."""
        return self.schemas.get(self._normalise_name(name))

    def find_name_of_schema(self, schema: TupleDesc) -> str:
        """Find the name of the given schema."""
        for name, s in self.schemas.items():
            if s == schema:
                return name
        return "_NO_SCHEMA_FOUND_"
    
    def print_schemas(self) -> None:
        """Print all schemas in the Catalog."""
        if not self.schemas:
            print("No schemas in catalog.")
            return
        
        print("Tables in Catalog:")
        for name, schema in self.schemas.items():
            print(f" {name}: {schema.str()}")

    def add_index(self, table_name: str, column_name: str, index) -> None:
        """Register an index for a table column."""
        normalised_table = self._normalise_name(table_name)
        if normalised_table not in self.schemas:
            raise KeyError(f"Unknown table '{table_name}'")
        column_name = column_name.lower()
        if not self.schemas[normalised_table].has_field(column_name):
            raise KeyError(f"Unknown column '{column_name}' for table '{table_name}'")
        self.indexes.setdefault(normalised_table, {})[column_name] = index

    def get_index(self, table_name: str, column_name: str) -> Optional[object]:
        """Return an index registered for the given table column, if any."""
        return self.indexes.get(self._normalise_name(table_name), {}).get(column_name.lower())

    def get_indexes(self, table_name: str) -> Dict[str, object]:
        """Return all registered indexes for a table."""
        return dict(self.indexes.get(self._normalise_name(table_name), {}))
