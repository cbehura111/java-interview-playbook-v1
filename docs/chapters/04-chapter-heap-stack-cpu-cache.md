# Java Backend Engineering Interview Handbook

## Volume 1 - Java Core & Concurrency

# Chapter 4 - Heap, Stack & CPU Cache

> **"Most concurrency bugs happen because developers don't fully understand where data is stored and how threads access it."**

---

# Learning Objectives

After this chapter, you will understand:

* JVM Memory Layout
* Heap Memory
* Stack Memory
* Metaspace
* CPU Cache
* Registers
* Why Local Variables are Thread Safe
* Why Objects Need Synchronization
* Escape Analysis
* Real Production Examples

---

# 4.1 Why This Chapter Matters

Imagine this Spring Boot code:

```java
public void transfer() {

	int amount = 500;

	Account account = repository.findById(1);

	account.setBalance(
			account.getBalance() - amount);
}
```

Interview question:

**Which variables are thread-safe?**

Many developers answer:

> "Everything."

Wrong.

Understanding **Heap vs Stack** immediately explains the answer.

---

# 4.2 JVM Memory Layout

When a Java application starts, the JVM creates several memory areas.

```text
				 JVM

	 +--------------------------+
	 |        Heap              |
	 +--------------------------+

	 +--------------------------+
	 |      Metaspace           |
	 +--------------------------+

Thread-1 Stack

Thread-2 Stack

Thread-3 Stack

Native Memory

Code Cache
```

Each area serves a different purpose.

---

# 4.3 Heap Memory

The **Heap** stores all objects created using `new`.

Example

```java
Account account = new Account();
```

The object lives in the Heap.

Every thread can access the Heap.

Example:

```text
			  Heap

	   +---------------+

	   Account

	   Balance=5000

	   Name=John

	   +---------------+

		 ▲       ▲

		 │       │

	 Thread1 Thread2
```

Since multiple threads can access the same object, synchronization may be required.

---

# 4.4 Stack Memory

Every thread has its own stack.

```text
Thread-1 Stack

transfer()

amount = 500

account reference
```

Thread-2

```text
transfer()

amount = 1000

account reference
```

Stacks are never shared.

This is why local variables are naturally thread-safe.

---

# 4.5 Stack Frame

Every method call creates a Stack Frame.

Example

```java
public void transfer() {

	int amount = 100;

	validate();

}
```

Stack becomes

```text
Thread Stack

validate()

↓

transfer()

↓

main()
```

When `validate()` finishes

its frame is removed.

---

# 4.6 What is Stored in Stack?

Suppose

```java
Customer customer = new Customer();
```

Stack stores

```text
customer → 0x12345
```

Heap stores

```text
Customer Object

Name

Address

Age
```

Important point:

The **reference** is stored in the stack.

The **actual object** is stored in the heap.

---

# 4.7 Why Local Variables Are Safe

Example

```java
public void calculate(){

	int total = 500;

}
```

Every thread gets

its own copy.

```text
Thread A

total = 500

------------------

Thread B

total = 500
```

There is no sharing.

No synchronization needed.

---

# 4.8 Why Objects Are Not Thread Safe

Example

```java
Account account =
repository.findById(1);
```

Now

```java
account.setBalance(100);
```

Another thread

```java
account.setBalance(200);
```

Both modify

the same Heap object.

```text
			Heap

	  Account

Balance = ?

Thread A

↓

Thread B
```

Race condition.

---

# 4.9 CPU Registers

Registers are the fastest storage available.

```text
CPU

Registers

↓

L1 Cache

↓

L2 Cache

↓

L3 Cache

↓

RAM
```

Operations happen here first.

Example

```java
int x = 10;
```

CPU loads

```text
Register

x=10
```

before writing back.

---

# 4.10 CPU Cache

Every CPU core has its own cache.

```text
		  Main Memory

		  balance=5000

		  ▲      ▲

		  │      │

Core1          Core2

L1 Cache      L1 Cache

5000          4500
```

Two cores can temporarily see different values.

This is exactly why the Java Memory Model exists.

---

# 4.11 Cache Coherency Problem

Thread A

```java
balance = 1000;
```

Thread B

```java
System.out.println(balance);
```

Thread B may still read

```text
500
```

because its cache has not yet been updated.

This leads to stale data.

Synchronization mechanisms ensure caches are synchronized when required.

---

# 4.12 Heap vs Stack

| Heap                      | Stack                  |
| ------------------------- | ---------------------- |
| Shared                    | Private                |
| Stores Objects            | Stores Local Variables |
| Large                     | Small                  |
| Managed by GC             | Automatic cleanup      |
| Can cause race conditions | Thread-safe by design  |

---

# 4.13 Example

```java
public class Bank {

	private Account account =
			new Account();

	public void transfer() {

		int amount = 500;

		account.withdraw(amount);

	}

}
```

Memory layout

```text
Heap

Bank

↓

Account

↓

Balance

-------------------

Thread Stack

amount

account reference
```

Notice:

Only the `amount` variable is private to the thread.

The `Account` object is shared.

---

# 4.14 Production Example

Spring Singleton Bean

```java
@Service
public class CounterService {

	private int counter;

}
```

Spring creates

one object.

```text
Singleton Bean

CounterService

↓

counter
```

Every request thread accesses the same bean instance.

This is why mutable fields in singleton beans can lead to race conditions.

A safer design is to keep singleton beans **stateless** or protect shared mutable state with appropriate synchronization.

---

# 4.15 Escape Analysis (Java Optimization)

The JIT compiler performs **Escape Analysis**.

If an object never leaves the current thread,

```java
Person person =
new Person();
```

the JVM may:

* Allocate it on the stack (or eliminate the allocation entirely through scalar replacement).
* Skip synchronization if it proves the object is thread-confined.

This optimization improves performance without changing program behavior.

---

# 4.16 Common Interview Questions

### Q1. Are local variables thread-safe?

Yes.

Every thread has its own stack.

---

### Q2. Are objects thread-safe?

No.

Objects in Heap are shared.

---

### Q3. Why is Stack thread-safe?

Each thread owns a separate stack, so no other thread can directly access its local variables.

---

### Q4. Where is an object stored?

Heap.

---

### Q5. Where is the object reference stored?

Typically in the stack (for local variables), while the object itself resides in the heap.

---

### Q6. Why do Spring singleton beans create concurrency problems?

Because one bean instance is shared across all request threads. Mutable shared state can be accessed concurrently.

---

# Production Interview Scenario

**Interviewer:**

> "A Spring Boot singleton service contains a field `private int counter;`. Occasionally the counter value is incorrect under heavy load. Why?"

A strong answer:

* Singleton beans are shared across threads.
* `counter++` is not atomic.
* Multiple request threads update the same heap object.
* Use `AtomicInteger`, synchronization, or redesign the service to be stateless.

---

# Best Practices

✅ Prefer stateless Spring singleton beans.

✅ Keep mutable data in local variables whenever possible.

✅ Use immutable objects for shared data.

✅ Protect shared mutable state with `synchronized`, locks, or atomic classes.

✅ Understand where your data lives before reasoning about thread safety.

---

# Chapter Summary

* Objects are stored in the **Heap** and may be shared across threads.
* Each thread has its own **Stack**, making local variables naturally thread-safe.
* CPU registers and caches improve performance but introduce visibility challenges.
* The Java Memory Model defines how updates become visible across threads.
* Spring singleton beans should generally avoid mutable shared state.

---

# Next Chapter

## Chapter 5 - Memory Visibility & Instruction Reordering

This chapter will dive deeper into:

* What "memory visibility" really means.
* Why CPUs and the JVM reorder instructions.
* The **happens-before** relationship in detail.
* How `volatile` prevents visibility issues.
* Real production bugs caused by instruction reordering.

> **After Chapter 5, we'll have completed the foundational theory. From Chapter 6 onward, we'll start implementing synchronization mechanisms (`synchronized`, `volatile`, locks, atomic classes) and then tackle the five production interview scenarios with a solid conceptual foundation.**
