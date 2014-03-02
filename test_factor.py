import unittest
from factor import Factor
from numpy.testing import assert_array_almost_equal


class TestFactor(unittest.TestCase):
    def test_marginalize_small_edge(self):
        a = Factor([(0, 2), (1, 2)])
        a.data[0, 0] = 1
        a.data[0, 1] = 2
        a.data[1, 0] = 5
        a.data[1, 1] = 8

        b = a.marginalize([0, 1])
        print b.data
        print b.data.shape
        self.assertEqual(b.variables, a.variables)
        self.assertEqual(b.axis_to_variable, a.axis_to_variable)
        assert_array_almost_equal(b.data, a.data)

        c = a.marginalize([1, 0])
        print c.data
        print c.data.shape
        self.assertEqual(c.variables, a.variables)
        self.assertEqual(c.axis_to_variable, a.axis_to_variable)
        assert_array_almost_equal(c.data, a.data)

    def test_marginalize_small(self):
        a = Factor([(0, 2), (1, 2)])
        a.data[0, 0] = 1
        a.data[0, 1] = 2
        a.data[1, 0] = 5
        a.data[1, 1] = 8

        c = Factor([(0, 2)])
        c.data[0] = 3
        c.data[1] = 13

        b = a.marginalize([0])
        print b.data
        print c.data
        print b.data.shape
        print c.data.shape
        self.assertEqual(b.data[0], c.data[0])
        self.assertEqual(b.data[1], c.data[1])
        self.assertEqual(b.variables, c.variables)
        self.assertEqual(b.axis_to_variable, c.axis_to_variable)
        assert_array_almost_equal(b.data, c.data)

        e = Factor([(1, 2)])
        e.data[0] = 6
        e.data[1] = 10

        d = a.marginalize([1])
        print d.data
        print e.data
        print d.data.shape
        print e.data.shape

        self.assertEqual(d.data[0], e.data[0])
        self.assertEqual(d.data[1], e.data[1])
        self.assertEqual(d.variables, e.variables)
        self.assertEqual(d.axis_to_variable, e.axis_to_variable)
        assert_array_almost_equal(d.data, e.data)

    def test_marginalize_larger(self):
        a = Factor([(0, 2), (4, 3), (20, 2)])
        a.data[0, 0, 0] = 1
        a.data[0, 0, 1] = 2
        a.data[0, 1, 0] = 5
        a.data[0, 1, 1] = 8
        a.data[0, 2, 0] = 9
        a.data[0, 2, 1] = 10

        a.data[1, 0, 0] = 11
        a.data[1, 0, 1] = 12
        a.data[1, 1, 0] = 15
        a.data[1, 1, 1] = 18
        a.data[1, 2, 0] = 19
        a.data[1, 2, 1] = 21

        c = Factor([(0, 2)])
        c.data[0] = 35
        c.data[1] = 96

        b = a.marginalize([0])
        print b.data
        print c.data
        print b.data.shape
        print c.data.shape
        self.assertEqual(b.variables, c.variables)
        self.assertEqual(b.axis_to_variable, c.axis_to_variable)
        assert_array_almost_equal(b.data, c.data)

        e = Factor([(4, 3), (20, 2)])
        e.data[0, 0] = 12
        e.data[0, 1] = 14
        e.data[1, 0] = 20
        e.data[1, 1] = 26
        e.data[2, 0] = 28
        e.data[2, 1] = 31

        d = a.marginalize([4, 20])
        print d.data
        print e.data
        print d.data.shape
        print e.data.shape
        self.assertEqual(d.variables, e.variables)
        self.assertEqual(d.axis_to_variable, e.axis_to_variable)
        assert_array_almost_equal(d.data, e.data)

    def test_multiply_small_b(self):
        a = Factor([(0, 2), (1, 2)])
        a.data[0, 0] = 1
        a.data[0, 1] = 2
        a.data[1, 0] = 5
        a.data[1, 1] = 6

        b = Factor([(1, 2)])
        b.data[0] = 2
        b.data[1] = 3

        c = Factor([(0, 2), (1, 2)])
        c.data[0, 0] = 2
        c.data[0, 1] = 6
        c.data[1, 0] = 10
        c.data[1, 1] = 18

        d = a.multiply(b)

        print d.data
        print c.data
        print d.data.shape
        print c.data.shape
        self.assertEqual(d.variables, c.variables)
        self.assertEqual(d.axis_to_variable, c.axis_to_variable)
        assert_array_almost_equal(d.data, c.data)

    def test_multiply_small_a(self):
        a = Factor([(0, 2), (1, 2)])
        a.data[0, 0] = 1
        a.data[0, 1] = 2
        a.data[1, 0] = 5
        a.data[1, 1] = 6

        e = Factor([(0, 2)])
        e.data[0] = 2
        e.data[1] = 3

        f = Factor([(0, 2), (1, 2)])
        f.data[0, 0] = 1 * 2
        f.data[0, 1] = 2 * 2
        f.data[1, 0] = 5 * 3
        f.data[1, 1] = 6 * 3

        g = a.multiply(e)

        print g.data
        print f.data
        print g.data.shape
        print f.data.shape
        self.assertEqual(g.variables, f.variables)
        self.assertEqual(g.axis_to_variable, f.axis_to_variable)
        assert_array_almost_equal(g.data, f.data)

    def test_multiply_larger(self):
        a = Factor([(0, 2), (3, 2), (12, 3)])
        a.data[0, 0, 0] = 2
        a.data[0, 0, 1] = 1
        a.data[0, 0, 2] = 2
        a.data[0, 1, 0] = 3
        a.data[0, 1, 1] = 7
        a.data[0, 1, 2] = 4

        a.data[1, 0, 0] = 1
        a.data[1, 0, 1] = 1
        a.data[1, 0, 2] = 3
        a.data[1, 1, 0] = 4
        a.data[1, 1, 1] = 9
        a.data[1, 1, 2] = 10

        b = Factor([(0, 2), (12, 3)])
        b.data[0, 0] = 2
        b.data[0, 1] = 3
        b.data[0, 2] = 1
        b.data[1, 0] = 5
        b.data[1, 1] = 1
        b.data[1, 2] = 7

        c = Factor([(0, 2), (3, 2), (12, 3)])
        c.data[0, 0, 0] = 2 * 2
        c.data[0, 0, 1] = 1 * 3
        c.data[0, 0, 2] = 2 * 1
        c.data[0, 1, 0] = 3 * 2
        c.data[0, 1, 1] = 7 * 3
        c.data[0, 1, 2] = 4 * 1

        c.data[1, 0, 0] = 1 * 5
        c.data[1, 0, 1] = 1 * 1
        c.data[1, 0, 2] = 3 * 7
        c.data[1, 1, 0] = 4 * 5
        c.data[1, 1, 1] = 9 * 1
        c.data[1, 1, 2] = 10 * 7

        d = a.multiply(b)

        print d.data
        print c.data
        print d.data.shape
        print c.data.shape
        self.assertEqual(d.variables, c.variables)
        self.assertEqual(d.axis_to_variable, c.axis_to_variable)
        assert_array_almost_equal(d.data, c.data)

    def test_divide_small(self):
        a = Factor([(0, 2), (1, 2)])
        a.data[0, 0] = 1.0
        a.data[0, 1] = 2.0
        a.data[1, 0] = 5.0
        a.data[1, 1] = 6.0

        b = Factor([(1, 2)])
        b.data[0] = 2.0
        b.data[1] = 3.0

        c = Factor([(0, 2), (1, 2)])
        c.data[0, 0] = 1.0 / 2.0
        c.data[0, 1] = 2.0 / 3.0
        c.data[1, 0] = 5.0 / 2.0
        c.data[1, 1] = 6.0 / 3.0

        d = a.multiply(b, divide=True)

        print d.data
        print c.data
        print d.data.shape
        print c.data.shape
        self.assertEqual(d.variables, c.variables)
        self.assertEqual(d.axis_to_variable, c.axis_to_variable)
        assert_array_almost_equal(d.data, c.data)


if __name__ == '__main__':
    unittest.main()
