"""Progress Display Utility Module

This module provides a spinner-based progress display for console applications,
supporting animated task status updates with completion indicators.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import sys
import threading
import time
from typing import Optional, Dict


class ProgressDisplay:
    """Animated progress display for console applications.

    Provides a spinning animation with task status updates and automatic
    verb tense conversion for completion messages.

    Attributes:
        VERB_MAPPING (Dict[str, str]): Maps present to past tense verbs
        animation (List[str]): Unicode spinner animation frames
        idx (int): Current animation frame index
        current_task (str): Description of current task
        stop (bool): Flag to stop animation thread
        last_task (Optional[str]): Previous task for completion message
        _animation_thread (Optional[threading.Thread]): Animation thread
    """

    VERB_MAPPING = {
        "Fetching": "Fetched",
        "Summarizing": "Summarized",
        "Generating": "Generated",
        "Creating": "Created"
    }

    def __init__(self):
        """Initialize progress display with default spinner animation."""
        self.animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.idx = 0
        self.current_task = ""
        self.stop = False
        self.last_task = None
        self._animation_thread: Optional[threading.Thread] = None

    def update_task(self, task: str) -> None:
        """Update the current task and display completion message for a previous task.

        Args:
            task (str): Description of a new task.
            Empty string clears display.

        Note:
            Automatically converts present tense verbs to past tense for
            completion messages using VERB_MAPPING.
        """
        if self.last_task:
            sys.stdout.write('\r' + ' ' * 80 + '\r')

            completed_task = self.last_task
            for present, past in self.VERB_MAPPING.items():
                if completed_task.startswith(present):
                    completed_task = completed_task.replace(present, past)
                    break
            print(f"✓ {completed_task}")

        if task:
            self.current_task = task
            sys.stdout.write(f"⠋ {task}")
            sys.stdout.flush()

        self.last_task = task

    def animate(self) -> None:
        """Animate the spinner while a task is in progress.

        Continuously updates the spinner frame until a stop flag is set.
        Runs in a separate thread started by start().
        """
        while not self.stop:
            if self.current_task:
                spinner = self.animation[self.idx % len(self.animation)]
                sys.stdout.write('\r')
                sys.stdout.write(f"{spinner} {self.current_task}")
                sys.stdout.flush()
            time.sleep(0.1)
            self.idx += 1

    def start(self) -> None:
        """Start the progress animation in a daemon thread."""
        self._animation_thread = threading.Thread(target=self.animate)
        self._animation_thread.daemon = True
        self._animation_thread.start()

    def stop_and_join(self) -> None:
        """Stop the animation and wait for the thread to complete.

        Sets stop flag and blocks until the animation thread terminates.
        Should be called before program exit to ensure a clean shutdown.
        """
        self.stop = True
        if self._animation_thread:
            self._animation_thread.join()
