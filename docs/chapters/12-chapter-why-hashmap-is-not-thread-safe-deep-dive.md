# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part III - Concurrent Collections

# Chapter 12 - Why HashMap is NOT Thread Safe (Deep Dive)

> **"This is one of the most frequently asked senior Java interview questions. Many developers know that `HashMap` is not thread-safe, but very few can explain *why*."**

---

# Learning Objectives

After this chapter, you will understand:

* Why HashMap is not thread-safe
* Race Conditions
* Lost Updates
* Concurrent Resize
* Java 7 Infinite Loop Bug
* Memory Corruption
* Why ConcurrentHashMap was introduced
* synchronizedMap vs ConcurrentHashMap
* Production Examples
* Interview Questions

---

# 12.1 The Interview Question

One of the most common interview questions is:

> **What happens if multiple threads access a HashMap concurrently?**

A poor answer:

> "HashMap is not thread-safe."

A senior engineer's answer:

> "Concurrent modifications can cause race conditions, lost updates, inconsistent reads, structural corruption during resize, and in Java 7 even infinite loops. The appropriate solution depends on the workload, often using `ConcurrentHashMap` or other synchronization strategies."

---

# 12.2 Let's Build a Scenario

Suppose two users transfer money simultaneously.

Both update an in-memory cache.

```java
Map<String,Integer> balances =
	new HashMap<>();
```

Thread A

```java
balances.put("A",1000);
```

Thread B

```java
balances.put("B",2000);
```

Looks harmless.

But internally multiple shared data structures are modified.

---

# 12.3 Why is HashMap Unsafe?

HashMap contains shared mutable state.

```text
Bucket Array

↓

Node

↓

next Pointer

↓

size

↓

threshold
```

All of these fields can be modified during `put()`, `remove()`, and resize operations.

There is **no internal synchronization** protecting these updates.

---

# 12.4 Race Condition Example

Initial value

```text
count = 10
```

Thread A

```text
Read = 10
```

Thread B

```text
Read = 10
```

Thread A

```text
Write = 11
```

Thread B

```text
Write = 11
```

Expected

```text
12
```

Actual

```text
11
```

One update is lost.

The same principle applies inside a `HashMap` when multiple threads modify it concurrently.

---

# 12.5 Concurrent put()

Suppose

Both threads calculate

```text
Bucket = 7
```

Execution

```text
Thread A

↓

Create Node

↓

Store

--------------------

Thread B

↓

Create Node

↓

Store
```

Depending on timing:

* One node may overwrite another.
* Links between nodes may be broken.
* Internal state may become inconsistent.

---

# 12.6 Structural Modification

HashMap is not just updating values.

It also updates:

```text
Bucket Array

↓

next Pointer

↓

Size

↓

Threshold
```

Multiple threads changing these simultaneously without coordination can corrupt the internal structure.

---

# 12.7 Concurrent Resize

One of the biggest problems.

Current Capacity

```text
16
```

Threshold

```text
12
```

Two threads insert the 13th element.

Execution

```text
Thread A

↓

Resize

----------------

Thread B

↓

Resize
```

Both attempt to redistribute the same nodes.

Without synchronization, the final structure may become inconsistent.

---

# 12.8 Java 7 Infinite Loop Bug

One of the most famous concurrency bugs in Java.

During resize,

Thread A

and

Thread B

could reorder linked-list nodes differently.

Example:

Original

```text
A

↓

B

↓

C
```

Corrupted

```text
A

↓

B

↓

A
```

A cycle is created.

Searching:

```java
map.get(key);
```

could loop forever, consuming 100% CPU.

> **Important:** This bug existed in the Java 7 implementation. Java 8 redesigned the resize algorithm and no longer suffers from this specific infinite-loop issue, but concurrent modification of `HashMap` is still unsupported and unsafe.

---

# 12.9 Lost Updates

Suppose

```java
map.put("A",100);
```

and

```java
map.put("A",200);
```

run simultaneously.

Final value:

Could be

```text
100
```

or

```text
200
```

depending on timing.

Neither thread has any guarantee about which update "wins."

---

# 12.10 Inconsistent Reads

Thread A

```java
map.put("A",100);
```

Thread B

```java
map.get("A");
```

Without synchronization,

Thread B may observe:

* Old value
* New value
* Intermediate internal state (behavior is undefined under concurrent modification)

This violates thread safety.

---

# 12.11 Memory Visibility

Even if Thread A successfully inserts:

```java
map.put("A",100);
```

another thread is **not guaranteed** to see the update immediately because there is no happens-before relationship.

Visibility is not guaranteed.

---

# 12.12 Collections.synchronizedMap()

Java provides

```java
Map<String,Integer> map =
Collections.synchronizedMap(
    new HashMap<>());
```

Internally,

every method is synchronized.

```text
put()

↓

Lock

↓

Execute

↓

Unlock
```

Simple,

but only one thread can access the map at a time.

---

# 12.13 ConcurrentHashMap

Designed specifically for concurrent access.

```java
ConcurrentHashMap<String,Integer> map =
	new ConcurrentHashMap<>();
```

Advantages:

* Thread-safe
* High throughput
* Better scalability
* No global lock for most operations
* Supports concurrent reads and many concurrent updates

We'll study its internals in the next chapter.

---

# 12.14 synchronizedMap vs ConcurrentHashMap

| Feature           | synchronizedMap | ConcurrentHashMap |
| ----------------- | --------------- | ----------------- |
| Thread Safe       | ✅               | ✅                 |
| Entire Map Locked | ✅               | ❌                 |
| Concurrent Reads  | ❌               | ✅                 |
| High Throughput   | ❌               | ✅                 |
| Scales Well       | ❌               | ✅                 |

---

# 12.15 Production Example

Suppose

Spring Boot

```java
@Service
public class SessionCache {

    private final Map<String,Session> sessions =
	    new HashMap<>();

}
```

Thousands of requests:

```java
sessions.put(id,session);
```

Race conditions become likely.

Correct implementation:

```java
private final ConcurrentHashMap<String,Session>
	sessions = new ConcurrentHashMap<>();
```

---

# 12.16 Common Interview Questions

### Q1. Why is HashMap not thread-safe?

Because it performs no synchronization while modifying shared internal data structures.

---

### Q2. What problems occur?

* Race conditions
* Lost updates
* Visibility issues
* Structural corruption
* Unsafe resize
* (Java 7) Infinite loop during resize

---

### Q3. Is `get()` thread-safe?

A `get()` that runs concurrently with writes is **not** thread-safe. If the map is safely published and never modified afterward, concurrent reads are generally safe.

---

### Q4. Does Java 8 fix HashMap thread safety?

No.

Java 8 fixed the specific resize infinite-loop bug from Java 7, but `HashMap` remains **not thread-safe**.

---

### Q5. Can synchronizedMap replace ConcurrentHashMap?

It can provide thread safety, but it serializes access with a single lock. `ConcurrentHashMap` generally offers much better scalability under concurrent workloads.

---

# Production Scenario

**Interviewer:**

> "A Spring Boot service stores user sessions in a shared `HashMap`. During load testing, sessions disappear and CPU usage spikes. What could be happening?"

A strong answer:

* Shared `HashMap` is being modified concurrently.
* Race conditions may overwrite entries or corrupt internal state.
* On older JVMs (Java 7), concurrent resize could even create infinite loops.
* Replace it with `ConcurrentHashMap` or redesign the shared state.
* Analyze thread dumps and heap dumps if corruption is suspected.

---

# Best Practices

✅ Never modify a shared `HashMap` from multiple threads.

✅ Use `ConcurrentHashMap` for concurrent access.

✅ Use immutable maps for read-only configuration.

✅ Synchronize external access if `HashMap` must be shared.

---

# Common Mistakes

❌ Assuming `put()` is atomic.

❌ Using `HashMap` as a shared cache in a web application.

❌ Ignoring resize behavior.

❌ Believing Java 8 made `HashMap` thread-safe.

---

# Chapter Summary

* `HashMap` is **not thread-safe**.
* Concurrent writes can lead to race conditions, lost updates, visibility issues, and structural corruption.
* Java 7 had a well-known infinite-loop bug during concurrent resize.
* Java 8 fixed that specific bug but did **not** make `HashMap` safe for concurrent modification.
* For concurrent workloads, `ConcurrentHashMap` is the preferred choice.

---

# Interview Tip

If asked:

> **"Why is HashMap not thread-safe?"**

Don't stop at:

> "Because multiple threads can modify it."

Instead explain:

1. Shared mutable bucket array.
2. Unsynchronized structural updates.
3. Resize and rehash issues.
4. Memory visibility.
5. Java 7 infinite-loop bug.
6. Why `ConcurrentHashMap` solves these problems.

This level of explanation distinguishes a Senior Engineer or Staff Engineer candidate from someone who has only memorized interview answers.

---

# Next Chapter

## Chapter 13 - ConcurrentHashMap (Complete Internal Architecture)

This will be one of the flagship chapters of the handbook, covering:

* Evolution from Java 7 to Java 8
* Segment-based locking (Java 7)
* CAS (Compare-And-Swap)
* Bucket-level synchronization (Java 8)
* Lock-free reads
* `computeIfAbsent()`
* `putIfAbsent()`
* `merge()`
* Weakly consistent iterators
* Internal source code walkthrough
* Performance comparisons
* Real production use cases (caches, session stores, rate limiters)
* Senior interview questions and debugging scenarios

This chapter directly answers the follow-up interview question:

> **"How does ConcurrentHashMap achieve thread safety without locking the entire map?"**
