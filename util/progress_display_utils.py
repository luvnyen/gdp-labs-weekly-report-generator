import sys
import time
import threading

class ProgressDisplay:
    def __init__(self):
        self.animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.idx = 0
        self.current_task = ""
        self.stop = False
        self.last_task = None
        self._animation_thread = None

    def update_task(self, task):
        if self.last_task:
            # Move to start of line and clear it
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            # Print completed task with proper past tense conversion
            completed_task = self.last_task
            if completed_task.startswith("Fetching"):
                completed_task = completed_task.replace("Fetching", "Fetched")
            elif completed_task.startswith("Summarizing"):
                completed_task = completed_task.replace("Summarizing", "Summarized")
            elif completed_task.startswith("Generating"):
                completed_task = completed_task.replace("Generating", "Generated")
            print(f"✓ {completed_task}")

        if task:
            self.current_task = task
            # Print a new task
            sys.stdout.write(f"⠋ {task}")
            sys.stdout.flush()

        self.last_task = task

    def animate(self):
        while not self.stop:
            if self.current_task:
                spinner = self.animation[self.idx % len(self.animation)]
                # Move to start of line
                sys.stdout.write('\r')
                # Print spinner and task
                sys.stdout.write(f"{spinner} {self.current_task}")
                sys.stdout.flush()
            time.sleep(0.1)
            self.idx += 1

    def start(self):
        """Start the progress animation in a separate thread"""
        self._animation_thread = threading.Thread(target=self.animate)
        self._animation_thread.daemon = True
        self._animation_thread.start()

    def stop_and_join(self):
        """Stop the animation and wait for the thread to complete"""
        self.stop = True
        if self._animation_thread:
            self._animation_thread.join()