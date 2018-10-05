import unittest
import sympy
from sympy.abc import x, y, z, a, b, c, f, t, k, n

from latex2sympy import process_sympy


theta = sympy.Symbol('theta')


# shorthand definitions
def _Add(a, b):
    return sympy.Add(a, b, evaluate=False)


def _Mul(a, b):
    return sympy.Mul(a, b, evaluate=False)


def _Pow(a, b):
    return sympy.Pow(a, b, evaluate=False)


def _Abs(a):
    return sympy.Abs(a, evaluate=False)


def _factorial(a):
    return sympy.factorial(a, evaluate=False)


def _log(a, b):
    return sympy.log(a, b, evaluate=False)


# These latex strings should parse to the corresponding
# SymPy expression
GOOD_PAIRS = [
    ("0", 0),
    ("1", 1),
    ("-3.14", _Mul(-1, 3.14)),
    ("(-7.13)(1.5)", _Mul(_Mul(-1, 7.13), 1.5)),
    ("x", x),
    ("2x", 2 * x),
    ("x^2", x**2),
    ("x^{3 + 1}", x**_Add(3,1)),
    ("-c", -c),
    ("a \\cdot b", a * b),
    ("a / b", a / b),
    ("a \\div b", a / b),
    ("a + b", a + b),
    ("a + b - a", _Add(a + b, -a)),
    ("a^2 + b^2 = c^2", sympy.Eq(a**2 + b**2, c**2)),
    ("\\sin \\theta", sympy.sin(theta)),
    ("\\sin(\\theta)", sympy.sin(theta)),
    ("\\sin^{-1} a", sympy.asin(a)),
    ("\\sin a \\cos b", _Mul(sympy.sin(a), sympy.cos(b))),
    ("\\sin \\cos \\theta", sympy.sin(sympy.cos(theta))),
    ("\\sin(\\cos \\theta)", sympy.sin(sympy.cos(theta))),
    ("\\frac{a}{b}", a / b),
    ("\\frac{a + b}{c}", _Mul(a + b, _Pow(c,-1))),
    ("\\frac{7}{3}", _Mul(7, _Pow(3,-1))),
    ("(\\csc x)(\\sec y)", sympy.csc(x) * sympy.sec(y)),
    ("\\lim_{x \\to 3} a", sympy.Limit(a, x, 3)),
    ("\\lim_{x \\rightarrow 3} a", sympy.Limit(a, x, 3)),
    ("\\lim_{x \\Rightarrow 3} a", sympy.Limit(a, x, 3)),
    ("\\lim_{x \\longrightarrow 3} a", sympy.Limit(a, x, 3)),
    ("\\lim_{x \\Longrightarrow 3} a", sympy.Limit(a, x, 3)),
    ("\\lim_{x \\to 3^{+}} a", sympy.Limit(a, x, 3, dir='+')),
    ("\\lim_{x \\to 3^{-}} a", sympy.Limit(a, x, 3, dir='-')),
    ("\\infty", sympy.oo),
    ("\\lim_{x \\to \\infty} \\frac{1}{x}", sympy.Limit(_Mul(1, _Pow(x,-1)), x, sympy.oo)),
    ("\\frac{d}{dx} x", sympy.Derivative(x, x)),
    ("\\frac{d}{dt} x", sympy.Derivative(x, t)),
    ("f(x)", f(x)),
    ("f(x, y)", f(x, y)),
    ("f(x, y, z)", f(x, y, z)),
    ("\\frac{d f(x)}{dx}", sympy.Derivative(f(x), x)),
    ("\\frac{d\\theta(x)}{dx}", sympy.Derivative(theta(x), x)),
    ("|x|", _Abs(x)),
    ("||x||", _Abs(sympy.Abs(x))),
    ("|x||y|", _Abs(x) * _Abs(y)),
    ("||x||y||", _Abs(_Abs(x) * _Abs(y))),
    ("\pi^{|xy|}", sympy.Symbol('pi')**_Abs(x * y)),
    ("\\int x dx", sympy.Integral(x, x)),
    ("\\int x d\\theta", sympy.Integral(x, theta)),
    ("\\int (x^2 - y)dx", sympy.Integral(x**2 - y, x)),
    ("\\int x + a dx", sympy.Integral(_Add(x, a), x)),
    ("\\int da", sympy.Integral(1, a)),
    ("\\int_0^7 dx", sympy.Integral(1, (x, 0, 7))),
    ("\\int_a^b x dx", sympy.Integral(x, (x, a, b))),
    ("\\int^b_a x dx", sympy.Integral(x, (x, a, b))),
    ("\\int_{a}^b x dx", sympy.Integral(x, (x, a, b))),
    ("\\int^{b}_a x dx", sympy.Integral(x, (x, a, b))),
    ("\\int_{a}^{b} x dx", sympy.Integral(x, (x, a, b))),
    ("\\int^{b}_{a} x dx", sympy.Integral(x, (x, a, b))),
    ("\\int_{f(a)}^{f(b)} f(z) dz", sympy.Integral(f(z), (z, f(a), f(b)))),
    ("\\int (x+a)", sympy.Integral(_Add(x,a), x)),
    ("\\int a + b + c dx", sympy.Integral(_Add(_Add(a,b),c), x)),
    ("\\int \\frac{dz}{z}", sympy.Integral(sympy.Pow(z,-1), z)),
    ("\\int \\frac{3 dz}{z}", sympy.Integral(3 * sympy.Pow(z, -1), z)),
    ("\\int \\frac{1}{x} dx", sympy.Integral(sympy.Pow(x, -1), x)),
    ("\\int \\frac{1}{a} + \\frac{1}{b} dx", sympy.Integral(_Add(_Pow(a,-1), sympy.Pow(b,-1)),x)),
    ("\\int \\frac{3 \cdot d\\theta}{\\theta}", sympy.Integral(3 * _Pow(theta,-1), theta)),
    ("\\int \\frac{1}{x} + 1 dx", sympy.Integral(_Add(_Pow(x, -1), 1), x)),
    ("x_0", sympy.Symbol('x_{0}')),
    ("x_{1}", sympy.Symbol('x_{1}')),
    ("x_a", sympy.Symbol('x_{a}')),
    ("x_{b}", sympy.Symbol('x_{b}')),
    ("h_\\theta", sympy.Symbol('h_{theta}')),
    ("h_{\\theta}", sympy.Symbol('h_{theta}')),
    ("h_{\\theta}(x_0, x_1)", sympy.Symbol('h_{theta}')(sympy.Symbol('x_{0}'), sympy.Symbol('x_{1}'))),
    ("x!", _factorial(x)),
    ("100!", _factorial(100)),
    ("\\theta!", _factorial(theta)),
    ("(x + 1)!", _factorial(_Add(x, 1))),
    ("(x!)!", _factorial(_factorial(x))),
    ("x!!!", _factorial(_factorial(_factorial(x)))),
    ("5!7!", _Mul(_factorial(5), _factorial(7))),
    ("\\sqrt{x}", sympy.sqrt(x)),
    ("\\sqrt{x + b}", sympy.sqrt(_Add(x, b))),
    ("\\sqrt[3]{\\sin x}", sympy.root(sympy.sin(x), 3)),
    ("\\sqrt[y]{\\sin x}", sympy.root(sympy.sin(x), y)),
    ("\\sqrt[\\theta]{\\sin x}", sympy.root(sympy.sin(x), theta)),
    ("x < y", sympy.StrictLessThan(x, y)),
    ("x \\leq y", sympy.LessThan(x, y)),
    ("x > y", sympy.StrictGreaterThan(x, y)),
    ("x \\geq y", sympy.GreaterThan(x, y)),
    ("\\mathit{x}", sympy.Symbol('x')),
    ("\\mathit{test}", sympy.Symbol('test')),
    ("\\mathit{TEST}", sympy.Symbol('TEST')),
    ("\\mathit{HELLO world}", sympy.Symbol('HELLO world')),
    ("\\sum_{k = 1}^{3} c", sympy.Sum(c, (k, 1, 3))),
    ("\\sum_{k = 1}^3 c", sympy.Sum(c, (k, 1, 3))),
    ("\\sum^{3}_{k = 1} c", sympy.Sum(c, (k, 1, 3))),
    ("\\sum^3_{k = 1} c", sympy.Sum(c, (k, 1, 3))),
    ("\\sum_{k = 1}^{10} k^2", sympy.Sum(k**2, (k, 1, 10))),
    ("\\sum_{n = 0}^{\\infty} \\frac{1}{n!}", sympy.Sum(_Pow(_factorial(n),-1), (n, 0, sympy.oo))),
    ("\\prod_{a = b}^{c} x", sympy.Product(x, (a, b, c))),
    ("\\prod_{a = b}^c x", sympy.Product(x, (a, b, c))),
    ("\\prod^{c}_{a = b} x", sympy.Product(x, (a, b, c))),
    ("\\prod^c_{a = b} x", sympy.Product(x, (a, b, c))),
    ("\\ln x", _log(x, sympy.E)),
    ("\\ln xy", _log(x * y, sympy.E)),
    ("\\log x", _log(x, 10)),
    ("\\log xy", _log(x * y, 10)),
    ("\\log_2 x", _log(x, 2)),
    ("\\log_{2} x", _log(x, 2)),
    ("\\log_a x", _log(x, a)),
    ("\\log_{a} x", _log(x, a)),
    ("\\log_{11} x", _log(x, 11)),
    ("\\log_{a^2} x", _log(x, _Pow(a, 2))),
    ("[x]", x),
    ("[a + b]", _Add(a, b)),
    ("\\frac{d}{dx} [ \\tan x ]", sympy.Derivative(sympy.tan(x), x))
]


# These bad latex strings should raise an exception when parsed
BAD_STRINGS = [
    "(",
    ")",
    "a / b /",
    "\\frac{d}{dx}",
    "(\\frac{d}{dx})"
    "\\sqrt{}",
    "\\sqrt",
    "{",
    "}",
    "1.1.1",
    "\\mathit{x + y}",
    "\\mathit{21}",
    "\\frac{2}{}",
    "\\frac{}{2}",
    "\\int",
    "1 +",
    "a +",
    "!",
    "!0",
    "_",
    "^",
    "a // b",
    "a \\cdot \\cdot b",
    "a \\div \\div b",
    "|",
    "||x|",
    "()",
    "((((((((((((((((()))))))))))))))))",
    "-",
    "\\frac{d}{dx} + \\frac{d}{dt}",
    "f()",
    "f(,",
    "f(x,,y)",
    "f(x,y,",
    "\\sin^x",
    "\\cos^2",
    "\\cos 1 \\cos",
    "@","#","$","%","&","*",
    "\\",
    "~",
    "\\frac{(2 + x}{1 - x)}"
]


class Latex2SympyTestCase(unittest.TestCase):

    def test_good_pairs(self):
        for s, eq in GOOD_PAIRS:
            self.assertEqual(process_sympy(s), eq)

    def test_bad_strings(self):
        for s in BAD_STRINGS:
            try:
                process_sympy(s)
            except:
                pass
            else:
                self.fail('No exception raised for bad input %s' % s)
