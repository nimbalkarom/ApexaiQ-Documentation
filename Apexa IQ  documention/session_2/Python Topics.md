# Python Topics

## 1. Variables and Data Types

Variables are used to store data in memory.

Data types determine the kind of value stored:

- `int` → whole numbers (`5`)
- `float` → decimal numbers (`3.14`)
- `str` → text (`"Hello"`)
- `bool` → `True` or `False`

### Example

```python
name = "Alice"
age = 25
height = 5.6
is_student = True
```

## 2. Operators

Symbols used to perform operations on variables/values:

- **Arithmetic:** `+`, `-`, `*`, `/`, `%`, `//`
- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical:** `and`, `or`, `not`

### Example

```python
result = (5 + 3) * 2  # 16
```

## 3. Control Flow

### If - else

Used for decision-making in code.

### Example

```python
age = 18

if age >= 18:
    print("Adult")
else:
    print("Minor")
```

## 4. Loops

Repeats code until a condition is met.

- **for loop** → iterate over sequences (lists, strings, etc.)
- **while loop** → repeat while a condition is true

### Example

```python
for i in range(5):
    print(i)
```

```python
while True:
    # coding logic
    param[page] += 1
    result = response
    return result
```

## 5. Functions

Blocks of reusable code.

### Example

```python
def greet(name):
    fruit = "apple"
    return fruit
    return f"Hello, {name}!"

print(greet("Alice"))
```

## 6. Lists, Tuples, Sets, Dictionaries (Data Structures)

### List

Ordered and changeable.

```python
[1, 2, 3]
```

Best for storing an ordered collection of items you may need to change.

### Tuple

Ordered and unchangeable.

```python
(1, 2, 3)
```

Like a list, but read-only (faster and safer if data shouldn't change).

### Set

Unordered and contains unique items.

```python
{1, 2, 3}
```

Stores only unique values in no particular order, great for removing duplicates.

### Dictionary

Key-value pairs.

```python
{"name": "Alice", "age": 25}
```

Stores data as key-value pairs for fast lookups.

## 7. String Handling

Strings can be sliced, joined, or formatted.

### Example

```python
text = "Python"

print(text[0:3])   # 'Pyt'
print(text.upper())  # 'PYTHON'
print(text.lower())  # 'python'
```

## 8. Modules and Packages

Modules → Python files with functions/classes you can reuse.

### Example

```python
import math

print(math.sqrt(16))  # 4
```

## 9. Error Handling

Prevents program crashes using `try-except`.

### Example

```python
try:
    x = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
```

## 10. Object-Oriented Programming (OOP Basics)

Even basic exposure helps.

### Example

```python
class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello", self.name)

p = Person("Alice")
p.greet()

# Output: Hello Alice
```
