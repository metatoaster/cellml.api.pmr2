import unittest

from cellml.api.pmr2.property import *


class TestClass(object):
    counter = None

    def __init__(self):
        self.counter = 0
        self.items = None

    @singleton_property
    def test_prop(self):
        self.counter += 1
        return self.counter

    @singleton_property
    def test_items(self):
        items = []
        return items


class PropertyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_side_effect_once(self):
        # to test this side effect is only triggered once
        tester = TestClass()
        value1 = tester.test_prop
        value2 = tester.test_prop

        self.assertEqual(value1, value2)
        self.assert_(isinstance(tester.test_prop, int))

    def test_0001_multiple_instances(self):
        # to test this side effect is only triggered once, even with
        # multiple instances.
        tester1 = TestClass()
        value1 = tester1.test_prop
        value2 = tester1.test_prop

        tester2 = TestClass()
        value3 = tester2.test_prop
        value4 = tester2.test_prop

        self.assertEqual(value1, value2)
        self.assertEqual(value1, value3)
        self.assertEqual(value1, value4)

    def test_0002_multiple_instances_instanced_attirbutes(self):
        # Make sure the different instances have unique items.

        tester1 = TestClass()
        tester1.test_items.append(1)
        tester1.test_items.append(2)

        tester2 = TestClass()
        tester2.test_items.append(3)
        tester2.test_items.append(4)

        self.assertEqual(tester1.test_items, [1, 2])
        self.assertEqual(tester2.test_items, [3, 4])

        self.assertEqual(tester2._test_items, tester2.test_items)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PropertyTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
