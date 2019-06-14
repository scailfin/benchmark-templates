"""Simple implementation for a backend workflow execution engine. This engine
runs each workflow as a subprocess.

NOTE: This class is primatily intended for testing purposes. It is not
recommended to be used as the workfow engine in production systems. The module
executes workflow steps using subprocess.call() (for compatibility).
"""

import os
import shutil

from datetime import datetime
from functools import partial
from multiprocessing import Lock, Pool
from string import Template

from benchtmpl.backend.multiprocess.io import FileCopy
from benchtmpl.workflow.resource.base import FileResource

import benchtmpl.backend.multiprocess.task as tasks
import benchtmpl.backend.reana.util as reana
import benchtmpl.error as err
import benchtmpl.util.core as util
import benchtmpl.workflow.state as wf
import benchtmpl.workflow.template.base as tmpl


class MultiProcessWorkflowEngine(object):
    """The workflow engine is used to execute workflow templates for a given
    set of arguments for template parameters as well as to check the state of
    the workflow execution.

    Workflow executions, referred to as runs, are identified by unique run ids
    that are assigned by the engine when the execution starts.
    """
    def __init__(self, base_dir):
        """Initialize the base directory under which all workflow runs are
        maintained. If the directory does not exist it will be created.

        Parameters
        ----------
        base_dir: string
            Path to directory on disk
        """
        self.base_dir = base_dir
        # Create the base directory if it does not exist
        util.create_dir(self.base_dir)
        # Dictionary of all
        self.tasks = dict()
        self.lock = Lock()

    def cancel_run(self, run_id):
        """Request to cancel execution of the given run.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        """
        with self.lock:
            # Catch errors in case the run has already been removed
            try:
                state, pool = self.tasks[run_id]
                # Close the pool and terminate any running processes
                if not pool is None:
                    pool.close()
                    pool.terminate()
                del self.tasks[run_id]
            except KeyError:
                pass

    def exec(self, template, arguments, run_async=True, verbose=False):
        """Execute a given workflow template for a set of argument values.
        Returns an unique identifier for the started workflow run.

        Parameters
        ----------
        template: benchtmpl.workflow.template.base.TemplateHandle
            Workflow template containing the parameterized specification and the
            parameter declarations
        arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
            Dictionary of argument values for parameters in the template
        run_async: bool, optional
            Run workflow asynchronously or synchronously. The syncronous mode
            is intended for test purposes and when used from a command line
            interface.
        verbose: bool, optional
            Print command strings to STDOUT during workflow execution

        Returns
        -------
        string

        Raises
        ------
        benchtmpl.error.MissingArgumentError
        """
        # Before we start creating directories and copying files make sure that
        # there are values for all template parameters (either in the arguments
        # dictionary or set as default values)
        template.validate_arguments(arguments)
        # Create unique run identifier
        identifier = util.get_unique_identifier()
        # Create run folder for input and output files
        run_dir = os.path.join(self.base_dir, identifier)
        os.makedirs(run_dir)
        # Copy all static files and files in the argument dictionary into the
        # run folder.
        try:
            # Copy all required code and input files
            reana.upload_files(
                template=template,
                arguments=arguments,
                loader=FileCopy(run_dir)
            )
            # Get list of workflow commands after substituting references to
            # parameters from the inputs/parameters section of the REANA
            # workflow specification.
            commands = get_commands(template, arguments)
            # Replace references to template parameters in the list of output
            # files from the workflow specification
            output_files = tmpl.replace_args(
                spec=template.workflow_spec.get('outputs', {}).get('files', {}),
                arguments=arguments,
                parameters=template.parameters
            )
            # Run workflow
            ts = datetime.now()
            state = wf.StateRunning(created_at=ts, started_at=ts)
            if run_async:
                pool = Pool(processes=1)
                task_callback_function = partial(
                    callback_function,
                    lock=self.lock,
                    tasks=self.tasks,
                    run_dir=run_dir,
                    output_files=output_files
                )
                with self.lock:
                    self.tasks[identifier] = (state, pool)
                pool.apply_async(
                    tasks.run,
                    args=(identifier, commands, run_dir, verbose),
                    callback=task_callback_function
                )
            else:
                with self.lock:
                    self.tasks[identifier] = (state, None)
                # Start the task and wait until completions
                result = tasks.run(
                    identifier=identifier,
                    commands=commands,
                    run_dir=run_dir,
                    verbose=verbose
                )
                # Call callback handler with task result
                callback_function(
                    result=result,
                    lock=self.lock,
                    tasks=self.tasks,
                    run_dir=run_dir,
                    output_files=output_files
                )
        except Exception as ex:
            # Remove run directory if anything goes wrong while preparing the
            # workflow and starting the run
            shutil.rmtree(run_dir)
            raise ex
        # Return run identifier
        return identifier

    def get_state(self, run_id):
        """Get the status of the workflow with the given identifier.

        Parameters
        ----------
        run_id: string
            Unique run identifier

        Returns
        -------
        benchtmpl.workflow.state.WorkflowState

        Raises
        ------
        benchtmpl.error.UnknownRunError
        """
        with self.lock:
            try:
                state, _ = self.tasks[run_id]
                return state
            except KeyError:
                raise err.UnknownRunError(run_id)

# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def callback_function(result, lock, tasks, run_dir, output_files):
    """Callback function for executed tasks. Notifies the workflow controller
    and removes the task from the task index.

    Parameters
    ----------
    result: (string, vizier.engine.task.processor.ExecResult)
        Tupe of task identifier and execution result
    tasks: dict
        Task index of the backend
    run_id: string
        Path to the working directory of the workflow run
    output_files: list(string)
        List containing relative paths to output files that the workflow
        generates.
    """
    task_id, result, messages = result
    try:
        with lock:
            state, pool = tasks[task_id]
            if result == wf.STATE_SUCCESS:
                # Create dictionary of resources from list of expected output
                # files.
                resources = dict()
                for file_id in output_files:
                    filepath = os.path.join(run_dir, file_id)
                    if os.path.isfile(filepath):
                        resources[file_id] = FileResource(
                            identifier=file_id,
                            filepath=filepath
                        )
                result_state = state.success(resources=resources)
            else:
                result_state = state.error(messages)
            # Close the pool and set the pool component of the task entry
            # to None
            if not pool is None:
                pool.close()
            tasks[task_id] = (result_state, None)
    except KeyError as ex:
        print('Key error {}'.format(ex))
        pass


def get_commands(template, arguments):
    """Get expanded commands from template workflow specification. In this
    simple implementations the commands within each step of the workflow
    specification are expanded for the given set of arguments and appended to
    the result list of commands.

    Parameters
    ----------
    template: benchtmpl.workflow.template.base.TemplateHandle
        Workflow template containing the parameterized specification and the
        parameter declarations
    arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
        Dictionary of argument values for parameters in the template

    Returns
    -------
    list(string)

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    """
    spec = template.workflow_spec
    # Get the input/parameters dictionary from the workflow specification and
    # replace all references to template parameters with the given arguments
    # or default values
    workflow_parameters = tmpl.replace_args(
        spec=spec.get('inputs', {}).get('parameters', {}),
        arguments=arguments,
        parameters=template.parameters
    )
    # Add all command stings in workflow steps to result after replacing
    # references to parameters
    result = list()
    steps = spec.get('workflow', {}).get('specification', {}).get('steps', [])
    for step in steps:
        for command in step.get('commands', []):
            try:
                result.append(Template(command).substitute(workflow_parameters))
            except KeyError as ex:
                raise err.InvalidTemplateError(str(ex))
    return result
