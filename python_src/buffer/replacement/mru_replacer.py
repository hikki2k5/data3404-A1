"""
MRU (Most Recently Used) Replacer implementation.
"""

from typing import List
from python_src.buffer.buffer_frame import BufferFrame, AllBufferFramesPinnedException
from python_src.buffer.replacement.replacer import Replacer


class MruReplacer(Replacer):
    """Most Recently Used replacement policy."""

    def get_name(self) -> str:
        """Get the name of the replacement policy."""
        return "MRU"

    def choose(self, pool: List[BufferFrame]) -> BufferFrame:
        """Choose the most recently used frame to replace."""
        # Find the frame that was least recently used (but not pinned)
        least_recently_used = None
        
        for frame in pool:
            if not frame.is_pinned():
                if least_recently_used is None:
                    least_recently_used = frame
                elif frame.get_clock_count() < least_recently_used.get_clock_count():
                    least_recently_used = frame
        
        if least_recently_used is None:
            raise AllBufferFramesPinnedException()
        
        return least_recently_used

    def notify(self, pool: List[BufferFrame], frame: BufferFrame) -> None:
        """Update the replacement policy when a frame is accessed."""
        # Increment clock count for accessed frame to mark it as more recently used
        frame.set_clock_count(frame.get_clock_count() + 1)
