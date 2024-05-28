"""
Examples Tests
"""

#noqa

from django.test import SimpleTestCase 

from app.calc import *

class CalcTestCase(SimpleTestCase):
    """Tetsing the Calc file """
    def test_add_numbers(self):
        x=3
        y=4
        res=add(x,y)
        self.assertEqual(res,7)
    
    def test_subtract_numbers(self):
        x=10
        y=4
        res = subtract(x,y)
        self.assertEqual(res,6)