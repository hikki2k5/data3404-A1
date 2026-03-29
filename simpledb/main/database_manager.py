"""
Database Components are initialised and stored in this class.
"""

import tempfile
import os
from simpledb.main.database_constants import DatabaseConstants
from simpledb.disk.disk_manager import DiskManager
from simpledb.buffer.buffer_manager import BufferManager, BufferAccessException
from simpledb.buffer.replacement.mru_replacer import MruReplacer
from simpledb.main.catalog.catalog import Catalog
from simpledb.heap.heap_file import HeapFile
from simpledb.main.catalog.tuple_desc import TupleDesc


class ComponentsNotInitialisedError(Exception):
    """Raised when database components are not initialized."""
    pass


class DatabaseManager:
    """Database Components are initialised and stored in this class."""

    def __init__(self):
        """Initialize the DatabaseManager."""
        self.is_initialised = False
        self.dm = None
        self.bm = None
        self.catalog = None
        self._temp_file = None
        self._initialise_components()

    def _initialise_components(self) -> None:
        """Initialize database components."""
        if not self.is_initialised:
            try:
                # Create temporary file for database
                self._temp_file = tempfile.NamedTemporaryFile(
                    prefix=DatabaseConstants.DEFAULT_DB_NAME,
                    suffix='.tmp',
                    delete=False
                )
                self._temp_file.close()  # Close so DiskManager can open it

                # Initialize DiskManager
                self.dm = DiskManager(DatabaseConstants.DEFAULT_DB_NAME, 1)

                # Initialize BufferManager with MRU replacer
                self.bm = BufferManager(
                    DatabaseConstants.MAX_BUFFER_FRAMES,
                    MruReplacer(),
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
                self.dm.reset()
        except Exception as e:
            print(f"Error resetting disk manager: {e}")

        # Clean up temporary file
        if self._temp_file and os.path.exists(self._temp_file.name):
            try:
                os.unlink(self._temp_file.name)
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")

    def get_heap_file(self, name: str) -> HeapFile:
        """Get a heap file by name."""
        schema = self.catalog.read_schema(name)
        return HeapFile(schema, name, self.bm)

    def get_temp_heap_file(self, schema: TupleDesc) -> HeapFile:
        """Get a temporary heap file with the given schema."""
        return HeapFile(schema, buffer_manager=self.bm)
