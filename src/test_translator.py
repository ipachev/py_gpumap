from unittest import TestCase

from func_def import FunctionConverter, MethodConverter
from data_model import FunctionRepresentation, MethodRepresentation, ExtractedClasses

import ast

class TestFunctionConverter(TestCase):
    def setUp(self):
        fr = FunctionRepresentation("", [], [], None, None)
        self.fc = FunctionConverter(fr)

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
        test_bool_ops
        test_compare
        test_call
        test_if_exp
        test_attribute
        test_subscript
        test_index
        test_slice
        test_ext_slice
        test_list_comp
        test_set_comp
        test_gen_exp
        test_dict_comp
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
        test_mat_mult
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

    def test_mat_mult(self):
        node = ast.parse("x @ y")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x @ y @ z")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.i @ y.i")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.a_method(a) @ y.a_method(b)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

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
         test_is
         test_is_not
         test_in
         test_not_in
        """

    def test_eq(self):
        # object comparison not yet supported
        node = ast.parse("1 == 3")
        self.assertEqual("(1 == 3)", self.fc.visit(node))

        node = ast.parse("1 == 3 == 4")
        self.assertEqual("(1 == 3 && 3 == 4)", self.fc.visit(node))

        node = ast.parse("a == 1")
        self.assertEqual("(a == 1)", self.fc.visit(node))

        node = ast.parse("a == b == c")
        self.assertEqual("(a == b && b == c)", self.fc.visit(node))

        node = ast.parse("a == x.some_method(b)")
        self.assertEqual("(a == x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) == x.some_method(b) " +
                         "== x.some_method(c) == x.some_method(d)")
        self.assertEqual("(x.some_method(a) == x.some_method(b) " +
                         "&& x.some_method(b) == x.some_method(c) " +
                         "&& x.some_method(c) == x.some_method(d))",
                         self.fc.visit(node))

    def test_noteq(self):
        # object comparison not yet supported
        node = ast.parse("1 != 3")
        self.assertEqual("(1 != 3)", self.fc.visit(node))

        node = ast.parse("1 != 3 != 4")
        self.assertEqual("(1 != 3 && 3 != 4)", self.fc.visit(node))

        node = ast.parse("a != 1")
        self.assertEqual("(a != 1)", self.fc.visit(node))

        node = ast.parse("a != b != c")
        self.assertEqual("(a != b && b != c)", self.fc.visit(node))

        node = ast.parse("a != x.some_method(b)")
        self.assertEqual("(a != x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) != x.some_method(b) " +
                         "!= x.some_method(c) != x.some_method(d)")
        self.assertEqual("(x.some_method(a) != x.some_method(b) " +
                         "&& x.some_method(b) != x.some_method(c) " +
                         "&& x.some_method(c) != x.some_method(d))",
                         self.fc.visit(node))

    def test_lessthan(self):
        # object comparison not yet supported
        node = ast.parse("1 < 3")
        self.assertEqual("(1 < 3)", self.fc.visit(node))

        node = ast.parse("1 < 3 < 4")
        self.assertEqual("(1 < 3 && 3 < 4)", self.fc.visit(node))

        node = ast.parse("a < 1")
        self.assertEqual("(a < 1)", self.fc.visit(node))

        node = ast.parse("a < b < c")
        self.assertEqual("(a < b && b < c)", self.fc.visit(node))

        node = ast.parse("a < x.some_method(b)")
        self.assertEqual("(a < x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) < x.some_method(b) " +
                         "< x.some_method(c) < x.some_method(d)")
        self.assertEqual("(x.some_method(a) < x.some_method(b) " +
                         "&& x.some_method(b) < x.some_method(c) " +
                         "&& x.some_method(c) < x.some_method(d))",
                         self.fc.visit(node))

    def test_lessthaneq(self):
        # object comparison not yet supported
        node = ast.parse("1 <= 3")
        self.assertEqual("(1 <= 3)", self.fc.visit(node))

        node = ast.parse("1 <= 3 <= 4")
        self.assertEqual("(1 <= 3 && 3 <= 4)", self.fc.visit(node))

        node = ast.parse("a <= 1")
        self.assertEqual("(a <= 1)", self.fc.visit(node))

        node = ast.parse("a <= b <= c")
        self.assertEqual("(a <= b && b <= c)", self.fc.visit(node))

        node = ast.parse("a <= x.some_method(b)")
        self.assertEqual("(a <= x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) <= x.some_method(b) " +
                         "<= x.some_method(c) <= x.some_method(d)")
        self.assertEqual("(x.some_method(a) <= x.some_method(b) " +
                         "&& x.some_method(b) <= x.some_method(c) " +
                         "&& x.some_method(c) <= x.some_method(d))",
                         self.fc.visit(node))

    def test_greaterthan(self):
        # object comparison not yet supported
        node = ast.parse("1 > 3")
        self.assertEqual("(1 > 3)", self.fc.visit(node))

        node = ast.parse("1 > 3 > 4")
        self.assertEqual("(1 > 3 && 3 > 4)", self.fc.visit(node))

        node = ast.parse("a > 1")
        self.assertEqual("(a > 1)", self.fc.visit(node))

        node = ast.parse("a > b > c")
        self.assertEqual("(a > b && b > c)", self.fc.visit(node))

        node = ast.parse("a > x.some_method(b)")
        self.assertEqual("(a > x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) > x.some_method(b) " +
                         "> x.some_method(c) > x.some_method(d)")
        self.assertEqual("(x.some_method(a) > x.some_method(b) " +
                         "&& x.some_method(b) > x.some_method(c) " +
                         "&& x.some_method(c) > x.some_method(d))",
                         self.fc.visit(node))

    def test_greaterthaneq(self):
        # object comparison not yet supported
        node = ast.parse("1 >= 3")
        self.assertEqual("(1 >= 3)", self.fc.visit(node))

        node = ast.parse("1 >= 3 >= 4")
        self.assertEqual("(1 >= 3 && 3 >= 4)", self.fc.visit(node))

        node = ast.parse("a >= 1")
        self.assertEqual("(a >= 1)", self.fc.visit(node))

        node = ast.parse("a >= b >= c")
        self.assertEqual("(a >= b && b >= c)", self.fc.visit(node))

        node = ast.parse("a >= x.some_method(b)")
        self.assertEqual("(a >= x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) >= x.some_method(b) " +
                         ">= x.some_method(c) >= x.some_method(d)")
        self.assertEqual("(x.some_method(a) >= x.some_method(b) " +
                         "&& x.some_method(b) >= x.some_method(c) " +
                         "&& x.some_method(c) >= x.some_method(d))",
                         self.fc.visit(node))

    def test_lessthan(self):
        # object comparison not yet supported
        node = ast.parse("1 < 3")
        self.assertEqual("(1 < 3)", self.fc.visit(node))

        node = ast.parse("1 < 3 < 4")
        self.assertEqual("(1 < 3 && 3 < 4)", self.fc.visit(node))

        node = ast.parse("a < 1")
        self.assertEqual("(a < 1)", self.fc.visit(node))

        node = ast.parse("a < b < c")
        self.assertEqual("(a < b && b < c)", self.fc.visit(node))

        node = ast.parse("a < x.some_method(b)")
        self.assertEqual("(a < x.some_method(b))", self.fc.visit(node))

        node = ast.parse("x.some_method(a) < x.some_method(b) " +
                         "< x.some_method(c) < x.some_method(d)")
        self.assertEqual(
            "(x.some_method(a) < x.some_method(b) " +
            "&& x.some_method(b) < x.some_method(c)" +
            " && x.some_method(c) < x.some_method(d))",
            self.fc.visit(node))

    def test_is(self):
        # object comparison not yet supported
        node = ast.parse("1 is 3")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("1 is 3 is 4")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is 1")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is b is c")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is x.some_method(b)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) is x.some_method(b)" +
                         " is x.some_method(c) is x.some_method(d)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_is_not(self):
        # object comparison not yet supported
        node = ast.parse("1 is not 3")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("1 is not 3 is not 4")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is not 1")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is not b is not c")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a is not x.some_method(b)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) is not x.some_method(b)" +
                         " is not x.some_method(c) is not x.some_method(d)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_in(self):
        node = ast.parse("1 in [1, 2, 3]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("1 in (1, 2, 3)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a in (1, 2, 3)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a in some_list")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(a in some_list) in (True)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in some_list")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in get_list()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in x.get_list()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_not_in(self):
        node = ast.parse("1 in [1, 2, 3]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("1 in (1, 2, 3)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a in (1, 2, 3)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a in some_list")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(a in some_list) in (True)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in some_list")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in get_list()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a) in x.get_list()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_call(self):
        node = ast.parse("some_function()")
        self.assertEquals("some_function()", self.fc.visit(node))

        node = ast.parse("some_function(1)")
        self.assertEquals("some_function(1)", self.fc.visit(node))

        node = ast.parse("some_function(1, 2, 3)")
        self.assertEquals("some_function(1, 2, 3)", self.fc.visit(node))

        node = ast.parse("some_function(a)")
        self.assertEquals("some_function(a)", self.fc.visit(node))

        node = ast.parse("some_function(a, b, c)")
        self.assertEquals("some_function(a, b, c)", self.fc.visit(node))

        node = ast.parse("some_function(*args)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_function(a, b, *args)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_function(a, b, param1=c)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_function(a, b, param1=c, param2=d)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method()")
        self.assertEquals("x.some_method()", self.fc.visit(node))

        node = ast.parse("x.some_method(1)")
        self.assertEquals("x.some_method(1)", self.fc.visit(node))

        node = ast.parse("x.some_method(1, 2, 3)")
        self.assertEquals("x.some_method(1, 2, 3)", self.fc.visit(node))

        node = ast.parse("x.some_method(a)")
        self.assertEquals("x.some_method(a)", self.fc.visit(node))

        node = ast.parse("x.some_method(a, b, c)")
        self.assertEquals("x.some_method(a, b, c)", self.fc.visit(node))

        node = ast.parse("x.some_method(*args)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a, b, *args)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a, b, param1=c)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.some_method(a, b, param1=c, param2=d)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_ifexp(self):
        node = ast.parse("a if test else b")
        self.assertEquals("(test ? a : b)", self.fc.visit(node))

        node = ast.parse("1 if test else 0")
        self.assertEquals("(test ? 1 : 0)", self.fc.visit(node))

        node = ast.parse("1 if a or b else 0")
        self.assertEquals("((a || b) ? 1 : 0)", self.fc.visit(node))

        node = ast.parse("1 if a or b and c else 0")
        self.assertEquals("((a || (b && c)) ? 1 : 0)", self.fc.visit(node))

        node = ast.parse("a if test1 and test2 else b")
        self.assertEquals("((test1 && test2) ? a : b)", self.fc.visit(node))

        node = ast.parse("a_func() if a or b and c else other_func()")
        self.assertEquals("((a || (b && c)) ? a_func() : other_func())", self.fc.visit(node))

        node = ast.parse("a if test_func() else b")
        self.assertEquals("(test_func() ? a : b)", self.fc.visit(node))

    def test_attribute(self):
        node = ast.parse("x.field1")
        self.assertEqual("x.field1", self.fc.visit(node))

        node = ast.parse("x._field2")
        self.assertEqual("x._field2", self.fc.visit(node))

        node = ast.parse("x.some_method")
        self.assertEqual("x.some_method", self.fc.visit(node))

        # x.123 is not valid and should not parse
        self.assertRaises(SyntaxError, ast.parse, "x.123")

    def test_subscript(self):
        """
        This test is covered by:
        test_index
        test_slice
        test_ext_slice
        """

    def test_index(self):
        node = ast.parse("some_list[0]")
        self.assertEqual("some_list[0]", self.fc.visit(node))

        node = ast.parse("some_list[i]")
        self.assertEqual("some_list[i]", self.fc.visit(node))

        node = ast.parse("some_list[i + j]")
        self.assertEqual("some_list[(i + j)]", self.fc.visit(node))

        node = ast.parse("some_list[func()]")
        self.assertEqual("some_list[func()]", self.fc.visit(node))

        node = ast.parse("some_list[func1() + func2()]")
        self.assertEqual("some_list[(func1() + func2())]", self.fc.visit(node))

        node = ast.parse("some_list[func(i) + func(j)]")
        self.assertEqual("some_list[(func(i) + func(j))]", self.fc.visit(node))

        node = ast.parse("some_list[x.some_method()]")
        self.assertEqual("some_list[x.some_method()]", self.fc.visit(node))

        node = ast.parse("some_list[x.some_method(i)]")
        self.assertEqual("some_list[x.some_method(i)]", self.fc.visit(node))

        node = ast.parse("get_list()[x.some_method(i)]")
        self.assertEqual("get_list()[x.some_method(i)]", self.fc.visit(node))

        node = ast.parse("x.get_list()[x.some_method(i)]")
        self.assertEqual("x.get_list()[x.some_method(i)]", self.fc.visit(node))

    def test_slice(self):
        node = ast.parse("some_list[0:5]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[i:i+5]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[i + j : i + j + 5]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[func1() : func2()]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[func(i) : func(j)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[x.some_method(i) : x.some_method(j)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("get_list()[1:5]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.get_list()[x.some_method(i): x.some_method(j)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_ext_slice(self):
        node = ast.parse("some_list[0:5, 3]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[i:i+5, i+7]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[i + j : i + j + 5, i + j + 8]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[func1() : func2(), func2() + 2]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[func(i) : func(j), func(j) + func(i)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("some_list[x.some_method(i) : x.some_method(j), x.some_method(k)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("get_list()[1:5, 7]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("x.get_list()[x.some_method(i): x.some_method(j), s.some_method(k)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_list_comp(self):
        node = ast.parse("[i * 2 for i in range(1, 1000)]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[item for item in a_list]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[(item1, item2) for item in some_tuples]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[func(item) for item in a_list]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[item for item in get_list()]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("[item for item in x.get_list()]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_set_comp(self):
        node = ast.parse("{i * 2 for i in range(1, 1000)}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{item for item in a_list}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{(item1, item2) for item in some_tuples}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{func(item) for item in a_list}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{item for item in get_list()}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{item for item in x.get_list()}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_gen_exp(self):
        node = ast.parse("(i * 2 for i in range(1, 1000))")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(item for item in a_list)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("((item1, item2) for item in some_tuples)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(func(item) for item in a_list)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(item for item in get_list())")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("(item for item in x.get_list())")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_dict_comp(self):
        node = ast.parse("{key: value for key, value in some_tuples}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{key: func(key) for key in a_list}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{x: 3*x for x in a_list}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{key: value for key, value in get_pairs()}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("{key: value for key, value in x.get_pairs()}")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_assign(self):
        class TestClass:
            pass

        # initial use of a1
        node = ast.parse("a1 = 1234")
        self.assertEquals("auto a1 = 1234", self.fc.visit(node))

        # reassignment of a1
        node = ast.parse("a1 = func()")
        self.assertEquals("a1 = func()", self.fc.visit(node))

        #initial use of a2
        node = ast.parse("a2 = func(x, y)")
        self.assertEquals("auto&& a2 = func(x, y)", self.fc.visit(node))

        node = ast.parse("a2.some_field = 1234")
        self.assertEquals("a2.some_field = 1234", self.fc.visit(node))

        # reassignment of a2
        node = ast.parse("a2 = b.some_method()")
        self.assertEquals("a2 = b.some_method()", self.fc.visit(node))

        node = ast.parse("a2 = b + c")
        self.assertEquals("a2 = (b + c)", self.fc.visit(node))

        node = ast.parse("a2 = b + func(c)")
        self.assertEquals("a2 = (b + func(c))", self.fc.visit(node))

        node = ast.parse("a2 = c.some_method() + b")
        self.assertEquals("a2 = (c.some_method() + b)", self.fc.visit(node))

        node = ast.parse("a2 = b + c.some_method(x)")
        self.assertEquals("a2 = (b + c.some_method(x))", self.fc.visit(node))

        #initial declaration of a3
        # assign a non-primitive
        self.fc.func_repr.args.append("var")
        self.fc.func_repr.arg_types.append(TestClass)

        node = ast.parse("a3 = var")
        self.assertEquals("auto&& a3 = var", self.fc.visit(node))

        # initial declaration of a4
        # assign a list
        self.fc.func_repr.args.append("var_list")
        self.fc.func_repr.arg_types.append("List<TestClass>")

        node = ast.parse("a4 = var_list")
        self.assertEquals("auto&& a4 = var_list", self.fc.visit(node))

        # initial declaration of a5
        # assign a non primitive list item
        node = ast.parse("a5 = var_list[3]")
        self.assertEquals("auto&& a5 = var_list[3]", self.fc.visit(node))

        # initial declaration of a6
        # assign a primitive list item
        self.fc.func_repr.args.append("var_list2")
        self.fc.func_repr.arg_types.append("List<int>")

        node = ast.parse("a6 = var_list2[3]")
        self.assertEquals("auto a6 = var_list2[3]", self.fc.visit(node))

        # not an initial declaration
        node = ast.parse("a_list[5] = func(x)")
        self.assertEquals("a_list[5] = func(x)", self.fc.visit(node))

        # this is only valid if get_list() returns a reference!
        node = ast.parse("get_list()[0] = func(y)")
        self.assertEquals("get_list()[0] = func(y)", self.fc.visit(node))

        # unpacking not allowed
        node = ast.parse("a, b = get_tuple()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a, b = (1, 2)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a, b = get_tuple(x)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        # multiple assignment not allowed
        node = ast.parse("a = b = c = 1")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("a = b = c = func(d)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_aug_assign(self):
        # a1 already declared
        self.fc.local_vars["a1"] = None

        node = ast.parse("a1 += 1234")
        self.assertEquals("a1 = a1 + 1234", self.fc.visit(node))

        # reassignment of a1
        node = ast.parse("a1 /= func()")
        self.assertEquals("a1 = a1 / func()", self.fc.visit(node))

        #initial use of a2
        node = ast.parse("a2 &= func(x, y)")
        self.assertEquals("a2 = a2 & func(x, y)", self.fc.visit(node))

        node = ast.parse("a2.some_field %= 1234")
        self.assertEquals("a2.some_field = a2.some_field % 1234", self.fc.visit(node))

        # reassignment of a2
        node = ast.parse("a2 *= b.some_method()")
        self.assertEquals("a2 = a2 * b.some_method()", self.fc.visit(node))

        node = ast.parse("a2 -= b + c")
        self.assertEquals("a2 = a2 - (b + c)", self.fc.visit(node))

        node = ast.parse("a2 += c.some_method() + b")
        self.assertEquals("a2 = a2 + (c.some_method() + b)", self.fc.visit(node))

        node = ast.parse("a2 /= b + c.some_method(x)")
        self.assertEquals("a2 = a2 / (b + c.some_method(x))", self.fc.visit(node))

        # not an initial declaration
        node = ast.parse("a_list[5] >>= func(x)")
        self.assertEquals("a_list[5] = a_list[5] >> func(x)", self.fc.visit(node))

        # this is only valid if get_list() returns a reference!
        node = ast.parse("get_list()[0] <<= func(y)")
        self.assertEquals("get_list()[0] = get_list()[0] << func(y)", self.fc.visit(node))

    def test_raise(self):
        # no exceptions allowed
        node = ast.parse("raise SyntaxError(\"message\")")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_assert(self):
        node = ast.parse("assert True")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("assert a + b > 0")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("assert a and b")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("assert check_condition()")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("assert x.check_condition(b)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_delete(self):
        # no del allowed
        node = ast.parse("del a_list[3]")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("del a")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_pass(self):
        node = ast.parse("pass")
        self.assertEquals("", self.fc.visit(node))

    def test_import(self):
        node = ast.parse("import a_module")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("import a_module.a_class")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("import a_module as m")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("import a_module.a_class as c")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_import_from(self):
        node = ast.parse("from a_module import a_class")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("from a_module import a_class as c")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("from . import a_module")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("from . import a_module as m")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_if(self):
        input_code = """
if a:
    b = func()
    c.some_method(d)
    if a and b or c:
        b.some_method(e)
    elif d < c.some_method2():
        c.some_method(e)
    else:
        a = func2(a)
else:
    a = func3(a)
"""
        output_code = """\
if (a) {
    auto&& b = func();
    c.some_method(d);
    if (((a && b) || c)) {
        b.some_method(e);
    } else {
        if ((d < c.some_method2())) {
            c.some_method(e);
        } else {
            a = func2(a);
        }
    }
} else {
    a = func3(a);
}\
"""
        self.fc.local_vars["a"] = None
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

    def test_for(self):
        input_code = """
for i in range(5, 1000, 5):
    b = func(i)
    for a in a_list:
        a.some_method(b)
        a.some_other_method(b)
        for j in range(len(another_list)):
            another_list[j].some_method()
"""
        output_code = """\
auto __iterator_1 = RangeIterator(5, 1000, 5);
while(__iterator_1.has_next()) {
    int i = __iterator_1.next();
    auto&& b = func(i);
    auto __iterator_2 = ListIterator<SomeClass>(a_list);
    while (__iterator_2.has_next()) {
        SomeClass &a = __iterator_2.next();
        a.some_method(b);
        a.some_other_method(b);
        auto __iterator_3 = RangeIterator(0, len(another_list), 1);
        while(__iterator_3.has_next()) {
            int j = __iterator_3.next();
            another_list[j].some_method();
        }
    }
}\
"""
        self.fc.local_vars["a_list"] = "List<SomeClass>" # a_list is a list
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

    def test_while(self):
        input_code = """\
while True:
    a = func1()
    b = func2()
    while a and b and a < b:
        a += 1
        b -= 1
    if a > b:
        break
    elif a == b:
        continue
"""
        output_code = """\
while (true) {
    auto&& a = func1();
    auto&& b = func2();
    while ((a && b && (a < b))) {
        a = a + 1;
        b = b - 1;
    }
    if ((a > b)) {
        break;
    } else {
        if ((a == b)) {
            continue;
        }
    }
}\
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

    def test_break(self):
        node = ast.parse("break")
        self.assertEquals("break", self.fc.visit(node))

    def test_continue(self):
        node = ast.parse("continue")
        self.assertEquals("continue", self.fc.visit(node))

    def test_try(self):
        input_code = """
try:
    a = b
    a.some_method(x)
    if a.check_condition():
        a.some_other_method(y)
except Error1:
    a.reset()
except Error2:
    pass
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_with(self):
        input_code = """
with some_func(x) as val:
    val.do_something()
    if val.check_something():
        val.do_something_else()
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

        input_code = """
with v as val:
    val.do_something()
    if val.check_something():
        val.do_something_else()
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_func_def(self):
        func_repr = FunctionRepresentation("get_length", ["x", "y", "z"],
                                           [float, float, float], float, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
def get_length(x, y, z):
    x_sq = x * x
    y_sq = y * y
    z_sq = z * z
    return sqrt(x_sq + y_sq + z_sq)
"""
        output_code = """\
__device__ float get_length(float x, float y, float z) {
    auto x_sq = (x * x);
    auto y_sq = (y * y);
    auto z_sq = (z * z);
    return sqrt(((x_sq + y_sq) + z_sq));
}
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

        func_repr = FunctionRepresentation("get_remainder", ["numerator", "denominator"],
                                           [int, int], int, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
def get_remainder(numerator, denominator):
    temp = numerator
    while temp - denominator > 0:
        temp -= denominator
    return temp
"""
        output_code = """\
__device__ int get_remainder(int numerator, int denominator) {
    auto temp = numerator;
    while (((temp - denominator) > 0)) {
        temp = temp - denominator;
    }
    return temp;
}
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

        class Vector3D:
            pass

        func_repr = FunctionRepresentation("get_length", ["v"], [Vector3D], float, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
def get_length(v):
    x_sq = v.x * v.x
    y_sq = v.y * v.y
    z_sq = v.z * v.z
    return sqrt(x_sq + y_sq + z_sq)
"""

        output_code = """\
__device__ float get_length(Vector3D&& v) {
    auto x_sq = (v.x * v.x);
    auto y_sq = (v.y * v.y);
    auto z_sq = (v.z * v.z);
    return sqrt(((x_sq + y_sq) + z_sq));
}
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

        func_repr = FunctionRepresentation("get_length", ["v"], [Vector3D], float, None)
        self.fc = FunctionConverter(func_repr, refs=[True])

        input_code = """
def get_length(v):
    x_sq = v.x * v.x
    y_sq = v.y * v.y
    z_sq = v.z * v.z
    return sqrt(x_sq + y_sq + z_sq)
"""

        output_code = """\
__device__ float get_length(Vector3D& v) {
    auto x_sq = (v.x * v.x);
    auto y_sq = (v.y * v.y);
    auto z_sq = (v.z * v.z);
    return sqrt(((x_sq + y_sq) + z_sq));
}
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.fc.visit(node))

        func_repr = FunctionRepresentation("get_length", ["v"], [Vector3D], float, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
def get_length(v):
    def calc_length(x, y, z):
        x_sq = x * x
        y_sq = y * y
        z_sq = z * z
        return sqrt(x_sq + y_sq + z_sq)
    return calc_length(v.x, v.y, v.z)
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_lambda(self):
        node = ast.parse("lambda x: x + 1")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("lambda x: func(x)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("lambda x, y: x + y")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_return(self):
        node = ast.parse("return")
        self.assertEquals("return", self.fc.visit(node))

        node = ast.parse("return a")
        self.assertEquals("return a", self.fc.visit(node))

        node = ast.parse("return a + b")
        self.assertEquals("return (a + b)", self.fc.visit(node))

        node = ast.parse("return 1")
        self.assertEquals("return 1", self.fc.visit(node))

        node = ast.parse("return True")
        self.assertEquals("return true", self.fc.visit(node))

        node = ast.parse("return func(x)")
        self.assertEquals("return func(x)", self.fc.visit(node))

        node = ast.parse("return x.some_method(y)")
        self.assertEquals("return x.some_method(y)", self.fc.visit(node))

    def test_yield(self):
        node = ast.parse("yield a")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield a + b")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield 1")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield True")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield func(x)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield x.some_method(y)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_yield_from(self):
        node = ast.parse("yield from a_generator")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield from get_generator(x)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

        node = ast.parse("yield from x.get_generator(y)")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_global(self):
        node = ast.parse("global var")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_nonlocal(self):
        node = ast.parse("nonlocal var")
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_ClassDef(self):
        input_code = """
class TestClass:
    def __init__(a, b):
        self.a = a
        self.b = b

    def some_method(arg1, arg2):
        return arg1 + arg2
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

    def test_async_func_def(self):
        func_repr = FunctionRepresentation("get_length", ["x", "y", "z"],
                                           [float, float, float], float, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
async def get_length(x, y, z):
    x_sq = x * x
    y_sq = y * y
    z_sq = z * z
    return sqrt(x_sq + y_sq + z_sq)
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

        func_repr = FunctionRepresentation("get_remainder", ["numerator", "denominator"],
                                           [int, int], int, None)
        self.fc = FunctionConverter(func_repr)

        input_code = """
async def get_remainder(numerator, denominator):
    temp = numerator
    while temp - denominator > 0:
        temp -= denominator
    return temp
"""

        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.fc.visit, node)

class TestMethodConverter(TestCase):
    class Vector1D:
        def __init__(self, v):
            self.v = v

    class Vector3D:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    def setUp(self):
        method_repr = MethodRepresentation(TestMethodConverter.Vector3D,
                                           "get_length", ["self"],
                                           [TestMethodConverter.Vector3D], float, None)
        v = TestMethodConverter.Vector3D(3,
                                         TestMethodConverter.Vector1D(4),
                                         TestMethodConverter.Vector1D(5))
        extracted = ExtractedClasses()
        class_repr = extracted.extract(v)
        self.mc = MethodConverter(class_repr, method_repr)

    def test_name(self):
        node = ast.parse("x")
        self.assertEqual("x", self.mc.visit(node))

        node = ast.parse("val")
        self.assertEqual("val", self.mc.visit(node))

        node = ast.parse("_val")
        self.assertEqual("_val", self.mc.visit(node))

        node = ast.parse("a_val")
        self.assertEqual("a_val", self.mc.visit(node))

        node = ast.parse("Val")
        self.assertEqual("Val", self.mc.visit(node))

        node = ast.parse("self")
        self.assertEqual("(*this)", self.mc.visit(node))

        node = ast.parse("selfxyz")
        self.assertEqual("selfxyz", self.mc.visit(node))

    def test_attribute(self):
        node = ast.parse("self.field1")
        self.assertEqual("(*this).field1", self.mc.visit(node))

        node = ast.parse("self._field2")
        self.assertEqual("(*this)._field2", self.mc.visit(node))

        node = ast.parse("self.some_method")
        self.assertEqual("(*this).some_method", self.mc.visit(node))

    def test_assign(self):
        class TestClass:
            pass

        # initial use of a1
        node = ast.parse("a1 = 1234")
        self.assertEquals("auto a1 = 1234", self.mc.visit(node))

        # reassignment of a1
        node = ast.parse("a1 = func()")
        self.assertEquals("a1 = func()", self.mc.visit(node))

        #initial use of a2
        node = ast.parse("a2 = func(x, y)")
        self.assertEquals("auto&& a2 = func(x, y)", self.mc.visit(node))

        node = ast.parse("a2.some_field = 1234")
        self.assertEquals("a2.some_field = 1234", self.mc.visit(node))

        # reassignment of a2
        node = ast.parse("a2 = b.some_method()")
        self.assertEquals("a2 = b.some_method()", self.mc.visit(node))

        node = ast.parse("a2 = b + c")
        self.assertEquals("a2 = (b + c)", self.mc.visit(node))

        node = ast.parse("a2 = b + func(c)")
        self.assertEquals("a2 = (b + func(c))", self.mc.visit(node))

        node = ast.parse("a2 = c.some_method() + b")
        self.assertEquals("a2 = (c.some_method() + b)", self.mc.visit(node))

        node = ast.parse("a2 = b + c.some_method(x)")
        self.assertEquals("a2 = (b + c.some_method(x))", self.mc.visit(node))

        #initial declaration of a3
        # assign a non-primitive
        self.mc.func_repr.args.append("var")
        self.mc.func_repr.arg_types.append(TestClass)

        node = ast.parse("a3 = var")
        self.assertEquals("auto&& a3 = var", self.mc.visit(node))

        # initial declaration of a4
        # assign a list
        self.mc.func_repr.args.append("var_list")
        self.mc.func_repr.arg_types.append("List<TestClass>")

        node = ast.parse("a4 = var_list")
        self.assertEquals("auto&& a4 = var_list", self.mc.visit(node))

        # initial declaration of a5
        # assign a non primitive list item
        node = ast.parse("a5 = var_list[3]")
        self.assertEquals("auto&& a5 = var_list[3]", self.mc.visit(node))

        # initial declaration of a6
        # assign a primitive list item
        self.mc.func_repr.args.append("var_list2")
        self.mc.func_repr.arg_types.append("List<int>")

        node = ast.parse("a6 = var_list2[3]")
        self.assertEquals("auto a6 = var_list2[3]", self.mc.visit(node))

        node = ast.parse("a7 = self.x")
        self.assertEquals("auto a7 = (*this).x", self.mc.visit(node))

        node = ast.parse("a8 = self.y")
        self.assertEquals("auto&& a8 = (*this).y", self.mc.visit(node))

        node = ast.parse("a9 = self")
        self.assertEquals("auto&& a9 = (*this)", self.mc.visit(node))

        # not an initial declaration
        node = ast.parse("a_list[5] = func(x)")
        self.assertEquals("a_list[5] = func(x)", self.mc.visit(node))

        # this is only valid if get_list() returns a reference!
        node = ast.parse("get_list()[0] = func(y)")
        self.assertEquals("get_list()[0] = func(y)", self.mc.visit(node))

        # unpacking not allowed
        node = ast.parse("a, b = get_tuple()")
        self.assertRaises(SyntaxError, self.mc.visit, node)

        node = ast.parse("a, b = (1, 2)")
        self.assertRaises(SyntaxError, self.mc.visit, node)

        node = ast.parse("a, b = get_tuple(x)")
        self.assertRaises(SyntaxError, self.mc.visit, node)

        # multiple assignment not allowed
        node = ast.parse("a = b = c = 1")
        self.assertRaises(SyntaxError, self.mc.visit, node)

        node = ast.parse("a = b = c = func(d)")
        self.assertRaises(SyntaxError, self.mc.visit, node)

    def test_func_def(self):
        input_code = """
def get_length(self):
    x_sq = self.x * self.x
    y_sq = self.y.val * self.y.val
    z_sq = self.z.val * self.z.val
    return sqrt(x_sq + y_sq + z_sq)
"""
        output_code = """\
__device__ float Vector3D::get_length() {
    auto x_sq = ((*this).x * (*this).x);
    auto y_sq = ((*this).y.val * (*this).y.val);
    auto z_sq = ((*this).z.val * (*this).z.val);
    return sqrt(((x_sq + y_sq) + z_sq));
}
"""
        node = ast.parse(input_code)
        self.assertEquals(output_code, self.mc.visit(node))


        input_code = """
def get_length(self):
    def calc_length(x, y, z):
        x_sq = x * x
        y_sq = y * y
        z_sq = z * z
        return sqrt(x_sq + y_sq + z_sq)
    return calc_length(self.x, self.y.val, self.z.val)
"""
        node = ast.parse(input_code)
        self.assertRaises(SyntaxError, self.mc.visit, node)
