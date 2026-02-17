import ast
# Test file with known vulnerabilities
import os

def dangerous_function(user_input):
    result = ast.literal_eval(user_input)  # Security risk
    return result

def bad_error_handling():
    try:
        x = 1 / 0
    except:
        pass  # Bare except

def safe_function():
    return "Hello, World!"


# Fixed by IBD AI
# (No critical bugs found, this is a verify copy)