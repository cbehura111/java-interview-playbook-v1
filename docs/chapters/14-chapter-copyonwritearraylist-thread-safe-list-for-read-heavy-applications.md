# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part III - Concurrent Collections

# Chapter 14 - CopyOnWriteArrayList (Thread-Safe List for Read-Heavy Applications)

> **"What if thousands of threads are reading a list while only a few occasionally modify it? Instead of synchronizing every read, Java takes a completely different approach-it creates a new copy of the list whenever a write occurs."**

This is the core idea behind `CopyOnWriteArrayList`.

It is one of the most elegant concurrent collections in Java and is frequently used in **event listeners, observer patterns, Spring Framework internals, and configuration registries**.

---

# Learning Objectives

After completing this chapter, you will understand:

* Why `ArrayList` is not thread-safe
* What Copy-On-Write means
* Internal Architecture
* Read Operations
* Write Operations
* Snapshot Iterators
* Memory Trade-offs
* Performance Analysis
* Production Use Cases
* Interview Questions

---

# 14.1 Why ArrayList Fails in Concurrent Applications

Suppose multiple threads access an `ArrayList`.

```java
List<String> users =
	new ArrayList<>();
```

Thread A

```java
users.add("Alice");
```

Thread B

```java
users.remove("Bob");
```

Thread C

```java
for(String user : users){

}
```

Possible problems:

* Race Conditions
* Inconsistent reads
* `ConcurrentModificationException`
* Data corruption

---

# 14.2 Traditional Synchronization

One solution is:

```java
List<String> users =
Collections.synchronizedList(
	new ArrayList<>());
```

Every operation acquires a lock.

```text
Read

↓

LOCK

↓

Read

↓

Unlock
```

Problem:

Thousands of readers block each other.

Performance decreases.

---

# 14.3 The Copy-On-Write Idea

Instead of locking readers,

Java copies the entire array whenever a write occurs.

```text
Original Array

↓

Copy Array

↓

Modify Copy

↓

Replace Reference
```

Readers continue using the old array.

No blocking.

---

# 14.4 Internal Architecture

Internally

```java
CopyOnWriteArrayList
```

maintains

```text
volatile Object[]

↓

Current Array
```

Notice

The array reference is **volatile**.

Whenever a write happens,

a completely new array replaces the old one.

This ensures that readers always see a consistent snapshot.

---

# 14.5 Read Operation

Suppose

```java
users.get(5);
```

Execution

```text
Read Current Array

↓

Return Element
```

No lock.

No copy.

Extremely fast.

---

# 14.6 Write Operation

Suppose

```java
users.add("David");
```

Execution

```text
Current Array

↓

Copy Entire Array

↓

Add Element

↓

Replace Array Reference
```

The old array remains unchanged.

Readers continue using it safely.

---

# 14.7 Example

```java
CopyOnWriteArrayList<String> users =
	new CopyOnWriteArrayList<>();

users.add("Alice");

users.add("Bob");

System.out.println(users);
```

Every `add()` creates a new internal array.

---

# 14.8 Snapshot Iterator

One of the biggest interview topics.

Example

```java
for(String user : users){

    System.out.println(user);

}
```

While iteration is happening,

another thread executes

```java
users.add("Charlie");
```

What happens?

The iterator continues reading

the original snapshot.

It does **not** see "Charlie" during the current iteration.

---

# 14.9 Why No ConcurrentModificationException?

ArrayList

```text
Iterator

↓

Collection Modified

↓

ConcurrentModificationException
```

CopyOnWriteArrayList

```text
Iterator

↓

Reads Snapshot

↓

No Exception
```

Because the iterator references an immutable snapshot captured when it was created.

---

# 14.10 Internal Example

Initial Array

```text
[A]

[B]

[C]
```

Thread A starts iteration.

Thread B adds

```text
[D]
```

New Array

```text
[A]

[B]

[C]

[D]
```

Thread A

continues reading

```text
[A]

[B]

[C]
```

The iterator is unaffected by the modification.

---

# 14.11 Performance Characteristics

| Operation | Performance |
| --------- | ----------- |
| get()     | O(1)        |
| iteration | O(n)        |
| add()     | O(n)        |
| remove()  | O(n)        |

Reads are fast.

Writes are expensive because every modification copies the underlying array.

---

# 14.12 Memory Cost

Suppose

Array Size

```text
100,000
```

One write

creates another

100,000-element array.

Memory usage temporarily doubles until the old array is no longer referenced and becomes eligible for garbage collection.

Therefore,

frequent writes

can create significant memory pressure.

---

# 14.13 Real Spring Boot Example

Suppose

Spring maintains

Application Listeners

```java
private final CopyOnWriteArrayList<
	ApplicationListener<?>> listeners =
	new CopyOnWriteArrayList<>();
```

Application events are fired constantly.

Listeners are added

only occasionally.

Perfect use case.

---

# 14.14 Event Listener Example

```java
CopyOnWriteArrayList<Runnable> listeners =
	new CopyOnWriteArrayList<>();

listeners.add(() ->
	System.out.println("Event"));

for(Runnable listener : listeners){

    listener.run();

}
```

Multiple threads can safely iterate over listeners while another thread registers a new one.

---

# 14.15 Observer Pattern

Used in

* Notification Systems
* Plugin Registries
* Event Publishers
* Configuration Watchers
* Monitoring Frameworks

Reason:

Many reads

Few writes

---

# 14.16 When NOT to Use It

Avoid

```text
100 Reads

100 Writes
```

Every write copies the array.

Performance becomes poor.

Better choices:

* `ConcurrentLinkedQueue`
* `ConcurrentHashMap`
* `Collections.synchronizedList()`
* Other concurrent data structures depending on access patterns

---

# 14.17 ArrayList vs CopyOnWriteArrayList

| Feature                         | ArrayList | CopyOnWriteArrayList  |
| ------------------------------- | --------- | --------------------- |
| Thread Safe                     | ❌         | ✅                     |
| Read Speed                      | Excellent | Excellent             |
| Write Speed                     | Excellent | Slower (copies array) |
| Iterator                        | Fail-fast | Snapshot              |
| ConcurrentModificationException | Yes       | No                    |

---

# 14.18 Common Interview Questions

### Q1. Why is it called Copy-On-Write?

Because every write operation creates a new copy of the underlying array before applying the modification.

---

### Q2. Why are reads so fast?

Readers access the current array directly without locking or copying.

---

### Q3. Why doesn't it throw ConcurrentModificationException?

Its iterators work on a snapshot of the array rather than the live collection.

---

### Q4. Is it suitable for write-heavy applications?

No.

Frequent copying makes writes expensive in terms of CPU and memory.

---

### Q5. What is the biggest disadvantage?

Every write creates a new array, increasing memory allocation and garbage collection overhead.

---

# Production Scenario

**Interviewer:**

> "Your application has thousands of event listeners reading a shared list, but new listeners are registered only a few times each day. Which collection would you choose?"

A strong answer:

* `CopyOnWriteArrayList`.
* Reads are lock-free and highly scalable.
* Snapshot iterators avoid `ConcurrentModificationException`.
* The low write frequency makes the copying overhead acceptable.

---

# Best Practices

✅ Use for **read-mostly** workloads.

✅ Keep write frequency low.

✅ Use snapshot iterators when concurrent modification is expected.

✅ Prefer immutable objects inside the list where practical.

---

# Common Mistakes

❌ Using `CopyOnWriteArrayList` for write-heavy workloads.

❌ Ignoring the memory overhead of copying large arrays.

❌ Assuming iterators always reflect the latest changes-they reflect the state of the list when the iterator was created.

---

# Chapter Summary

* `CopyOnWriteArrayList` is optimized for read-heavy scenarios.
* Reads are lock-free and operate on the current array.
* Every write creates a new copy of the underlying array.
* Iterators are snapshot-based and never throw `ConcurrentModificationException`.
* It is ideal for listener lists, plugin registries, and observer-pattern implementations.

---

# Progress Update

### Part III - Concurrent Collections

* ✅ Chapter 11 - HashMap Internals
* ✅ Chapter 12 - Why HashMap is NOT Thread Safe
* ✅ Chapter 13 - ConcurrentHashMap
* ✅ Chapter 14 - CopyOnWriteArrayList

---

# Next Chapter

## Chapter 15 - BlockingQueue (Producer-Consumer Pattern)

The next chapter will cover one of the most practical concurrent collections used in enterprise systems:

* What is a `BlockingQueue`?
* Producer-Consumer Pattern
* `put()` vs `offer()`
* `take()` vs `poll()`
* `ArrayBlockingQueue`
* `LinkedBlockingQueue`
* `PriorityBlockingQueue`
* `DelayQueue`
* How `ThreadPoolExecutor` uses `BlockingQueue`
* Spring Boot asynchronous processing
* Kafka consumer internals
* Production scenarios
* Senior interview questions

This chapter connects Java concurrency concepts with real-world systems such as thread pools, messaging platforms, order processing, and asynchronous workflows.
