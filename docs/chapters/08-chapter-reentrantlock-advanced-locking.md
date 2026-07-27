# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part II - Synchronization

# Chapter 8 - ReentrantLock (Advanced Locking)

> **"While `synchronized` is simple and reliable, `ReentrantLock` provides greater flexibility and control. It is widely used in enterprise applications, high-performance libraries, and the Java Collections Framework."**

---

# Learning Objectives

After this chapter, you will understand:

* Why `ReentrantLock` exists
* Internal Working
* Fair vs Non-Fair Locking
* Reentrant Nature
* `lock()`
* `unlock()`
* `tryLock()`
* `lockInterruptibly()`
* `Condition`
* Deadlock Prevention
* Performance Comparison
* Production Use Cases

---

# 8.1 Why Another Lock?

If `synchronized` already provides mutual exclusion, why introduce another locking mechanism?

Because `synchronized` has limitations:

* No timeout while acquiring a lock.
* Cannot interrupt a thread waiting for a lock.
* Only one implicit condition queue (`wait`/`notify`).
* Limited control over lock acquisition.

`ReentrantLock` addresses these limitations by providing a richer API.

---

# 8.2 What is ReentrantLock?

`ReentrantLock` is a class from the `java.util.concurrent.locks` package that provides explicit locking.

Unlike `synchronized`, where the JVM acquires and releases the lock automatically, you control when the lock is acquired and released.

```java
Lock lock = new ReentrantLock();
```

---

# 8.3 Basic Example

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class BankAccount {

	private int balance = 10000;

	private final Lock lock = new ReentrantLock();

	public void withdraw(int amount) {

		lock.lock();

		try {

			balance -= amount;

		} finally {

			lock.unlock();

		}

	}

}
```

> **Always release the lock inside a `finally` block.** This ensures the lock is released even if an exception occurs.

---

# 8.4 What Happens Internally?

When a thread executes:

```java
lock.lock();
```

the following occurs:

```text
Thread

↓

Requests Lock

↓

Available?

↓

YES → Acquire Lock

↓

Execute Critical Section

↓

unlock()

↓

Next Waiting Thread
```

Only one thread owns the lock at any time.

---

# 8.5 Reentrant Nature

Just like `synchronized`, `ReentrantLock` is **reentrant**.

```java
public class Account {

	private final Lock lock = new ReentrantLock();

	public void transfer() {

		lock.lock();

		try {

			validate();

		} finally {

			lock.unlock();

		}

	}

	private void validate() {

		lock.lock();

		try {

			// validation logic

		} finally {

			lock.unlock();

		}

	}

}
```

The same thread can acquire the lock multiple times.

Internally:

```text
Lock Count

Acquire → 1

Acquire → 2

Unlock → 1

Unlock → 0

Released
```

---

# 8.6 Fair vs Non-Fair Lock

### Non-Fair Lock (Default)

```java
Lock lock = new ReentrantLock();
```

A newly arriving thread may acquire the lock before waiting threads.

Advantages:

* Higher throughput
* Better performance

Disadvantage:

* Thread starvation is possible.

---

### Fair Lock

```java
Lock lock = new ReentrantLock(true);
```

Threads acquire the lock in FIFO order.

```text
Thread-1

↓

Thread-2

↓

Thread-3
```

Advantages:

* Predictable scheduling
* No starvation

Disadvantages:

* Lower throughput
* Increased context switching

Most production systems use the **default non-fair mode** unless fairness is a strict requirement.

---

# 8.7 tryLock()

One of the biggest advantages over `synchronized`.

```java
if(lock.tryLock()){

	try{

		processPayment();

	} finally{

		lock.unlock();

	}

}else{

	System.out.println("Resource Busy");

}
```

If the lock is unavailable, the thread continues immediately instead of blocking.

Useful for responsive applications.

---

# 8.8 Timed tryLock()

```java
if(lock.tryLock(5, TimeUnit.SECONDS)){

	try{

		process();

	} finally{

		lock.unlock();

	}

}
```

The thread waits for up to five seconds.

If the lock cannot be acquired within the timeout, it proceeds without waiting indefinitely.

---

# 8.9 lockInterruptibly()

Suppose a thread is waiting for a lock.

Using:

```java
lock.lock();
```

it cannot respond to interruption until the lock is acquired.

With:

```java
lock.lockInterruptibly();
```

the waiting thread can be interrupted.

```java
try {

	lock.lockInterruptibly();

	try {

		process();

	} finally {

		lock.unlock();

	}

} catch (InterruptedException e) {

	Thread.currentThread().interrupt();

}
```

Useful for graceful shutdowns and task cancellation.

---

# 8.10 Condition Objects

With `synchronized`, there is only one waiting queue per monitor.

`ReentrantLock` allows multiple independent waiting queues.

```java
Condition notFull = lock.newCondition();

Condition notEmpty = lock.newCondition();
```

Example:

Producer

```text
Wait until queue has space
```

Consumer

```text
Wait until queue has data
```

Each condition has its own queue, making coordination more efficient.

---

# 8.11 Producer-Consumer Example

```java
lock.lock();

try{

	while(queue.isEmpty()){

		notEmpty.await();

	}

	process(queue.remove());

} finally{

	lock.unlock();

}
```

Producer:

```java
lock.lock();

try{

	queue.add(item);

	notEmpty.signal();

} finally{

	lock.unlock();

}
```

This is much more expressive than using `wait()` and `notify()`.

---

# 8.12 Deadlock Prevention Using tryLock()

Two locks:

```text
Account-A

Account-B
```

Without care:

Thread-1

```text
A → B
```

Thread-2

```text
B → A
```

Deadlock.

Using:

```java
if(lock.tryLock()){
```

both threads can back off and retry later instead of waiting forever.

---

# 8.13 Performance Comparison

| Feature                | synchronized | ReentrantLock         |
| ---------------------- | ------------ | --------------------- |
| Automatic Lock Release | ✅            | ❌                     |
| Timeout Support        | ❌            | ✅                     |
| Interruptible Lock     | ❌            | ✅                     |
| Fair Lock              | ❌            | ✅                     |
| Multiple Conditions    | ❌            | ✅                     |
| Easy to Use            | ✅            | Slightly More Complex |

Modern JVMs have optimized `synchronized` significantly. Choose `ReentrantLock` for its additional capabilities rather than assuming it is always faster.

---

# 8.14 Real Spring Boot Example

Inventory Service

```java
@Service
public class InventoryService {

	private final Lock lock = new ReentrantLock();

	public void reserveStock(Product product){

		lock.lock();

		try{

			if(product.getQuantity() > 0){

				product.setQuantity(
					product.getQuantity() - 1
				);

			}

		} finally{

			lock.unlock();

		}

	}

}
```

In distributed applications with multiple JVMs, this lock only protects threads within the same application instance. Cross-instance coordination requires database or distributed locking.

---

# 8.15 Common Interview Questions

### Q1. Why use `ReentrantLock` instead of `synchronized`?

When you need timeout support, interruptible locking, fairness, or multiple condition variables.

---

### Q2. What happens if `unlock()` is forgotten?

The lock remains held, and other threads may block indefinitely, effectively causing a deadlock.

---

### Q3. Why is `finally` mandatory?

To guarantee the lock is released even if an exception occurs.

---

### Q4. What is a Fair Lock?

A lock that grants access in approximately FIFO order, reducing starvation at the cost of throughput.

---

### Q5. Is `ReentrantLock` reentrant?

Yes.

The same thread can acquire it multiple times. Each acquisition must be matched with a corresponding `unlock()`.

---

# Production Scenario

**Interviewer:**

> "Your payment service occasionally hangs because several threads are waiting on locks. How would you investigate?"

A strong answer:

1. Capture a thread dump (`jstack`).
2. Look for threads in the `BLOCKED` or `WAITING` state.
3. Check whether any `ReentrantLock` is not being released.
4. Ensure every `lock()` has a matching `unlock()` inside a `finally` block.
5. Consider `tryLock()` with timeouts to avoid indefinite waiting.
6. Review lock ordering to eliminate deadlocks.

---

# Best Practices

✅ Always call `unlock()` in a `finally` block.

✅ Prefer `tryLock()` when indefinite blocking is undesirable.

✅ Use fair locks only when starvation is unacceptable.

✅ Keep critical sections short.

✅ Avoid holding locks while making database calls or remote API requests.

---

# Chapter Summary

* `ReentrantLock` provides explicit, flexible locking.
* It supports fairness, interruption, timeouts, and multiple conditions.
* It is reentrant, just like `synchronized`.
* Proper lock management is essential to avoid deadlocks.
* Use it when advanced synchronization features are required.

---

# Progress Update

**Completed Chapters:**

* ✅ Chapter 1 - Introduction to Concurrency
* ✅ Chapter 2 - Java Memory Model
* ✅ Chapter 3 - Process & Thread Lifecycle
* ✅ Chapter 4 - Heap, Stack & CPU Cache
* ✅ Chapter 5 - Memory Visibility
* ✅ Chapter 6 - `synchronized`
* ✅ Chapter 7 - `volatile`
* ✅ Chapter 8 - `ReentrantLock`

**Next Chapter:**

## Chapter 9 - ReadWriteLock

We'll cover:

* Why multiple readers should not block each other
* Read Lock vs Write Lock
* Lock Downgrading
* Cache implementation using `ReadWriteLock`
* Performance benchmarks
* Production examples (configuration cache, pricing engine, in-memory reference data)
* Common interview questions and pitfalls

This chapter introduces a locking strategy that significantly improves throughput for **read-heavy applications**, a common pattern in enterprise Java systems.
