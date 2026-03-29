"""
Heap Page class representing a page full of records.
"""

from python_src.disk.data_page import DataPage
from python_src.disk.page import Page
from python_src.heap.tuple_desc import TupleDesc


class HeapPage(DataPage):
    """Represents a page full of records."""

    def __init__(self, page: Page, schema: TupleDesc):
        """Initialize a HeapPage."""
        self.data = bytearray(page.get_data())
        self.schema = schema

    def iterator(self):
        """Get an iterator over tuples in this page."""
        from python_src.access.read.data_page_iterator import DataPageIterator
        return DataPageIterator(self, self.schema)
