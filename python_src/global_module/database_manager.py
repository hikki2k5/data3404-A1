# Catalog
"""
Catalog for storing database schemas.
"""

from typing import Dict
from python_src.heap.tuple_desc import TupleDesc


class Catalog:
    """Stores the schemas for the database."""
    """Currently just stores the Schema in-memory, does not write it to disk"""

    def __init__(self):
        """Initialize the Catalog."""
        self.schemas: Dict[str, TupleDesc] = {}

    def add_schema(self, schema: TupleDesc, name: str) -> None:
        """Store a schema definition in the Catalog."""
        if name not in self.schemas:
            self.schemas[name] = schema
        else:
            raise RuntimeError("Schema Already Exists")

    def read_schema(self, name: str) -> TupleDesc:
        """Get the schema associated with the given name."""
        return self.schemas.get(name)

    def find_name_of_schema(self, schema: TupleDesc) -> str:
        """Find the name of the given schema."""
        for name, s in self.schemas.items():
            if s == schema:
                return name
        return "_NO_SCHEMA_FOUND_"
