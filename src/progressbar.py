"""Receive and report data about current state of execution."""

import time

from utiltext import translate


class _ProgressBar:
    """Carry and report info on current status of execution."""

    def __init__(self):
        """Initialize progress bar."""
        # Stage is a text description of the current goal.
        self.current_stage = "Initializing"
        # Step is a single operation.
        self.current_step = 1
        # Steps to complete stage
        self.max_step = 1
        # Start times
        self.start_time = 0
        # Flag to start/stop reporting
        self.reporting = False

    def report_progress(self):
        """Print current task status."""
        while self.reporting:
            # Get the current time relative to start of program execution
            current_time = time.time() - self.start_time
            percentage_complete = round(self.current_step / self.max_step * 100, 2)
            percentage_complete = str(percentage_complete).rjust(5, " ")
            # Print message
            print(
                translate.text(
                    f"{int(current_time)}s: [{self.current_stage}] "
                    f"{percentage_complete}% complete "
                    f"({self.current_step} / {self.max_step} tasks)"
                )
            )
            # Wait 1 second between reports.
            # Subtract the time it takes to run this function and switch threads.
            time.sleep(1 - (current_time % 1))

    def start_progress_bar(self):
        """Start reporting."""
        self.reporting = True
        self.start_time = time.time()
        self.report_progress()

    def end_progress_bar(self):
        """End reporting."""
        self.reporting = False

    def start_new_stage(self, stage_text, max_steps):
        """Set a new series of tasks."""
        self.current_stage = stage_text
        self.max_step = int(max_steps)
        self.current_step = 0

    def set_step(self, step):
        """Set completed tasks to input value."""
        self.current_step = int(step)

    def update_step(self):
        """Increment completed tasks by one."""
        self.current_step += 1


# Shared instance of class
progressbar = _ProgressBar()
