# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part II - Synchronization

# Chapter 10 - StampedLock (High-Performance Locking)

> **"Most applications read data far more frequently than they modify it. `StampedLock` was designed to make those reads as fast as possible while still maintaining correctness."**

Introduced in **Java 8**, `StampedLock` is an advanced synchronization mechanism in the `java.util.concurrent.locks` package. Unlike `ReentrantLock` and `ReadWriteLock`, it introduces **Optimistic Reading**, allowing threads to read shared data without immediately acquiring a traditional lock.

---

# Learning Objectives

After this chapter, you will understand:

* Why `StampedLock` was introduced
* Optimistic Locking
* Pessimistic Locking
* Read Lock
* Write Lock
* Lock Conversion
* Internal Working
* Performance Benefits
* Production Use Cases
* Common Interview Questions

---

# 10.1 Why Do We Need StampedLock?

Imagine a stock trading platform.

Every second:

* 500,000 price lookups
* 200 portfolio updates
* 100 administrator changes

The workload is approximately:

```text
Reads  : 99.9%

Writes : 0.1%
```

Using `ReadWriteLock`:

Every read still acquires and releases a lock.

This overhead becomes noticeable under extremely high read traffic.

`StampedLock` reduces that overhead through **optimistic reads**.

---

# 10.2 What is StampedLock?

A `StampedLock` supports three locking modes:

```text
Write Lock

↓

Read Lock

↓

Optimistic Read
```

Unlike `ReentrantLock`, every lock acquisition returns a **stamp**, which represents the current lock state.

Example:

```java
StampedLock lock = new StampedLock();
```

---

# 10.3 Traditional Read Lock

```java
long stamp = lock.readLock();

try {

	return product;

} finally {

	lock.unlockRead(stamp);

}
```

This behaves similarly to `ReadWriteLock`.

Readers can proceed concurrently.

---

# 10.4 Write Lock

```java
long stamp = lock.writeLock();

try {

	updateInventory();

} finally {

	lock.unlockWrite(stamp);

}
```

Only one writer is permitted.

All readers wait until the writer finishes.

---

# 10.5 Optimistic Read

This is the most important feature.

```java
long stamp = lock.tryOptimisticRead();

Product p = product;
```

Notice:

No lock is acquired.

No thread blocks.

The read proceeds optimistically under the assumption that no writer is active.

---

# 10.6 Why Is It Called Optimistic?

Because the thread assumes:

> "I believe nobody will modify the data while I'm reading it."

If that assumption is correct:

No locking overhead.

Maximum performance.

If not:

Retry using a proper read lock.

---

# 10.7 Validation

Every optimistic read must be validated.

```java
long stamp = lock.tryOptimisticRead();

Product p = product;

if (!lock.validate(stamp)) {

	stamp = lock.readLock();

	try {

		p = product;

	} finally {

		lock.unlockRead(stamp);

	}

}
```

This ensures correctness if a writer modified the data during the optimistic read.

---

# 10.8 Internal Working

Execution flow:

```text
Optimistic Read

↓

Writer Modified Data?

↓

NO

↓

Success

------------------

YES

↓

Validation Failed

↓

Acquire Read Lock

↓

Read Again
```

This fallback mechanism is what makes `StampedLock` both fast and safe.

---

# 10.9 Lock Conversion

One advantage of `StampedLock` is lock conversion.

Suppose you already hold a read lock.

```java
long stamp = lock.readLock();
```

Later you decide to update the object.

Instead of releasing the read lock and acquiring a write lock separately:

```java
stamp = lock.tryConvertToWriteLock(stamp);
```

If successful:

```text
Read Lock

↓

Write Lock
```

Otherwise, the conversion fails and you must explicitly acquire the write lock.

---

# 10.10 Real Example

```java
public void updatePrice() {

	long stamp = lock.readLock();

	try {

		if (priceChanged()) {

			long ws =
				lock.tryConvertToWriteLock(stamp);

			if (ws != 0L) {

				stamp = ws;

				update();

			}

		}

	} finally {

		lock.unlock(stamp);

	}

}
```

This avoids unnecessary unlock/relock operations.

---

# 10.11 Real Production Example

Market Data Cache

```java
public double getPrice() {

	long stamp =
		lock.tryOptimisticRead();

	double p = price;

	if (!lock.validate(stamp)) {

		stamp = lock.readLock();

		try {

			p = price;

		} finally {

			lock.unlockRead(stamp);

		}

	}

	return p;

}
```

This pattern is common in:

* Trading systems
* Analytics engines
* Pricing services
* Real-time dashboards

where reads vastly outnumber writes.

---

# 10.12 ReadWriteLock vs StampedLock

| Feature                 | ReadWriteLock | StampedLock                      |
| ----------------------- | ------------- | -------------------------------- |
| Multiple Readers        | ✅             | ✅                                |
| Exclusive Writer        | ✅             | ✅                                |
| Optimistic Read         | ❌             | ✅                                |
| Lock Conversion         | ❌             | ✅                                |
| Reentrant               | ✅             | ❌                                |
| Higher Read Performance | Good          | Excellent (read-heavy workloads) |

---

# 10.13 Important Limitation

Unlike `ReentrantLock`:

**`StampedLock` is NOT reentrant.**

Example:

```java
writeLock();

↓

call another method

↓

writeLock()
```

The second acquisition by the same thread will block, potentially causing a deadlock.

This is one of the most common interview questions about `StampedLock`.

---

# 10.14 When Should You Use StampedLock?

Good candidates:

* In-memory caches
* Pricing engines
* Configuration services
* Routing tables
* GIS (Geographic Information Systems)
* Market data feeds
* Read-heavy microservices

Avoid it for:

* Write-heavy workloads
* Recursive locking
* Complex nested locking scenarios

---

# 10.15 Performance

Typical workload:

```text
Reads  = 100,000

Writes = 100
```

Performance trend:

```text
synchronized

↓

ReadWriteLock

↓

StampedLock (Optimistic Read)
```

> The exact improvement depends on workload characteristics, CPU architecture, JVM version, and contention. Always benchmark with realistic production traffic before choosing a synchronization strategy.

---

# 10.16 Common Interview Questions

### Q1. Why was `StampedLock` introduced?

To improve scalability in highly read-intensive applications by introducing optimistic reads and lock conversion.

---

### Q2. What is an Optimistic Read?

A read performed without immediately acquiring a traditional lock, followed by validation to ensure no writer modified the data.

---

### Q3. Why must `validate()` be called?

Because another thread may have updated the shared data while the optimistic read was in progress.

---

### Q4. Is `StampedLock` reentrant?

No.

Unlike `synchronized` and `ReentrantLock`, it is **not** reentrant.

---

### Q5. Can `StampedLock` always replace `ReadWriteLock`?

No.

It is best suited for read-heavy scenarios and requires more careful programming due to its non-reentrant nature.

---

# Production Scenario

**Interviewer:**

> "Your pricing engine performs millions of reads per minute but only a few updates. Which lock would you choose?"

A strong answer:

* Consider `StampedLock` with optimistic reads.
* Validate optimistic reads before using the data.
* Fall back to a read lock if validation fails.
* Benchmark against `ReadWriteLock` because the actual benefit depends on the workload.

---

# Best Practices

✅ Always validate optimistic reads.

✅ Keep write operations short.

✅ Use lock conversion when appropriate.

✅ Understand that `StampedLock` is **not** reentrant.

✅ Benchmark before adopting it in production.

---

# Common Mistakes

❌ Forgetting to call `validate()` after an optimistic read.

❌ Assuming optimistic reads are always correct.

❌ Treating `StampedLock` as reentrant.

❌ Using it in write-heavy applications without measuring performance.

---

# Chapter Summary

* `StampedLock` extends traditional read-write locking with optimistic reads.
* Optimistic reads avoid locking when no writer is active, improving scalability.
* Every optimistic read must be validated.
* `StampedLock` supports lock conversion but is **not** reentrant.
* It is a powerful choice for read-dominant systems such as caches, pricing engines, and market data services.

---

# Progress Update

### ✅ Part I - Foundations

* Chapter 1 - Introduction to Concurrency
* Chapter 2 - Java Memory Model
* Chapter 3 - Process & Thread Lifecycle
* Chapter 4 - Heap, Stack & CPU Cache
* Chapter 5 - Memory Visibility & Instruction Reordering

### ✅ Part II - Synchronization

* Chapter 6 - `synchronized`
* Chapter 7 - `volatile`
* Chapter 8 - `ReentrantLock`
* Chapter 9 - `ReadWriteLock`
* Chapter 10 - `StampedLock`

---

# Next Chapter

## Chapter 11 - HashMap Internals (From Source Code to Production)

This will be one of the largest and most detailed chapters in the handbook (approximately 40-50 pages in book form). It will cover:

* Internal structure of `HashMap`
* Buckets and arrays
* Hash function
* Collision handling
* Linked List vs Red-Black Tree
* Resize (Rehashing)
* Load Factor
* Initial Capacity
* Time Complexity
* Java 7 vs Java 8 implementation differences
* Why `HashMap` is not thread-safe
* `ConcurrentHashMap` overview
* Production debugging scenarios
* Source code walkthroughs
* Senior interview questions

This chapter directly prepares you for the **first scenario-based interview question** from your original list: **"What happens if multiple threads access a HashMap concurrently?"**
