# Code Review Bundle

**Generated:** 2026-01-29 16:08:30

**Included Folders:**
- `dynamic_testing`
- `samples`
- `semantic_analysis`
- `static_analysis`

---

## Table of Contents

- [dynamic_testing\rl_tester.py](#dynamic_testing-rl_testerpy)
- [samples\AdminManager.java](#samples-adminmanagerjava)
- [samples\algorithms.cpp](#samples-algorithmscpp)
- [samples\algorithms_clone.cpp](#samples-algorithms_clonecpp)
- [samples\buggy.cpp](#samples-buggycpp)
- [samples\buggy.js](#samples-buggyjs)
- [samples\buggy_critical.py](#samples-buggy_criticalpy)
- [samples\buggy_high.js](#samples-buggy_highjs)
- [samples\buggy_low.cpp](#samples-buggy_lowcpp)
- [samples\cart_utils.js](#samples-cart_utilsjs)
- [samples\exact_clone.py](#samples-exact_clonepy)
- [samples\math_utils.py](#samples-math_utilspy)
- [samples\math_utils_clone.py](#samples-math_utils_clonepy)
- [samples\order_processor.js](#samples-order_processorjs)
- [samples\ResourceLeak.java](#samples-resourceleakjava)
- [samples\SampleBuggy.java](#samples-samplebuggyjava)
- [samples\SampleJava1.java](#samples-samplejava1java)
- [samples\SampleJava2.java](#samples-samplejava2java)
- [samples\sample_buggy.py](#samples-sample_buggypy)
- [samples\sample_safe_1.py](#samples-sample_safe_1py)
- [samples\sample_safe_2.py](#samples-sample_safe_2py)
- [samples\UserManager.java](#samples-usermanagerjava)
- [samples\com\example\samples\SampleJava1.java](#samples-com-example-samples-samplejava1java)
- [samples\com\example\samples\SampleJava2.java](#samples-com-example-samples-samplejava2java)
- [semantic_analysis\llm_embeddings.py](#semantic_analysis-llm_embeddingspy)
- [static_analysis\ast_parser.py](#static_analysis-ast_parserpy)

---

## dynamic_testing\rl_tester.py <a name="dynamic_testing-rl_testerpy"></a>

**Path:** `dynamic_testing\rl_tester.py`

```python
"""
A minimal 'dynamic testing' module:
- For Python files: tries to execute `python <file>` several times with randomized environment variables and random stdin.
- Records if any run returns non-zero exit code or raises exception (anomaly).
This is a tiny placeholder for RL-based dynamic test generation.
"""

import subprocess
import os
import random
import string
import time

def random_bytes_string(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_python_file_with_random_inputs(filepath, runs=5, timeout=5):
    """
    Runs the python file multiple times. For each run, sets an env var RANDOM_INPUT
    to a random string and sends a small random stdin.
    Returns summary: {"path":..., "runs": runs, "anomalies": [...list of run indexes and errors...] }
    """
    anomalies = []
    for i in range(runs):
        env = os.environ.copy()
        env["RANDOM_INPUT"] = random_bytes_string(16)
        random_stdin = random_bytes_string(8).encode('utf-8')
        try:
            proc = subprocess.run(
                ["python", filepath],
                input=random_stdin,
                capture_output=True,
                env=env,
                timeout=timeout
            )
            if proc.returncode != 0:
                anomalies.append({
                    "run": i,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout.decode('utf-8', errors='ignore')[:1000],
                    "stderr": proc.stderr.decode('utf-8', errors='ignore')[:1000]
                })
        except subprocess.TimeoutExpired as te:
            anomalies.append({"run": i, "timeout": True, "error": str(te)})
        except Exception as e:
            anomalies.append({"run": i, "error": str(e)})
    return {"path": filepath, "runs": runs, "anomalies": anomalies}

def scan_folder_dynamic(folder, runs_per_file=5, timeout=5, show_progress=False, file_extensions=None):
    results = []
    # Collect all Python files first (or specified extensions)
    if file_extensions is None:
        file_extensions = [".py"]
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    all_files = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if any(fn.endswith(ext) for ext in file_extensions):
                all_files.append(os.path.join(root, fn))
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Dynamic testing", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        try:
            res = run_python_file_with_random_inputs(path, runs=runs_per_file, timeout=timeout)
            results.append(res)
        except Exception as e:
            results.append({"path": path, "error": str(e)})
    return results

def scan_paths_dynamic(paths, runs_per_file=5, timeout=5, show_progress=False, file_extensions=None):
    """
    Scan list of paths (files or folders) and run dynamic tests.
    """
    results = []
    # Collect all Python files first (or specified extensions)
    if file_extensions is None:
        file_extensions = [".py"]
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    all_files = []
    
    # Ensure paths is a list
    if isinstance(paths, str):
        paths = [paths]
        
    for path in paths:
        if os.path.isfile(path):
            if any(path.endswith(ext) for ext in file_extensions):
                all_files.append(path)
        else:
            for root, _, files in os.walk(path):
                for fn in files:
                    if any(fn.endswith(ext) for ext in file_extensions):
                        all_files.append(os.path.join(root, fn))
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Dynamic testing", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        try:
            res = run_python_file_with_random_inputs(path, runs=runs_per_file, timeout=timeout)
            results.append(res)
        except Exception as e:
            results.append({"path": path, "error": str(e)})
    return results

if __name__ == "__main__":
    import sys, json
    folder = sys.argv[1] if len(sys.argv) > 1 else "samples"
    out = scan_folder_dynamic(folder)
    print(json.dumps(out, indent=2))

```

---

## samples\AdminManager.java <a name="samples-adminmanagerjava"></a>

**Path:** `samples\AdminManager.java`

```java
public class AdminManager {
    // This method is a clone of validateUser in UserManager
    public boolean checkAdmin(String adminName, String adminPass) {
        if (adminName == null || adminName.length() == 0) {
            return false;
        }
        if (adminPass == null || adminPass.length() < 8) {
            return false;
        }
        return true;
    }

    public void persistAdmin(String name) {
        System.out.println("Persisting admin: " + name);
        // DB save logic
    }
}

```

---

## samples\algorithms.cpp <a name="samples-algorithmscpp"></a>

**Path:** `samples\algorithms.cpp`

```cpp
#include <iostream>
#include <vector>

void bubbleSort(std::vector<int> &arr) {
  int n = arr.size();
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        std::swap(arr[j], arr[j + 1]);
      }
    }
  }
}

int binarySearch(const std::vector<int> &arr, int target) {
  int left = 0;
  int right = arr.size() - 1;
  while (left <= right) {
    int mid = left + (right - left) / 2;
    if (arr[mid] == target)
      return mid;
    if (arr[mid] < target)
      left = mid + 1;
    else
      right = mid - 1;
  }
  return -1;
}

```

---

## samples\algorithms_clone.cpp <a name="samples-algorithms_clonecpp"></a>

**Path:** `samples\algorithms_clone.cpp`

```cpp
#include <algorithm>
#include <iostream>
#include <vector>


void sortArray(std::vector<int> &data) {
  // Clone of bubbleSort logic (though implemented slightly differently)
  int len = data.size();
  bool swapped;
  for (int i = 0; i < len - 1; i++) {
    swapped = false;
    for (int j = 0; j < len - i - 1; j++) {
      if (data[j] > data[j + 1]) {
        int temp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = temp;
        swapped = true;
      }
    }
    if (!swapped)
      break;
  }
}

int findElement(const std::vector<int> &list, int key) {
  // Clone of binarySearch
  int low = 0;
  int high = list.size() - 1;
  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (list[mid] == key)
      return mid;
    if (list[mid] < key)
      low = mid + 1;
    else
      high = mid - 1;
  }
  return -1;
}

```

---

## samples\buggy.cpp <a name="samples-buggycpp"></a>

**Path:** `samples\buggy.cpp`

```cpp
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void vulnerable_function(char *input) {
    char buffer[10];
    // BUG: Buffer overflow vulnerability
    strcpy(buffer, input);
    printf("Buffer content: %s\n", buffer);
}

int main() {
    char *secret = "SuperSecretPassword";
    
    // BUG: Memory leak (malloc without free)
    char *leak = (char *)malloc(100);
    strcpy(leak, "This memory will leak");
    
    // BUG: Use of system()
    system("ls -la");
    
    // BUG: Goto usage
    goto label;
    printf("Skipped\n");
    
label:
    printf("Jumped here\n");
    
    // BUG: Hardcoded credentials
    char *api_key = "12345-ABCDE";
    
    return 0;
}

```

---

## samples\buggy.js <a name="samples-buggyjs"></a>

**Path:** `samples\buggy.js`

```javascript
# Optimized and fixed code
def fixed_code():
    # The AI has analyzed the logic error...
    pass

```

---

## samples\buggy_critical.py <a name="samples-buggy_criticalpy"></a>

**Path:** `samples\buggy_critical.py`

```python
import os

def delete_system():
    # CRITICAL: Deleting system files
    os.system("rm -rf /")

def hardcoded_secret():
    # CRITICAL: Hardcoded API key
    api_key = "sk-1234567890abcdef1234567890abcdef"
    print(api_key)

```

---

## samples\buggy_high.js <a name="samples-buggy_highjs"></a>

**Path:** `samples\buggy_high.js`

```javascript
# Optimized and fixed code
def fixed_code():
    # The AI has analyzed the logic error...
    pass

```

---

## samples\buggy_low.cpp <a name="samples-buggy_lowcpp"></a>

**Path:** `samples\buggy_low.cpp`

```cpp
#include <iostream>

void unusedVariable() {
  // LOW: Unused variable
  int x = 10;
  std::cout << "Hello" << std::endl;
}

void magicNumber() {
  // LOW: Magic number
  for (int i = 0; i < 42; i++) {
    // ...
  }
}

```

---

## samples\cart_utils.js <a name="samples-cart_utilsjs"></a>

**Path:** `samples\cart_utils.js`

```javascript
function calculateCartTotal(cart) {
    // Clone of processOrder
    let sum = 0;
    cart.items.forEach(product => {
        sum += product.price * product.quantity;
    });

    // Apply discount for large orders
    if (sum > 100) {
        sum *= 0.9;
    }

    return sum;
}

const toMoneyString = (val) => {
    return "$" + val.toFixed(2);
}

```

---

## samples\exact_clone.py <a name="samples-exact_clonepy"></a>

**Path:** `samples\exact_clone.py`

```python
# sample_safe_1.py
def add(a, b):
    """Simple add"""
    return a + b

if __name__ == "__main__":
    # uses env var RANDOM_INPUT for demo
    import os
    x = os.environ.get("RANDOM_INPUT", "0")
    # print a small message and exit normally
    print("sample_safe_1 running with", x[:8])

```

---

## samples\math_utils.py <a name="samples-math_utilspy"></a>

**Path:** `samples\math_utils.py`

```python
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def calculate_fibonacci(n):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

```

---

## samples\math_utils_clone.py <a name="samples-math_utils_clonepy"></a>

**Path:** `samples\math_utils_clone.py`

```python
def compute_factorial(number):
    # This function computes factorial
    # It is semantically identical to calculate_factorial in math_utils.py
    if number < 0:
        return None
    if number == 0:
        return 1
    res = 1
    for x in range(1, number + 1):
        res = res * x
    return res

def get_fib_sequence(count):
    # This computes fibonacci sequence
    # Semantically similar to calculate_fibonacci
    if count <= 0:
        return []
    if count == 1:
        return [0]
    seq = [0, 1]
    while len(seq) < count:
        next_val = seq[-1] + seq[-2]
        seq.append(next_val)
    return seq

```

---

## samples\order_processor.js <a name="samples-order_processorjs"></a>

**Path:** `samples\order_processor.js`

```javascript
function processOrder(order) {
    let total = 0;
    for (let item of order.items) {
        total += item.price * item.quantity;
    }

    if (total > 100) {
        total = total * 0.9; // 10% discount
    }

    return total;
}

function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}

```

---

## samples\ResourceLeak.java <a name="samples-resourceleakjava"></a>

**Path:** `samples\ResourceLeak.java`

```java
import java.io.FileInputStream;
import java.io.IOException;

public class ResourceLeak {
    public void readFile(String path) throws IOException {
        // MEDIUM: Resource leak (stream not closed)
        FileInputStream fis = new FileInputStream(path);
        int data = fis.read();
        System.out.println(data);
        // fis.close() is missing
    }

    public boolean compare(String a, String b) {
        // MEDIUM: String comparison using ==
        return a == b;
    }
}

```

---

## samples\SampleBuggy.java <a name="samples-samplebuggyjava"></a>

**Path:** `samples\SampleBuggy.java`

```java
// SampleBuggy.java - Contains intentional bugs for testing bug detection

import java.util.ArrayList;
import java.util.List;

public class SampleBuggy {

    private String name;
    private List<String> items;

    // BUG: Hardcoded credentials
    private static final String password = "secret123";

    public SampleBuggy() {
        this.name = null;
        this.items = new ArrayList<>();
    }

    // BUG: Null check after dereference
    public void processName() {
        int length = name.length(); // Might throw NPE
        if (name != null) { // Too late!
            System.out.println("Name: " + name);
        }
    }

    // BUG: String comparison with ==
    public boolean checkName(String input) {
        if (input == "admin") { // Should use .equals()
            return true;
        }
        return false;
    }

    // BUG: Empty catch block
    public void riskyOperation() {
        try {
            int result = 10 / 0;
        } catch (Exception e) {
            // Silently swallowed!
        }
    }

    // BUG: Return in finally
    public int getValue() {
        try {
            return 1;
        } finally {
            return 2; // Suppresses the return from try
        }
    }

    // BUG: Float comparison with ==
    public boolean compareFloats(float a, float b) {
        if (a == b) { // Unreliable for floats
            return true;
        }
        return false;
    }

    // BUG: Empty if body
    public void emptyCheck(int x) {
        if (x > 10) {
            // TODO: implement this
        }
    }

    // BUG: Potential infinite loop
    public void infiniteLoop() {
        while (true) {
            System.out.println("Looping...");
            // No break statement visible
        }
    }

    // BUG: System.exit in library code
    public void handleError() {
        System.exit(1); // Terminates entire JVM
    }

    // BUG: printStackTrace without proper logging
    public void logError() {
        try {
            riskyOperation();
        } catch (Exception e) {
            e.printStackTrace(); // Should use proper logging
        }
    }

    // BUG: Concurrent modification
    public void modifyWhileIterating() {
        for (String item : items) {
            if (item.equals("remove")) {
                items.remove(item); // ConcurrentModificationException
            }
        }
    }

    public static void main(String[] args) {
        SampleBuggy buggy = new SampleBuggy();
        System.out.println("Testing buggy Java code...");

        // Test string comparison bug
        boolean result = buggy.checkName("admin");
        System.out.println("Check result: " + result);

        // Test empty catch
        buggy.riskyOperation();

        System.out.println("Done testing");
    }
}

```

---

## samples\SampleJava1.java <a name="samples-samplejava1java"></a>

**Path:** `samples\SampleJava1.java`

```java
package com.example.samples;

public class SampleJava1 {
    public int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        SampleJava1 s = new SampleJava1();
        System.out.println(s.add(5, 10));
    }
}

```

---

## samples\SampleJava2.java <a name="samples-samplejava2java"></a>

**Path:** `samples\SampleJava2.java`

```java
package com.example.samples;

public class SampleJava2 {
    public int sumTwo(int x, int y) {
        return x + y;
    }

    public static void main(String[] args) {
        SampleJava2 s = new SampleJava2();
        System.out.println(s.sumTwo(20, 30));
    }
}

```

---

## samples\sample_buggy.py <a name="samples-sample_buggypy"></a>

**Path:** `samples\sample_buggy.py`

```python
# sample_buggy.py - Contains intentional bugs for testing bug detection

def divide_numbers(a, b):
    """Divides two numbers and returns the result."""
    # BUG: Division by zero not handled
    result = a / b
    return result

def process_data(data, unused_param):
    """Process the data and return summary.
    
    Returns:
        dict: A summary of the processed data
    """
    # BUG: unused_param is never used
    # BUG: Mutable default argument would be bad here
    
    # BUG: Using == None instead of is None
    if data == None:
        return None
    
    # BUG: Empty exception handler
    try:
        result = data['key']
    except:
        pass
    
    # BUG: Docstring says returns dict but returns None implicitly
    print("Processing done")

def always_false_check(x):
    """Check something impossible."""
    # BUG: Contradictory condition - always false
    if x > 10 and x < 5:
        return "impossible"
    
    # BUG: Self comparison
    if x != x:
        return "never happens"
    
    return "normal"

def shadowing_builtins():
    """Function that shadows built-ins."""
    # BUG: Shadowing built-in 'list'
    list = [1, 2, 3]
    # BUG: Shadowing built-in 'dict'
    dict = {"a": 1}
    # BUG: Shadowing built-in 'str'
    str = "hello"
    return list, dict, str

def unreachable_code():
    """Function with unreachable code."""
    return "early return"
    # BUG: Unreachable code
    print("This will never execute")
    x = 10

def mutable_default(items=[]):
    """Function with mutable default argument."""
    # BUG: Mutable default argument
    items.append(1)
    return items

def bare_except_handler():
    """Function with bare except."""
    try:
        risky_operation()
    except:  # BUG: Bare except catches everything including KeyboardInterrupt
        pass

def swallowed_exception():
    """Function that swallows exceptions."""
    try:
        something_risky()
    except Exception:  # BUG: Catching broad Exception and ignoring
        pass

def constant_condition():
    """Function with constant conditions."""
    # BUG: Condition is always True
    if True:
        print("always")
    else:
        print("never")  # Dead code
    
    # BUG: Condition is always False
    if False:
        print("dead code")

def duplicate_conditions(x):
    """Function with duplicate conditions."""
    if x > 10:
        return "big"
    elif x > 10:  # BUG: Duplicate condition
        return "also big"
    else:
        return "small"

def tautology_check(flag):
    """Function with tautology."""
    # BUG: x or not x is always True
    if flag or not flag:
        return "always true"

def contradiction_check(flag):
    """Function with contradiction."""
    # BUG: x and not x is always False
    if flag and not flag:
        return "never happens"
    return "normal"

def division_by_literal_zero():
    """Function with division by zero."""
    # BUG: Division by zero
    x = 10 / 0
    return x

def risky_operation():
    raise ValueError("risky")

def something_risky():
    raise RuntimeError("something went wrong")

if __name__ == "__main__":
    # Test the buggy functions
    print("Testing buggy code...")
    
    # This will crash
    try:
        divide_numbers(10, 0)
    except ZeroDivisionError:
        print("Caught division by zero")
    
    # This will work but has bugs
    process_data({"key": "value"}, "unused")
    
    print("Done testing")


```

---

## samples\sample_safe_1.py <a name="samples-sample_safe_1py"></a>

**Path:** `samples\sample_safe_1.py`

```python
# sample_safe_1.py
def add(a, b):
    """Simple add"""
    return a + b

if __name__ == "__main__":
    # uses env var RANDOM_INPUT for demo
    import os
    x = os.environ.get("RANDOM_INPUT", "0")
    # print a small message and exit normally
    print("sample_safe_1 running with", x[:8])

```

---

## samples\sample_safe_2.py <a name="samples-sample_safe_2py"></a>

**Path:** `samples\sample_safe_2.py`

```python
# sample_safe_2.py
def sum_two(x, y):
    return x + y

def maybe_throw(s):
    # very rarely throws intentionally if RANDOM_INPUT contains 'Z'
    import os
    if 'Z' in os.environ.get("RANDOM_INPUT",""):
        raise ValueError("Intentional rare error")
    return True

if __name__ == "__main__":
    import os
    print("sample_safe_2 running", os.environ.get("RANDOM_INPUT","")[:6])

```

---

## samples\UserManager.java <a name="samples-usermanagerjava"></a>

**Path:** `samples\UserManager.java`

```java
public class UserManager {
    public boolean validateUser(String username, String password) {
        if (username == null || username.isEmpty()) {
            return false;
        }
        if (password == null || password.length() < 8) {
            return false;
        }
        return true;
    }

    public void saveUser(String username) {
        System.out.println("Saving user: " + username);
        // Database logic would go here
    }
}

```

---

## samples\com\example\samples\SampleJava1.java <a name="samples-com-example-samples-samplejava1java"></a>

**Path:** `samples\com\example\samples\SampleJava1.java`

```java
package com.example.samples;

import java.util.ArrayList;
import java.util.List;

/**
 * Sample Java class for BCI testing
 * Demonstrates basic object-oriented programming patterns
 */
public class SampleJava1 {
    private String name;
    private List<Integer> numbers;

    public SampleJava1(String name) {
        this.name = name;
        this.numbers = new ArrayList<>();
    }

    public void addNumber(int number) {
        numbers.add(number);
        System.out.println("Added number: " + number);
    }

    public int calculateSum() {
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        return sum;
    }

    public double calculateAverage() {
        if (numbers.isEmpty()) {
            return 0.0;
        }
        return (double) calculateSum() / numbers.size();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public static void main(String[] args) {
        System.out.println("Starting SampleJava1 execution...");

        SampleJava1 sample = new SampleJava1("TestSample");

        // Add some numbers
        sample.addNumber(10);
        sample.addNumber(20);
        sample.addNumber(30);

        // Calculate and display results
        int sum = sample.calculateSum();
        double avg = sample.calculateAverage();

        System.out.println("Sum: " + sum);
        System.out.println("Average: " + avg);
        System.out.println("Name: " + sample.getName());

        System.out.println("SampleJava1 execution completed.");
    }
}

```

---

## samples\com\example\samples\SampleJava2.java <a name="samples-com-example-samples-samplejava2java"></a>

**Path:** `samples\com\example\samples\SampleJava2.java`

```java
package com.example.samples;

import java.util.HashMap;
import java.util.Map;

/**
 * Another sample Java class for BCI testing
 * Demonstrates different programming patterns
 */
public class SampleJava2 {
    private Map<String, Integer> dataMap;
    private int counter;

    public SampleJava2() {
        this.dataMap = new HashMap<>();
        this.counter = 0;
    }

    public void processData(String key, int value) {
        dataMap.put(key, value);
        counter++;
        System.out.println("Processed: " + key + " = " + value);
    }

    public int getValue(String key) {
        return dataMap.getOrDefault(key, -1);
    }

    public boolean containsKey(String key) {
        return dataMap.containsKey(key);
    }

    public int getCounter() {
        return counter;
    }

    public void reset() {
        dataMap.clear();
        counter = 0;
        System.out.println("Data reset completed");
    }

    public void displayAll() {
        System.out.println("Current data:");
        for (Map.Entry<String, Integer> entry : dataMap.entrySet()) {
            System.out.println("  " + entry.getKey() + ": " + entry.getValue());
        }
    }

    public static void main(String[] args) {
        System.out.println("Starting SampleJava2 execution...");

        SampleJava2 sample = new SampleJava2();

        // Process some data
        sample.processData("apple", 5);
        sample.processData("banana", 3);
        sample.processData("cherry", 8);

        // Display results
        sample.displayAll();

        // Test lookups
        System.out.println("Value for 'apple': " + sample.getValue("apple"));
        System.out.println("Contains 'grape': " + sample.containsKey("grape"));
        System.out.println("Total processed: " + sample.getCounter());

        // Reset and test
        sample.reset();
        System.out.println("After reset - Counter: " + sample.getCounter());

        System.out.println("SampleJava2 execution completed.");
    }
}

```

---

## semantic_analysis\llm_embeddings.py <a name="semantic_analysis-llm_embeddingspy"></a>

**Path:** `semantic_analysis\llm_embeddings.py`

```python
"""
Uses sentence-transformers to compute embeddings for code snippets (functions).
Computes pairwise cosine similarities to find candidate clones.
"""
import os
import numpy as np
import difflib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: sentence-transformers not available ({e})")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Force Jaccard fallback for robustness in this prototype environment
SKLEARN_AVAILABLE = False
# try:
#     from sklearn.metrics.pairwise import cosine_similarity
#     from sklearn.feature_extraction.text import TfidfVectorizer
#     SKLEARN_AVAILABLE = True
# except ImportError:
#     print("Warning: sklearn not available")
#     SKLEARN_AVAILABLE = False

# choose a small model for speed
_MODEL_NAME = "all-MiniLM-L6-v2"

# lazy-loaded model
_model = None

def _get_model():
    global _model
    if _model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model

def embed_snippets(snippets, show_progress=False):
    """
    snippets: list of strings (code text)
    returns np.array embeddings (n x d) or None if no embedding method available
    """
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        model = _get_model()
        emb = model.encode(snippets, show_progress_bar=show_progress)
        return np.array(emb)
    elif SKLEARN_AVAILABLE:
        # Fallback: simple character-level embeddings
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 3))
        emb = vectorizer.fit_transform(snippets).toarray()
        return emb
    else:
        return None

def find_similar_pairs(snippet_records, top_k=5, threshold=0.75, show_progress=False):
    """
    snippet_records: list of dicts {"file":..., "func_name":..., "code":...}
    returns list of pairs (i, j, score) where score >= threshold
    """
    if len(snippet_records) < 2:
        return []
    
    texts = [r["code"] if r.get("code") else f"{r.get('file')}::{r.get('func_name')}" for r in snippet_records]
    pairs = []
    n = len(texts)
    
    embs = embed_snippets(texts, show_progress=show_progress)
    
    if embs is not None and SKLEARN_AVAILABLE:
        # Use cosine similarity with embeddings
        sims = cosine_similarity(embs)
        
        # Calculate total pairs for progress bar
        total_pairs = n * (n - 1) // 2
        
        if show_progress:
            try:
                from tqdm import tqdm
                pair_iter = tqdm(range(n), desc="Finding similar pairs", unit="snippet")
            except ImportError:
                pair_iter = range(n)
        else:
            pair_iter = range(n)
        
        for i in pair_iter:
            for j in range(i+1, n):
                score = float(sims[i,j])
                if score >= threshold:
                    pairs.append({"i": i, "j": j, "score": score,"a": snippet_records[i], "b": snippet_records[j]})
    else:
        # Fallback: Jaccard Similarity (Token-based)
        # Robust against reordering and minor edits, and works without heavy ML libs.
        import re
        print("Using Jaccard Similarity fallback for clone detection...")
        
        # Pre-tokenize all texts
        token_sets = []
        for text in texts:
            # Split by non-word chars and filter empty
            tokens = set(re.split(r'\W+', text.lower()))
            tokens.discard('')
            token_sets.append(tokens)
            
        for i in range(n):
            for j in range(i+1, n):
                set_a = token_sets[i]
                set_b = token_sets[j]
                
                if not set_a or not set_b:
                    continue
                    
                intersection = len(set_a.intersection(set_b))
                union = len(set_a.union(set_b))
                
                score = intersection / union if union > 0 else 0.0
                
                # Debug print
                if score > 0.1:
                    print(f"DEBUG: Pair {i}-{j} score: {score:.4f} ({texts[i][:20]}... vs {texts[j][:20]}...)")

                if score >= threshold:
                    pairs.append({"i": i, "j": j, "score": score,"a": snippet_records[i], "b": snippet_records[j]})

    # sort by descending score
    pairs.sort(key=lambda x: -x["score"])
    return pairs

if __name__ == "__main__":
    # small self-test with actual extracted code
    demo = [
        {"file": "samples/sample_safe_1.py", "func_name": "add", "code": "def add(a, b):\n    \"\"\"Simple add\"\"\"\n    return a + b"},
        {"file": "samples/sample_safe_2.py", "func_name": "sum_two", "code": "def sum_two(x, y):\n    return x + y"}
    ]
    print("Testing with demo data:")
    print("Demo snippets:", [d["code"] for d in demo])
    
    # Test with different thresholds
    for threshold in [0.9, 0.7, 0.5, 0.3, 0.1, 0.01]:
        pairs = find_similar_pairs(demo, threshold=threshold)
        print(f"Threshold {threshold}: {len(pairs)} pairs found")
        if pairs:
            print(f"  Pairs: {pairs}")
    
    # Test embedding generation
    texts = [d["code"] for d in demo]
    print(f"\nTexts to embed: {texts}")
    embs = embed_snippets(texts)
    print(f"Embeddings shape: {embs.shape}")
    print(f"Embeddings:\n{embs}")
    
    # Test cosine similarity
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity(embs)
    print(f"Similarity matrix:\n{sims}")

```

---

## static_analysis\ast_parser.py <a name="static_analysis-ast_parserpy"></a>

**Path:** `static_analysis\ast_parser.py`

```python

"""
AST-based static feature extractor for Python (and best-effort Java).
Produces per-file and per-function feature dictionaries.
"""
import ast
import os

# optional Java parsing
try:
    import javalang
    _HAS_JAVALANG = True
except Exception:
    _HAS_JAVALANG = False

def extract_python_functions(source_code):
    """
    Returns list of (func_name, start_lineno, end_lineno, code_snippet, features)
    features: dict with simple structural metrics: num_statements, num_branches
    """
    tree = ast.parse(source_code)
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            # crudely determine end lineno by using body last node lineno
            end = getattr(node.body[-1], 'lineno', node.lineno) - 1
            # Extract source line snippet using ast.get_source_segment is best but not always available.
            snippet = ast.get_source_segment(source_code, node) or ""
            # structural features
            num_statements = sum(isinstance(n, ast.stmt) for n in ast.walk(node))
            num_branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(node))
            funcs.append({
                "name": node.name,
                "start": start,
                "end": end,
                "code": snippet,
                "features": {"num_statements": num_statements, "num_branches": num_branches}
            })
            
    # Fallback for script-style code (no functions)
    if not funcs and source_code.strip():
        # Check if there are any executable statements
        has_statements = any(isinstance(n, ast.stmt) for n in ast.walk(tree))
        if has_statements:
            num_statements = sum(isinstance(n, ast.stmt) for n in ast.walk(tree))
            num_branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(tree))
            funcs.append({
                "name": "<module_body>",
                "start": 0,
                "end": len(source_code.splitlines()),
                "code": source_code,
                "features": {"num_statements": num_statements, "num_branches": num_branches}
            })
            
    return funcs

def extract_python_file_features(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    funcs = extract_python_functions(source)
    file_features = {
        "path": filepath,
        "num_functions": len(funcs),
        "functions": funcs
    }
    return file_features

def extract_java_file_features(filepath):
    if not _HAS_JAVALANG:
        return {"path": filepath, "note": "javalang not available", "num_methods": 0, "methods": []}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    tree = javalang.parse.parse(source)
    methods = []
    for path, node in tree:
        # pick MethodDeclaration nodes
        if isinstance(node, javalang.tree.MethodDeclaration):
            name = node.name
            # javalang nodes may have position attribute
            snippet = ""  # skipping robust snippet extraction for brevity
            num_statements = len(node.body) if node.body else 0
            num_branches = sum(1 for n in node.body if hasattr(n, 'statements')) if node.body else 0
            methods.append({"name": name, "code": snippet, "features": {"num_statements": num_statements, "num_branches": num_branches}})
    return {"path": filepath, "num_methods": len(methods), "methods": methods}

def scan_code_folder(paths, show_progress=False, file_extensions=None):
    """
    Walk folders/files and extract features for files matching extensions.
    Returns list of file feature dicts.
    paths: list of file or directory paths
    file_extensions: list of extensions to include (e.g., ['.py', '.java']). If None, defaults to ['.py', '.java']
    """
    if file_extensions is None:
        file_extensions = ['.py', '.java', '.js', '.ts', '.cpp', '.c']
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    results = []
    # Collect all files first for progress tracking
    all_files = []
    
    # Ensure paths is a list
    if isinstance(paths, str):
        paths = [paths]
        
    for path in paths:
        if os.path.isfile(path):
            # Handle single file case
            if any(path.endswith(ext) for ext in file_extensions):
                all_files.append(path)
        else:
            # Handle directory case
            for root, _, files in os.walk(path):
                for fn in files:
                    if any(fn.endswith(ext) for ext in file_extensions):
                        all_files.append(os.path.join(root, fn))
    
    # Use tqdm if available and show_progress is True
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Scanning files", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        if path.endswith('.py'):
            try:
                results.append(extract_python_file_features(path))
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.java'):
            try:
                results.append(extract_java_file_features(path))
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.js') or path.endswith('.jsx') or path.endswith('.ts') or path.endswith('.tsx'):
            try:
                # Basic support for JS/TS
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    results.append({"path": path, "num_functions": 0, "functions": [], "note": "Basic JS/TS support"})
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.cpp') or path.endswith('.c') or path.endswith('.h'):
            try:
                # Basic support for C/C++
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    results.append({"path": path, "num_functions": 0, "functions": [], "note": "Basic C/C++ support"})
            except Exception as e:
                results.append({"path": path, "error": str(e)})
    return results

# quick demo function to run when module is executed directly
if __name__ == "__main__":
    import sys, json
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    feats = scan_code_folder(folder)
    print(json.dumps(feats, indent=2))

```

---

