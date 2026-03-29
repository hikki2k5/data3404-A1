"""
Data File Iterator base class.
"""

from abc import ABC, abstractmethod
from python_src.access.read.access_iterator import AccessIterator
from python_src.buffer.buffer_manager import BufferAccessException, BufferManager
from python_src.heap.tuple_desc import TupleDesc
from python_src.heap.page_id import PageId
from python_src.heap.tuple import Tuple
from python_src.disk.data_page import DataPage


class DataFileIterator(AccessIterator, ABC):
    """Iterator to traverse a file collection of data pages."""

    def __init__(self, data_file_page: PageId, buffer_manager: BufferManager, schema: TupleDesc):
        """Initialize the DataFileIterator."""
        self.buffer_manager = buffer_manager
        self.schema = schema
        self.current_page_id = PageId(data_file_page.get())
        self.marked_page_id = PageId(data_file_page.get())
        self.page_iterator = None
        self.current_data_page = None
        
        try:
            self._advance_to_next_page()
        except BufferAccessException:
            pass

    def _advance_to_next_page(self) -> None:
        """Advance to the next page."""
        if self.current_data_page is not None:
            self.buffer_manager.unpin(self.current_page_id, False)
        
        if not self.current_page_id.is_valid():
            self.page_iterator = None
            return
        
        page = self.buffer_manager.get_page(self.current_page_id)
        self.current_data_page = self.get_data_page(self.current_page_id)
        self.page_iterator = self.current_data_page.iterator()
        
        # Get next page
        self.current_page_id = self.current_data_page.get_next_page_id()

    @abstractmethod
    def get_data_page(self, page_id: PageId) -> DataPage:
        """Get the data page for the given page ID."""
        pass

    def __iter__(self):
        """Return self as iterator."""
        return self

    def __next__(self) -> Tuple:
        """Get the next tuple."""
        if not self.has_next():
            raise StopIteration()

        return self.page_iterator.__next__()

    def has_next(self) -> bool:
        """Check if there is a next tuple."""
        if self.page_iterator is None:
            return False
        
        if self.page_iterator.has_next():
            return True
        
        # Try next page
        if self.current_page_id.is_valid():
            try:
                self._advance_to_next_page()
                return self.has_next()
            except:
                return False
        
        return False

    def get_schema(self) -> TupleDesc:
        """Get the schema of tuples."""
        return self.schema

    def close(self) -> None:
        """Close the iterator."""
        if self.current_data_page is not None:
            self.buffer_manager.unpin(self.current_page_id, False)

    def mark(self) -> None:
        """Mark the current position."""
        self.marked_page_id = PageId(self.current_page_id.get())
        if self.page_iterator is not None:
            self.marked_slot = self.page_iterator.get_slot_no()

    def reset(self) -> None:
        """Reset to the marked position."""
        self.current_page_id = PageId(self.marked_page_id.get())
        try:
            self._advance_to_next_page()
            if hasattr(self, 'marked_slot') and self.page_iterator is not None:
                self.page_iterator.set_slot(self.marked_slot)
        except BufferAccessException:
            pass
