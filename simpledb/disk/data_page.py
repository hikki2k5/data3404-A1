"""
Data Page class for storing records on disk.
"""

from simpledb.main.database_constants import DatabaseConstants
from simpledb.disk.page import Page
from simpledb.heap.page_id import PageId
from simpledb.heap.tuple import Tuple
from simpledb.main.catalog.type import Type
from simpledb.main.catalog.tuple_desc import TupleDesc


class DataPage(Page):
    """Abstract Data Page class for storing records."""

    # Positions (as byte offsets) of header fields within page
    PREV_PAGE_POS = 0
    NEXT_PAGE_POS = 4
    RECORD_COUNT_POS = 8
    RELATION_NAME_POS = 12
    RECORD_START_POS = RELATION_NAME_POS + 2 + DatabaseConstants.MAX_TABLE_NAME_LENGTH

    def initialise(self, relation_name: str) -> None:
        """Initialize the page with the given schema."""
        invalid = PageId(DatabaseConstants.INVALID_PAGE_ID)
        self.set_previous_page_id(invalid)
        self.set_next_page_id(invalid)
        self.set_record_count(0)
        self.set_relation_name(relation_name)

    def get_previous_page_id(self) -> PageId:
        """Get the PageId of the previous page."""
        return PageId(self.get_integer_value(self.PREV_PAGE_POS))

    def set_previous_page_id(self, previous: PageId) -> None:
        """Set the PageId of the previous page."""
        self.set_integer_value(previous.get(), self.PREV_PAGE_POS)

    def get_next_page_id(self) -> PageId:
        """Get the PageId of the next page."""
        return PageId(self.get_integer_value(self.NEXT_PAGE_POS))

    def set_next_page_id(self, next_page: PageId) -> None:
        """Set the PageId of the next page."""
        self.set_integer_value(next_page.get(), self.NEXT_PAGE_POS)

    def get_record_count(self) -> int:
        """Get the number of records currently stored on the page."""
        return self.get_integer_value(self.RECORD_COUNT_POS)

    def set_record_count(self, count: int) -> None:
        """Set the number of records currently stored on the page."""
        self.set_integer_value(count, self.RECORD_COUNT_POS)

    def set_relation_name(self, name: str) -> None:
        """Set the name of the relation used by this page."""
        self.set_string_value(name, self.RELATION_NAME_POS)

    def get_relation_name(self) -> str:
        """Get the name of the relation used by this page."""
        return self.get_string_value(self.RELATION_NAME_POS)

    def insert_record_auto(self, record: Tuple) -> bool:
        """Insert a record into the next available slot."""
        next_slot = self.get_record_count()
        if next_slot >= self.get_max_records_on_page(record):
            return False
        self.insert_record(next_slot, record)
        self.set_record_count(next_slot + 1)
        return True

    def insert_record(self, slot_no: int, record: Tuple) -> None:
        """Insert a record into the specified slot."""
        offset = self.RECORD_START_POS + slot_no * record.get_schema().get_max_tuple_length()
        self._write(record, offset)

    def get_record(self, slot_no: int, record: Tuple) -> None:
        """Read the record at position slot_no from the page."""
        offset = self.RECORD_START_POS + slot_no * record.get_schema().get_max_tuple_length()
        self._read(record, offset)
        record.set_slot_id(slot_no)

    @staticmethod
    def get_max_records_on_page(record_or_schema) -> int:
        """Get the maximum number of records that can fit on the page."""
        if isinstance(record_or_schema, Tuple):
            schema = record_or_schema.get_schema()
        else:
            schema = record_or_schema
        return (DatabaseConstants.PAGE_SIZE - DataPage.RECORD_START_POS) // schema.get_max_tuple_length()

    def _write(self, tuple_obj: Tuple, offset: int) -> None:
        """Low-level: Write the tuple to the given offset in the page."""
        schema = tuple_obj.get_schema()
        length = schema.get_num_fields()
        for i in range(length):
            column_type = schema.get_field_type(i)
            value = tuple_obj.get_column(i)

            if column_type == Type.STRING:
                self.set_string_value(value, offset)
            elif column_type == Type.INTEGER:
                self.set_integer_value(value, offset)
            elif column_type == Type.DOUBLE:
                self.set_double_value(value, offset)
            elif column_type == Type.BOOLEAN:
                self.set_boolean_value(value, offset)
            else:
                raise AssertionError("Invalid column type")

            offset += column_type.get_len()

    def _read(self, tuple_obj: Tuple, offset: int) -> None:
        """Low-level: Read a tuple from the page starting at the offset."""
        schema = tuple_obj.get_schema()
        length = schema.get_num_fields()
        for i in range(length):
            column_type = schema.get_field_type(i)
            
            if column_type == Type.STRING:
                value = self.get_string_value(offset)
            elif column_type == Type.INTEGER:
                value = self.get_integer_value(offset)
            elif column_type == Type.DOUBLE:
                value = self.get_double_value(offset)
            elif column_type == Type.BOOLEAN:
                value = self.get_boolean_value(offset)
            else:
                raise AssertionError("Invalid column type")

            tuple_obj.set_column(i, value)
            offset += column_type.get_len()
