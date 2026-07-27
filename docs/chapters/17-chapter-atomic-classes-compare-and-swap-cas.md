# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part IV - Atomic Operations

# Chapter 17 - Atomic Classes & Compare-And-Swap (CAS)

> **"Locks provide correctness by making threads wait. Atomic classes achieve correctness by allowing threads to compete using hardware-supported atomic instructions. Instead of blocking, failed operations simply retry."**

Atomic classes are the foundation of many high-performance concurrent data structures in Java, including **ConcurrentHashMap**, **ConcurrentLinkedQueue**, **ForkJoinPool**, and parts of the JVM itself.

---

# Learning Objectives

After completing this chapter, you will understand:

* Why Atomic Classes exist
* Compare-And-Swap (CAS)
* Hardware Atomic Instructions
* Lock-Free Programming
* AtomicInteger
* AtomicLong
* AtomicBoolean
* AtomicReference
* Atomic Arrays
* CAS Retry Loops
* ABA Problem
* Production Use Cases

---

# 17.1 Why Do We Need Atomic Classes?

Suppose multiple threads increment a counter.

```java
count++;
```

Looks simple.

Internally it performs three operations.

```text
Read

↓

Increment

↓

Write
```

These three operations are **not atomic**.

---

# 17.2 Race Condition

Initial value

```text
count = 5
```

Thread A

```text
Read = 5
```

Thread B

```text
Read = 5
```

Thread A

```text
Write = 6
```

Thread B

```text
Write = 6
```

Expected

```text
7
```

Actual

```text
6
```

One update is lost.

---

# 17.3 Traditional Solution

Use synchronization.

```java
synchronized void increment() {
    count++;
}
```

Problem:

```text
Acquire Lock

↓

Increment

↓

Release Lock
```

Locks introduce:

* Context switching
* Waiting
* Contention
* Reduced throughput

Can we avoid locks?

Yes.

---

# 17.4 What is CAS?

CAS means

**Compare-And-Swap**

It is a single atomic CPU instruction.

Conceptually:

```text
Current Value = 10

↓

Expected Value = 10 ?

↓

YES

↓

Replace with 11

↓

Success
```

If another thread already changed the value:

```text
Current = 12

↓

Expected = 10

↓

NO

↓

Retry
```

No lock.

No waiting.

---

# 17.5 CAS Loop

Atomic operations internally use a retry loop.

```text
Read Value

↓

Try CAS

↓

Success?

↓

YES → Done

↓

NO

↓

Read Again

↓

Retry
```

Only one thread succeeds each time.

---

# 17.6 AtomicInteger

Instead of

```java
int count = 0;
```

use

```java
AtomicInteger count =
	new AtomicInteger();
```

Increment

```java
count.incrementAndGet();
```

No explicit synchronization required.

---

# 17.7 Example

```java
AtomicInteger visitors =
	new AtomicInteger();

visitors.incrementAndGet();

System.out.println(
	visitors.get());
```

Output

```text
1
```

---

# 17.8 Common AtomicInteger Methods

```java
incrementAndGet();
```

Increment then return.

---

```java
getAndIncrement();
```

Return current value,

then increment.

---

```java
decrementAndGet();
```

Decrease value.

---

```java
addAndGet(10);
```

Add a value atomically.

---

```java
compareAndSet(old,new);
```

CAS operation.

---

# 17.9 compareAndSet()

Example

```java
AtomicInteger balance =
	new AtomicInteger(100);

balance.compareAndSet(
	100,
	200);
```

Execution

```text
Current = 100

↓

Expected = 100

↓

Update = 200
```

Returns

```text
true
```

If another thread changed the balance first:

Returns

```text
false
```

---

# 17.10 AtomicLong

Same concept.

```java
AtomicLong requestCount =
	new AtomicLong();
```

Suitable for

* API Counters
* Metrics
* Request Tracking

---

# 17.11 AtomicBoolean

Example

```java
AtomicBoolean started =
	new AtomicBoolean(false);
```

Useful for

```text
Application Started?

↓

YES

↓

Skip
```

Only one thread can successfully change the value from `false` to `true` using `compareAndSet`.

---

# 17.12 AtomicReference

Sometimes

objects

must be updated atomically.

```java
AtomicReference<User> user =
	new AtomicReference<>();
```

Example

```java
user.compareAndSet(
	oldUser,
	newUser);
```

Useful for immutable object replacement.

---

# 17.13 Production Example

Configuration Refresh

```java
AtomicReference<Config> config =
	new AtomicReference<>();
```

Refresh

```java
config.set(newConfig);
```

Readers

```java
Config current =
	config.get();
```

No locking required for replacing the configuration reference.

---

# 17.14 Atomic Arrays

Java also provides

```text
AtomicIntegerArray

AtomicLongArray

AtomicReferenceArray
```

Each element can be updated atomically.

Useful for:

* Counters
* Metrics
* Shared state arrays

---

# 17.15 LongAdder

One of the most important interview topics.

Suppose

100 threads

increment

```text
Counter
```

Using

```text
AtomicInteger
```

All threads compete for one variable.

Contention increases.

LongAdder works differently.

```text
Cell1

Cell2

Cell3

Cell4
```

Each thread updates a different internal cell.

Final value

```text
Cell1

+

Cell2

+

Cell3

+

Cell4
```

Result:

Much higher throughput under heavy contention.

---

# 17.16 AtomicInteger vs LongAdder

| Feature         | AtomicInteger | LongAdder          |
| --------------- | ------------- | ------------------ |
| Single Variable | ✅             | ❌ (Multiple Cells) |
| Low Contention  | Excellent     | Excellent          |
| High Contention | Good          | Excellent          |
| Memory Usage    | Lower         | Higher             |

Use `LongAdder` for frequently updated shared counters.

---

# 17.17 ABA Problem

Classic CAS problem.

Suppose

Initial

```text
A
```

Thread A

reads

```text
A
```

Thread B changes

```text
A

↓

B

↓

A
```

Thread A performs CAS.

CAS succeeds,

even though the value changed twice.

This is called the **ABA Problem**.

---

# 17.18 Solution to ABA

Java provides

```text
AtomicStampedReference
```

Each value includes

```text
Value

+

Version Number
```

Example

```text
A,1

↓

B,2

↓

A,3
```

CAS detects the version change even though the value returned to `A`.

---

# 17.19 Real Spring Boot Example

API Request Counter

```java
@Service
public class MetricsService {

    private final AtomicLong requests =
	    new AtomicLong();

    public void increment() {

	requests.incrementAndGet();

    }

    public long totalRequests() {

	return requests.get();

    }

}
```

For very high request rates, consider `LongAdder` instead of `AtomicLong`.

---

# 17.20 Common Interview Questions

### Q1. Why use AtomicInteger instead of synchronized?

Atomic classes avoid blocking and generally perform better under low to moderate contention by using CAS instead of locks.

---

### Q2. What is CAS?

Compare-And-Swap.

An atomic operation that updates a value only if it still matches the expected value.

---

### Q3. Does CAS always succeed?

No.

If another thread updates the value first,

CAS fails,

and the operation retries or handles the failure.

---

### Q4. What is the ABA Problem?

A value changes from A → B → A.

A simple CAS cannot detect the intermediate modification.

---

### Q5. When should you use LongAdder?

For high-contention counters where many threads frequently update the same value.

---

# Production Scenario

**Interviewer:**

> "Your API gateway maintains a request counter that is incremented millions of times per minute. Which implementation would you choose?"

A strong answer:

* `AtomicLong` is suitable for moderate contention.
* Under very high contention, prefer `LongAdder` because it distributes updates across multiple internal cells, reducing contention.
* If exact intermediate values are needed during updates, evaluate whether `AtomicLong` better matches the consistency requirements.

---

# Best Practices

✅ Use atomic classes for simple shared state.

✅ Use `LongAdder` for high-frequency counters.

✅ Use `AtomicReference` with immutable objects.

✅ Understand that CAS may retry under contention.

---

# Common Mistakes

❌ Replacing every lock with CAS.

❌ Assuming CAS always succeeds on the first attempt.

❌ Ignoring the ABA problem in advanced lock-free algorithms.

❌ Using `AtomicInteger` for highly contended metrics when `LongAdder` would scale better.

---

# Chapter Summary

* Atomic classes provide lock-free thread safety using CAS.
* CAS compares the current value with an expected value before updating.
* `AtomicInteger`, `AtomicLong`, `AtomicBoolean`, and `AtomicReference` support common atomic operations.
* `LongAdder` improves scalability for highly contended counters.
* The ABA problem can be addressed with versioned references such as `AtomicStampedReference`.

---

# Progress Update

### Part IV - Atomic Operations

* ✅ Chapter 17 - Atomic Classes & Compare-And-Swap (CAS)

---

# Next Chapter

## Chapter 18 - Thread Pools & Executor Framework

The next chapter begins the **Executor Framework** section and covers one of the most important topics for enterprise Java development:

* Why creating threads manually is a bad practice
* Executor Framework architecture
* Executor vs ExecutorService
* ThreadPoolExecutor internals
* Fixed, Cached, Single, Scheduled thread pools
* Task queues and worker threads
* Thread pool sizing (CPU-bound vs I/O-bound)
* RejectedExecutionHandler
* Graceful shutdown
* Spring Boot `@Async` integration
* Production tuning and interview scenarios

This chapter is essential for understanding how modern Java applications efficiently manage thousands of concurrent tasks without creating thousands of threads.
