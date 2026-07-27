# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part III - Concurrent Collections

# Chapter 13 - ConcurrentHashMap (Complete Internal Architecture)

> **"ConcurrentHashMap is one of the greatest engineering achievements in the Java Collections Framework. It provides high-performance concurrent access without locking the entire map."**

This chapter is one of the most important for **Senior Java**, **Lead**, **Staff Engineer**, and **Architect** interviews.

---

# Learning Objectives

After completing this chapter, you will understand:

* Why ConcurrentHashMap was introduced
* Java 7 Architecture
* Java 8 Architecture
* Segment Locking
* Bucket Locking
* CAS (Compare-And-Swap)
* Lock-Free Reads
* Tree Bins
* Concurrent Resize
* computeIfAbsent()
* putIfAbsent()
* merge()
* Weakly Consistent Iterators
* Production Best Practices

---

# 13.1 Why ConcurrentHashMap?

Suppose your application stores:

* Active Sessions
* JWT Tokens
* Product Cache
* Exchange Rates
* Configuration

Thousands of users access them simultaneously.

Using

```java
HashMap<String, User> users = new HashMap<>();
```

creates race conditions.

Using

```java
Collections.synchronizedMap(...)
```

solves thread safety,

but introduces another problem.

```text
Thread A

↓

LOCK

↓

Thread B waits

↓

Thread C waits

↓

Thread D waits
```

Only one thread can access the map.

Throughput drops significantly under heavy load.

---

# 13.2 Solution

Java introduced

```java
ConcurrentHashMap
```

to allow:

* Multiple Readers
* Multiple Writers (to different buckets)
* High Throughput
* Thread Safety

without a single global lock.

---

# 13.3 Java 7 Architecture

Before Java 8,

ConcurrentHashMap used

**Segments**.

```text
ConcurrentHashMap

	  |

-------------------------

|     |      |      |

Seg0 Seg1  Seg2  Seg3
```

Each segment was itself a small hash table protected by its own lock.

---

# 13.4 Segment Locking

Suppose

Thread A

writes

Segment 0

Thread B

writes

Segment 3

Execution

```text
Thread A

↓

Segment 0 Locked

-------------------

Thread B

↓

Segment 3 Locked
```

No blocking.

Different segments could be updated simultaneously.

---

# 13.5 Limitation of Segments

Problem:

If two hot keys

belonged to

Segment 2

all writes still blocked each other.

Scalability was limited by the number of segments.

This design was replaced in Java 8.

---

# 13.6 Java 8 Architecture

Java 8 removed segments completely.

Now the structure is much simpler.

```text
Bucket Array

↓

Node

↓

Node

↓

TreeNode
```

Instead of locking an entire segment,

ConcurrentHashMap locks only the bucket being modified.

---

# 13.7 Bucket-Level Locking

Suppose

Bucket 2

and

Bucket 9

Execution

```text
Thread A

↓

Bucket 2

------------------

Thread B

↓

Bucket 9
```

Both execute simultaneously.

This dramatically improves concurrency.

---

# 13.8 Lock-Free Reads

One of the biggest improvements.

Example

```java
User user = map.get(id);
```

No lock.

Reads are generally lock-free and rely on carefully designed memory visibility guarantees.

This allows thousands of concurrent read operations with minimal contention.

---

# 13.9 CAS (Compare-And-Swap)

One of the most important interview topics.

Instead of always locking,

ConcurrentHashMap first attempts

CAS.

Conceptually:

```text
Current Value = X

↓

Expected Value = X ?

↓

YES

↓

Update

↓

Done

NO

↓

Retry
```

CAS is implemented using low-level atomic CPU instructions exposed through JVM primitives.

---

# 13.10 Example

Suppose

Bucket empty

Thread A

```java
put("A",100)
```

Thread B

```java
put("A",200)
```

Both attempt CAS.

Only one succeeds.

The other retries,

possibly falling back to bucket synchronization if necessary.

---

# 13.11 Tree Bins

Just like HashMap,

ConcurrentHashMap converts

Linked List

↓

Red Black Tree

when collisions become excessive.

Benefits:

```text
Search

O(log n)
```

instead of

```text
O(n)
```

---

# 13.12 Concurrent Resize

One of the smartest engineering features.

HashMap

```text
One Thread

↓

Resize
```

ConcurrentHashMap

```text
Thread A

↓

Move Buckets

------------------

Thread B

↓

Help Resize

------------------

Thread C

↓

Help Resize
```

Multiple threads can participate in transferring buckets during resize, reducing pause times under heavy load.

---

# 13.13 putIfAbsent()

Instead of

```java
if(map.get(key)==null){

	map.put(key,value);

}
```

which is **not atomic**,

use

```java
map.putIfAbsent(key,value);
```

Entire operation

```text
Check

↓

Insert
```

is atomic.

---

# 13.14 computeIfAbsent()

One of the most useful methods.

```java
User user =
map.computeIfAbsent(

	id,

	this::loadUser

);
```

Meaning

```text
Exists?

↓

Yes

↓

Return

----------------

No

↓

Create

↓

Insert

↓

Return
```

The mapping function is applied atomically for a given key.

---

# 13.15 merge()

Example

```java
map.merge(

	"A",

	1,

	Integer::sum

);
```

Useful for counters.

Instead of

```java
count++;

put();
```

which is unsafe,

`merge()` performs the update atomically for the specified key.

---

# 13.16 Weakly Consistent Iterator

Unlike HashMap,

ConcurrentHashMap

supports iteration

while updates occur.

```java
for(User u : map.values()){

}
```

The iterator:

* Does **not** throw `ConcurrentModificationException`.
* Reflects some updates made during iteration, but not necessarily all of them.

This is known as a **weakly consistent iterator**.

---

# 13.17 Real Spring Boot Example

Session Cache

```java
@Service
public class SessionCache {

	private final ConcurrentHashMap<String, Session>
			sessions = new ConcurrentHashMap<>();

	public void add(Session session){

		sessions.put(session.getId(), session);

	}

	public Session get(String id){

		return sessions.get(id);

	}

}
```

Thousands of requests

can safely

read and update

the cache concurrently.

---

# 13.18 Performance Comparison

| Collection        | Thread Safe | Read Performance            | Write Performance            |
| ----------------- | ----------- | --------------------------- | ---------------------------- |
| HashMap           | ❌           | Excellent (single-threaded) | Excellent (single-threaded)  |
| synchronizedMap   | ✅           | Poor under contention       | Poor under contention        |
| ConcurrentHashMap | ✅           | Excellent                   | Excellent for most workloads |

---

# 13.19 Common Interview Questions

### Q1. Why is ConcurrentHashMap faster?

Because it avoids a single global lock by combining lock-free reads, fine-grained synchronization, and atomic operations.

---

### Q2. Does ConcurrentHashMap lock the entire map?

No.

In Java 8+, synchronization is generally limited to individual buckets during updates.

---

### Q3. Is get() synchronized?

No.

Reads are designed to be lock-free while remaining thread-safe.

---

### Q4. Why use computeIfAbsent()?

To atomically compute and insert a value only if it is missing, avoiding race conditions.

---

### Q5. Can ConcurrentHashMap store null keys?

No.

Neither null keys nor null values are allowed.

This avoids ambiguity in concurrent operations.

---

# Production Scenario

**Interviewer:**

> "Your authentication service stores one million active sessions. Thousands of users log in simultaneously. Which map implementation would you choose?"

A strong answer:

* Use `ConcurrentHashMap`.
* Reads remain highly scalable.
* Updates are synchronized at a fine-grained level.
* Methods like `putIfAbsent()` and `computeIfAbsent()` help avoid race conditions.
* For distributed deployments, remember that `ConcurrentHashMap` protects only the current JVM instance.

---

# Common Mistakes

❌ Using

```java
if(map.get(k)==null){
	map.put(k,v);
}
```

This check-then-act sequence is not atomic.

Use:

```java
map.putIfAbsent(k,v);
```

or

```java
map.computeIfAbsent(...)
```

instead.

---

❌ Storing null values

```java
map.put("A",null);
```

Results in

```text
NullPointerException
```

because `ConcurrentHashMap` prohibits null keys and values.

---

❌ Assuming iteration is a snapshot

Iterators are weakly consistent, not immutable snapshots.

---

# Best Practices

✅ Prefer `computeIfAbsent()` over manual check-then-put logic.

✅ Use `merge()` for concurrent counters.

✅ Use immutable value objects whenever possible.

✅ Avoid long-running work inside `computeIfAbsent()` mapping functions.

✅ Remember that `ConcurrentHashMap` is thread-safe within a single JVM, not across multiple application instances.

---

# Chapter Summary

* `ConcurrentHashMap` is designed for high-performance concurrent access.
* Java 7 used segment-based locking; Java 8 moved to bucket-level synchronization.
* Reads are generally lock-free.
* CAS reduces lock contention.
* `computeIfAbsent()`, `putIfAbsent()`, and `merge()` provide atomic operations.
* Weakly consistent iterators allow safe iteration during concurrent modifications.
* It is the preferred choice for thread-safe in-memory maps in enterprise Java applications.

---

# Progress Update

### Completed Concurrent Collection Chapters

* ✅ Chapter 11 - HashMap Internals
* ✅ Chapter 12 - Why HashMap is NOT Thread Safe
* ✅ Chapter 13 - ConcurrentHashMap

---

# Next Chapter

## Chapter 14 - CopyOnWriteArrayList

We'll explore:

* Why `ArrayList` is not thread-safe
* Internal Copy-On-Write mechanism
* Snapshot iterators
* Read vs write performance trade-offs
* Event listener implementations
* Observer pattern
* Spring Framework use cases
* Performance analysis
* Production scenarios
* Senior interview questions

This chapter introduces another important concurrent collection optimized for **read-mostly workloads**, complementing the map-based structures covered so far.
