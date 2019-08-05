"""Simple tests to ensure correctness of the workflow state classes."""

import datetime as dt
import os
import pytest

from benchtmpl.workflow.state import (
    StateError, StatePending, StateRunning, StateSuccess, WorkflowState,
    LABEL_STATE_TYPE
)
from benchtmpl.workflow.resource.base import FileResource

DIR = os.path.dirname(os.path.realpath(__file__))
LOCAL_FILE = os.path.join(DIR, '../.files/schema.json')


class TestWorkflowStates(object):
    """Test instantiating the different workflow state classes."""
    def test_deserialize_error(self):
        """Test error when deserializing document with invalid type."""
        with pytest.raises(ValueError):
            WorkflowState.from_dict({LABEL_STATE_TYPE: 'unknown'})

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
        # Test serialization and deserialization
        state = WorkflowState.from_dict(state.to_dict())
        assert state.is_error()
        assert not state.is_pending()
        assert not state.is_running()
        assert not state.is_success()
        assert not state.is_active()
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
        # Test serialization and deserialization
        state = WorkflowState.from_dict(state.to_dict())
        assert (state.is_pending())
        assert state.is_active()
        assert not state.is_error()
        assert not state.is_running()
        assert not state.is_success()
        assert state.created_at == created_at

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
        # Create an exception to get error state fromrunning state
        error = state.error(messages=['Error', 'State'])
        assert error.created_at == state.created_at
        assert error.started_at == state.started_at
        assert len(error.messages) == 2
        assert error.messages[0] == 'Error'
        assert error.messages[1] == 'State'
        success = state.success(
            resources={'myfile': FileResource('myfile', LOCAL_FILE)}
        )
        assert success.is_success()
        assert not success.is_error()
        assert not success.is_pending()
        assert not success.is_running()
        assert not success.is_active()
        assert success.created_at == state.created_at
        assert success.started_at == state.started_at
        assert len(success.resources) == 1
        # Test serialization and deserialization
        state = WorkflowState.from_dict(state.to_dict())
        assert state.is_active()
        assert state.is_running()
        assert not state.is_pending()
        assert not state.is_error()
        assert not state.is_success()
        assert state.created_at == created_at
        assert state.started_at == started_at

    def test_success_state(self):
        """Test creating instances of the success state class."""
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
        assert len(state.resources) == 0
        state = StateSuccess(
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            resources=[FileResource('myfile', LOCAL_FILE)]
        )
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.finished_at == finished_at
        assert len(state.resources) == 1
        # Test serialization and deserialization
        state = WorkflowState.from_dict(state.to_dict())
        assert state.is_success()
        assert not state.is_error()
        assert not state.is_pending()
        assert not state.is_running()
        assert not state.is_active()
        assert state.created_at == created_at
        assert state.started_at == started_at
        assert state.finished_at == finished_at
        assert len(state.resources) == 1
        # Error when passing invalid resource object
        with pytest.raises(ValueError):
            StateSuccess(
                created_at=created_at,
                started_at=started_at,
                finished_at=finished_at,
                resources=FileResource('myfile', LOCAL_FILE)
            )
