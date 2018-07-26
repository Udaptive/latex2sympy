# flake8: noqa

from latex2sympy import process_sympy
from sympy import \
    Eq, Rational, Add, Mul, Pow, Abs, Limit, Derivative, Integral, \
    E, I, pi, oo, Symbol, \
    sqrt, exp, ln, sin, cos, tan, csc, sec, cot, asin, acos, atan, acot, \
    sinh, cosh, tanh, asinh, factorial2, re, im, div, simplify
from sympy.abc import x, y, theta
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing import latex
import numpy as np


def equivalent( expr1, expr2 ):
    if expr1.is_Equality != expr2.is_Equality:
        # Equation vs. expression
        return False
    if expr1.is_Equality:
        # Test for equivalent equations
        # Two equations are equivalent if they are linearly dependent
        # This can be checked by taking RHS - LHS for the equations and seeing if they are multiples
        d1 = simplify( ( expr1.rhs - expr1.lhs ).expand() )
        d2 = simplify( ( expr2.rhs - expr2.lhs ).expand() )
        # Handle boundary case of zero
        if d1 == 0 or d2 == 0:
            return d1 == d2
        # Check for linear dependence
        q, r = div( d1, d2 )
        return q.is_number and r == 0
    # Test for equivalent expressions, using progressively stronger tactics
    # First check for identical expressions after simplification; this is for expressions involving infinity
    if simplify( expr1 ) == simplify( expr2 ):
        return True
    # Expressions are equivalent iff their difference simplifies to zero
    try:
        equiv = simplify( expr2 - expr1 ) == 0
    except NotImplementedError:
        print 'sympy could not simplify', expr2 - expr1
        equiv = False
    return equiv

# Generate a random expression

vars = [ x, y, Symbol( 'Z' ), theta ]
ops = list( '+-*/^' )
funcs = [ sqrt, sin, cos, tan, exp, sinh, cosh, tanh, Abs, Limit, Derivative, Integral, ]#'ln', 'log' ]

def apply_func( term, var ):
    func = np.random.choice( funcs )
    if func == Limit:
        term = func( term, var, np.random.choice( [ -oo, 0, oo ] ) )
    elif func == Derivative:
        term = func( term, var, np.random.randint( 1, high=4 ) )
    elif func == Integral:
        if np.random.rand() < 0.5:
            # Indefinite
            term = func( term, var )
        else:
            # Definite
            llim = np.random.choice( [ np.random.randint( 1, high=21 ), Symbol( 'a' ) ] )
            ulim = llim + np.random.choice( [ np.random.randint( 1, high=21 ), Symbol( 'b' ) ] )
            term = func( term, ( var, llim, ulim ) )
    else:
        term = func( term )
    return term

def generate_term():
    coef = np.random.randint( 1, high=21 )
    var = np.random.choice( vars )
    power = np.random.randint( 0, high=6 )
    term = coef * var ** power
    if np.random.rand() < 0.5:
        # Apply a function to the term
        term = apply_func( term, var )
        if np.random.rand() < 0.2:
            # Use function composition
            term = apply_func( term, var )
    return term

class TestLatex(object):

# Test approach 1:
#   Create test case in sympy
#   Convert to latex
#   Test if equivalent to original sympy object

    def test_static_cases(self):

        test_cases = [
        # Linear algebra
            1*x,
            Eq( 8*x, 0 ),
            Eq( 10*x, 5 ),
            Eq( x-4*x, -21 ),
            Eq( 3*x, 21 ),
            Eq( 2 + 5, x ),
            Eq( 3*(x - 4), x ),
            Eq( 12, 2*x ),
            Eq( 3*(x - 4)/x, 1 ),
            Eq( 12/x, 2 ),
            0.5*x + 0.1,
            Rational( 1, 10 ) + Rational( 1, 2 )*x,
            Add( x, 2*x, -3*x, evaluate=False ),
        # Trigonometry
            sin(x),
            cos(x),
            tan(x),
            csc(x),
            sec(x),
            cot(x),
            1 - sin(x)**2,
            cos(x)**2,
            Eq( sin(x)**2, x ),
            Eq( -x, 1 - cos(x)**2 - 2*x ),
            sin(2*x),
            2*sin(x)*cos(x),
            Eq( 1 - sin(2*x), 0 ),
            Eq( sin(x)**2, 2*sin(x)*cos(x) - cos(x)**2 ),
            cos(x*y),
            acos(x),
            Pow( cos(x), 1, evaluate=False ),
            Pow( cos(x), 0, evaluate=False ),
        # Hyperbolic functions
            sinh(x),
            cosh(x),
            tanh(x),
            #csch(x),
            #sech(x),
            #coth(x),
        # Exponential
            E,
            sqrt(E),
            E**x,
            exp(x),
            exp(ln(x), evaluate=False),
        # Imaginary/Complex
            I,
            3 + 8*I,
            re(x+I*y, evaluate=False),
            im(x+y*I, evaluate=False),
            re(1-I, evaluate=False),
            im(1-I, evaluate=False),
            E**(I*theta),
        # Infinity
            oo,
            Add( oo, oo, evaluate=False ),
            Add( oo, Mul( 3, oo, evaluate=False ), evaluate=False ),
            -oo,
            Add( -oo, -oo, evaluate=False ),
            Mul( -2, oo, evaluate=False ),
            Mul( -2, -oo, evaluate=False ),
            Mul( -2, -oo, -5, evaluate=False ),
        # Calculus
            Limit(x**2, x, theta),
        # Miscellaneous
            Abs(x),
            parse_expr( 'n!' ),
            parse_expr( 'n!!' ),
            factorial2(2*x+y),
            pi,
            Pow(0, 0, evaluate=False),
            ]

        failed_tests = []
        for expr in test_cases:
            try:
                s_l_expr = latex( expr )
                l_expr = process_sympy( s_l_expr )
                equiv = equivalent( expr, l_expr )
                e = None
            except Exception as e:
                # Parsing failed
                l_expr = None
                equiv = False
            if not equiv:
                print '%s %s' % ( s_l_expr, 'PASSED' if equiv else 'FAILED' )
                failed_tests.append( ( s_l_expr, l_expr ) )
                print 'sympy: %s\nlatex: %s' % ( expr, l_expr )
                if e is not None:
                    print e
                print

        if failed_tests:
            print len( failed_tests ), 'failed test cases'
        assert len(failed_tests) == 0

    def test_generated_cases(self):

        failed_tests = []
        n_tests = 20
        print 'Generating', n_tests, 'test_cases\n'
        for _ in np.arange( n_tests ):
            n_terms = np.random.randint( 1, high=5 )
            expr = generate_term()
            for _ in np.arange( n_terms - 1 ):
                term = generate_term()
                op = np.random.choice( ops )
                if op == '+':
                    expr = expr + term
                elif op == '-':
                    expr = expr - term
                elif op == '*':
                    expr = expr * term
                elif op == '/':
                    expr = expr / term
                elif op == '^':
                    expr = expr ** term
                else:
                    assert False
            s_l_expr = latex( expr )
            try:
                l_expr = process_sympy( s_l_expr )
                equiv = equivalent( expr, l_expr )
                e = None
            except Exception as e:
                # Parsing failed
                l_expr = None
                equiv = False
            if not equiv:
                print '%s %s' % ( s_l_expr, 'PASSED' if equiv else 'FAILED' )
                failed_tests.append( ( s_l_expr, l_expr ) )
                print 'sympy: %s\nlatex: %s' % ( expr, l_expr )
                if e is not None:
                    print e
                print

        if failed_tests:
            print len( failed_tests ), 'failed test cases'
        assert len(failed_tests) == 0

# A limitation of test approach 1 is the sympy object used to generate the latex could have simplified the original input
# provided to the sympy parser, removing the opportunity to test the original, unsimplified version.

# Test approach 2:
#   Write test case in latex and construct equivalent sympy object
#   Parse and test for equivalence
# This is useful for testing latex that can't conveniently be generated from a sympy object

    def test_explicit_latex(self):

        test_cases = [
            ( '0x', Mul( 0, x, evaluate=False ) ),
            ( '0 = 0', Eq( 0, 0 ) ),
            ( '0 = 1', Eq( 0, 1 ) ),
            ( '10x = 10x', Eq( 10*x, 10*x ) ),
            ( r'\sin ^ { - 1 } ( x )', asin(x) ),
            ( r'\cos^{-1}x', acos(x) ),
            ( r'\tan^ {-1 }x', atan(x) ),
            ( r'\cot^ {-1 }x', acot(x) ),
            ( r'\sinh^{-1}(x)', asinh(x) ),
            ( r'\sqrt{-1}', I ),
            ( r'\exp{x}', exp(x) ),
            ( r'\exp(x)', exp(x) ),
            ( 'e^{x}', E**x ),
            ]

        failed_tests = []
        for s_l_expr, expr in test_cases:
            l_expr = process_sympy( s_l_expr )
            equiv = equivalent( expr, l_expr )
            if not equiv:
                print '%s %s' % ( s_l_expr, 'PASSED' if equiv else 'FAILED' )
                failed_tests.append( ( s_l_expr, l_expr ) )
                print 'sympy: %s\nlatex: %s\n' % ( expr, l_expr )

        if failed_tests:
            print len( failed_tests ), 'failed test cases'
        assert len(failed_tests) == 0

# Test approach 3
# Test cases that should fail to parse

    def test_parsing_failures(self):

        test_cases = [
            r'\poo', # \poo is not a control sequence
            r'\sqrt{\x}', # \x is not a control sequence
        # Syntax errors
            '(x',
            'x)',
            '{x',
            '}x',
            'x}',
            'x{',
            '{',
            '}',
            'x^',
            'x_',
            'x^_',
            'x_^',
        # Misinterpreted legitimate control sequences do not fail and give incorrect output; treat them as cases that should fail until interpreted
            r'\frac{\partial^2U}{\partial y^2}', # partial derivative
            r'\cos 90^\circ', # degrees
            r'\cfrac{2}{1+\cfrac{2}{1+\cfrac{2}{1+\cfrac{2}{1}}}}', # continued fraction
            r'\dfrac{1}{2}', # display mode
            r'\binom{9}{3}', # binomial coefficient
            ]

        failed_tests = []
        for s_l_expr in test_cases:
            try:
                l_expr = process_sympy( s_l_expr )
                passed = False
            except:
                passed = True
            if not passed:
                print '%s %s' % ( s_l_expr, 'PASSED' if passed else 'FAILED' )
                failed_tests.append( ( s_l_expr, l_expr ) )
                print '  %s\n' % l_expr

        if failed_tests:
            print len( failed_tests ), 'failed test cases'
        assert len(failed_tests) == 0

# Test approach 4
# Test cases that should parse but for which the equivalent sympy input is not yet known
# These should eventually all be moved into one of the other test groups

    def test_nyi(self):

        test_cases = [
            r'\int^5_1 2x\,dx = 24', # small space \,
            ]

        failed_tests = []
        for s_l_expr in test_cases:
            try:
                l_expr = process_sympy( s_l_expr )
                passed = True
                e = None
            except Exception as e:
                passed = False
                l_expr = None
            if not passed:
                failed_tests.append( ( s_l_expr, l_expr ) )
                print '%s %s' % ( s_l_expr, 'PASSED' if passed else 'FAILED' )
                if e is not None:
                    print '%s\n' % e

        if failed_tests:
            print len( failed_tests ), 'failed test cases'
        assert len(failed_tests) == 0
