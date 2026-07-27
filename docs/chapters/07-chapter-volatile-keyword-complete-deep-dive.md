# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part II - Synchronization

# Chapter 7 - `volatile` Keyword (Complete Deep Dive)

> **"Use `volatile` when multiple threads need to see the latest value of a variable, but they don't need mutual exclusion."**

One of the most common senior Java interview questions is:

> **What is the difference between `volatile` and `synchronized`?**

To answer that confidently, you first need to understand what `volatile` really guarantees-and just as importantly, what it does **not** guarantee.

---

# Learning Objectives

After this chapter, you will understand:

* What is `volatile`?
* Why `volatile` was introduced
* Memory Visibility
* Happens-Before Guarantee
* Instruction Reordering
* Memory Barriers
* When to use `volatile`
* When **not** to use `volatile`
* `volatile` vs `synchronized`
* Real-world Production Examples

---

# 7.1 The Problem `volatile` Solves

Consider a background worker.

```java
public class Worker {

	private boolean running = true;

	public void work() {

		while (running) {
			processTask();
		}

	}

	public void stop() {
		running = false;
	}
}
```

Question:

Will `work()` always stop?

Answer:

**No.**

---

# 7.2 Why Doesn't It Stop?

Suppose we have two CPU cores.

```text
Core-1

running = true

↓

Loop continues

-------------------------

Core-2

running = false
```

Core-1 may continue reading the cached value:

```text
running = true
```

It never observes the updated value.

This is a **visibility problem**.

---

# 7.3 Fixing It with `volatile`

```java
public class Worker {

	private volatile boolean running = true;

	public void work() {

		while (running) {
			processTask();
		}

	}

	public void stop() {
		running = false;
	}
}
```

Now, when `stop()` updates `running`, the worker thread is guaranteed to observe the change according to the Java Memory Model.

---

# 7.4 What Does `volatile` Actually Guarantee?

`volatile` provides two guarantees:

## 1. Visibility

When one thread updates a `volatile` variable, every other thread reading that variable will observe the latest value.

---

## 2. Ordering

Operations before writing a `volatile` variable cannot be reordered after the write, and operations after reading a `volatile` variable cannot be reordered before the read.

This establishes a **happens-before** relationship.

---

# 7.5 What `volatile` Does NOT Guarantee

Consider:

```java
private volatile int counter = 0;
```

Multiple threads execute:

```java
counter++;
```

Is this safe?

**No.**

---

# 7.6 Why `counter++` is Unsafe

The statement:

```java
counter++;
```

actually performs:

```text
Read counter

↓

Increment

↓

Write counter
```

Example:

Current value

```text
10
```

Thread-A

```text
Read = 10
```

Thread-B

```text
Read = 10
```

Thread-A

```text
Write = 11
```

Thread-B

```text
Write = 11
```

Expected:

```text
12
```

Actual:

```text
11
```

One update is lost.

This is a **race condition**.

---

# 7.7 `volatile` vs `AtomicInteger`

Wrong:

```java
private volatile int counter;

counter++;
```

Correct:

```java
private final AtomicInteger counter = new AtomicInteger();

counter.incrementAndGet();
```

`AtomicInteger` uses **Compare-And-Swap (CAS)** internally to perform atomic updates without traditional locking.

---

# 7.8 How `volatile` Works Internally

Imagine two CPU cores.

Without `volatile`:

```text
Core-1 Cache

flag = true

--------------

Core-2 Cache

flag = false
```

Different cores may temporarily observe different values.

With `volatile`, the JVM inserts memory barriers so that reads and writes obey the visibility and ordering rules defined by the Java Memory Model.

---

# 7.9 Happens-Before Rule

```java
private volatile boolean ready;
```

Thread-1

```java
data = load();

ready = true;
```

Thread-2

```java
if (ready) {
	use(data);
}
```

Because `ready` is `volatile`:

```
data = load()

↓

ready = true

↓

Thread-2 reads ready

↓

Thread-2 sees updated data
```

This is guaranteed by the JMM.

---

# 7.10 Real Production Example

Spring Boot Scheduler

```java
@Component
public class JobScheduler {

	private volatile boolean enabled = true;

	@Scheduled(fixedDelay = 5000)
	public void run() {

		if (!enabled)
			return;

		processJobs();

	}

	public void disable() {
		enabled = false;
	}
}
```

Without `volatile`, the scheduler thread might continue processing jobs after another thread has disabled it.

---

# 7.11 Singleton Bean Example

```java
@Service
public class FeatureFlagService {

	private volatile boolean featureEnabled;

	public boolean isEnabled() {
		return featureEnabled;
	}

	public void enable() {
		featureEnabled = true;
	}
}
```

Every request thread immediately observes changes to the feature flag without needing synchronized access.

---

# 7.12 Double-Checked Locking

One of the most famous interview topics.

Incorrect implementation:

```java
if(instance == null){
	synchronized(this){
		if(instance == null){
			instance = new Singleton();
		}
	}
}
```

Correct implementation:

```java
private static volatile Singleton instance;
```

Why?

Without `volatile`, instruction reordering could allow another thread to see a reference to a partially constructed object.

---

# 7.13 When Should You Use `volatile`?

Good use cases:

* Stop flags
* Shutdown signals
* Feature toggles
* Configuration refresh flags
* Initialization status
* Read-mostly shared variables

---

# 7.14 When Should You NOT Use `volatile`?

Avoid `volatile` for:

* Counters
* Banking transactions
* Money transfers
* Inventory updates
* Shared collections
* Compound operations

These require atomicity in addition to visibility.

---

# 7.15 `volatile` vs `synchronized`

| Feature                  | `volatile`                      | `synchronized`                        |
| ------------------------ | ------------------------------- | ------------------------------------- |
| Visibility               | ✅                               | ✅                                     |
| Atomicity                | ❌                               | ✅                                     |
| Mutual Exclusion         | ❌                               | ✅                                     |
| Prevents Race Conditions | ❌                               | ✅                                     |
| Thread Blocking          | ❌                               | ✅ (waiting threads block)             |
| Performance              | Higher for simple state sharing | Lower under contention due to locking |

---

# 7.16 Interview Questions

### Q1. What does `volatile` guarantee?

Visibility and ordering according to the Java Memory Model.

---

### Q2. Does `volatile` make code thread-safe?

Not always.

It only solves visibility problems.

---

### Q3. Can `volatile` replace `synchronized`?

No.

If multiple operations must execute atomically, synchronization or atomic classes are required.

---

### Q4. Why is `counter++` unsafe?

Because it is a compound operation consisting of read, modify, and write steps.

---

### Q5. When should you use `volatile`?

For simple shared state where threads only need to observe the latest value, such as stop flags or configuration flags.

---

# Production Scenario

**Interviewer:**

> "A background thread refuses to stop even after another thread updates a stop flag. How would you fix it?"

A strong answer:

1. Check whether the stop flag is declared `volatile`.
2. Verify there is a happens-before relationship between the write and the read.
3. If more than a simple flag is shared, consider `AtomicBoolean` or synchronization.
4. Avoid busy-wait loops if blocking mechanisms are more appropriate.

---

# Best Practices

✅ Use `volatile` for visibility-only use cases.

✅ Use `AtomicBoolean` when atomic updates are also needed.

✅ Never use `volatile` as a replacement for locking in complex business logic.

✅ Understand the distinction between **visibility**, **ordering**, and **atomicity**.

---

# Common Interview Mistakes

❌ "volatile makes variables thread-safe."

**Correct:** It only guarantees visibility and ordering.

❌ "volatile prevents all race conditions."

**Correct:** It does not make compound operations atomic.

❌ "volatile is always faster than synchronized."

**Correct:** It often has lower overhead, but it solves a different problem. The right choice depends on the required semantics.

---

# Chapter Summary

* `volatile` ensures that updates to a variable become visible to all threads.
* It also prevents certain harmful instruction reorderings.
* `volatile` does **not** provide mutual exclusion or atomicity.
* It is ideal for flags, configuration values, and state indicators.
* Compound operations still require synchronization or atomic classes.

---

# Next Chapter

## Chapter 8 - `ReentrantLock` (Advanced Locking)

In the next chapter, we'll explore one of the most frequently used locking mechanisms in enterprise Java applications.

Topics include:

* Why `ReentrantLock` exists when `synchronized` already works
* Fair vs Non-Fair Locks
* `tryLock()`
* `lockInterruptibly()`
* `Condition` objects
* Deadlock avoidance techniques
* Performance comparison with `synchronized`
* Real-world Spring Boot examples
* Senior-level interview questions

This chapter will transition from JVM-managed intrinsic locks to the more flexible locking mechanisms available in `java.util.concurrent.locks`.
