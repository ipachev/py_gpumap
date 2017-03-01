from unittest import TestCase
from func_def import FunctionConverter
import ast

# def calc(a):
#     return a.calc()
#
# class ClassA:
#     def __init__(self, x, y, d):
#         self.x = x
#         self.y = y
#         self.d = d
#
#
#
# class ClassB:
#     def __init__(self, i, j, k):
#         self.i = i
#         self.j = j
#         self.k = k
#
#
#
# class ClassC:
#     def __init__(self, val):
#         self.val = val
#
# class ClassD:
#     def __init__(self, r):
#         self.r = r


class TestFunctionConverter(TestCase):
    def setUp(self):
        self.fc = FunctionConverter(None)

    def test_literal_num(self):
        node = ast.parse("1234")
        self.assertEqual("1234", self.fc.visit(node))

        node = ast.parse("12.34")
        self.assertEqual("12.34", self.fc.visit(node))

        node = ast.parse("0x1ABCDEF")
        self.assertEqual("28036591", self.fc.visit(node))

        # G is not a valid hex digit and should not parse
        self.assertRaises(SyntaxError, ast.parse, "0x1ABCDEFG")

        node = ast.parse("0b11010101")
        self.assertEqual("213", self.fc.visit(node))

        # 8 is not a valid binary digit and should not parse
        self.assertRaises(SyntaxError, ast.parse, "0b11010181")

    def test_literal_string(self):
        node = ast.parse("\"1234\"")
        self.assertEqual("\"1234\"", self.fc.visit(node))

        node = ast.parse("\"abcde\"")
        self.assertEqual("\"abcde\"", self.fc.visit(node))

        node = ast.parse("\'12345\'")
        self.assertEqual("\"12345\"", self.fc.visit(node))

        node = ast.parse("\'abcdef\'")
        self.assertEqual("\"abcdef\"", self.fc.visit(node))

    def test_literal_bytes(self):
        node = ast.parse("b\"some_bytes\"")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("B\"some_bytes\"")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_list(self):
        node = ast.parse("[]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[a, b, c]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[1, 3, 5, 7]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[\"a\", \"b\", \"c\"]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_tuple(self):
        node = ast.parse("()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(a, b, c)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(1, 3, 5, 7)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(\"a\", \"b\", \"c\")")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_set(self):
        node = ast.parse("{a, b, c}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{1, 3, 5, 7}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{\"a\", \"b\", \"c\"}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_dict(self):
        node = ast.parse("{}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{a: 1, b: 3, c: 5, d: 7}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{a: \"a\", b: \"b\", c: \"c\"}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{\"a\": 1, \"b\": 2, \"c\": 3}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_ellipsis(self):
        node = ast.parse("...")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_name_constant(self):
        node = ast.parse("True")
        self.assertEqual("true", self.fc.visit(node))

        node = ast.parse("False")
        self.assertEqual("false", self.fc.visit(node))

        node = ast.parse("None")
        self.assertEqual("null", self.fc.visit(node))

    def test_name(self):
        node = ast.parse("x")
        self.assertEqual("x", self.fc.visit(node))

        node = ast.parse("val")
        self.assertEqual("val", self.fc.visit(node))

        node = ast.parse("_val")
        self.assertEqual("_val", self.fc.visit(node))

        node = ast.parse("a_val")
        self.assertEqual("a_val", self.fc.visit(node))

        node = ast.parse("Val")
        self.assertEqual("Val", self.fc.visit(node))

    def test_starred(self):
        node = ast.parse("*args")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("*obj.args")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("*obj.gen_args()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_expr(self):
        """
        This test is covered by:
        test_unary_ops
        test_bin_ops
        """
        pass

    def test_unary_ops(self):
        """
        This test is covered by:
        test_unary_add
        test_unary_sub
        test_not
        test_invert
        """
        pass

    def test_unary_add(self):
        node = ast.parse("+1234")
        self.assertEqual("(+1234)", self.fc.visit(node))

        node = ast.parse("+1234.56")
        self.assertEqual("(+1234.56)", self.fc.visit(node))

        node = ast.parse("+x.a_field")
        self.assertEqual("(+x.a_field)", self.fc.visit(node))

        node = ast.parse("+x.a_method(y)")
        self.assertEqual("(+x.a_method(y))", self.fc.visit(node))

    def test_unary_sub(self):
        node = ast.parse("-1234")
        self.assertEqual("(-1234)", self.fc.visit(node))

        node = ast.parse("-1234.56")
        self.assertEqual("(-1234.56)", self.fc.visit(node))

        node = ast.parse("-x.a_field")
        self.assertEqual("(-x.a_field)", self.fc.visit(node))

        node = ast.parse("-x.a_method(y)")
        self.assertEqual("(-x.a_method(y))", self.fc.visit(node))

    def test_not(self):
        node = ast.parse("not True")
        self.assertEqual("(!true)", self.fc.visit(node))

        node = ast.parse("not b")
        self.assertEqual("(!b)", self.fc.visit(node))

        node = ast.parse("not x.a_field")
        self.assertEqual("(!x.a_field)", self.fc.visit(node))

        node = ast.parse("not x.a_method(y)")
        self.assertEqual("(!x.a_method(y))", self.fc.visit(node))

    def test_invert(self):
        node = ast.parse("~num")
        self.assertEqual("(~num)", self.fc.visit(node))

        node = ast.parse("~0b1010011")
        self.assertEqual("(~83)", self.fc.visit(node))

        node = ast.parse("~x.a_field")
        self.assertEqual("(~x.a_field)", self.fc.visit(node))

        node = ast.parse("~x.a_method(y)")
        self.assertEqual("(~x.a_method(y))", self.fc.visit(node))

    def test_bin_ops(self):
        """
        This test is covered by:
        test_add
        test_sub
        test_mult
        test_div
        test_floordiv
        test_modulo
        test_pow
        test_lshift
        test_rshift
        test_bit_or
        test_bit_xor
        test_bit_and
        """
        pass

    def test_add(self):
        node = ast.parse("31 + 57")
        self.assertEqual("(31 + 57)", self.fc.visit(node))

        node = ast.parse("31 + (-57)")
        self.assertEqual("(31 + (-57))", self.fc.visit(node))

        node = ast.parse("31 + x")
        self.assertEqual("(31 + x)", self.fc.visit(node))

        node = ast.parse("y + 57")
        self.assertEqual("(y + 57)", self.fc.visit(node))

        node = ast.parse("x + y")
        self.assertEqual("(x + y)", self.fc.visit(node))

        node = ast.parse("x + y + z")
        self.assertEqual("((x + y) + z)", self.fc.visit(node))

        node = ast.parse("x.i + y.i")
        self.assertEqual("(x.i + y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) + y.a_method(b)")
        self.assertEqual("(x.a_method(a) + y.a_method(b))", self.fc.visit(node))

    def test_sub(self):
        node = ast.parse("31 - 57")
        self.assertEqual("(31 - 57)", self.fc.visit(node))

        node = ast.parse("31 - (+57)")
        self.assertEqual("(31 - (+57))", self.fc.visit(node))

        node = ast.parse("31 - x")
        self.assertEqual("(31 - x)", self.fc.visit(node))

        node = ast.parse("y - 57")
        self.assertEqual("(y - 57)", self.fc.visit(node))

        node = ast.parse("x - y")
        self.assertEqual("(x - y)", self.fc.visit(node))

        node = ast.parse("x - y - z")
        self.assertEqual("((x - y) - z)", self.fc.visit(node))

        node = ast.parse("x.i - y.i")
        self.assertEqual("(x.i - y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) - y.a_method(b)")
        self.assertEqual("(x.a_method(a) - y.a_method(b))", self.fc.visit(node))

    def test_div(self):
        node = ast.parse("31 / 57")
        self.assertEqual("(31 / 57)", self.fc.visit(node))

        node = ast.parse("31 / (-57)")
        self.assertEqual("(31 / (-57))", self.fc.visit(node))

        node = ast.parse("31 / x")
        self.assertEqual("(31 / x)", self.fc.visit(node))

        node = ast.parse("y / 57")
        self.assertEqual("(y / 57)", self.fc.visit(node))

        node = ast.parse("x / y")
        self.assertEqual("(x / y)", self.fc.visit(node))

        node = ast.parse("x / y / z")
        self.assertEqual("((x / y) / z)", self.fc.visit(node))

        node = ast.parse("x.i / y.i")
        self.assertEqual("(x.i / y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) / y.a_method(b)")
        self.assertEqual("(x.a_method(a) / y.a_method(b))", self.fc.visit(node))

    def test_floordiv(self):
        node = ast.parse("31 // 57")
        self.assertEqual("int(31 / 57)", self.fc.visit(node))

        node = ast.parse("31 // (-57)")
        self.assertEqual("int(31 / (-57))", self.fc.visit(node))

        node = ast.parse("31 // x")
        self.assertEqual("int(31 / x)", self.fc.visit(node))

        node = ast.parse("y // 57")
        self.assertEqual("int(y / 57)", self.fc.visit(node))

        node = ast.parse("x // y")
        self.assertEqual("int(x / y)", self.fc.visit(node))

        node = ast.parse("x.i // y.i")
        self.assertEqual("int(x.i / y.i)", self.fc.visit(node))

        node = ast.parse("x // y // z")
        self.assertEqual("int(int(x / y) / z)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) // y.a_method(b)")
        self.assertEqual("int(x.a_method(a) / y.a_method(b))", self.fc.visit(node))

    def test_modulo(self):
        node = ast.parse("31 % 57")
        self.assertEqual("(31 % 57)", self.fc.visit(node))

        node = ast.parse("31 % (-57)")
        self.assertEqual("(31 % (-57))", self.fc.visit(node))

        node = ast.parse("31 % x")
        self.assertEqual("(31 % x)", self.fc.visit(node))

        node = ast.parse("y % 57")
        self.assertEqual("(y % 57)", self.fc.visit(node))

        node = ast.parse("x % y")
        self.assertEqual("(x % y)", self.fc.visit(node))

        node = ast.parse("x % y % z")
        self.assertEqual("((x % y) % z)", self.fc.visit(node))

        node = ast.parse("x.i % y.i")
        self.assertEqual("(x.i % y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) % y.a_method(b)")
        self.assertEqual("(x.a_method(a) % y.a_method(b))", self.fc.visit(node))

    def test_pow(self):
        node = ast.parse("31 ** 57")
        self.assertEqual("pow(31, 57)", self.fc.visit(node))

        node = ast.parse("31 ** (-57)")
        self.assertEqual("pow(31, (-57))", self.fc.visit(node))

        node = ast.parse("31 ** x")
        self.assertEqual("pow(31, x)", self.fc.visit(node))

        node = ast.parse("y ** 57")
        self.assertEqual("pow(y, 57)", self.fc.visit(node))

        node = ast.parse("x ** y")
        self.assertEqual("pow(x, y)", self.fc.visit(node))

        node = ast.parse("x ** y ** z")
        self.assertEqual("pow(x, pow(y, z))", self.fc.visit(node))

        node = ast.parse("x.i ** y.i")
        self.assertEqual("pow(x.i, y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a)** y.a_method(b)")
        self.assertEqual("pow(x.a_method(a), y.a_method(b))", self.fc.visit(node))

    def test_lshift(self):
        node = ast.parse("0b11010101 << 7")
        self.assertEqual("(213 << 7)", self.fc.visit(node))

        node = ast.parse("0b11010101 << (-7)")
        self.assertEqual("(213 << (-7))", self.fc.visit(node))

        node = ast.parse("0b11010101 << x")
        self.assertEqual("(213 << x)", self.fc.visit(node))

        node = ast.parse("y << 7")
        self.assertEqual("(y << 7)", self.fc.visit(node))

        node = ast.parse("x << y")
        self.assertEqual("(x << y)", self.fc.visit(node))

        node = ast.parse("x << y << z")
        self.assertEqual("((x << y) << z)", self.fc.visit(node))

        node = ast.parse("x.i << y.i")
        self.assertEqual("(x.i << y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) << y.a_method(b)")
        self.assertEqual("(x.a_method(a) << y.a_method(b))", self.fc.visit(node))

    def test_rshift(self):
        node = ast.parse("0b11010101 >> 7")
        self.assertEqual("(213 >> 7)", self.fc.visit(node))

        node = ast.parse("0b11010101 >> (-7)")
        self.assertEqual("(213 >> (-7))", self.fc.visit(node))

        node = ast.parse("0b11010101 >> x")
        self.assertEqual("(213 >> x)", self.fc.visit(node))

        node = ast.parse("y >> 7")
        self.assertEqual("(y >> 7)", self.fc.visit(node))

        node = ast.parse("x >> y")
        self.assertEqual("(x >> y)", self.fc.visit(node))

        node = ast.parse("x >> y >> z")
        self.assertEqual("((x >> y) >> z)", self.fc.visit(node))

        node = ast.parse("x.i >> y.i")
        self.assertEqual("(x.i >> y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) >> y.a_method(b)")
        self.assertEqual("(x.a_method(a) >> y.a_method(b))", self.fc.visit(node))

    def test_bit_or(self):
        node = ast.parse("0b11010101 | 0b0111")
        self.assertEqual("(213 | 7)", self.fc.visit(node))

        node = ast.parse("0b11010101 | x")
        self.assertEqual("(213 | x)", self.fc.visit(node))

        node = ast.parse("y | 0b0111")
        self.assertEqual("(y | 7)", self.fc.visit(node))

        node = ast.parse("x | y")
        self.assertEqual("(x | y)", self.fc.visit(node))

        node = ast.parse("x | y | z")
        self.assertEqual("((x | y) | z)", self.fc.visit(node))

        node = ast.parse("x.i | y.i")
        self.assertEqual("(x.i | y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) | y.a_method(b)")
        self.assertEqual("(x.a_method(a) | y.a_method(b))", self.fc.visit(node))

    def test_bit_xor(self):
        node = ast.parse("0b11010101 ^ 0b0111")
        self.assertEqual("(213 ^ 7)", self.fc.visit(node))

        node = ast.parse("0b11010101 ^ x")
        self.assertEqual("(213 ^ x)", self.fc.visit(node))

        node = ast.parse("y ^ 0b0111")
        self.assertEqual("(y ^ 7)", self.fc.visit(node))

        node = ast.parse("x ^ y")
        self.assertEqual("(x ^ y)", self.fc.visit(node))

        node = ast.parse("x ^ y ^ z")
        self.assertEqual("((x ^ y) ^ z)", self.fc.visit(node))

        node = ast.parse("x.i ^ y.i")
        self.assertEqual("(x.i ^ y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) ^ y.a_method(b)")
        self.assertEqual("(x.a_method(a) ^ y.a_method(b))", self.fc.visit(node))

    def test_bit_and(self):
        node = ast.parse("0b11010101 & 0b0111")
        self.assertEqual("(213 & 7)", self.fc.visit(node))

        node = ast.parse("0b11010101 & x")
        self.assertEqual("(213 & x)", self.fc.visit(node))

        node = ast.parse("y & 0b0111")
        self.assertEqual("(y & 7)", self.fc.visit(node))

        node = ast.parse("x & y")
        self.assertEqual("(x & y)", self.fc.visit(node))

        node = ast.parse("x & y & z")
        self.assertEqual("((x & y) & z)", self.fc.visit(node))

        node = ast.parse("x.i & y.i")
        self.assertEqual("(x.i & y.i)", self.fc.visit(node))

        node = ast.parse("x.a_method(a) & y.a_method(b)")
        self.assertEqual("(x.a_method(a) & y.a_method(b))", self.fc.visit(node))

    def test_bool_op(self):
        """
        This test is covered by:
        test_and
        test_or
        """
        pass

    def test_and(self):
        node = ast.parse("a and b")
        self.assertEqual("(a && b)", self.fc.visit(node))

        node = ast.parse("not a and b")
        self.assertEqual("((!a) && b)", self.fc.visit(node))

        node = ast.parse("a and not b")
        self.assertEqual("(a && (!b))", self.fc.visit(node))

        node = ast.parse("a and b and c")
        self.assertEqual("(a && b && c)", self.fc.visit(node))

        node = ast.parse("a and b and c and d")
        self.assertEqual("(a && b && c && d)", self.fc.visit(node))

        node = ast.parse("a and (b and c)")
        self.assertEqual("(a && (b && c))", self.fc.visit(node))

        node = ast.parse("a and b or c")
        self.assertEqual("((a && b) || c)", self.fc.visit(node))

        node = ast.parse("a and (b or c)")
        self.assertEqual("(a && (b || c))", self.fc.visit(node))

    def test_or(self):
        node = ast.parse("a or b")
        self.assertEqual("(a || b)", self.fc.visit(node))

        node = ast.parse("not a or b")
        self.assertEqual("((!a) || b)", self.fc.visit(node))

        node = ast.parse("a or not b")
        self.assertEqual("(a || (!b))", self.fc.visit(node))

        node = ast.parse("a or b or c")
        self.assertEqual("(a || b || c)", self.fc.visit(node))

        node = ast.parse("a or b or c or d")
        self.assertEqual("(a || b || c || d)", self.fc.visit(node))

        node = ast.parse("a or (b or c)")
        self.assertEqual("(a || (b || c))", self.fc.visit(node))

        node = ast.parse("a or b and c")
        self.assertEqual("(a || (b && c))", self.fc.visit(node))

        node = ast.parse("(a or b) and c")
        self.assertEqual("((a || b) && c)", self.fc.visit(node))

    def test_compare(self):
        """
        Tested by
         test_eq
         test_noteq
         test_lessthan
         test_lessthanequal
         test_greaterthan
         test_greatherthanequal
         
        """

    def test_attribute(self):
        node = ast.parse("x.field1")
        self.assertEqual("x.field1", self.fc.visit(node))

        node = ast.parse("x._field2")
        self.assertEqual("x._field2", self.fc.visit(node))

        node = ast.parse("x.some_method")
        self.assertEqual("x.some_method", self.fc.visit(node))

        # x.123 is not valid and should not parse
        self.assertRaises(SyntaxError, ast.parse, "x.123")
