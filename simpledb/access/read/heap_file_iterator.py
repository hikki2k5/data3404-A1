"""
Heap File Iterator for traversing a HeapFile.
"""

from simpledb.access.read.data_file_iterator import DataFileIterator
from simpledb.buffer.buffer_manager import BufferManager, BufferAccessException
from simpledb.disk.data_page import DataPage
from simpledb.heap.page_id import PageId
from simpledb.heap.heap_page import HeapPage
from simpledb.main.catalog.tuple_desc import TupleDesc


class HeapFileIterator(DataFileIterator):
    """Iterator to traverse over a HeapFile."""

    def __init__(self, data_file_page: PageId, buffer_manager: BufferManager, schema: TupleDesc):
        """Initialize the HeapFileIterator."""
        super().__init__(data_file_page, buffer_manager, schema)

    def get_data_page(self, page_id: PageId) -> DataPage:
        """Get the data page for the given page ID."""
        page = self.buffer_manager.get_page(page_id)
        return HeapPage(page, self.schema)
