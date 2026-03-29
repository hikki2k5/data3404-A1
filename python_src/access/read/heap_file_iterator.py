"""
Heap File Iterator for traversing a HeapFile.
"""

from python_src.access.read.data_file_iterator import DataFileIterator
from python_src.buffer.buffer_manager import BufferManager, BufferAccessException
from python_src.disk.data_page import DataPage
from python_src.heap.page_id import PageId
from python_src.heap.heap_page import HeapPage
from python_src.heap.tuple_desc import TupleDesc


class HeapFileIterator(DataFileIterator):
    """Iterator to traverse over a HeapFile."""

    def __init__(self, data_file_page: PageId, buffer_manager: BufferManager, schema: TupleDesc):
        """Initialize the HeapFileIterator."""
        super().__init__(data_file_page, buffer_manager, schema)

    def get_data_page(self, page_id: PageId) -> DataPage:
        """Get the data page for the given page ID."""
        page = self.buffer_manager.get_page(page_id)
        return HeapPage(page, self.schema)
