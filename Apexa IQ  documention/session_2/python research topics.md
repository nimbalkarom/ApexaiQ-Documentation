# Research Notes

Notes on core Python concepts and general software engineering practices, organized as reference tables.

---

## 1. Python Research Topics

| Topic | What It Is | Key Points |
|---|---|---|
| **Indentation** | Python uses whitespace (not braces) to define code blocks | Consistent indent (usually 4 spaces) is mandatory; mixing tabs/spaces causes `IndentationError`; defines scope for loops, functions, classes, conditionals |
| **Comments** | Text ignored by the interpreter, used to explain code | `#` for single-line comments; triple-quoted strings (`'''` or `"""`) used for multi-line comments/docstrings; good comments explain *why*, not *what* |
| **Functions** | Reusable, named blocks of code | Defined with `def`; can take positional, keyword, default, `*args`, `**kwargs` parameters; return values with `return`; support recursion, closures, and lambda (anonymous) functions |
| **OOP (Object-Oriented Programming)** | Programming paradigm based on objects and classes | Core pillars: Encapsulation, Abstraction, Inheritance, Polymorphism; Python supports classes, objects, `__init__`, `self`, class/instance/static methods, magic/dunder methods (`__str__`, `__repr__`, etc.) |
| **File Handling** | Reading/writing files from Python | `open()` with modes (`r`, `w`, `a`, `rb`, `wb`, etc.); `with` statement auto-closes files; methods like `.read()`, `.write()`, `.readlines()`; works with text, CSV, JSON, binary files |
| **Exception Handling** | Managing runtime errors gracefully | `try` / `except` / `else` / `finally` blocks; can catch specific exceptions or use a general `Exception`; custom exceptions via subclassing `Exception`; `raise` to trigger errors intentionally |
| **NumPy & Pandas** | Core data science/analysis libraries | NumPy: fast array/matrix operations, vectorization, broadcasting; Pandas: `DataFrame`/`Series` for tabular data, filtering, grouping, merging, handling missing data (`NaN`) |
| **Selenium for Scraping** | Browser automation library, often used for web scraping | Automates real browsers (Chrome, Firefox) via WebDriver; useful for JS-heavy/dynamic sites where simple HTTP requests fail; locates elements (by ID, XPath, CSS selector), simulates clicks/typing/scrolling |
| **Regex (Regular Expressions)** | Pattern-matching language for strings | Python's `re` module (`match`, `search`, `findall`, `sub`); common patterns: `\d`, `\w`, `\s`, quantifiers (`*`, `+`, `?`, `{n,m}`), groups `()`, anchors (`^`, `$`) |
| **Multithreading / Multiprocessing** | Running multiple tasks "at once" | Multithreading: multiple threads in one process, good for I/O-bound tasks, limited by the GIL; Multiprocessing: multiple separate processes, true parallel execution, good for CPU-bound tasks |
| **Concurrency vs. Parallelism** | Two different ways of handling multiple tasks | Concurrency = dealing with multiple tasks by interleaving/switching (not necessarily simultaneous); Parallelism = literally running multiple tasks at the same time on multiple cores; concurrency is about structure, parallelism is about execution |

---

## 2. Other Topics (Software Engineering Practices)

| Topic | What It Is | Key Points |
|---|---|---|
| **SDLC (Software Development Life Cycle)** | The overall process of building software | Stages: Requirement Analysis → Design → Development → Testing → Deployment → Maintenance; models include Waterfall, Agile, Spiral, V-Model |
| **Agile & Scrum** | Iterative approach to software delivery | Agile: values flexibility, customer collaboration, incremental delivery (per the Agile Manifesto); Scrum: a specific Agile framework with sprints, daily stand-ups, sprint planning/review/retrospective, roles like Scrum Master and Product Owner |
| **Code Version Control** | Tracking and managing changes to code over time | Git is the standard tool; concepts include commits, branches, merging, pull requests, rebasing; platforms like GitHub/GitLab/Bitbucket host repositories and enable collaboration |
| **Documentation (Doc)** | Written material explaining code/systems | Includes docstrings, README files, API docs, architecture diagrams; good docs improve onboarding, maintainability, and reduce knowledge silos |
| **Risk Management** | Identifying and mitigating project/technical risks | Steps: identify risks → assess likelihood/impact → mitigate/plan contingencies → monitor; applies to schedule risk, technical debt, security risk, dependency risk |
| **Python Coding Standards** | Conventions for writing consistent, readable Python | Naming conventions (snake_case for functions/variables, PascalCase for classes), consistent indentation, meaningful names, avoiding overly long functions |
| **PEP-8** | Python's official style guide | Covers indentation (4 spaces), line length (~79 chars), whitespace rules, naming conventions, import ordering; widely enforced via linters |
| **Comments / Docstrings** | Explaining code intent and usage | Docstrings (`"""..."""`) document functions/classes/modules and are accessible via `help()` or `__doc__`; follow formats like Google style, NumPy style, or reStructuredText |
| **Error Handling & Logging** | Managing failures and tracking application behavior | Use `try/except` for error handling; the `logging` module for structured logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` levels) instead of `print()` statements |
| **Efficient Code** | Writing performant, resource-conscious code | Consider time/space complexity (Big-O), avoid unnecessary loops/recomputation, use built-in functions and appropriate data structures, profile before optimizing |
| **Various Principles** | Design principles for maintainable code | Includes DRY (Don't Repeat Yourself), KISS (Keep It Simple), YAGNI (You Aren't Gonna Need It), SOLID principles (for OOP design) |
| **Unit Testing / Validation** | Verifying individual pieces of code work correctly | Python's `unittest` or `pytest` frameworks; tests should be isolated, repeatable, and fast; validation ensures inputs/outputs meet expected constraints |
| **Ruff, Black** | Python tooling for code quality | Black: an opinionated auto-formatter that enforces consistent style; Ruff: a fast linter (and formatter) that checks for style violations, unused imports, bugs, and PEP-8 compliance |
