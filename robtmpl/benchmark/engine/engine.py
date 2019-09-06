# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Benchmark engine executes and monitors benchmarks runs. Information about
individual runs is maintained in a relational database.
"""

import os

from robtmpl.benchmark.monitor import JobMonitor

import robtmpl.core.util as util
import robtmpl.benchmark.util as benchutil
import robtmpl.workflow.state as state


class BenchmarkEngine(object):
    """Benchmark engine to execute benchmark workflows for a given set of
    argument values. All workflows are executed by a given workflow engine.

    The engine has a monitor running in the background that periodically polls
    the workflow engine to update the status of running rub.

    Information about runs are stored in the following table in the underlying
    database:

        CREATE TABLE benchmark_run(
            run_id CHAR(32) NOT NULL,
            submission_id CHAR(32) NOT NULL,
            state VARCHAR(8) NOT NULL,
            created_at CHAR(26) NOT NULL,
            started_at CHAR(26),
            ended_at CHAR(26),
            PRIMARY KEY(run_id)
        );

    """
    def __init__(self, connector, repository, backend, interval=None):
        """Initialize the database connector, the workflow execution backend,
        and the job monitor.

        The sleep inteval for the job monitor is initialized from the respective
        environment variable if no value is given.

        Parameters
        ----------
        connector: robtmpl.core.db.base.DatabaseConnector
            Connector for openning connections to the underlying database
        backend: robtmpl.workflow.engine.WorkflowEngine
            Workflow engine that is used to run benchmarks
        interval: int, optional
            Sleep interval for the job monitor
        """
        self.connector = connector
        self.repo = repository
        self.backend = backend
        self.monitor = JobMonitor(
            backend=self,
            interval=config.MONITOR_INTERVAL(interval)
        )
        # Read information for active jobs from the database
        with connector.connect() as con:
            rs = con.execute(
                'SELECT * FROM benchmark_run WHERE state IN(?, ?)',
                (state.STATE_PENDING, state.STATE_RUNNING)).fetchall()
            )
            for row in rs:
                run_state = benchutil.run_state(rs)
                self.monitor.add(run_id=rs['run_id'], state=run_state)
        # Start the monitor thread
        self.monitor.run()

    def exec(self, submission, arguments):
        """Run benchmark for given set of arguments. Returns the identifier of
        the created run and the resulting workflow run state.

        Parameters
        ----------
        benchmark: benchengine.benchmark.base.BenchmarkHandle
            Handle for benchmark that is being executed
        arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
            Dictionary of argument values for parameters in the template

        Returns
        -------
        string, benchtmpl.workflow.state.WorkflowState

        Raises
        ------
        benchtmpl.error.MissingArgumentError
        """
        # Execute the benchmark workflow for the given set of arguments.
        wftemplate = submission.template.get_workflow_template()
        run_id, run_state = backend.execute(
            template=wftemplate,
            arguments=arguments
        )
        # Insert run info and run results into database.
        sql = 'INSERT INTO benchmark_run('
        sql += 'run_id, submission_id, state, created_at, started_at, ended_at'
        sql += ') VALUES(?, ?, ?, ?, ?, ?)'
        type_id = run_state.type_id
        tcreate = run_state.created_at.isoformat()
        tstart = run_state.started_at.isoformat()
        if not run_state.is_active():
            tend = run_state.finished_at.isoformat()
        else:
            tend = None
        with self.connector.connect() as con:
            con.execute(
                sql,
                (run_id, submission.identifier, type_id, tcreate, tstart, tend)
            )
            con.commit()
        # Depending on the state we may either want to get the workfow results
        # or monitor the workflow for state updates.
        if run_state.is_success():
            # If the workflow completed successfully, add the results to the
            # benchmark repository.
            fh = run_state.resources[wftemplate.schema.result_file_id]
            result = util.read_object(fh.filepath)
            self.repo.insert_results(run_id=run_id, result=results)
        elif run_state.is_active():
            # If the run is active add it to the monitor to poll for state
            # updates
            self.monitor.add(run_id=run_id, state=run_state)
        return run_id, run_state

    def update_state(self, run_id, run_state):
        """
        """
        pass
