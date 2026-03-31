import math
import re
from typing import Union, Dict, Any

class SmartScientificCalculator:
    """
    Scientific calculator with intelligent error handling and syntax suggestions.
    Fixes ^ to **, handles implicit multiplication, and provides helpful error messages.
    """
    
    def __init__(self):
        self.memory = 0
        self.history = []
        self.last_result = None
        
        # Define available functions with their signatures for help
        self.function_help = {
            'sin': {'args': 'x', 'desc': 'Sine of x (radians)', 'example': 'sin(1.57) ≈ 1'},
            'cos': {'args': 'x', 'desc': 'Cosine of x (radians)', 'example': 'cos(0) = 1'},
            'tan': {'args': 'x', 'desc': 'Tangent of x (radians)', 'example': 'tan(0.785) ≈ 1'},
            'asin': {'args': 'x', 'desc': 'Arc sine (inverse sine)', 'example': 'asin(1) ≈ 1.57'},
            'acos': {'args': 'x', 'desc': 'Arc cosine (inverse cosine)', 'example': 'acos(1) = 0'},
            'atan': {'args': 'x', 'desc': 'Arc tangent (inverse tangent)', 'example': 'atan(1) ≈ 0.785'},
            'sinh': {'args': 'x', 'desc': 'Hyperbolic sine', 'example': 'sinh(1) ≈ 1.175'},
            'cosh': {'args': 'x', 'desc': 'Hyperbolic cosine', 'example': 'cosh(0) = 1'},
            'tanh': {'args': 'x', 'desc': 'Hyperbolic tangent', 'example': 'tanh(0) = 0'},
            'sqrt': {'args': 'x', 'desc': 'Square root', 'example': 'sqrt(16) = 4'},
            'cbrt': {'args': 'x', 'desc': 'Cube root', 'example': 'cbrt(27) = 3'},
            'log': {'args': 'x, base', 'desc': 'Logarithm (default base 10)', 'example': 'log(100) = 2 or log(8, 2) = 3'},
            'ln': {'args': 'x', 'desc': 'Natural logarithm (base e)', 'example': 'ln(2.718) ≈ 1'},
            'log10': {'args': 'x', 'desc': 'Logarithm base 10', 'example': 'log10(1000) = 3'},
            'log2': {'args': 'x', 'desc': 'Logarithm base 2', 'example': 'log2(8) = 3'},
            'exp': {'args': 'x', 'desc': 'e raised to power x', 'example': 'exp(1) ≈ 2.718'},
            'abs': {'args': 'x', 'desc': 'Absolute value', 'example': 'abs(-5) = 5'},
            'floor': {'args': 'x', 'desc': 'Round down to integer', 'example': 'floor(3.7) = 3'},
            'ceil': {'args': 'x', 'desc': 'Round up to integer', 'example': 'ceil(3.2) = 4'},
            'round': {'args': 'x, n', 'desc': 'Round to n decimal places', 'example': 'round(3.14159, 2) = 3.14'},
            'factorial': {'args': 'n', 'desc': 'Factorial of n', 'example': 'factorial(5) = 120'},
            'gcd': {'args': 'a, b', 'desc': 'Greatest common divisor', 'example': 'gcd(12, 8) = 4'},
            'lcm': {'args': 'a, b', 'desc': 'Least common multiple', 'example': 'lcm(4, 6) = 12'},
            'deg': {'args': 'rad', 'desc': 'Convert radians to degrees', 'example': 'deg(3.14159) ≈ 180'},
            'rad': {'args': 'deg', 'desc': 'Convert degrees to radians', 'example': 'rad(180) ≈ 3.14159'},
            'pow': {'args': 'base, exp', 'desc': 'Power function', 'example': 'pow(2, 3) = 8'},
        }
        
        # Constants
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,
            'tau': 2 * math.pi,
        }
        
        # Safe evaluation namespace
        self.safe_dict = self._build_safe_dict()
        self.safe_dict.update({
        'log2': math.log2,
        'log10': math.log10,
        }
        )
    
    def _build_safe_dict(self) -> Dict[str, Any]:
        """Build safe dictionary for eval()"""
        safe = {
            'abs': abs,
            'round': round,
            'max': max,
            'min': min,
            'sum': sum,
            'pow': pow,
        }
        
        # Add math module functions
        math_funcs = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
                      'sinh', 'cosh', 'tanh', 'sqrt', 'exp', 'log',
                      'log10', 'log2', 'floor', 'ceil', 'factorial',
                      'gcd', 'lcm', 'degrees', 'radians']
        
        for func in math_funcs:
            if func == 'sqrt':
                safe['sqrt'] = self._smart_sqrt
            elif hasattr(math, func):
                safe[func] = getattr(math, func)
        
        # Custom implementations
        safe['ln'] = math.log
        safe['cbrt'] = lambda x: math.copysign(abs(x) ** (1/3), x)
        safe['deg'] = math.degrees
        safe['rad'] = math.radians
        safe['log'] = self._smart_log
        safe['log2'] = lambda x: math.log2(x)
        safe['log10'] = lambda x: math.log10(x)
        safe['asin'] = self._safe_asin
        safe['acos'] = self._safe_acos
        safe['atan'] = self._safe_atan
        safe['factorial'] = self._safe_factorial
        
        # Add constants
        safe.update(self.constants)
        
        return safe

    #### Smart Functions
    def _smart_log(self, x, base=None):
        if x <= 0:
            raise ValueError(f"Error: Cannot compute logarithm of {x}")
        if base is None:
            return math.log10(x)
        if base <= 0 or base == 1:
            raise ValueError(f"Invalid logarithm base: {base}")
        return math.log(x, base)
    
    def _smart_sqrt(self, x):
        if x < 0:
            raise ValueError("Error: math domain error")
        return math.sqrt(x)
    
    def _safe_asin(self, x):
        if x < -1 or x > 1:
            raise ValueError("Error: math domain error")
        return math.asin(x)

    def _safe_acos(self, x):
        if x < -1 or x > 1:
            raise ValueError("Error: math domain error")
        return math.acos(x)

    def _safe_atan(self, x):
        return math.atan(x)
    
    def _safe_factorial(self, n):
        if n < 0:
            raise ValueError("Error: factorial() not defined for negative values")
        if not isinstance(n, (int, float)) or n != int(n):
            raise ValueError("Error: factorial() only defined for non-negative integers")
        return math.factorial(int(n))
    
    def _preprocess_expression(self, expr: str) -> str:
        """
        Preprocess expression to fix syntax issues:
        - Replace ^ with **
        - Handle implicit multiplication (including function chaining)
        - Convert factorial shorthand
        - Handle percentages
        - Protect log2/log10 from regex
        - Auto-close unbalanced parentheses
        """
        expr = expr.strip()
        expr = expr.replace('^', '**')
        
        # Protect special function names from regex modifications
        protected = {'log2': '§LOG2§', 'log10': '§LOG10§'}
        for key, val in protected.items():
            expr = re.sub(rf'\b{key}\b', val, expr)

        # Handle implicit multiplication before log2 and log10
        expr = re.sub(r'(\d)(?=\s*log[12]\s*\()', r'\1*', expr)
        
        # Percentages: 50% -> (50/100)
        expr = re.sub(r'(\d+\.?\d*)%', r'(\1/100)', expr)
        
        # Factorials: number! or (expr)! -> factorial(number)
        expr = re.sub(r'(\d+|\([^)]*\))!', r'factorial(\1)', expr)
        
        # === IMPLICIT MULTIPLICATION RULES ===
        # number before '(' e.g., 2(3) -> 2*(3)
        expr = re.sub(r'(\d)\s*\(', r'\1*(', expr)
        
        # ')' before number e.g., (2)3 -> (2)*3
        expr = re.sub(r'\)\s*(\d)', r')*\1', expr)
        
        # ')' before '(' e.g., (2+3)(4+5) -> (2+3)*(4+5)
        expr = re.sub(r'\)\s*\(', r')*(', expr)
        
        # === KEY FIX: number before function (including log2, log10, etc.) ===
        # Matches: digit followed by a function name (letters + optional digits) then '('
        expr = re.sub(r'(\d)\s*([a-zA-Z_][a-zA-Z0-9_]*\()', r'\1*\2', expr)
        
        # function call followed by another function call: sin(x)cos(y) -> sin(x)*cos(y)
        # Also updated to handle functions with digits
        expr = re.sub(r'\)\s*([a-zA-Z_][a-zA-Z0-9_]*\()', r')*\1', expr)
        
        # number before constant e.g., 2pi -> 2*pi
        if self.constants:
            consts = '|'.join(re.escape(c) for c in self.constants.keys())
            expr = re.sub(r'(\d)\s*(' + consts + r')', r'\1*\2', expr)
        
        # Restore protected names
        for key, val in protected.items():
            expr = expr.replace(val, key)
        
        # Auto-close parentheses if unbalanced
        open_count = expr.count('(')
        close_count = expr.count(')')
        if open_count > close_count:
            expr += ')' * (open_count - close_count)
        
        # Final internal sanity check
        if '§' in expr:
            raise ValueError("Error: internal parsing issue")
        
        # Remove trailing '*' after log2 or log
        expr = re.sub(r'(log[12])\*', r'\1', expr)
        return expr

    #### Calculation
    def calculate(self, expression: str) -> Union[int, float, str]:
        if not expression or expression.strip() == '':
            return "Error: Empty expression"
        
        original = expression.strip()
        
        # Handle special commands
        if original.lower() in ['help', 'h']:
            return self._show_help()
        if original.lower() in ['history', 'hist']:
            return self._show_history()
        if original.lower() in ['memory', 'mem', 'mr']:
            return self.memory
        if original.lower().startswith('ms '):
            try:
                val = float(original[3:].strip())
                self.memory = val
                return f"Stored {val}"
            except:
                return "Error: Invalid memory value"
        if original.lower() == 'mc':
            self.memory = 0
            return "Memory cleared"
        if original.lower() == 'constants':
            return self._show_constants()
        
        try:
            # Preprocess expression
            processed = self._preprocess_expression(original)
            
            # Evaluate
            result = eval(processed, {"__builtins__": {}}, self.safe_dict)
            
            # Store in history
            self.history.append((original, processed, result))
            if len(self.history) > 50:
                self.history.pop(0)
            
            self.last_result = result
            
            # Format result nicely
            if isinstance(result, complex):
                if result.imag == 0:
                    result = result.real
                else:
                    result = str(result)

            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 10)
            return result
        
        except ZeroDivisionError:
            return "Error: divide by zero"
        except Exception as e:
            return str(e)

    #### Help / Constants / History
    def _show_help(self) -> str:
        help_text = """
Available functions:
  sin, cos, tan, asin, acos, atan, sinh, cosh, tanh
  sqrt, cbrt, exp, ln, log, log10, log2
  factorial, gcd, lcm, abs, floor, ceil, round
  deg, rad, pow

Constants: pi, e, phi, tau

Special commands:
  help, history, mem, ms <value>, mc, constants
        """
        return help_text.strip()
    
    def _show_constants(self) -> str:
        lines = ["Constants:"]
        for name, value in self.constants.items():
            lines.append(f"  {name} = {value}")
        return '\n'.join(lines)
    
    def _show_history(self) -> str:
        if not self.history:
            return "No history yet"
        lines = ["Calculation History (last 10):"]
        for orig, proc, result in self.history[-10:]:
            if orig != proc:
                lines.append(f"  {orig} → {proc} = {result}")
            else:
                lines.append(f"  {orig} = {result}")
        return '\n'.join(lines)


# Interactive CLI
def main():
    calc = SmartScientificCalculator()
    
    print("SMART SCIENTIFIC CALCULATOR")
    print("Type 'help' for usage or 'exit' to quit")
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            result = calc.calculate(user_input)
            print(f"= {result}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()