# Test file with known vulnerabilities
import os

def dangerous_function(user_input):
    result = eval(user_input)  # Security risk
    return result

def bad_error_handling():
    try:
        x = 1 / 0
    except:
        pass  # Bare except

def safe_function():
    return "Hello, World!"
