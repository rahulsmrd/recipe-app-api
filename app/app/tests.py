"""
Examples Tests
"""

# noqa

from django.test import SimpleTestCase # noqa

from app.calc import add, subtract # noqa

class CalcTestCase(SimpleTestCase): # noqa
    """Tetsing the Calc file """
    def test_add_numbers(self): # noqa
        x = 3
        y = 4
        res = add(x, y)
        self.assertEqual(res, 7)

    def test_subtract_numbers(self): # noqa
        x = 10
        y = 4
        res = subtract(x, y)
        self.assertEqual(res, 6)
