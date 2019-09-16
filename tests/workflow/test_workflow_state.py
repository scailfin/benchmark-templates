# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Simple tests to ensure correctness of the workflow state classes."""

import datetime as dt
import os
import pytest

from robtmpl.workflow.state.base import (
    StateError, StatePending, StateRunning, StateSuccess, WorkflowState
)
from robtmpl.workflow.resource import FileResource

import robtmpl.util as util


class TestWorkflowStates(object):
    """Test instantiating the different workflow state classes."""

    def test_error_state(self):
        """Test creating instances of the error state class."""
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        stopped_at = started_at + dt.timedelta(seconds=10)
        state = StateError(
            created_at=created_at,
            started_at=started_at,
            stopped_at=stopped_at
        )
        assert state.is_error()
        assert not state.is_pending()
        assert not state.is_running()
        assert not state.is_success()
        assert not state.is_active()
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.stopped_at == stopped_at
        assert len(state.messages) == 0
        state = StateError(
            created_at=created_at,
            started_at=started_at,
            stopped_at=stopped_at,
            messages=['A', 'B', 'C']
        )
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.stopped_at == stopped_at
        assert len(state.messages) == 3

    def test_pending_state(self):
        """Test creating instances of the pending state class."""
        created_at = dt.datetime.now()
        state = StatePending(created_at)
        assert state.is_pending()
        assert state.is_active()
        assert not state.is_error()
        assert not state.is_running()
        assert not state.is_success()
        assert state.created_at == created_at
        running = state.start()
        assert state.created_at == running.created_at
        assert not running.started_at is None
        state = StatePending(created_at)
        error = state.error(messages=['there', 'was', 'a', 'error'])
        assert error.is_error()
        assert len(error.messages) == 4

    def test_running_state(self):
        """Test creating instances of the running state class."""
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        state = StateRunning(created_at=created_at, started_at=started_at)
        assert state.is_active()
        assert state.is_running()
        assert not state.is_pending()
        assert not state.is_error()
        assert not state.is_success()
        assert state.created_at == created_at
        assert state.started_at == started_at
        # Create an exception to get error state from running state
        error = state.error(messages=['Error', 'State'])
        assert error.created_at == state.created_at
        assert error.started_at == state.started_at
        assert len(error.messages) == 2
        assert error.messages[0] == 'Error'
        assert error.messages[1] == 'State'
        success = state.success(
            files={'myfile': FileResource('myfile', '/dev/null')}
        )
        assert success.is_success()
        assert not success.is_error()
        assert not success.is_pending()
        assert not success.is_running()
        assert not success.is_active()
        assert success.created_at == state.created_at
        assert success.started_at == state.started_at
        assert len(success.files) == 1

    def test_success_state(self, tmpdir):
        """Test creating instances of the success state class."""
        # Create new file resource for test purposes
        filename = os.path.join(str(tmpdir), 'res.json')
        util.write_object(filename=filename, obj={'A': 1})
        # Create instance of successfule workflow state without a file resource
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        finished_at = started_at + dt.timedelta(seconds=10)
        state = StateSuccess(
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at
        )
        assert state.is_success()
        assert not state.is_error()
        assert not state.is_pending()
        assert not state.is_running()
        assert not state.is_active()
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.finished_at == finished_at
        assert len(state.files) == 0
        # Create state instance with file resource
        state = StateSuccess(
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            files=[FileResource('myfile', filename)]
        )
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.finished_at == finished_at
        assert len(state.files) == 1
        # Get the file resource
        f = state.get_file('myfile')
        assert util.read_object(filename) == {'A': 1}
        f.delete()
        assert not os.path.exists(f.filename)
        # Invalid file resource lists
        with pytest.raises(ValueError):
            StateSuccess(
                created_at=created_at,
                started_at=started_at,
                finished_at=finished_at,
                files=[
                    FileResource('myfile', filename),
                    FileResource('myfile', filename)
                ]
            )
