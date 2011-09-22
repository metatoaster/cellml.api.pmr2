import unittest

from cellml.api.pmr2.property import *


class InstanceTestClass(object):
    counter = None

    def __init__(self):
        self.counter = 0
        self.items = None

    @instance_property
    def test_prop(self):
        self.counter += 1
        return self.counter

    @instance_property
    def test_items(self):
        items = []
        return items

    @instance_property
    def test_nested(self):
        return self.test_prop * 1


class SingletonTestClass(object):
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

    @singleton_property
    def test_nested(self):
        return self.test_prop * 1


class InstancePropertyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_side_effect_once(self):
        # to test this side effect is only triggered once
        tester = InstanceTestClass()
        value1 = tester.test_prop
        value2 = tester.test_prop

        self.assert_(isinstance(tester.test_prop, int))
        self.assertEqual(tester.counter, value1)
        self.assertEqual(tester.counter, value2)

    def test_0001_multiple_instances(self):
        # to test this side effect is only triggered once, even with
        # multiple instances.
        tester1 = InstanceTestClass()
        value1 = tester1.test_prop
        value2 = tester1.test_prop

        tester2 = InstanceTestClass()
        value3 = tester2.test_prop
        value4 = tester2.test_prop

        self.assertEqual(tester1.counter, value1)
        self.assertEqual(value1, value2)
        self.assertEqual(value1, value3)
        self.assertEqual(value1, value4)

    def test_0002_multiple_instances_instanced_attributes(self):
        # Make sure the different instances have unique items.

        tester1 = InstanceTestClass()

        tester1.test_items.append(1)
        tester1.test_items.append(2)

        tester2 = InstanceTestClass()
        tester2.test_items.append(3)
        tester2.test_items.append(4)

        self.assertEqual(tester1.test_items, [1, 2])
        self.assertEqual(tester2.test_items, [3, 4])

        # since this property creates a local instance.
        self.assertEqual(tester2._test_items, tester2.test_items)

    def test_0003_empty_not_multiple(self):
        # Make sure empty instances are not recreated on every access.

        tester = InstanceTestClass()
        self.assertEqual(id(tester.test_items), id(tester.test_items))

    def test_0004_delete(self):

        tester = InstanceTestClass()
        tester.test_items.append(1)
        del tester.test_items
        self.assertEqual(tester.test_items, [])


class SingletonPropertyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_side_effect_once(self):
        # to test this side effect is only triggered once
        tester = SingletonTestClass()
        value1 = tester.test_prop
        value2 = tester.test_prop

        self.assert_(isinstance(tester.test_prop, int))
        self.assertEqual(tester.counter, value1)
        self.assertEqual(tester.counter, value2)

    def test_0001_multiple_instances(self):
        # to test this side effect is only triggered once, even with
        # multiple instances.
        tester1 = SingletonTestClass()
        value1 = tester1.test_prop
        value2 = tester1.test_prop

        tester2 = SingletonTestClass()
        value3 = tester2.test_prop
        value4 = tester2.test_prop

        # They won't be incremented because the decorator instance 
        # already contain the value.
        self.assertEqual(tester1.counter, 0)
        self.assertEqual(tester2.counter, 0)

        self.assertEqual(value1, 1)
        self.assertEqual(value1, value2)
        self.assertEqual(value1, value3)
        self.assertEqual(value1, value4)

    def test_0002_multiple_instances_instanced_attributes(self):
        # Make sure the different instances all share the same 
        # singleton attribute.

        tester1 = SingletonTestClass()
        tester2 = SingletonTestClass()

        # They also have to be the same.
        self.assertEqual(id(tester1.test_items), id(tester2.test_items))

        tester1.test_items.append(1)
        tester1.test_items.append(2)

        tester2.test_items.append(3)
        tester2.test_items.append(4)

        self.assertEqual(tester1.test_items, [1, 2, 3, 4])
        self.assertEqual(tester2.test_items, [1, 2, 3, 4])

    def test_0003_persisted_singleton(self):
        # Since this is still within the same thread of execution,
        # the values from test_0002 should persist also.

        tester = SingletonTestClass()
        tester.test_items.append(5)
        tester.test_items.append(6)

        self.assertEqual(tester.test_items, [1, 2, 3, 4, 5, 6])

    def test_0004_delete_singleton(self):
        # still can be deleted however to allow reinstantiation.

        tester = SingletonTestClass()
        self.assertEqual(tester.test_items, [1, 2, 3, 4, 5, 6])
        del tester.test_items
        tester.test_items.append(7)
        tester.test_items.append(8)

        self.assertEqual(tester.test_items, [7, 8])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SingletonPropertyTestCase))
    suite.addTest(makeSuite(InstancePropertyTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
