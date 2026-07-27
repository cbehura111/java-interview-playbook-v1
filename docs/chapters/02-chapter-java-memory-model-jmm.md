# Java Backend Engineering Interview Handbook

## Volume 1 - Java Core & Concurrency

# Chapter 2 - Java Memory Model (JMM)

> **"The Java Memory Model is one of the most important topics in senior Java interviews. Almost every concurrency mechanism-`volatile`, `synchronized`, locks, atomic classes, and concurrent collections-is built on top of it."**

---

# 2.1 Why Do We Need the Java Memory Model?

Imagine two threads in a banking application.

**Thread-1**

```java
account.setBalance(5000);
account.setUpdated(true);
```

**Thread-2**

```java
if(account.isUpdated()) {
	System.out.println(account.getBalance());
}
```

At first glance, it seems obvious that Thread-2 should always print **5000**.

Unfortunately...

**That is NOT guaranteed.**

Thread-2 may print:

```
0
```

or even never see `updated = true`.

Why?

Because modern CPUs, compilers, and the JVM all optimize memory access.

Without defined rules, every machine could behave differently.

The Java Memory Model (JMM) defines those rules.

---

# 2.2 What is the Java Memory Model?

**Definition**

The Java Memory Model defines how:

* Threads communicate
* Variables are stored
* Variables are read
* Changes become visible
* Instructions are reordered

It guarantees that Java programs behave consistently across:

* Intel CPUs
* AMD CPUs
* ARM processors
* Windows
* Linux
* macOS

Without JMM, a multithreaded Java application might work correctly on one machine and fail unpredictably on another.

---

# 2.3 Why CPUs Don't Always Read RAM

Reading RAM is relatively slow.

Modern CPUs therefore use multiple levels of cache.

```
				CPU

			 Registers
				 |
			  L1 Cache
				 |
			  L2 Cache
				 |
			  L3 Cache
				 |
			 Main Memory
```

Access times increase dramatically as we move farther from the CPU:

| Memory   | Relative Speed |
| -------- | -------------- |
| Register | Fastest        |
| L1 Cache | Very Fast      |
| L2 Cache | Fast           |
| L3 Cache | Moderate       |
| RAM      | Slowest        |

Each CPU core maintains its own caches to improve performance.

---

# 2.4 The Visibility Problem

Suppose we have:

```java
boolean running = true;
```

Thread-1

```java
while(running){
	// processing
}
```

Thread-2

```java
running = false;
```

Logically, Thread-1 should stop.

However, it may continue forever.

Why?

Because Thread-1 may keep reading the cached value:

```
running = true
```

instead of the updated value from main memory.

This is called a **visibility problem**.

---

# 2.5 Working Memory vs Main Memory

The Java Memory Model introduces an abstraction.

Every thread has its own **Working Memory**.

```
			   Main Memory

		balance = 5000

		updated = true

			  ^      ^
			  |      |

	 ----------------------------

	  Thread A Working Memory

	  balance = 0

	  updated = false

	 ----------------------------

	  Thread B Working Memory

	  balance = 5000

	  updated = true
```

A thread may continue using its local copy until synchronization forces it to refresh from main memory.

This abstraction explains why two threads can temporarily observe different values for the same variable.

---

# 2.6 Three Guarantees of the JMM

The JMM provides rules around three key properties.

## 1. Visibility

When one thread updates a variable, when will another thread see that change?

This is controlled using mechanisms like:

* `volatile`
* `synchronized`
* locks
* atomic classes

---

## 2. Atomicity

Can another thread interrupt an operation halfway through?

Example:

```java
counter++;
```

Looks like one statement.

Actually it is three operations.

```
Read

|

Increment

|

Write
```

Two threads executing this simultaneously can overwrite each other's updates, leading to lost increments.

---

## 3. Ordering

The compiler and CPU are allowed to reorder instructions to improve performance, provided the behavior remains correct for a single thread.

Example:

```java
x = 10;
ready = true;
```

The JVM may internally execute:

```
ready = true;

x = 10;
```

In a multithreaded program, another thread might observe `ready == true` before `x` has been updated.

The JMM defines when such reorderings are permitted and how synchronization prevents harmful ones.

---

# 2.7 Happens-Before Relationship

One of the most important concepts in concurrency is the **Happens-Before** relationship.

If operation A **happens-before** operation B, then:

* All writes performed by A are guaranteed to be visible to B.
* The execution order between A and B is preserved.

Common happens-before relationships include:

* Exiting a `synchronized` block happens-before entering the same monitor.
* Writing to a `volatile` variable happens-before reading that variable.
* Calling `Thread.start()` happens-before the new thread begins execution.
* Completion of a thread happens-before another thread successfully returns from `Thread.join()`.

These guarantees are the foundation of safe communication between threads.

---

# 2.8 Example Without Synchronization

```java
public class SharedData {

	private boolean ready = false;
	private int number = 0;

	public void writer() {
		number = 42;
		ready = true;
	}

	public void reader() {
		if (ready) {
			System.out.println(number);
		}
	}
}
```

Although it appears correct, there is no guarantee that `reader()` will observe `number == 42` after seeing `ready == true`.

Without synchronization, visibility and ordering are not guaranteed.

---

# 2.9 Example Using `volatile`

```java
public class SharedData {

	private volatile boolean ready = false;
	private int number = 0;

	public void writer() {
		number = 42;
		ready = true;
	}

	public void reader() {
		if (ready) {
			System.out.println(number);
		}
	}
}
```

Declaring `ready` as `volatile` ensures that:

* Updates to `ready` are immediately visible to other threads.
* Writes before `ready = true` are also visible to any thread that subsequently reads `ready`.

This makes the communication between the writer and reader safe in this pattern.

---

# 2.10 Real Production Example

Consider a Spring Boot microservice that loads configuration asynchronously at startup.

```java
private volatile boolean initialized = false;

public void loadConfiguration() {
	// Load configuration from database
	initialized = true;
}

public void processRequest() {
	if (!initialized) {
		throw new IllegalStateException("Configuration not loaded");
	}
}
```

Without `volatile`, request-handling threads might continue to see `initialized == false` even after the configuration has finished loading.

---

# Common Interview Questions

### Q1: Why is the Java Memory Model needed?

**Answer:** It defines consistent rules for visibility, ordering, and synchronization so that multithreaded Java programs behave correctly across different CPUs and operating systems.

---

### Q2: Does `volatile` make operations atomic?

**Answer:** No. It guarantees visibility and restricts certain instruction reorderings, but operations like `count++` remain non-atomic.

---

### Q3: Why can one thread fail to see another thread's update?

**Answer:** Because threads may read cached copies of variables or observe reordered instructions unless synchronization establishes a happens-before relationship.

---

### Q4: Is `counter++` atomic?

**Answer:** No. It consists of three steps: read, increment, and write. Multiple threads can interleave these steps and lose updates.

---

# Chapter Summary

* The Java Memory Model defines how threads interact through memory.
* Each thread may work with cached copies of variables.
* The JMM guarantees visibility, atomicity (through synchronization mechanisms), and ordering.
* The happens-before relationship is the key concept for reasoning about thread safety.
* `volatile` improves visibility but does not make compound operations atomic.

---

# What's Next?

In **Chapter 3 - Processes, Threads & Thread Lifecycle**, we'll build on the JMM by exploring:

* How the JVM creates and manages threads.
* The complete lifecycle of a Java thread.
* Context switching and its performance cost.
* Thread priorities and scheduling.
* Thread states and debugging with thread dumps.

These concepts will prepare you for understanding thread pools, executors, and the production concurrency scenarios later in Volume 1.
