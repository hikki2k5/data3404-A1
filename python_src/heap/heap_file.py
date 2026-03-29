"""
HeapFile - a collection of unordered pages containing tuples.
"""

from python_src.heap.tuple_desc import TupleDesc
from python_src.heap.page_id import PageId
from python_src.heap.heap_page import HeapPage
from python_src.buffer.buffer_manager import BufferManager, BufferAccessException
from python_src.disk.header_page import HeaderPage
from python_src.global_module.database_constants import DatabaseConstants
import time
import random


class HeapFile:
    """Represents a collection of unordered pages containing tuples."""

    def __init__(self, schema: TupleDesc, relation_name: str = None, buffer_manager: BufferManager = None):
        """Initialize a HeapFile."""
        self.schema = schema
        self.buffer_manager = buffer_manager
        self.relation_name = relation_name
        self.first_page_id = None
        
        if relation_name is not None and buffer_manager is not None:
            # Persistent HeapFile
            self.first_page_id = HeaderPage.get_file_entry_static(buffer_manager, relation_name)
            if not self.first_page_id.is_valid():
                self.first_page_id = buffer_manager.get_new_page()
                HeaderPage.set_file_entry_static(buffer_manager, relation_name, self.first_page_id)
                first_page = HeapPage(buffer_manager.get_page(self.first_page_id), schema)
                first_page.initialise(relation_name)
                buffer_manager.unpin(self.first_page_id, True)
        else:
            # Temporary HeapFile
            ts = str(int(time.time() * 1000))
            rnd = str(100 + (int(random.random() * 100) % 100))
            self.relation_name = "tmp" + ts[-min(DatabaseConstants.MAX_TABLE_NAME_LENGTH + 6, len(ts)):]
            self.first_page_id = buffer_manager.get_new_page()
            first_page = HeapPage(buffer_manager.get_page(self.first_page_id), schema)
            first_page.initialise(self.relation_name)
            buffer_manager.unpin(self.first_page_id, True)

    def iterator(self):
        """Get an iterator over tuples in this file."""
        from python_src.access.read.heap_file_iterator import HeapFileIterator
        return HeapFileIterator(self.first_page_id, self.buffer_manager, self.schema)

    def inserter(self):
        """Get an inserter for this file."""
        from python_src.access.write.heap_file_inserter import HeapFileInserter
        return HeapFileInserter(self.first_page_id, self.buffer_manager, self.schema)

    def get_schema(self) -> TupleDesc:
        """Get the schema of this heap file."""
        return self.schema

    def print_stats(self) -> str:
        """Print statistics about this heap file."""
        return f"Relation {self.relation_name}, firstPageId {self.first_page_id.get()}, schema {hash(self.schema)}"
