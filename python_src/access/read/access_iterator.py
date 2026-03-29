"""
Generic Iterator Class for Access Patterns.
"""

from abc import ABC, abstractmethod
from typing import Iterator
from python_src.heap.tuple import Tuple
from python_src.heap.tuple_desc import TupleDesc
from python_src.buffer.buffer_manager import BufferAccessException


class AccessIterator(ABC, Iterator):
    """Generic Iterator Class for database access patterns."""

    @abstractmethod
    def close(self) -> None:
        """Close the iterator and release resources."""
        pass

    @abstractmethod
    def get_schema(self) -> TupleDesc:
        """Get the schema of tuples produced by this iterator."""
        pass

    def remove(self) -> None:
        """Remove operation is not supported."""
        raise UnsupportedOperationError()

    @abstractmethod
    def mark(self) -> None:
        """Update the marked position to the current position."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Return to previously marked position."""
        pass

    @abstractmethod
    def __has_next__(self) -> bool:
        """Check if there is a next element."""
        pass

    @abstractmethod
    def __next__(self) -> Tuple:
        """Get the next tuple."""
        pass
