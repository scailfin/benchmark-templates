"""Utilities for workflow templates that use the REANA workflow engine and/or
the REANA workflow specification format.
"""

import os

import benchtmpl.error as err
import benchtmpl.workflow.template.base as tmpl


def upload_files(template, arguments, loader):
    """Upload all local files that are listed in the inputs/files section of
    the REANA workflow specification. Uses a loader function to allow use of
    this method in cases where the workflow is executed locally or remote using
    a REANA cluster instance.

    Raises errors if (i) an unknown parameter is referenced or (ii) if the type
    of a referenced parameter in the input files section is not of type file.

    Parameters
    ----------
    template: benchtmpl.workflow.template.base.TemplateHandle
        Workflow template containing the parameterized specification and the
        parameter declarations
    arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
        Dictionary of argument values for parameters in the template
    loader: func
        File (up)load function that takes a filepath as the first argument and
        a (remote) target path as the second argument

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    benchtmpl.error.MissingArgumentError
    benchtmpl.error.UnknownParameterError
    """
    for val in template.workflow_spec.get('inputs', {}).get('files', []):
        # Set source and target values depending on whether the list
        # entry references a template parameter or not
        if tmpl.is_parameter(val):
            var = tmpl.get_parameter_name(val)
            # Raise error if the type of the referenced parameter is
            # not file
            para = template.get_parameter(var)
            if not para.is_file():
                raise err.InvalidTemplateError('expected file parameter for \'{}\''.format(var))
            arg = arguments.get(var)
            if arg is None:
                if para.default_value is None:
                    raise err.MissingArgumentError(var)
                else:
                    # Set source path to default value (assuming that
                    # the default points to a file in the template
                    # base directory)
                    source = os.path.join(
                        template.base_dir,
                        para.default_value
                    )
            else:
                # Get path to source file from file handle
                source = arg.value.filepath
            if para.has_constant():
                target = para.get_constant()
            else:
                target = arg.value.name
        else:
            source = os.path.join(template.base_dir, val)
            target = val
        # Upload source file
        loader(source, target)
