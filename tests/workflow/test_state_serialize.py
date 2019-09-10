# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test serialization/deserialization methods for workflow states."""

import pytest

from robtmpl.workflow.resource import FileResource

import robtmpl.core.util as util
import robtmpl.workflow.state.base as state
import robtmpl.workflow.state.serializer as serialize


"""Default timestamps."""
CREATED_AT = '2019-09-15T11:23:19'
FINISHED_AT = '2019-10-05T08:17:09'
STARTED_AT = '2019-09-16T11:46:31'

class TestWorkflowStateSerializer(object):
    """Unit tests for the serialize/deserialize methods for workflow states."""
    def test_error_state(self):
        """Test serialization/deserialization of error states."""
        s = state.StateError(
            created_at=util.to_datetime(CREATED_AT),
            started_at=util.to_datetime(STARTED_AT),
            stopped_at=util.to_datetime(FINISHED_AT),
            messages=['there', 'were', 'errors']
        )
        s = serialize.deserialize_state(serialize.serialize_state(s))
        assert s.is_error()
        assert s.messages == ['there', 'were', 'errors']
        self.validate_date(s.created_at, util.to_datetime(CREATED_AT))
        self.validate_date(s.started_at, util.to_datetime(STARTED_AT))
        self.validate_date(s.stopped_at, util.to_datetime(FINISHED_AT))

    def test_invalid_object(self):
        """Ensure there is an error if an object with an unknown state
        type is given.
        """
        with pytest.raises(KeyError):
            serialize.deserialize_state({
                serialize.LABEL_STATE_TYPE: 'unknown'
            })
        with pytest.raises(ValueError):
            serialize.deserialize_state({
                serialize.LABEL_STATE_TYPE: 'unknown',
                serialize.LABEL_CREATED_AT: CREATED_AT
            })

    def test_pending_state(self):
        """Test serialization/deserialization of pending states."""
        s = state.StatePending(created_at=util.to_datetime(CREATED_AT))
        s = serialize.deserialize_state(serialize.serialize_state(s))
        assert s.is_pending()
        self.validate_date(s.created_at, util.to_datetime(CREATED_AT))

    def test_running_state(self):
        """Test serialization/deserialization of running states."""
        s = state.StateRunning(
            created_at=util.to_datetime(CREATED_AT),
            started_at=util.to_datetime(STARTED_AT)
        )
        s = serialize.deserialize_state(serialize.serialize_state(s))
        assert s.is_running()
        self.validate_date(s.created_at, util.to_datetime(CREATED_AT))
        self.validate_date(s.started_at, util.to_datetime(STARTED_AT))

    def test_success_state(self):
        """Test serialization/deserialization of success states."""
        s = state.StateSuccess(
            created_at=util.to_datetime(CREATED_AT),
            started_at=util.to_datetime(STARTED_AT),
            finished_at=util.to_datetime(FINISHED_AT),
            files=[
                FileResource('myfile1', 'dev/null/myfile1'),
                FileResource('myfile2', 'dev/null/myfile2')
            ]
        )
        s = serialize.deserialize_state(serialize.serialize_state(s))
        assert s.is_success()
        assert s.get_file('myfile1').filename == 'dev/null/myfile1'
        assert s.get_file('myfile2').filename == 'dev/null/myfile2'
        self.validate_date(s.created_at, util.to_datetime(CREATED_AT))
        self.validate_date(s.started_at, util.to_datetime(STARTED_AT))
        self.validate_date(s.finished_at, util.to_datetime(FINISHED_AT))

    def validate_date(self, dt, ts):
        """Ensure that the given datetime is matches the given timestamp."""
        assert dt.year == ts.year
        assert dt.month == ts.month
        assert dt.day == ts.day
        assert dt.hour == ts.hour
        assert dt.minute == ts.minute
        assert dt.second == ts.second
