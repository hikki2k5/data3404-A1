"""
Header Page class for the database catalog.
"""

from simpledb.disk.page import Page
from simpledb.heap.page_id import PageId
from simpledb.main.database_constants import DatabaseConstants


class HeaderPage(Page):
    """Represents the header page containing the catalog."""

    # Offsets for positions of values in the HeaderPage
    NEXT_PAGE_INDEX = 0
    NUM_POINTERS_INDEX = 4
    HEADER_SIZE = 4 + 4
    POINTER_PAGE_ID_OFFSET = 0
    POINTER_REL_NAME_OFFSET = 4
    POINTER_ENTRY_SIZE = 4 + 2 + DatabaseConstants.MAX_TABLE_NAME_LENGTH

    def __init__(self, page: Page = None):
        """Initialize a HeaderPage."""
        if page is None:
            super().__init__()
        else:
            super().__init__(page.get_data())

    def initialise(self) -> None:
        """Initialize the HeaderPage to default values."""
        invalid_page = PageId(DatabaseConstants.INVALID_PAGE_ID)
        self.set_next_page(invalid_page)
        max_space = DatabaseConstants.PAGE_SIZE - self.HEADER_SIZE
        max_number_of_pointers = max_space // self.POINTER_ENTRY_SIZE
        self.set_num_pointers(max_number_of_pointers)
        # Initialize all records on the page
        for i in range(max_number_of_pointers):
            self.set_file_entry(invalid_page, "", i)

    def set_next_page(self, page_id: PageId) -> None:
        """Set the PageId of the next HeaderPage."""
        if page_id is None:
            raise RuntimeError("Page ID is NULL")
        self.set_integer_value(page_id.get(), self.NEXT_PAGE_INDEX)

    def get_next_page(self) -> PageId:
        """Get the PageId of the next header page."""
        page_id = self.get_integer_value(self.NEXT_PAGE_INDEX)
        return PageId(page_id)

    def set_num_pointers(self, value: int) -> None:
        """Set the maximum number of pointers in the page."""
        self.set_integer_value(value, self.NUM_POINTERS_INDEX)

    def get_num_pointers(self) -> int:
        """Get the maximum number of pointers that can be stored on this page."""
        return self.get_integer_value(self.NUM_POINTERS_INDEX)

    def set_file_entry(self, page_id: PageId, entry: str, record_number: int) -> None:
        """Create an entry in this page of (pageId, entryText)."""
        assert len(entry) <= DatabaseConstants.MAX_TABLE_NAME_LENGTH
        assert 0 <= record_number < self.get_num_pointers()

        offset = self.HEADER_SIZE + record_number * self.POINTER_ENTRY_SIZE
        self.set_integer_value(page_id.get(), offset + self.POINTER_PAGE_ID_OFFSET)
        self.set_string_value(entry, offset + self.POINTER_REL_NAME_OFFSET)

    def get_file_entry(self, record_number: int, empty_page: PageId) -> str:
        """Get the (pageId, entryText) entry associated with the record number."""
        assert 0 <= record_number < self.get_num_pointers()

        offset = self.HEADER_SIZE + record_number * self.POINTER_ENTRY_SIZE
        empty_page.set(self.get_integer_value(offset + self.POINTER_PAGE_ID_OFFSET))
        return self.get_string_value(offset + self.POINTER_REL_NAME_OFFSET)

    @staticmethod
    def get_file_entry_static(buffer_manager, entry: str) -> PageId:
        """Get the file entry from the header page."""
        if len(entry) > DatabaseConstants.MAX_TABLE_NAME_LENGTH:
            raise AssertionError("Entry cannot be longer than specified value")

        current_page_id = PageId(DatabaseConstants.FIRST_PAGE_ID)
        temp_page_id = PageId()
        
        while current_page_id.is_valid():
            hpage = HeaderPage(buffer_manager.get_page(current_page_id))
            num_records = hpage.get_num_pointers()
            for i in range(num_records):
                entry_name = hpage.get_file_entry(i, temp_page_id)
                if entry_name == entry and temp_page_id.is_valid():
                    buffer_manager.unpin(current_page_id, False)
                    return temp_page_id
            
            temp_page_id = current_page_id
            current_page_id = hpage.get_next_page()
            buffer_manager.unpin(temp_page_id, False)
        
        return PageId(DatabaseConstants.INVALID_PAGE_ID)

    @staticmethod
    def set_file_entry_static(buffer_manager, entry: str, page_id: PageId) -> None:
        """Put a file entry in the header page."""
        if len(entry) > DatabaseConstants.MAX_TABLE_NAME_LENGTH:
            raise AssertionError("Entry cannot be longer than specified value")

        if not (page_id.is_valid() and page_id.get() < buffer_manager.get_total_disk_pages()):
            raise AssertionError("Expects PageId to exist")

        if HeaderPage.get_file_entry_static(buffer_manager, entry).is_valid():
            raise AssertionError("File Entry Already Exists")

        current_page_id = PageId(DatabaseConstants.FIRST_PAGE_ID)
        temp_page_id = PageId()
        
        while current_page_id.is_valid():
            hpage = HeaderPage(buffer_manager.get_page(current_page_id))
            num_records = hpage.get_num_pointers()
            for i in range(num_records):
                hpage.get_file_entry(i, temp_page_id)
                if not temp_page_id.is_valid():
                    hpage.set_file_entry(page_id, entry, i)
                    buffer_manager.unpin(current_page_id, True)
                    buffer_manager.flush_dirty()
                    return
            
            temp_page_id = current_page_id
            current_page_id = hpage.get_next_page()
            buffer_manager.unpin(temp_page_id, False)
        
        # If we reach here, no space on any page, create new page
        new_page_id = buffer_manager.get_new_page()
        new_page = HeaderPage(buffer_manager.get_page(new_page_id))
        new_page.initialise()
        new_page.set_file_entry(page_id, entry, 0)
        buffer_manager.unpin(new_page_id, True)
        buffer_manager.flush_dirty()
