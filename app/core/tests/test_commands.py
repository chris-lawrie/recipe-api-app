"""
Test custom Django management commands
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# This decorator is the 'patched_check' in the methods below
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """
    Run these tests via terminal with:
        docker-compose run --rm app sh -c "python manage.py test"
    """
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for dtabse if database ready"""
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    # this decorator is the 'patched_slee' arg below
    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperatinalError"""

        # mocking notes:
        #   - the first two times patched_check is called it raises
        #     Psycopg2Error
        #   - the following 3 times it raises operataional error
        #   - then it returns true
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assert_equal(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
