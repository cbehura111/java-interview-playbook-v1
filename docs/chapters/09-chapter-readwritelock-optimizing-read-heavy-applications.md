# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part II - Synchronization

# Chapter 9 - ReadWriteLock (Optimizing Read-Heavy Applications)

> **"Not every operation modifies data. If 1,000 users are only reading data, why should they block each other?"**

This is exactly the problem that `ReadWriteLock` solves.

It is one of the most important concurrency utilities for building high-performance caches, pricing engines, configuration services, and other read-heavy backend systems.

---

# Learning Objectives

After this chapter, you will understand:

* Why `ReadWriteLock` exists
* Read Lock vs Write Lock
* Internal Working
* Lock Compatibility
* Lock Downgrading
* Lock Upgrading
* ReentrantReadWriteLock
* Performance Benefits
* Production Use Cases
* Common Interview Questions

---

# 9.1 Why Another Lock?

Consider an online shopping application.

Every second:

* 8,000 users view products
* 1,500 users search products
* 300 users check prices
* 20 admins update prices

Almost everyone is **reading**.

Very few are **writing**.

If we use `synchronized`:

```text
Reader-1

↓

Reader-2

↓

Reader-3

↓

Writer
```

Every reader blocks every other reader.

This wastes CPU resources and reduces throughput.

---

# 9.2 What is ReadWriteLock?

A `ReadWriteLock` provides **two different locks**:

* Read Lock
* Write Lock

```text
Read Lock

Multiple Threads

↓

Allowed

----------------------

Write Lock

Single Thread

↓

Exclusive
```

This allows multiple readers to access shared data simultaneously while still ensuring writers have exclusive access.

---

# 9.3 ReentrantReadWriteLock

Java provides the implementation:

```java
ReadWriteLock lock =
		new ReentrantReadWriteLock();
```

Internally:

```java
Lock readLock = lock.readLock();

Lock writeLock = lock.writeLock();
```

---

# 9.4 Reader Example

```java
import java.util.concurrent.locks.*;

public class ProductCache {

	private final ReadWriteLock lock =
			new ReentrantReadWriteLock();

	private final Lock read =
			lock.readLock();

	public Product getProduct() {

		read.lock();

		try {

			return product;

		} finally {

			read.unlock();

		}

	}

}
```

Many readers can execute this method simultaneously.

---

# 9.5 Multiple Readers

Suppose

Thread-1

```text
Read Product
```

Thread-2

```text
Read Product
```

Thread-3

```text
Read Product
```

Execution

```text
Reader-1

─────────────►

Reader-2

─────────────►

Reader-3

─────────────►
```

All three execute together.

No waiting.

---

# 9.6 Writer Example

```java
private final Lock write =
		lock.writeLock();

public void updateProduct(Product p){

	write.lock();

	try{

		this.product = p;

	} finally{

		write.unlock();

	}

}
```

Only one writer is allowed.

---

# 9.7 What Happens During Writing?

Suppose

Reader-1

Reader-2

Writer

Execution

```text
Reader

Reader

↓

Finish

↓

Writer Starts
```

The writer waits until all active readers have completed.

Similarly, while a writer holds the lock, new readers must wait.

---

# 9.8 Lock Compatibility

| Lock Held  | Read Request | Write Request |
| ---------- | ------------ | ------------- |
| Read Lock  | ✅ Allowed    | ❌ Wait        |
| Write Lock | ❌ Wait       | ❌ Wait        |
| No Lock    | ✅ Allowed    | ✅ Allowed     |

This compatibility matrix is the key behavior of `ReadWriteLock`.

---

# 9.9 Production Example

Configuration Cache

```java
@Service
public class ConfigCache {

	private final ReadWriteLock lock =
			new ReentrantReadWriteLock();

	private Map<String,String> cache =
			new HashMap<>();

	public String get(String key){

		lock.readLock().lock();

		try{

			return cache.get(key);

		} finally{

			lock.readLock().unlock();

		}

	}

	public void refresh(Map<String,String> data){

		lock.writeLock().lock();

		try{

			cache = data;

		} finally{

			lock.writeLock().unlock();

		}

	}

}
```

Thousands of application threads can read configuration concurrently, while periodic refreshes remain safe.

---

# 9.10 Lock Downgrading

Lock downgrading means:

```text
Write Lock

↓

Read Lock
```

This is supported.

Example:

```java
write.lock();

try {

	updateCache();

	read.lock();

} finally {

	write.unlock();

}

try {

	readCache();

} finally {

	read.unlock();

}
```

The thread updates shared data and then continues reading it without allowing another writer to modify it in between.

---

# 9.11 Lock Upgrading

Suppose:

```text
Read Lock

↓

Write Lock
```

Is this allowed?

**No.**

Example:

```java
read.lock();

write.lock();
```

This can cause deadlock if multiple readers attempt the same upgrade simultaneously.

If a write is needed, release the read lock first and then acquire the write lock.

---

# 9.12 Internal Working

Internally,

`ReentrantReadWriteLock`

maintains:

```text
Reader Count

Writer Owner

Waiting Queue
```

Execution

```text
Read Request

↓

Writer Active?

↓

YES

↓

WAIT

--------------------

NO

↓

Increment Reader Count

↓

Read
```

This coordination ensures readers and writers interact safely.

---

# 9.13 Performance Benefits

Suppose

10,000 reads

100 writes

Using

```text
synchronized
```

Only one thread executes at a time.

Using

```text
ReadWriteLock
```

Thousands of readers execute concurrently.

This dramatically improves throughput in read-heavy workloads.

> **Important:** If your workload is write-heavy, `ReadWriteLock` may not provide a benefit and can even introduce additional overhead.

---

# 9.14 Real Spring Boot Example

Pricing Service

```java
@Service
public class PricingService {

	private final ReadWriteLock lock =
			new ReentrantReadWriteLock();

	private Map<String, Double> prices =
			new HashMap<>();

	public Double getPrice(String sku){

		lock.readLock().lock();

		try{

			return prices.get(sku);

		} finally{

			lock.readLock().unlock();

		}

	}

	public void updatePrice(String sku,
							Double price){

		lock.writeLock().lock();

		try{

			prices.put(sku, price);

		} finally{

			lock.writeLock().unlock();

		}

	}

}
```

This pattern is common in pricing engines, feature flag services, and in-memory reference data.

---

# 9.15 Common Interview Questions

### Q1. Why use `ReadWriteLock` instead of `synchronized`?

Because multiple readers can execute concurrently, improving performance in read-heavy applications.

---

### Q2. Can multiple readers execute together?

Yes.

As long as no writer holds the write lock.

---

### Q3. Can multiple writers execute together?

No.

Only one writer may hold the write lock at a time.

---

### Q4. Is lock upgrading supported?

No.

Acquiring the write lock while already holding the read lock can lead to deadlock.

---

### Q5. Is lock downgrading supported?

Yes.

Acquire the read lock before releasing the write lock.

---

# Production Scenario

**Interviewer:**

> "Your product catalog receives 50,000 read requests per minute but only a few updates each hour. Which synchronization mechanism would you choose?"

A strong answer:

* `ReentrantReadWriteLock` is a good fit because reads vastly outnumber writes.
* Readers can proceed concurrently, while updates remain exclusive.
* If reads become almost entirely lock-free through immutable snapshots or concurrent collections, those approaches may offer even better scalability depending on the design.

---

# Best Practices

✅ Use `ReadWriteLock` only for read-heavy workloads.

✅ Keep write operations as short as possible.

✅ Never attempt lock upgrading.

✅ Consider immutable data structures for frequently read data.

✅ Measure performance before replacing `synchronized`; additional complexity is not always justified.

---

# Common Mistakes

❌ Using `ReadWriteLock` for write-heavy applications.

❌ Holding the write lock while making remote API calls.

❌ Attempting to upgrade a read lock to a write lock.

❌ Assuming it always outperforms `synchronized`.

---

# Chapter Summary

* `ReadWriteLock` separates read and write access.
* Multiple readers can proceed concurrently.
* Writers require exclusive access.
* Lock downgrading is supported; lock upgrading is not.
* It is ideal for caches, configuration services, and other read-dominant workloads.

---

# Progress Update

**Completed Chapters**

* ✅ Chapter 1 - Introduction to Concurrency
* ✅ Chapter 2 - Java Memory Model
* ✅ Chapter 3 - Process & Thread Lifecycle
* ✅ Chapter 4 - Heap, Stack & CPU Cache
* ✅ Chapter 5 - Memory Visibility
* ✅ Chapter 6 - `synchronized`
* ✅ Chapter 7 - `volatile`
* ✅ Chapter 8 - `ReentrantLock`
* ✅ Chapter 9 - `ReadWriteLock`

---

# Next Chapter

## Chapter 10 - StampedLock (High-Performance Locking)

We'll cover:

* Why `StampedLock` was introduced
* Optimistic Reads
* Pessimistic Reads
* Write Locks
* Lock Conversion
* Internal Working
* Performance comparison with `ReadWriteLock`
* Real-world examples (market data, inventory caches, geospatial services)
* Interview questions and production pitfalls

`StampedLock` is considered an advanced concurrency utility and is a favorite topic for Staff Engineer and Architect-level Java interviews because it demonstrates deep knowledge of balancing correctness and performance.
