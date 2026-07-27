# Part VI - JVM Memory Management & Garbage Collection

# Chapter 27: JVM Runtime Memory Areas (One of the Most Frequently Asked JVM Interview Topics)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Walmart, Visa, Adobe, Atlassian

---

# 1. Why Do Interviewers Ask This?

This is one of the first JVM questions asked in senior Java interviews.

The interviewer wants to know whether you understand:

* How Java applications execute
* Where objects are stored
* Where local variables live
* How methods are executed
* Why `StackOverflowError` occurs
* Why `OutOfMemoryError` occurs

Typical interview question:

> **Explain JVM Memory Areas.**

---

# 2. 30-Second Interview Answer

> The JVM divides memory into several runtime areas. The Heap stores objects and is shared by all threads. Each thread has its own Stack, which stores method frames, local variables, and references. The Program Counter (PC) Register keeps track of the next instruction to execute. The Native Method Stack supports JNI/native code. The Method Area stores class metadata and, in modern JVMs, is implemented using Metaspace.

---

# 3. JVM Runtime Memory Layout

```text
				JVM Runtime Memory

 ┌──────────────────────────────────────────┐
 │                                          │
 │              Heap (Shared)               │
 │                                          │
 └──────────────────────────────────────────┘

 ┌──────────────────────────────────────────┐
 │         Method Area / Metaspace          │
 └──────────────────────────────────────────┘

		Thread-1                Thread-2

 ┌──────────────┐         ┌──────────────┐
 │ PC Register  │         │ PC Register  │
 ├──────────────┤         ├──────────────┤
 │ Java Stack   │         │ Java Stack   │
 ├──────────────┤         ├──────────────┤
 │ Native Stack │         │ Native Stack │
 └──────────────┘         └──────────────┘
```

---

# 4. Heap Memory

The **Heap** stores:

* Objects
* Arrays
* Object instances

Example

```java
Student student = new Student();
```

Memory

```text
Stack                  Heap

student ─────────────► Student Object
```

Important:

The variable is **not** stored in the Heap.

Only the object is.

---

# 5. Java Stack

Every thread gets its own stack.

The stack stores:

* Local variables
* Primitive values
* Object references
* Method call frames

Example

```java
public void calculate() {

	int x = 10;

	Student s = new Student();

}
```

Memory

```text
Stack Frame

x = 10

s ─────────► Heap Object
```

---

# 6. Stack Frames

Every method call creates a new frame.

Example

```java
main()

↓

login()

↓

validate()

↓

encrypt()
```

Memory

```text
Top

encrypt()

validate()

login()

main()

Bottom
```

When a method returns,

its frame is removed.

---

# 7. Program Counter (PC) Register

Each thread has its own PC Register.

Purpose

Tracks

```text
Next JVM Instruction
```

Without it,

the JVM couldn't resume execution correctly after context switches.

---

# 8. Native Method Stack

Used for

* JNI
* Native C/C++ libraries

Example

```java
System.loadLibrary(...);
```

Native code executes using the native method stack.

---

# 9. Method Area (Metaspace)

Stores

* Class metadata
* Method metadata
* Runtime constant pool
* Field information
* Method bytecode information

Example

```java
class Employee {

}
```

Metadata goes into

```text
Metaspace
```

---

# 10. PermGen vs Metaspace

Java 7

```text
PermGen
```

Java 8+

```text
Metaspace
```

Difference

| PermGen               | Metaspace                                           |
| --------------------- | --------------------------------------------------- |
| Fixed size            | Uses native memory and can grow (subject to limits) |
| Often required tuning | More flexible                                       |
| Removed in Java 8     | Current implementation                              |

---

# 11. Thread Memory

Every thread owns

```text
Stack

PC Register

Native Stack
```

Shared

```text
Heap

Metaspace
```

Interview Favourite:

> Heap is shared.

> Stack is private.

---

# 12. Example

```java
public static void main(String[] args) {

	Employee emp =
		new Employee();

}
```

Memory

```text
Stack

emp

↓

Heap

Employee Object

↓

Method Area

Employee.class Metadata
```

---

# 13. StackOverflowError

Cause

Too many stack frames.

Classic example

```java
public void recurse() {

	recurse();

}
```

Execution

```text
recurse()

↓

recurse()

↓

recurse()

↓

...
```

Eventually

```text
StackOverflowError
```

---

# 14. OutOfMemoryError

Different problem.

Example

```java
List<byte[]> list =
		new ArrayList<>();

while(true){

	list.add(new byte[1024*1024]);

}
```

Heap

```text
1 MB

↓

2 MB

↓

100 MB

↓

500 MB

↓

Heap Full
```

Result

```text
OutOfMemoryError
```

---

# 15. Stack vs Heap

| Stack             | Heap              |
| ----------------- | ----------------- |
| Per thread        | Shared            |
| Stores frames     | Stores objects    |
| Fast allocation   | Managed by GC     |
| Automatic cleanup | Garbage collected |
| Small             | Larger            |

---

# 16. Production Example

Spring Boot Application

Request

↓

Controller

↓

Service

↓

Repository

Each method creates

```text
Stack Frames
```

Business Objects

```text
Heap
```

Application classes

```text
Metaspace
```

---

# 17. Common Interview Traps

### Are objects stored on the stack?

❌ Generally no.

Objects are typically allocated on the heap. However, modern JVMs may optimise some allocations (for example, through escape analysis and scalar replacement), but this is an implementation optimisation and shouldn't change your conceptual model.

---

### Are references stored on the Heap?

❌ Local references are stored in stack frames.

The referenced object lives in the heap.

---

### Is Stack shared?

❌ No.

Every thread has its own stack.

---

### Can StackOverflowError be fixed by increasing Heap?

❌ No.

Stack and Heap are separate memory areas.

---

### Can Metaspace run out of memory?

✅ Yes.

Example:

* Excessive dynamic class generation
* Class loader leaks

Error

```text
OutOfMemoryError: Metaspace
```

---

# 18. Production Debugging Story

Problem

Application crashed after several days.

Error

```text
OutOfMemoryError: Metaspace
```

Investigation

Application repeatedly created new class loaders for dynamically generated classes without releasing them.

Result

Metaspace kept growing.

Fix

* Eliminate the class loader leak.
* Reuse class loaders where appropriate.
* Set monitoring and sensible Metaspace limits.

---

# 19. Senior-Level Follow-up Questions

1. Explain JVM runtime memory.
2. Difference between Heap and Stack?
3. Where are objects stored?
4. Where are local variables stored?
5. What is Metaspace?
6. Difference between PermGen and Metaspace?
7. Why does `StackOverflowError` occur?
8. Why does `OutOfMemoryError` occur?
9. Is Heap thread-safe?
10. What happens during a method call?

---

# 20. Real Interview Scenario

**Interviewer:**

> "Your application throws `StackOverflowError`. How would you debug it?"

### Strong Answer

> I'd first inspect the stack trace to identify repeated method calls, which often indicate infinite recursion. If recursion is intentional, I'd verify that there's a valid termination condition. If the call depth is legitimately very large, I'd consider converting the algorithm to an iterative approach rather than simply increasing the thread stack size.

---

# 21. Cheat Sheet

| Memory Area  | Purpose                                    |
| ------------ | ------------------------------------------ |
| Heap         | Objects and arrays                         |
| Stack        | Method frames, local variables, references |
| PC Register  | Next JVM instruction                       |
| Native Stack | JNI/native methods                         |
| Metaspace    | Class metadata                             |

---

## Memory Ownership

| Shared    | Per Thread   |
| --------- | ------------ |
| Heap      | Stack        |
| Metaspace | PC Register  |
|           | Native Stack |

---

## 🎯 Interview Secret

When the interviewer asks:

> **"Explain JVM Memory."**

Don't just list the memory areas.

A senior-level answer is:

> "The JVM separates memory based on responsibility. Shared memory such as the Heap stores application objects and is managed by the garbage collector. Each thread has its own Stack, PC Register, and Native Stack, allowing methods to execute independently without interfering with other threads. Class metadata is stored in Metaspace. Understanding which area is shared versus thread-local helps explain common issues such as `OutOfMemoryError`, `StackOverflowError`, and concurrency behaviour."

That demonstrates both JVM knowledge and the ability to relate it to real production problems.

---

## Next Chapter

**Chapter 28 - Object Creation, Allocation & Escape Analysis**

We'll cover:

* Object creation lifecycle
* TLAB (Thread Local Allocation Buffer)
* Eden allocation
* Escape Analysis
* Scalar Replacement
* Stack allocation optimisations
* Object headers
* Compressed OOPs
* JIT optimisations
* Production memory tuning

This is one of the most valuable JVM internals topics for senior Java interviews because it connects Java code directly to how the JVM allocates and optimises memory.
