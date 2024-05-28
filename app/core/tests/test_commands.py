"""Test of Custom Management"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
# one of error that raises when DB is not ready
from django.db.utils import OperationalError
# other type of error that raises when DB is not ready
from django.core.management import call_command
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CustomTests(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_check):
        """Test Commands"""

        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_check):
        """Tests waiting for database when gettiing Operational error"""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        """
        side_effect is used to raise a error when the database connection fails
        we can add the occurence of the errors as :
            Psycopg2Error for the first 2 times
            OperationalError for the next 3 times
            and then returns a boolean indicating
            whether the database connection is successful
            or not
            2 and 3 are very rough numbers this can be extended
            But these are the most preferable.
        """
        call_command("wait_for_db")
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
