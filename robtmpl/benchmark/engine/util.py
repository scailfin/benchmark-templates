# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper classes and methods for the benchmark engine."""

import robtmpl.core.util as util
import robtmpl.workflow.state as state


def run_state(row):
    """Factory method to create instances of states for workflow runs from
    the values that are stored in the run table of the underlying database.

    Raises ValueError if an invalid type identifier is given.

    Note that the database only maintains timestamp information. All additional
    resources, i.e., for success and error states, are not contained in the
    database and therefore not in the returned state instance.

    Parameters
    ----------
    row: dict
        Values for a row in the benchmark_run table

    Returns
    -------
    robtmpl.workflow.state.WorkflowState

    Raises
    ------
    ValueError
    """
    type_id = rs['state'],
    created_at = rs['created_at'],
    started_at = rs['started_at'],
    ended_at = rs['ended_at']
    if type_id == state.STATE_PENDING:
        return state.StatePending(created_at=util.to_datetime(created_at))
    elif type_id == state.STATE_RUNNING:
        return state.StateRunning(
            created_at=util.to_datetime(created_at),
            started_at=util.to_datetime(started_at)
        )
    elif type_id == state.STATE_ERROR:
        return state.StateError(
            created_at=util.to_datetime(created_at),
            started_at=util.to_datetime(started_at),
            stopped_at=util.to_datetime(ended_at)
        )
    elif type_id == state.STATE_SUCCESS:
        return state.StateSuccess(
            created_at=util.to_datetime(created_at),
            started_at=util.to_datetime(started_at),
            finished_at=util.to_datetime(ended_at)
        )
    else:
        raise ValueError('invalid state \'{}\''.format(type_id))
