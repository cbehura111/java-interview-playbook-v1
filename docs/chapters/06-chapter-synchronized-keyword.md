# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part II - Synchronization

---

# Chapter 6 - `synchronized` Keyword

> **"The `synchronized` keyword is the foundation of Java's concurrency model. Before `ReentrantLock`, `StampedLock`, or `AtomicInteger`, there was `synchronized`-and it remains one of the most important interview topics."**

---

# Learning Objectives

By the end of this chapter, you will understand:

* What is synchronization?
* Why synchronization is required
* How `synchronized` works internally
* Object Monitor
* Monitor Lock
* Intrinsic Lock
* Reentrant Locking
* Object-level Lock
* Class-level Lock
* Block Synchronization
* Performance Considerations
* Common Interview Questions
* Production Best Practices

---

# 6.1 Why Do We Need Synchronization?

Consider an ATM system.

Two customers attempt to withdraw money simultaneously.

Current Balance

```text
₹10,000
```

Thread-1

```text
Withdraw ₹6,000
```

Thread-2

```text
Withdraw ₹5,000
```

Without synchronization:

Both threads read:

```text
Balance = ₹10,000
```

Thread-1 updates:

```text
Balance = ₹4,000
```

Thread-2 updates:

```text
Balance = ₹5,000
```

Final balance becomes:

```text
₹5,000
```

Instead of:

```text
-₹1,000 (or one withdrawal should fail)
```

This is called a **Race Condition**.

---

# 6.2 What is Synchronization?

Synchronization ensures:

> **Only one thread can execute a critical section of code at a time.**

Think of it as a single restroom with one key.

```text
Person A

↓

Gets Key

↓

Uses Room

↓

Returns Key

↓

Person B
```

Only one person enters at a time.

---

# 6.3 Critical Section

A **Critical Section** is code that accesses shared mutable data.

Example

```java
balance = balance - amount;
```

Since `balance` is shared,

multiple threads can modify it simultaneously.

This section must be synchronized.

---

# 6.4 Example Without Synchronization

```java
public class BankAccount {

	private int balance = 10000;

	public void withdraw(int amount) {

		balance = balance - amount;

	}

}
```

Suppose

Thread A

```text
balance = 10000
```

Thread B

```text
balance = 10000
```

Both update

Final result becomes incorrect.

---

# 6.5 Using `synchronized`

```java
public class BankAccount {

	private int balance = 10000;

	public synchronized void withdraw(int amount) {

		balance -= amount;

	}

}
```

Now,

only one thread executes `withdraw()` at a time.

The second thread waits until the first thread exits the method.

---

# 6.6 How `synchronized` Works Internally

Every Java object has an associated **Monitor** (also called an intrinsic lock).

```text
Account Object

+--------------------+

balance = 10000

Monitor Lock

+--------------------+
```

When a thread enters a synchronized method:

```text
Acquire Monitor

↓

Execute Code

↓

Release Monitor
```

If another thread already owns the monitor:

```text
BLOCKED
```

until the monitor becomes available.

---

# 6.7 Object-Level Lock

```java
public synchronized void transfer() {

}
```

Equivalent to:

```java
public void transfer() {

	synchronized(this){

	}

}
```

The lock belongs to the current object (`this`).

Different object instances have different monitors and can be accessed concurrently.

---

# 6.8 Block Synchronization

Instead of locking the whole method:

```java
public void transfer(){

	validate();

	synchronized(this){

		balance -= 500;

	}

	log();

}
```

Only the critical section is locked.

Benefits:

* Better performance
* Smaller lock scope
* Reduced contention

**Best Practice:** Synchronize the smallest possible section that needs protection.

---

# 6.9 Class-Level Lock

Static methods belong to the class rather than an object.

```java
public static synchronized void updateRate(){

}
```

Equivalent to:

```java
synchronized(Bank.class){

}
```

Only one thread across the entire JVM can execute this synchronized static method for that class at a time.

---

# 6.10 Object Lock vs Class Lock

```java
public synchronized void withdraw(){}

public static synchronized void updateRate(){}
```

These use **different locks**.

| Method                | Lock Used                         |
| --------------------- | --------------------------------- |
| Instance synchronized | Object Monitor (`this`)           |
| Static synchronized   | Class Monitor (`ClassName.class`) |

They do not block each other because they synchronize on different monitor objects.

---

# 6.11 Reentrant Synchronization

One of the best interview questions.

Example

```java
public synchronized void transfer(){

	validate();

}

public synchronized void validate(){

}
```

Question:

Will this deadlock?

Answer:

**No.**

Java monitors are **reentrant**.

The thread already holding the monitor can acquire it again without blocking.

---

# 6.12 Lock Ownership

Example

Thread A enters

```java
withdraw()
```

Thread B also enters

```java
withdraw()
```

Execution

```text
Thread A

↓

Acquire Lock

↓

Execute

↓

Release Lock

↓

Thread B

↓

Acquire Lock

↓

Execute
```

Only one thread owns the monitor at a time.

---

# 6.13 Monitor Lifecycle

```text
Thread

↓

Request Monitor

↓

Available?

↓

YES → Execute

↓

NO → BLOCKED

↓

Monitor Released

↓

Acquire Lock

↓

Execute

↓

Release Lock
```

This lifecycle is managed by the JVM.

---

# 6.14 Production Example

Spring Boot

```java
@Service
public class SequenceService {

	private int sequence;

	public synchronized int next(){

		return ++sequence;

	}

}
```

Without synchronization:

Two requests could receive the same sequence number.

With synchronization:

Each request gets a unique value.

> **Note:** For simple counters, `AtomicInteger` is usually a better choice because it avoids blocking and scales better under contention.

---

# 6.15 Common Mistakes

### Locking Entire Methods

```java
public synchronized void process(){

	validate();

	callAPI();

	save();

}
```

Suppose

`callAPI()`

takes:

```text
5 seconds
```

Every other thread waits unnecessarily.

Instead:

```java
validate();

callAPI();

synchronized(this){

	save();

}
```

Only the database update is synchronized.

---

# 6.16 Performance Impact

Synchronization introduces costs:

* Lock acquisition
* Lock release
* Thread blocking
* Context switching
* Reduced parallelism under heavy contention

Modern JVMs optimize uncontended locks very effectively, but poor lock design can still become a bottleneck.

---

# 6.17 When Should We Use `synchronized`?

Good candidates:

* Updating shared objects
* Singleton state
* In-memory caches
* Shared counters (if contention is low)
* Critical business logic

Avoid using it for:

* Long-running network calls
* Database queries
* File uploads/downloads
* External API calls

Holding a lock while waiting on I/O reduces throughput.

---

# 6.18 Interview Questions

### Q1. What does `synchronized` do?

It ensures that only one thread at a time executes a synchronized block or method for the same monitor.

---

### Q2. Is `synchronized` reentrant?

Yes.

A thread that already owns the monitor can enter another synchronized block guarded by the same monitor.

---

### Q3. What is a Monitor?

A monitor is the JVM-managed synchronization mechanism associated with every Java object. It controls mutual exclusion for synchronized code.

---

### Q4. Difference between synchronized method and block?

Method synchronization locks the entire method.

Block synchronization locks only a selected portion of code.

---

### Q5. Can two synchronized methods execute simultaneously?

* **On different objects:** Yes.
* **On the same object:** No, if they synchronize on the same monitor.

---

# Production Scenario

**Interviewer:**

> "Our inventory service occasionally oversells products when many customers order at the same time. How would you fix it?"

A good answer:

* Identify the shared mutable state.
* Synchronize the critical update or use database locking/optimistic locking depending on the architecture.
* Keep the synchronized section as small as possible.
* For distributed systems, remember that `synchronized` only works within a single JVM. Across multiple application instances, use database locks, distributed locks (e.g., Redis), or other coordination mechanisms.

---

# Best Practices

✅ Synchronize only the critical section.

✅ Keep synchronized blocks short.

✅ Prefer immutable objects where possible.

✅ Don't synchronize long-running I/O operations.

✅ For high-contention counters, prefer `AtomicInteger` or `LongAdder`.

✅ Understand that `synchronized` protects only threads within the same JVM process.

---

# Chapter Summary

* `synchronized` provides mutual exclusion and memory visibility.
* Every Java object has an intrinsic monitor.
* Synchronization can be applied to methods or blocks.
* Java monitors are reentrant.
* Smaller synchronized blocks improve scalability.
* `synchronized` is simple and reliable but should be used thoughtfully to avoid unnecessary contention.

---

# Next Chapter

## Chapter 7 - `volatile` Keyword (Complete Deep Dive)

In the next chapter, we'll answer questions like:

* What exactly does `volatile` do?
* Why is `volatile` different from `synchronized`?
* When should you use `volatile` instead of a lock?
* Why doesn't `volatile` make `count++` thread-safe?
* How is `volatile` used in real-world frameworks like Spring and Kafka?

We'll also compare `volatile` and `synchronized` side by side, a topic that appears frequently in senior Java interviews.
