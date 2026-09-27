# Introduction to JavaScript

## Content

- Introduction
- Basics of Js
- Control Flows
- Functions
- Arrays and Objects
- DOM Manipulation
- Event Handling
- Callback
- Promise
- Async and Await
- Closures

---

## Introduction

### What is JavaScript?

- It is created by Brendan Eich
- Initially for adding simple interactivity in Netscape browser
- Important core technology like HTML, CSS in Web App Development

### Where does it run?

- **Browser** - Client Side Scripting (Interactivity, DOM updates)
- **Node.js** - Server Side Scripting (backend apps, APIs)
- **Cross Platform** (desktop, mobile, IoT with framework)

### Basic Web Dev Analogy

- **HTML** - Structure (headings, paragraphs, buttons)
- **CSS** - Styling (colors, layout, animations)
- **JS** - Behavior (click actions, form validation, dynamic content)

---

## Basics of JavaScript

### Variables

| Keyword | Description |
|---|---|
| `var` | Used in old JavaScript code till 2015 |
| `let` | Introduced in 2015, declared before use, can't be redeclared in same scope |
| `const` | Introduced in 2015, can't be redeclared, reassigned, has block scope |

### When to Use var, let, or const?

1. Always declare variables
2. Always use `const` if the value should not be changed
3. Always use `const` if the type should not be changed (Arrays and Objects)
4. Only use `let` if you can't use `const`
5. Only use `var` if you MUST support old browsers

### Datatypes

| Type | Example |
|---|---|
| String | `"Apexaiq"` |
| Number | `25`, `3.14` |
| Boolean | `true`, `false` |
| Null | Intentional empty value |
| Undefined | Declared but not assigned |
| Object | Collection of key-value pairs |
| Arrays | Collection of the ordered of different type |

### Operators

| Type | Symbols |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `==`, `===`, `!=`, `<`, `>` |
| Logical | `&&` (AND), `\|\|` (OR), `!` (NOT) |
| Assignment | `=`, `+=`, `-=`, `*=`, `/=` |

---

## Control Flow

### Conditional Statements

- **if** - to specify a block of code to be executed, if a specified condition is true
- **else** - to specify a block of code to be executed, if the same condition is false
- **else if** - to specify a new condition to test, if the first condition is false
- **Switch** - to specify many alternative blocks of code to be executed

### Loops

- **for** - loops through a block of code a number of times
- **for/in** - loops through the properties of an object
- **for/of** - loops through the values of any iterable
- **while** - loops through a block of code while a specified condition is true
- **do/while** - also loops through a block of code while a specified condition is true

---

## Function

### What is a Function?

- A block of code designed to perform a task
- Runs only when it is called/invoked
- Helps in reusing code

### Key Points

- **Parameters** - input values
- **Return** - output value
- **Scope**:
  - Global (accessible everywhere)
  - Local (inside function)
  - Block (inside `{ }` with `let`/`const`)

### Types of Function

1. **Function Declaration (Named Function)**
   - Defined with the `function` keyword
   - Hoisted - can be called before declaration

2. **Function Expression**
   - Function stored in a variable
   - Not hoisted - can only be used after definition

3. **Arrow Function (ES6)**
   - Shorter syntax using `=>`
   - Does not have its own `this` (important in objects & classes)

4. **Anonymous Function**
   - Function without a name (often used as a callback)

5. **Immediately Invoked Function Expression (IIFE)**
   - Runs automatically after being defined

6. **Higher-Order Function**
   - A function that takes another function as argument or returns a function

7. **Recursive Function**
   - A function that calls itself

---

## Array

### What is an Array?

- An ordered list of values (like a container for multiple items)
- Can store numbers, strings, objects, even functions

### Array Properties & Methods

| Method | Description |
|---|---|
| `.length` | Total items |
| `.push()` | Add at end |
| `.pop()` | Remove from end |
| `.shift()` | Remove first item |
| `.unshift()` | Add at start |
| `.map()`, `.filter()`, `.reduce()` | For processing |

---

## Objects

### What is an Object?

- A collection of key-value pairs
- Keys are properties (always strings or symbols)
- Values can be anything (string, number, array, function, object)

### Features Provided by Object

- Accessing Properties
- Adding / Updating Properties
- Deleting Properties
- Methods (Functions inside Objects)
- Built-in Object Methods

---

## DOM

### What is DOM?

- The DOM is a programming interface for HTML and XML documents
- It represents the page structure as a tree of nodes (elements, attributes, text, etc.)
- JavaScript can manipulate the DOM to change the page content, style, or structure dynamically

### Why DOM is Important?

- Lets us change content dynamically (e.g., update text, images)
- Enables interaction with users (like clicking buttons, filling forms)
- Helps in creating dynamic websites instead of static ones

### DOM Manipulation Methods

- Selecting elements
- Changing content
- Changing style
- Creating new elements

---

## Event Handling

### What is an Event?

- An event is an action that happens in the browser (e.g., a user clicks a button, presses a key, or moves the mouse)
- JavaScript can "listen" for these events and respond to them

### Common Types of Events

- `onclick` - when a user clicks an element
- `onmouseover` - when the mouse is over an element
- `onkeydown` / `onkeyup` - when a key is pressed or released
- `onsubmit` - when a form is submitted
- `onchange` - when the value of input changes

---

## Callback

### What is a Callback?

- A function passed as an argument to another function
- Allows one function to call another function later
- Useful for tasks that take time (like reading files, API calls)
- Makes code more flexible & reusable

### Why We Use Callbacks?

- **Reusability** → We can change the callback without touching the main function
- **Async Handling** → Used to wait for tasks (like API requests, file reading)
- **Control Flow** → Defines what should happen after a task is complete

---

## Promise

### What is a Promise?

- A special JavaScript object used for handling asynchronous operations
- Represents a value that may be available now, later, or never
- Has 3 states:
  - **Pending** → waiting for result
  - **Fulfilled** → operation successful (resolved)
  - **Rejected** → operation failed (error)

### Why Use Promises?

- **Avoids Callback Hell** → no deeply nested callbacks
- **Cleaner async handling** with `.then()` and `.catch()`
- **Chainable** → run multiple async operations in sequence

---

## Async and Await

### What is it?

- Async/Await is syntax built on top of Promises
- Makes asynchronous code look and behave like synchronous code
- Helps write code that is cleaner, easier to read, and debug
- `async` → tells JavaScript that the function will return a Promise
- `await` → pauses the function until the Promise is fulfilled or rejected

### Why Use Async and Await?

- Cleaner code → looks like step-by-step instructions
- Avoids chaining `.then()` → no more promise nesting
- Easy error handling → use `try...catch`
- Best practice → modern way of handling async tasks

---

## Closures

### What is a Closure?

- A function that remembers variables from its outer scope, even after the outer function has finished executing
- Created automatically whenever a function is defined inside another function
- Helps in data hiding, encapsulation, and creating private variables

### Why Use Closures?

- **Data Privacy** → Variables stay hidden & can't be accessed directly
- **Encapsulation** → Only specific functions can use the hidden variables
- **Stateful Functions** → Useful for counters, caching, event handlers, etc.
- **Functional Programming** → Forms the base of many advanced JS patterns

---

