"""
Database Components are initialised and stored in this class.
"""

import os
from simpledb.main.database_constants import DatabaseConstants
from simpledb.disk.disk_manager import DiskManager
from simpledb.buffer.buffer_manager import BufferManager, BufferAccessException
from simpledb.buffer.replacement.random_replacer import RandomReplacer
from simpledb.main.catalog.catalog import Catalog
from simpledb.heap.heap_file import HeapFile
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.index.hash_index import HashIndex
from simpledb.heap.tuple import Tuple


class ComponentsNotInitialisedError(Exception):
    """Raised when database components are not initialized."""
    pass


class DatabaseManager:
    """Database Components are initialised and stored in this class."""

    def __init__(self, db_filename: str = DatabaseConstants.DEFAULT_DB_NAME, buffer_frames: int = DatabaseConstants.MAX_BUFFER_FRAMES):
        """Initialize the DatabaseManager."""
        self.is_initialised = False
        self.dm = None
        self.bm = None
        self.catalog = None
        self._temp_file = None
        self._initialise_components(db_filename, buffer_frames)

    def _initialise_components(self, db_filename: str, buffer_frames: int) -> None:
        """Initialize database components."""
        if not self.is_initialised:
            try:
                # Initialize DiskManager
                self.dm = DiskManager(db_filename, 1, self._temp_file)

                # Initialize BufferManager with Random replacer
                if ( buffer_frames < 3):
                    raise ValueError("Buffer frames must be at least 3.")
                self.bm = BufferManager(
                    buffer_frames,
                    RandomReplacer(),
                    self.dm
                )

                # Initialize Catalog
                self.catalog = Catalog()
                self.is_initialised = True

            except Exception as e:
                # Clean up on failure
                if self._temp_file and os.path.exists(self._temp_file.name):
                    os.unlink(self._temp_file.name)
                raise e

    def reset_components(self) -> None:
        """Reset database components."""
        self.close()
        self.is_initialised = False
        self._initialise_components()

    def get_catalog(self) -> Catalog:
        """Get the catalog component."""
        if self.catalog is None:
            raise ComponentsNotInitialisedError()
        return self.catalog

    def get_disk_manager(self) -> DiskManager:
        """Get the disk manager component."""
        if self.dm is None:
            raise ComponentsNotInitialisedError()
        return self.dm

    def get_buffer_manager(self) -> BufferManager:
        """Get the buffer manager component."""
        if self.bm is None:
            raise ComponentsNotInitialisedError()
        return self.bm

    def close(self) -> None:
        """Close the database and clean up resources."""
        try:
            if self.bm:
                self.bm.flush_dirty()
        except BufferAccessException as e:
            print(f"Error flushing buffer: {e}")

        try:
            if self.dm:
                self.dm.db_file.close()
        except Exception as e:
            print(f"Error closing disk manager: {e}")

        # Clean up temporary file
        if self._temp_file and os.path.exists(self._temp_file.name):
            try:
                os.unlink(self._temp_file.name)
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")

    def get_heap_file(self, name: str) -> HeapFile:
        """Get a heap file by name."""
        schema = self.catalog.read_schema(name)
        if schema is None:
            raise KeyError(f"Unknown table '{name}'")
        relation_name = self.catalog.find_name_of_schema(schema)
        return HeapFile(
            schema,
            relation_name,
            self.bm,
            insert_callback=lambda tuple_obj: self._update_indexes_for_insert(relation_name, tuple_obj),
        )

    def get_temp_heap_file(self, schema: TupleDesc) -> HeapFile:
        """Get a temporary heap file with the given schema."""
        return HeapFile(schema, buffer_manager=self.bm)

    def create_hash_index(self, table_name: str, column_name: str, index_name: str = None, bucket_count: int = 8) -> HashIndex:
        """Create, populate, and register a hash index for a table column."""
        schema = self.catalog.read_schema(table_name)
        if schema is None:
            raise KeyError(f"Unknown table '{table_name}'")
        if not schema.has_field(column_name):
            raise KeyError(f"Unknown column '{column_name}' for table '{table_name}'")

        resolved_name = index_name or f"{table_name}_{column_name}_hash_idx"
        index = HashIndex(resolved_name, table_name, column_name, schema, bucket_count)
        table = self.get_heap_file(table_name)
        index.build_from_table(table)
        self.catalog.add_index(table_name, column_name, index)
        return index

    def get_index(self, table_name: str, column_name: str):
        """Fetch a registered index by table and column."""
        return self.catalog.get_index(table_name, column_name)

    def _update_indexes_for_insert(self, table_name: str, tuple_obj: Tuple) -> None:
        """Update all indexes registered on a table after an insert succeeds."""
        for index in self.catalog.get_indexes(table_name).values():
            index.insert(tuple_obj)
