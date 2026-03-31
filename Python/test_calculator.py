#!/usr/bin/env python3
"""
Automated Testing Suite for Smart Scientific Calculator
Tests all functionality with mathematically correct expected values
"""

import math
import time
import sys
import re
from dataclasses import dataclass
from typing import Union, List

# Import the calculator from the other file
from smart_calculator import SmartScientificCalculator


@dataclass
class TestCase:
    """Defines a single test case"""
    name: str
    expression: str
    expected: Union[float, int, str]
    tolerance: float = 1e-9
    description: str = ""


@dataclass  
class TestResult:
    """Results from running a test"""
    name: str
    expression: str
    expected: Union[float, int, str]
    actual: Union[float, int, str]
    passed: bool
    error_message: str = ""
    execution_time: float = 0.0


class CalculatorTester:
    """Automated tester for the calculator"""
    
    def __init__(self, calculator_class):
        self.calc_class = calculator_class
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
        
    def run_test(self, test_case: TestCase, calc=None) -> TestResult:
        calc = calc if calc else self.calc_class()
        start_time = time.time()
        
        try:
            actual = calc.calculate(test_case.expression)
            execution_time = time.time() - start_time
            
            # Handle different types of expected values
            if isinstance(test_case.expected, str):
                actual_str = str(actual).lower()
                expected_str = test_case.expected.lower()
                passed = expected_str in actual_str
            elif isinstance(test_case.expected, (int, float)):
                try:
                    passed = abs(float(actual) - float(test_case.expected)) <= test_case.tolerance
                except:
                    passed = False
            else:
                passed = actual == test_case.expected
            
            error_msg = "" if passed else f"Expected {test_case.expected}, got {actual}"
            
        except Exception as e:
            execution_time = time.time() - start_time
            actual = f"EXCEPTION: {str(e)}"
            passed = False
            error_msg = str(e)
        
        result = TestResult(
            name=test_case.name,
            expression=test_case.expression,
            expected=test_case.expected,
            actual=actual,
            passed=passed,
            error_message=error_msg,
            execution_time=execution_time
        )
        
        self.results.append(result)
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        return result
    
    def run_test_suite(self, test_cases: List[TestCase], suite_name: str = "Test Suite"):
        """Run a suite of tests"""
        print(f"\n{'='*70}")
        print(f"Running: {suite_name}")
        print(f"{'='*70}")
        shared_calc = self.calc_class() if "MEMORY" in suite_name else None
        
        for test in test_cases:
            result = self.run_test(test, shared_calc)
            status = "PASS:" if result.passed else "FAIL:"
            print(f"{status} | {test.name:30} | {test.expression:20} | Expected: {test.expected} | Got: {result.actual}")
            if not result.passed and result.error_message:
                print(f"     Error: {result.error_message}")
    
    def print_summary(self):
        """Print final test summary"""
        total = len(self.results)
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {total}")
        if total > 0:
            print(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
            print(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")
        
        if self.failed > 0:
            print(f"\nFailed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.expression}")
                    print(f"    Expected: {r.expected}, Got: {r.actual}")
        print(f"{'='*70}\n")


def get_all_test_cases():
    """Returns all test cases organized by category"""
    
    # 1. BASIC ARITHMETIC
    basic_arithmetic = [
        TestCase("Addition_simple", "2 + 3", 5),
        TestCase("Addition_no_spaces", "2+3", 5),
        TestCase("Addition_multiple", "2+3+4", 9),
        TestCase("Addition_negative", "5 + (-3)", 2),
        TestCase("Addition_decimals", "2.5 + 3.5", 6.0),
        TestCase("Subtraction_simple", "10 - 4", 6),
        TestCase("Subtraction_negative_result", "4 - 10", -6),
        TestCase("Subtraction_decimals", "5.5 - 2.2", 3.3, tolerance=1e-9),
        TestCase("Multiplication_simple", "6 * 7", 42),
        TestCase("Multiplication_no_spaces", "6*7", 42),
        TestCase("Multiplication_decimals", "2.5 * 4", 10.0),
        TestCase("Multiplication_negative", "-3 * 4", -12),
        TestCase("Division_simple", "8 / 2", 4.0),
        TestCase("Division_result_decimal", "7 / 2", 3.5),
        TestCase("Division_by_one", "5 / 1", 5.0),
        TestCase("Division_negative", "-10 / 2", -5.0),
        TestCase("Mixed_operations", "2 + 3 * 4", 14),
        TestCase("Mixed_with_parens", "(2 + 3) * 4", 20),
        TestCase("Complex_mixed", "10 - 2 * 3 + 4 / 2", 6.0),
    ]
    
    # 2. EXPONENTIATION (The critical fix!)
    exponentiation = [
        TestCase("Power_simple", "2**3", 8),
        TestCase("Power_caret_fixed", "2^3", 8, description="Caret -> ** conversion"),
        TestCase("Power_zero_exp", "5^0", 1),
        TestCase("Power_one_exp", "5^1", 5),
        TestCase("Power_negative_exp", "2^-2", 0.25),
        TestCase("Power_fractional", "9^0.5", 3.0),
        TestCase("Power_complex_expr", "10-2^2", 6),
        TestCase("Power_with_parens", "(2+3)^2", 25),
        TestCase("Power_chain", "2^3^2", 512),
        TestCase("Power_large", "2^10", 1024),
        TestCase("Power_sqrt_equiv", "9^(1/2)", 3.0),
    ]
    
    # 3. TRIGONOMETRY
    trigonometry = [
        TestCase("Sin_zero", "sin(0)", 0.0),
        TestCase("Sin_pi/2", "sin(pi/2)", 1.0, tolerance=1e-9),
        TestCase("Sin_pi", "sin(pi)", 0.0, tolerance=1e-9),
        TestCase("Cos_zero", "cos(0)", 1.0),
        TestCase("Cos_pi/2", "cos(pi/2)", 0.0, tolerance=1e-9),
        TestCase("Cos_pi", "cos(pi)", -1.0, tolerance=1e-9),
        TestCase("Tan_zero", "tan(0)", 0.0),
        TestCase("Tan_pi/4", "tan(pi/4)", 1.0, tolerance=1e-9),
        TestCase("Asin_0", "asin(0)", 0.0),
        TestCase("Asin_1", "asin(1)", math.pi/2, tolerance=1e-9),
        TestCase("Acos_1", "acos(1)", 0.0),
        TestCase("Acos_0", "acos(0)", math.pi/2, tolerance=1e-9),
        TestCase("Atan_0", "atan(0)", 0.0),
        TestCase("Atan_1", "atan(1)", math.pi/4, tolerance=1e-9),
        TestCase("Sinh_0", "sinh(0)", 0.0),
        TestCase("Cosh_0", "cosh(0)", 1.0),
        TestCase("Tanh_0", "tanh(0)", 0.0),
    ]
    
    # 4. LOGARITHMS
    logarithms = [
        TestCase("Log10_10", "log(10)", 1.0),
        TestCase("Log10_100", "log(100)", 2.0),
        TestCase("Log10_1000", "log(1000)", 3.0),
        TestCase("Log10_1", "log(1)", 0.0),
        TestCase("Log2_8", "log2(8)", 3.0),
        TestCase("Log2_1", "log2(1)", 0.0),
        TestCase("Ln_e", "ln(e)", 1.0, tolerance=1e-9),
        TestCase("Ln_1", "ln(1)", 0.0),
        TestCase("Log_custom_base", "log(8, 2)", 3.0),
        TestCase("Log_custom_base10", "log(1000, 10)", 3.0),
    ]
    
    # 5. ROOTS AND POWERS
    roots = [
        TestCase("Sqrt_perfect", "sqrt(16)", 4.0),
        TestCase("Sqrt_zero", "sqrt(0)", 0.0),
        TestCase("Sqrt_one", "sqrt(1)", 1.0),
        TestCase("Sqrt_decimal", "sqrt(2)", 2**0.5, tolerance=1e-9),
        TestCase("Cbrt_perfect", "cbrt(27)", 3.0),
        TestCase("Cbrt_8", "cbrt(8)", 2.0),
        TestCase("Cbrt_negative", "cbrt(-8)", -2.0),
        TestCase("Exp_0", "exp(0)", 1.0),
        TestCase("Exp_1", "exp(1)", math.e, tolerance=1e-9),
        TestCase("Exp_ln", "exp(ln(5))", 5.0, tolerance=1e-9),
    ]
    
    # 6. FACTORIALS
    factorials = [
        TestCase("Factorial_0", "factorial(0)", 1),
        TestCase("Factorial_1", "factorial(1)", 1),
        TestCase("Factorial_5", "factorial(5)", 120),
        TestCase("Factorial_10", "factorial(10)", 3628800),
        TestCase("Factorial_shorthand", "5!", 120),
        TestCase("Factorial_shorthand_0", "0!", 1),
        TestCase("GCD_simple", "gcd(12, 8)", 4),
        TestCase("GCD_same", "gcd(5, 5)", 5),
        TestCase("GCD_coprime", "gcd(7, 3)", 1),
        TestCase("LCM_simple", "lcm(4, 6)", 12),
        TestCase("LCM_same", "lcm(5, 5)", 5),
    ]
    
    # 7. CONSTANTS
    constants = [
        TestCase("Pi_value", "pi", math.pi),
        TestCase("E_value", "e", math.e),
        TestCase("Phi_value", "phi", (1 + math.sqrt(5)) / 2),
        TestCase("Tau_value", "tau", 2 * math.pi),
        TestCase("Pi_times_2", "2 * pi", 2 * math.pi),
        TestCase("E_squared", "e**2", math.e ** 2, tolerance=1e-9),
        TestCase("Sin_pi", "sin(pi)", 0.0, tolerance=1e-9),
        TestCase("Cos_pi", "cos(pi)", -1.0, tolerance=1e-9),
        TestCase("Ln_e", "ln(e)", 1.0, tolerance=1e-9),
    ]
    
    # 8. IMPLICIT MULTIPLICATION
    implicit_mult = [
        TestCase("Implicit_const", "2pi", 2 * math.pi),
        TestCase("Implicit_func", "2sin(0)", 0.0),
        TestCase("Implicit_func2", "3sin(pi/2)", 3.0),
        TestCase("Implicit_paren", "2(3)", 6),
        TestCase("Implicit_paren_expr", "2(3+4)", 14),
        TestCase("Implicit_complex", "2pi*e", 2 * math.pi * math.e, tolerance=1e-9),
    ]
    
    # 9. PERCENTAGES
    percentages = [
        TestCase("Percent_50", "50%", 0.5),
        TestCase("Percent_100", "100%", 1.0),
        TestCase("Percent_0", "0%", 0.0),
        TestCase("Percent_25", "25%", 0.25),
        TestCase("Percent_decimal", "12.5%", 0.125),
        TestCase("Percent_in_calc", "100 * 50%", 50.0),
    ]
    
    # 10. ROUNDING
    rounding = [
        TestCase("Abs_positive", "abs(5)", 5),
        TestCase("Abs_negative", "abs(-5)", 5),
        TestCase("Abs_zero", "abs(0)", 0),
        TestCase("Floor_integer", "floor(3.0)", 3),
        TestCase("Floor_down", "floor(3.7)", 3),
        TestCase("Floor_negative", "floor(-3.2)", -4),
        TestCase("Ceil_integer", "ceil(3.0)", 3),
        TestCase("Ceil_up", "ceil(3.2)", 4),
        TestCase("Ceil_negative", "ceil(-3.7)", -3),
        TestCase("Round_simple", "round(3.5)", 4),
        TestCase("Round_down", "round(3.4)", 3),
        TestCase("Round_decimal", "round(3.14159, 2)", 3.14),
    ]
    
    # 11. EDGE CASES AND ERRORS
    edge_cases = [
        TestCase("Empty_string", "", "Error: Empty expression"),
        TestCase("Whitespace_only", "   ", "Error: Empty expression"),
        TestCase("Zero_division", "1/0", "Error: divide by zero"),
        TestCase("Negative_sqrt", "sqrt(-1)", "Error: math domain error"),
        TestCase("Negative_log", "log(-5)", "Error: Cannot compute logarithm of -5"),
        TestCase("Asin_domain", "asin(2)", "Error: math domain error"),
        TestCase("Factorial_negative", "factorial(-1)", "Error: factorial() not defined for negative values"),
    ]
    
    # 12. MEMORY
    memory = [
        TestCase("Memory_store", "ms 42", "Stored 42.0"),
        TestCase("Memory_recall", "mem", 42.0),
        TestCase("Memory_clear", "mc", "Memory cleared"),
        TestCase("Memory_after_clear", "mem", 0),
    ]
    
    # 13. COMPLEX EXPRESSIONS
    complex_expr = [
        TestCase("Complex_trig_log", "sin(log(100))", math.sin(2), tolerance=1e-9),
        TestCase("Complex_nested", "sqrt(factorial(5) + 1)", math.sqrt(121), tolerance=1e-9),
        TestCase("Complex_mixed_ops", "2^3 * 3^2 + sqrt(16)", 8 * 9 + 4),
        TestCase("Complex_constants", "pi * e / phi", math.pi * math.e / ((1+math.sqrt(5))/2), tolerance=1e-9),
        TestCase("Complex_trig_identity", "sin(pi/4)**2 + cos(pi/4)**2", 1.0, tolerance=1e-9),
        TestCase("Complex_deg_rad", "deg(rad(90))", 90.0, tolerance=1e-9),
        TestCase("Complex_log_chain", "log(exp(ln(e)))", math.log10(math.e), tolerance=1e-9),
    ]

    # 14. LOGARITHM EDGE CASES
    log_edge_cases = [
        TestCase("Log10_zero", "log(0)", "Error: Cannot compute logarithm of 0"),
        TestCase("Log_custom_negative_base", "log(8, -2)", "Invalid logarithm base: -2"),
        TestCase("Log_custom_base_one", "log(8, 1)", "Invalid logarithm base: 1"),
        TestCase("Implicit_log2", "2log2(8)", 6),
    ]

    # 15. PERCENTAGES WITH OPERATIONS
    percent_operations = [
        TestCase("Percent_addition", "50% + 25%", 0.75),
        TestCase("Percent_in_calc_with_parentheses", "(50% + 25%) * 200", 150.0),
        TestCase("Percent_division", "100% / 4", 0.25),
    ]

    # 16. IMPLICIT MULTIPLICATION EDGE CASES
    implicit_edge_cases = [
        TestCase("Implicit_multiple_parens", "2(3+4)(5)", 70),
        TestCase("Implicit_nested_parens", "(2+3)(4+5)", 45),
        TestCase("Implicit_multiple_functions", "3sin(pi/2)cos(0)", 3.0),
    ]

    # 17. CHAINED EXPONENTS AND FUNCTIONS
    chained_exponents = [
        TestCase("Exponent_factorial", "2^3!", 64),
        TestCase("Factorial_exponent", "(2+1)!^2", 36),
    ]

    # 18. DECIMALS AND PRECISION
    decimal_precision = [
        TestCase("Floating_point_addition", "0.1 + 0.2", 0.3, tolerance=1e-9),
        TestCase("Division_precision", "1/3", 1/3, tolerance=1e-9),
    ]

    # 19. EDGE CASE PARENTHESES
    parentheses_cases = [
        TestCase("Unbalanced_open", "(2+3", 5),
        TestCase("Nested_unbalanced", "((2+3)*4", 20),
    ]

    # 20. NEGATIVE NUMBERS AND FUNCTIONS
    negative_numbers = [
        TestCase("Negative_sqrt", "-sqrt(9)", -3),
        TestCase("Negative_exponent_precedence", "-2^2", -4),
        TestCase("Negative_exponent_with_parens", "(-2)^2", 4),
    ]
    
    return {
        "1. BASIC ARITHMETIC": basic_arithmetic,
        "2. EXPONENTIATION": exponentiation,
        "3. TRIGONOMETRY": trigonometry,
        "4. LOGARITHMS": logarithms,
        "5. ROOTS AND POWERS": roots,
        "6. FACTORIALS": factorials,
        "7. CONSTANTS": constants,
        "8. IMPLICIT MULTIPLICATION": implicit_mult,
        "9. PERCENTAGES": percentages,
        "10. ROUNDING": rounding,
        "11. EDGE CASES": edge_cases,
        "12. MEMORY OPERATIONS": memory,
        "13. COMPLEX EXPRESSIONS": complex_expr,
        "14. LOGARITHM EDGE CASES": log_edge_cases,
        "15. PERCENTAGES WITH OPERATIONS": percent_operations,
        "16. IMPLICIT MULTIPLICATION EDGE CASES": implicit_edge_cases,
        "17. CHAINED EXPONENTS AND FUNCTIONS": chained_exponents,
        "18. DECIMALS AND PRECISION": decimal_precision,
        "19. EDGE CASE PARENTHESES": parentheses_cases,
        "20. NEGATIVE NUMBERS AND FUNCTIONS": negative_numbers,
    }


def main():
    """Main test runner"""
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║       AUTOMATED CALCULATOR TESTING SUITE                             ║")
    print("║       Testing Smart Scientific Calculator                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    tester = CalculatorTester(SmartScientificCalculator)
    test_suites = get_all_test_cases()
    
    # Run all test suites
    for suite_name, test_cases in test_suites.items():
        tester.run_test_suite(test_cases, suite_name)
    
    # Print final summary
    tester.print_summary()
    
    # Return exit code (0 = success, 1 = failure)
    return 0 if tester.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())