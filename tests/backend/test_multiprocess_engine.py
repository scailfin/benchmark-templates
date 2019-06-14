"""Test functinality of the multiprocess backend."""

from unittest import TestCase

import os
import shutil
import time

from benchtmpl.backend.multiprocess.engine import MultiProcessWorkflowEngine
from benchtmpl.io.files.base import FileHandle
from benchtmpl.workflow.template.repo import TemplateRepository

import benchtmpl.error as err


DATA_FILE = './tests/files/workflows/helloworld/data/names.txt'
TEMPLATE_FILE = 'tests/files/template/reana.yaml'
TMP_DIR = './tests/files/.tmp'
WORKFLOW_DIR = './tests/files/template'


class TestMultiprocessWorkflowEngine(TestCase):
    """Test executing workflows from templates using the multiprocess workflow
    engine.
    """
    def setUp(self):
        """Create an empty target directory for each test and intitialize the
        file loader function.
        """
        self.tearDown()
        self.engine = MultiProcessWorkflowEngine(
            base_dir=os.path.join(TMP_DIR, 'engine')
        )
        self.repo = TemplateRepository(base_dir=os.path.join(TMP_DIR, 'repo'))

    def tearDown(self):
        """Remove the temporary target directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_run_helloworld(self):
        """Execute the helloworld example."""
        template = self.repo.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=TEMPLATE_FILE
        )
        arguments = {
            'names': template.get_argument('names', FileHandle(DATA_FILE)),
            'sleeptime': template.get_argument('sleeptime', 3)
        }
        # Run workflow asyncronously
        run_id = self.engine.exec(template, arguments)
        while self.engine.get_state(run_id).is_active():
            time.sleep(1)
        state = self.engine.get_state(run_id)
        self.validate_run_result(state)
        # Cancel run
        arguments = {
            'names': template.get_argument('names', FileHandle(DATA_FILE)),
            'sleeptime': template.get_argument('sleeptime', 30)
        }
        run_id = self.engine.exec(template, arguments)
        while self.engine.get_state(run_id).is_active():
            # Cancel the run
            self.engine.cancel_run(run_id)
            break
        with self.assertRaises(err.UnknownRunError):
            self.engine.get_state(run_id)
        # Run workflow syncronously
        arguments = {
            'names': template.get_argument('names', FileHandle(DATA_FILE)),
            'sleeptime': template.get_argument('sleeptime', 1)
        }
        sync_run_id = self.engine.exec(template, arguments, run_async=False)
        self.assertNotEqual(run_id, sync_run_id)
        state = self.engine.get_state(sync_run_id)
        print(state.type_id)
        self.validate_run_result(state)

    def validate_run_result(self, state):
        """Validate the results of a run of the helloworld workflow."""
        self.assertTrue(state.is_success())
        self.assertEqual(len(state.resources), 1)
        self.assertTrue('results/greetings.txt' in state.resources)
        greetings = list()
        with open(state.resources['results/greetings.txt'].filepath, 'r') as f:
            for line in f:
                greetings.append(line.strip())
        self.assertEqual(len(greetings), 2)
        self.assertEqual(greetings[0], 'Hello Alice!')
        self.assertEqual(greetings[1], 'Hello Bob!')


if __name__ == '__main__':
    import unittest
    unittest.main()
