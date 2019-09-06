# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The job monitor is used to periodically poll a workflow backend for status
updates of running jobs.
"""

import time
import threading

import robtmpl.core.error as err


class JobMonitor(object):
    """The job monitor periodically checks the state of a list of running jobs.
    The monitor is associated with a benchmark engine.
    """
    def __init__(self, engine, interval=1):
        """Initialize the associated benchmark engine and the sleep interval.

        Parameters
        ----------
        engine: robtmpl.benchmark.engine.BenchmarkEngine
            Associated benchmark engine
        interval: int, optional
            Sleep interval
        """
        self.engine = engine
        self.interval = interval
        # Active jobs are maintained as a dictionary that maintains the current
        # status (value) of running jobs (key)
        self.jobs = dict()

    def add(self, run_id, state):
        """Add a new run to the monitor. This will raise a ValueError if the
        current state of the job is inactive.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        state: robtmpl.workflow.state.WorkflowState
            Current state of the workflow run

        Raises
        ------
        ValueError
        """
        # Only monitor active jobs. Raise a ValueError if the job is not active
        if not state.is_active():
            raise ValueError('cannot monitor inactive job')
        self.jobs[run_id] = state

    def poll(self):
        """The main routine of the monitor is an endless loop that periodically
        polls the backend to update the state information for monitored jobs.

        If a job status change is detected the state information for the run is
        updated in the underlying database.
        """
        while True:
            runs = self.jobs.keys()
            for run_id in runs:
                prev_state = self.jobs[run_id]
                # Get the current state for the workflow run. This may raise
                # an exception if the run is unknown to the backend (e.g., if
                # the backend is non-persistent and has been restarted).
                try:
                    state = self.engine.backend.get_state(run_id)
                except err.UnknownRunError as ex:
                    # If the run is unknown set the state to error
                    state = current_state.error(messages=[str(ex)])
                if state.type_id != prev_state.type_id:
                    self.engine.update_state(run_id=run_id, run_state=state)
                    if not state.is_active():
                        del self.jobs[run_id]
            time.sleep(self.interval)

    def run(self):
        """Start the worker thread that polls the backend for status updates."""
        thread = threading.Thread(target=self.poll, args=())
        thread.daemon = True
        thread.start()
