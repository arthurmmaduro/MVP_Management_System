import importlib
from unittest.mock import patch

from django.test import SimpleTestCase


class TestLoggingConfig(SimpleTestCase):
    def test_logging_uses_file_handler_for_project_loggers_when_log_dir_is_available(
        self,
    ):
        with patch('pathlib.Path.mkdir') as mkdir_mock:
            logging_module = importlib.reload(
                importlib.import_module('setup.settings.components.logging')
            )

        self.assertIn('app_file', logging_module.LOGGING['handlers'])
        self.assertEqual(logging_module.LOGGING['root']['handlers'], ['console'])
        self.assertEqual(
            logging_module.LOGGING['loggers']['customer']['handlers'],
            ['console', 'app_file'],
        )
        mkdir_mock.assert_called_once_with(exist_ok=True)

    def test_logging_falls_back_to_console_when_log_dir_cannot_be_created(self):
        with patch('pathlib.Path.mkdir', side_effect=OSError):
            logging_module = importlib.reload(
                importlib.import_module('setup.settings.components.logging')
            )

        self.assertNotIn('app_file', logging_module.LOGGING['handlers'])
        self.assertEqual(logging_module.LOGGING['root']['handlers'], ['console'])
        self.assertEqual(
            logging_module.LOGGING['loggers']['customer']['handlers'],
            ['console'],
        )
