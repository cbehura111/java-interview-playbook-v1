# Part IV - Atomic Operations

# Chapter 19: AtomicReference, AtomicStampedReference & the ABA Problem

> **Interview Difficulty:** ⭐⭐⭐⭐⭐ (Senior/Lead Java Developer)
>
> **Frequently Asked By:** Amazon, Microsoft, Oracle, Goldman Sachs, Visa, Walmart, Uber, Atlassian

---

# 1. Why Do Interviewers Ask This?

This topic separates **mid-level** developers from **senior** engineers.

The interviewer wants to know whether you understand:

* Lock-free programming
* CAS limitations
* ABA Problem
* JVM atomic primitives
* Immutable object updates
* Concurrent algorithm design

Typical question:

> We know CAS prevents race conditions. Then why do we need AtomicStampedReference?

---

# 2. 30-Second Interview Answer

> `AtomicReference` atomically updates object references using CAS. However, CAS only checks whether the reference is the same-it cannot detect if the value changed from A→B→A in between. This is called the ABA problem. `AtomicStampedReference` solves it by associating a version number (stamp) with the reference, so CAS verifies both the object reference and its version.

---

# 3. Interviewer's Expectation

After the initial answer, expect:

* What is AtomicReference?
* Why not synchronized?
* What is ABA?
* Is ABA always a problem?
* How does AtomicStampedReference work?
* Difference between AtomicStampedReference and AtomicMarkableReference?
* Where is ABA seen in production?

---

# 4. Why AtomicReference?

Atomic classes aren't limited to primitives.

Suppose:

```java
class UserSession {
    String token;
    long expiry;
}
```

Two threads update the session.

Without synchronization:

```java
session = new UserSession(...);
```

One update may overwrite another.

AtomicReference provides atomic replacement.

```java
AtomicReference<UserSession> session =
	new AtomicReference<>();
```

---

# 5. Basic Operations

## set()

```java
session.set(newSession);
```

Blind replacement.

---

## get()

```java
UserSession current = session.get();
```

Lock-free read.

---

## compareAndSet()

```java
session.compareAndSet(oldSession, newSession);
```

Updates only if the current reference is exactly `oldSession`.

---

# 6. Production Example

Configuration Refresh

Imagine:

```text
Current Config

↓

New Config arrives

↓

Replace entire object
```

Instead of modifying fields individually:

```java
config.timeout = 30;
config.retry = 5;
config.url = "...";
```

Create a new immutable object:

```java
Configuration newConfig =
	new Configuration(...);

configReference.set(newConfig);
```

Readers always see a consistent snapshot.

This pattern is common in:

* Configuration management
* Feature flags
* Routing tables
* Caches

---

# 7. CAS on Objects

Suppose

```text
Reference

↓

User Object A
```

Thread A:

```java
compareAndSet(A, B)
```

Works only if the reference still points to **A**.

CAS compares the reference, **not the object's internal fields**.

---

# 8. The ABA Problem

This is one of the most common senior interview questions.

Initial state:

```text
Reference

↓

A
```

Thread 1 reads:

```text
A
```

Before Thread 1 performs CAS...

Thread 2 executes:

```text
A

↓

B

↓

A
```

Now Thread 1 performs:

```java
compareAndSet(A, C)
```

CAS succeeds.

But something changed!

CAS couldn't detect:

```text
A

↓

B

↓

A
```

This hidden modification is called the **ABA Problem**.

---

# 9. Why is ABA Dangerous?

Imagine a lock-free stack.

Initial:

```text
Top

↓

Node A

↓

Node B
```

Thread 1 reads:

```text
Top = A
```

Meanwhile

Thread 2:

* Pops A
* Pops B
* Pushes A again

Stack becomes

```text
Top

↓

A
```

Thread 1 still thinks nothing changed.

CAS succeeds.

The stack is now corrupted.

---

# 10. Real Production Example

Memory allocators

Network packet queues

Lock-free stacks

Work-stealing schedulers

These algorithms reuse objects.

Reference may become:

```text
A

↓

B

↓

A
```

CAS cannot distinguish this.

---

# 11. AtomicStampedReference

Solution:

Store

```text
Reference

+

Version Number
```

Instead of

```text
A
```

Store

```text
(A,1)
```

Update:

```text
(B,2)
```

Again:

```text
(A,3)
```

Even though reference returned to A,

Version changed.

CAS fails correctly.

---

# 12. Internal View

Instead of

```text
Reference

↓

Object
```

Store

```text
Reference

↓

Object

Stamp = 5
```

CAS checks

Reference

AND

Stamp

Both must match.

---

# 13. Example

```java
AtomicStampedReference<String> ref =
	new AtomicStampedReference<>("A",1);
```

Current

```text
(A,1)
```

Update

```java
int stamp = ref.getStamp();

ref.compareAndSet(
    "A",
    "B",
    stamp,
    stamp+1
);
```

Result

```text
(B,2)
```

---

# 14. ABA Detection

Thread1 reads

```text
(A,1)
```

Thread2

```text
(A,1)

↓

(B,2)

↓

(A,3)
```

Thread1

tries

```text
CAS(A,1)
```

Fails.

Why?

Current value

```text
(A,3)
```

Stamp changed.

Exactly what we wanted.

---

# 15. AtomicMarkableReference

Instead of

Reference + Version

Stores

Reference + Boolean

```text
Reference

Deleted = true
```

Useful for:

* Logical deletion
* Lock-free linked lists
* Concurrent skip lists

Not useful when version history matters.

---

# 16. Comparison

| Feature              | AtomicReference | AtomicStampedReference | AtomicMarkableReference |
| -------------------- | --------------- | ---------------------- | ----------------------- |
| Atomic Object Update | ✅               | ✅                      | ✅                       |
| Version Tracking     | ❌               | ✅                      | ❌                       |
| Boolean Marker       | ❌               | ❌                      | ✅                       |
| Solves ABA           | ❌               | ✅                      | Partially               |
| Memory Overhead      | Low             | Higher                 | Medium                  |

---

# 17. Immutable Object Pattern

One of the best production practices.

Instead of

```java
config.setUrl(...);
config.setRetry(...);
config.setTimeout(...);
```

Do

```java
Configuration updated =
	new Configuration(...);

configRef.set(updated);
```

Benefits

* Thread-safe
* No partial updates
* Easy rollback
* Easy caching

---

# 18. Interview Traps

### Is AtomicReference thread-safe?

✅ Yes.

Updating the reference is atomic.

The object it points to may still be mutable and require its own synchronization.

---

### Does AtomicReference solve every concurrency issue?

❌ No.

Only the reference update is atomic.

---

### Does AtomicStampedReference eliminate ABA?

✅ It detects ABA by including a version stamp.

---

### Why not always use AtomicStampedReference?

Extra memory and version management introduce overhead. If ABA is impossible or irrelevant, `AtomicReference` is simpler and faster.

---

# 19. Senior-Level Follow-up Questions

1. What exactly does CAS compare for object references?
2. Why can't CAS detect ABA?
3. Where does ABA occur in production?
4. Why is AtomicStampedReference slower?
5. Why does AtomicReference work well with immutable objects?
6. How does ConcurrentLinkedQueue avoid corruption?
7. Why are lock-free algorithms difficult to implement?
8. Is AtomicReference linearizable?
9. What is AtomicMarkableReference used for?
10. Why doesn't every concurrent collection use AtomicStampedReference?

---

# 20. Production Debugging Scenario

### Problem

A high-throughput lock-free queue occasionally loses elements under stress testing.

### Investigation

* No locks
* Heavy CAS retries
* Objects recycled frequently

### Root Cause

ABA caused a CAS operation to succeed even though the node had been removed and reinserted.

### Fix

* Introduce versioned references (`AtomicStampedReference`) where appropriate, or redesign the algorithm to avoid node reuse without safe reclamation.
* Re-test with high-concurrency stress tests (for example, `jcstress` or similar concurrency testing approaches).

---

# 21. Cheat Sheet

### Remember

* ✅ `AtomicReference` performs atomic updates on object references.
* ✅ CAS checks the reference value, not the object's internal state.
* ✅ ABA means a value changes **A → B → A**, making a simple CAS believe nothing changed.
* ✅ `AtomicStampedReference` pairs the reference with a version number to detect ABA.
* ✅ `AtomicMarkableReference` pairs a reference with a boolean flag, useful for logical deletion.
* ✅ Prefer immutable objects with `AtomicReference` for configuration, caches, routing tables, and feature flags.

---

## 🎯 Interview Quick Revision

| Scenario                                  | Best Choice                |
| ----------------------------------------- | -------------------------- |
| Replace immutable configuration           | `AtomicReference`          |
| Detect ABA in lock-free algorithm         | `AtomicStampedReference`   |
| Logical deletion in concurrent structures | `AtomicMarkableReference`  |
| Primitive counter                         | `AtomicLong` / `LongAdder` |
| High-write metrics                        | `LongAdder`                |

---

### Next Chapter

**Chapter 20 - Lock-Free Programming Patterns**

We'll cover:

* Lock-Free vs Wait-Free vs Obstruction-Free
* Progress guarantees
* CAS retry algorithms
* Memory barriers
* False sharing
* Cache-line padding
* `@Contended`
* Ring Buffers
* LMAX Disruptor
* How Kafka and high-performance systems leverage lock-free techniques
* Senior interview scenarios and production debugging
