# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Definition of workflow states. The classes in this module represent the
different possible states of a workflow run. There are four different states:
(PENDING) the workflow run has been submitted and is waiting to start running,
(RUNNING) the workflow is actively executing at the moment,
(ERROR) workflow execution was interrupted by an error or canceled by the user,
(SUCCESS) the workflow run completed successfully.
"""

from datetime import datetime

import traceback

from benchtmpl.workflow.resource.base import ResourceDescriptor

import benchtmpl.util.core as util


"""Definition of state type identifier."""
STATE_ERROR = 'ERROR'
STATE_PENDING = 'PENDING'
STATE_RUNNING = 'RUNNING'
STATE_SUCCESS = 'SUCCESS'


"""Labels for serialization."""
LABEL_CREATED_AT = 'createdAt'
LABEL_FINISHED_AT = 'finishedAt'
LABEL_MESSAGES = 'messages'
LABEL_RESOURCES = 'resources'
LABEL_STARTED_AT = 'startedAt'
LABEL_STATE_TYPE = 'type'
LABEL_STOPPED_AT = 'stoppedAt'


class WorkflowState(object):
    """The base class for workflow states contains the state type identifier
    that is used by the different state type methods. The state also maintains
    the timestamp of workflow run creation. Subclasses will add additional
    timestamps and properties.
    """
    def __init__(self, type_id, created_at=None):
        """Initialize the type identifier and the 'created at' timestamp.

        Parameters
        ----------
        type_id: string
            Type identifier
        """
        self.type_id = type_id
        self.created_at = created_at if not created_at is None else datetime.now()

    @staticmethod
    def from_dict(doc):
        """Get instance of a workflow state from a dictionary serialization as
        created by the to_dict() method of the sub-types.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a workflow state

        Returns
        -------
        benchtmpl.workflow.state.WorkflowState

        Raises
        ------
        KeyError
        ValueError
        """
        type_id = doc[LABEL_STATE_TYPE]
        if type_id == STATE_PENDING:
            return StatePending.from_dict(doc)
        elif type_id == STATE_RUNNING:
            return StateRunning.from_dict(doc)
        elif type_id == STATE_ERROR:
            return StateError.from_dict(doc)
        elif type_id == STATE_SUCCESS:
            return StateSuccess.from_dict(doc)
        else:
            raise ValueError('invalid state type \'{}\''.format(type_id))

    def is_active(self):
        """A workflow is in active state if it is either pending or running.

        Returns
        --------
        bool
        """
        return self.type_id in [STATE_PENDING, STATE_RUNNING]

    def is_error(self):
        """Returns True if the workflow state is of type ERROR.

        Returns
        -------
        bool
        """
        return self.type_id == STATE_ERROR

    def is_pending(self):
        """Returns True if the workflow state is of type PENDING.

        Returns
        -------
        bool
        """
        return self.type_id == STATE_PENDING

    def is_running(self):
        """Returns True if the workflow state is of type RUNNING.

        Returns
        -------
        bool
        """
        return self.type_id == STATE_RUNNING

    def is_success(self):
        """Returns True if the workflow state is of type SUCCESS.

        Returns
        -------
        bool
        """
        return self.type_id == STATE_SUCCESS

    def to_dict(self):
        """Get dictionary serialization for the workflow state.

        Returns
        -------
        dict
        """
        return {
            LABEL_STATE_TYPE: self.type_id,
            LABEL_CREATED_AT: self.created_at.isoformat()
        }


class StateError(WorkflowState):
    """Error state representation for a workflow run. The workflow has three
    timestamps: the workflow creation time, workflow run start time and the
    time at which the error occured (ot workflow was canceled). The state also
    maintains an optional list of error messages.
    """
    def __init__(self, created_at, started_at, stopped_at=None, messages=None):
        """Initialize the timestamps that are associated with the workflow
        state and the optional error messages.

        Parameters
        ----------
        created_at: datetime.datetime
            Timestamp of workflow creation
        started_at: datetime.datetime
            Timestamp when the workflow started running
        stopped_at: datetime.datetime, optional
            Timestamp when workflow error occurred or the when the workflow was
            canceled
        messages: list(string), optional
            Optional list of error messages
        """
        super(StateError, self).__init__(
            type_id=STATE_ERROR,
            created_at=created_at
        )
        self.started_at = started_at
        self.stopped_at = stopped_at if not stopped_at is None else datetime.now()
        self.messages = messages if not messages is None else list()

    @staticmethod
    def from_dict(doc):
        """Get instance of a error workflow state from a dictionary
        serialization.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a error workflow state

        Returns
        -------
        benchtmpl.workflow.state.StateError

        Raises
        ------
        KeyError
        """
        return StateError(
            created_at=util.to_datetime(doc[LABEL_CREATED_AT]),
            started_at=util.to_datetime(doc[LABEL_STARTED_AT]),
            stopped_at=util.to_datetime(doc[LABEL_STOPPED_AT]),
            messages=doc[LABEL_MESSAGES]
        )

    def to_dict(self):
        """Get dictionary serialization for the workflow state. Extends the base
        serialization with start and stop timestamps, and potential error
        messages.

        Returns
        -------
        dict
        """
        obj = super(StateError, self).to_dict()
        obj[LABEL_STARTED_AT] = self.started_at.isoformat()
        obj[LABEL_STOPPED_AT] = self.stopped_at.isoformat()
        obj[LABEL_MESSAGES] = self.messages
        return obj


class StatePending(WorkflowState):
    """State representation for a pending workflow that is waiting to start
    running. The workflow has only one timestamp representing the workflow
    creation time.
    """
    def __init__(self, created_at=None):
        """Initialize the timestamp that is associated with the workflow state.

        Parameters
        ----------
        created_at: datetime.datetime, optional
            Timestamp of workflow creation
        """
        super(StatePending, self).__init__(
            type_id=STATE_PENDING,
            created_at=created_at
        )

    @staticmethod
    def from_dict(doc):
        """Get instance of a pending workflow state from a dictionary
        serialization.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a pending workflow state

        Returns
        -------
        benchtmpl.workflow.state.StatePending

        Raises
        ------
        KeyError
        """
        return StatePending(created_at=util.to_datetime(doc[LABEL_CREATED_AT]))

    def error(self, messages=None):
        """Get instance of error state for a pending wokflow. If the exception
        that caused the workflow execution to terminate is given it will be used
        to create the list of error messages.

        Since the workflow did not start to run the started_at timestamp is set
        to the current time just like the stopped_at timestamp.

        Parameters
        ----------
        messages: list(string), optional
            Optional list of error messages

        Returns
        -------
        benchtmpl.workflow.state.StateError
        """
        ts = datetime.now()
        return StateError(
            created_at=self.created_at,
            started_at=ts,
            stopped_at=ts,
            messages=messages
        )

    def start(self):
        """Get instance of running state with the same create at timestamp as
        this state and the started at with the current timestamp.

        Returns
        -------
        benchtmpl.workflow.state.StateRunning
        """
        return StateRunning(created_at=self.created_at)


class StateRunning(WorkflowState):
    """State representation for a active workflow run. The workflow has two
    timestamps: the workflow creation time and the workflow run start time.
    """
    def __init__(self, created_at, started_at=None):
        """Initialize the timestamps that are associated with the workflow
        state.

        Parameters
        ----------
        created_at: datetime.datetime
            Timestamp of workflow creation
        started_at: datetime.datetime
            Timestamp when the workflow started running
        """
        super(StateRunning, self).__init__(
            type_id=STATE_RUNNING,
            created_at=created_at
        )
        self.started_at = started_at if not started_at is None else datetime.now()

    def error(self, messages=None):
        """Get instance of error state for a running wokflow. If the exception
        that caused the workflow execution to terminate is given it will be used
        to create the list of error messages.

        Parameters
        ----------
        messages: list(string), optional
            Optional list of error messages

        Returns
        -------
        benchtmpl.workflow.state.StateError
        """
        return StateError(
            created_at=self.created_at,
            started_at=self.started_at,
            messages=messages
        )

    @staticmethod
    def from_dict(doc):
        """Get instance of a running workflow state from a dictionary
        serialization.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a running workflow state

        Returns
        -------
        benchtmpl.workflow.state.StateRunning

        Raises
        ------
        KeyError
        """
        return StateRunning(
            created_at=util.to_datetime(doc[LABEL_CREATED_AT]),
            started_at=util.to_datetime(doc[LABEL_STARTED_AT])
        )

    def success(self, resources=None):
        """Get instance of success state for a competed wokflow.

        Parameters
        ----------
        resources: dict(benchtmpl.workflow.resource.ResourceDescriptor), optional
            Optional dictionary of created resources

        Returns
        -------
        benchtmpl.workflow.state.StateSuccess
        """
        return StateSuccess(
            created_at=self.created_at,
            started_at=self.started_at,
            resources=resources
        )

    def to_dict(self):
        """Get dictionary serialization for the workflow state. Extends the base
        serialization with the start timestamp.

        Returns
        -------
        dict
        """
        obj = super(StateRunning, self).to_dict()
        obj[LABEL_STARTED_AT] = self.started_at.isoformat()
        return obj


class StateSuccess(WorkflowState):
    """Success state representation for a workflow run. The workflow has three
    timestamps: the workflow creation time, workflow run start time and the
    time when the workflow execution finished. The state also maintains handles
    to any resources that were created by the workflow run.
    """
    def __init__(self, created_at, started_at, finished_at=None, resources=None):
        """Initialize the timestamps that are associated with the workflow
        state and the set of created resources.

        Parameters
        ----------
        created_at: datetime.datetime
            Timestamp of workflow creation
        started_at: datetime.datetime
            Timestamp when the workflow started running
        finished_at: datetime.datetime, optional
            Timestamp when workflow execution completed
        resources: dict(benchtmpl.workflow.resource.ResourceDescriptor), optional
            Optional dictionary of created resources

        Raises
        ------
        ValueError
        """
        super(StateSuccess, self).__init__(
            type_id=STATE_SUCCESS,
            created_at=created_at
        )
        self.started_at = started_at
        self.finished_at = finished_at if not finished_at is None else datetime.now()
        if not resources is None:
            if isinstance(resources, dict):
                self.resources = resources
            elif isinstance(resources, list):
                self.resources = dict()
                for res in resources:
                    self.resources[res.identifier] = res
            else:
                raise ValueError('invalid data type for resources')
        else:
            self.resources = dict()

    @staticmethod
    def from_dict(doc):
        """Get instance of a success workflow state from a dictionary
        serialization.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a success workflow state

        Returns
        -------
        benchtmpl.workflow.state.StateSuccess

        Raises
        ------
        KeyError
        """
        resources = dict()
        if LABEL_RESOURCES in doc:
            for res in doc[LABEL_RESOURCES]:
                desc = ResourceDescriptor.from_dict(res)
                resources[desc.identifier] = desc
        return StateSuccess(
            created_at=util.to_datetime(doc[LABEL_CREATED_AT]),
            started_at=util.to_datetime(doc[LABEL_STARTED_AT]),
            finished_at=util.to_datetime(doc[LABEL_FINISHED_AT]),
            resources=resources
        )

    def to_dict(self):
        """Get dictionary serialization for the workflow state. Extends the base
        serialization with start and finished timestamps, and potential result
        resources.

        Returns
        -------
        dict
        """
        obj = super(StateSuccess, self).to_dict()
        obj[LABEL_STARTED_AT] = self.started_at.isoformat()
        obj[LABEL_FINISHED_AT] = self.finished_at.isoformat()
        obj[LABEL_RESOURCES] = [r.to_dict() for r in self.resources.values()]
        return obj
