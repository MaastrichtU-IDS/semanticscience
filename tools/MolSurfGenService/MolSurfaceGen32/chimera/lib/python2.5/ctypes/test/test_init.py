from ctypes import *
import unittest

class X(Structure):
    _fields_ = [("a", c_int),
                ("b", c_int)]
    new_was_called = False

    def __new__(cls):
        result = super(X, cls).__new__(cls)
        result.new_was_called = True
        return result

    def __init__(self):
        self.a = 9
        self.b = 12

class Y(Structure):
    _fields_ = [("x", X)]


class InitTest(unittest.TestCase):
    def test_get(self):
        # make sure the only accessing a nested structure
        # doesn't call the structure's __new__ and __init__
        y = Y()
        self.failUnlessEqual((y.x.a, y.x.b), (0, 0))
        self.failUnlessEqual(y.x.new_was_called, False)

        # But explicitely creating an X structure calls __new__ and __init__, of course.
        x = X()
        self.failUnlessEqual((x.a, x.b), (9, 12))
        self.failUnlessEqual(x.new_was_called, True)

        y.x = x
        self.failUnlessEqual((y.x.a, y.x.b), (9, 12))
        self.failUnlessEqual(y.x.new_was_called, False)

if __name__ == "__main__":
    unittest.main()
