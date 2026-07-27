# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part III - Concurrent Collections

# Chapter 16 - ConcurrentLinkedQueue (Lock-Free Queue)

> **"Traditional concurrent collections rely on locks to ensure thread safety. `ConcurrentLinkedQueue` takes a different approach-it uses lock-free algorithms and atomic CPU instructions to achieve high scalability."**

`ConcurrentLinkedQueue` is widely used in **high-throughput messaging systems, asynchronous frameworks, task dispatchers, networking libraries, and low-latency applications**.

---

# Learning Objectives

After completing this chapter, you will understand:

* What is `ConcurrentLinkedQueue`?
* Why Lock-Free Data Structures Matter
* Internal Architecture
* CAS (Compare-And-Swap)
* Michael-Scott Queue Algorithm
* `offer()`, `poll()`, `peek()`
* Lock-Free vs Blocking Queues
* Performance Characteristics
* Production Use Cases
* Interview Questions

---

# 16.1 Why Another Queue?

Suppose thousands of threads continuously submit tasks.

Using

```java
Queue<Task> queue =
		new LinkedList<>();
```

Problems:

* Not thread-safe
* Race conditions
* Requires external synchronization

Using

```java
BlockingQueue<Task>
```

solves thread safety,

but locking introduces contention.

Can we avoid locks entirely?

Yes.

That's exactly why `ConcurrentLinkedQueue` exists.

---

# 16.2 What is ConcurrentLinkedQueue?

`ConcurrentLinkedQueue` is an **unbounded**, **thread-safe**, **non-blocking FIFO queue**.

```java
ConcurrentLinkedQueue<String> queue =
		new ConcurrentLinkedQueue<>();
```

Characteristics:

* Lock-free
* Thread-safe
* FIFO ordering
* High throughput
* Non-blocking operations

---

# 16.3 Internal Structure

Internally the queue is a linked list.

```text
Head

↓

Node

↓

Node

↓

Node

↓

Tail
```

Each node contains:

```java
class Node<E>{

	volatile E item;

	volatile Node<E> next;

}
```

Both `item` and `next` are updated atomically.

---

# 16.4 Lock-Free Algorithm

Unlike

```text
ReentrantLock

↓

Acquire Lock

↓

Modify Queue

↓

Release Lock
```

ConcurrentLinkedQueue uses

```text
CAS

↓

Success?

↓

YES

Done

↓

NO

Retry
```

No thread waits for another.

---

# 16.5 Michael-Scott Queue

The implementation is based on the famous

**Michael-Scott Lock-Free Queue Algorithm**

Published in

1996.

Idea:

```text
Tail

↓

CAS

↓

Append Node

↓

Move Tail
```

Multiple threads may attempt to append simultaneously.

Only one CAS succeeds.

Others retry.

---

# 16.6 offer()

```java
queue.offer("Task-101");
```

Execution

```text
Current Tail

↓

CAS

↓

Insert New Node

↓

Move Tail
```

No lock.

Multiple producers can insert concurrently.

---

# 16.7 poll()

```java
String task =
		queue.poll();
```

Execution

```text
Head

↓

Read Next

↓

CAS

↓

Move Head
```

The head advances atomically.

If the queue is empty,

`poll()` returns

```text
null
```

It does **not** block.

---

# 16.8 peek()

```java
queue.peek();
```

Returns

```text
First Element
```

without removing it.

If empty

```text
null
```

is returned.

---

# 16.9 Producer Example

```java
ConcurrentLinkedQueue<String> queue =
		new ConcurrentLinkedQueue<>();

queue.offer("Laptop");

queue.offer("Phone");
```

Queue

```text
Laptop

↓

Phone
```

---

# 16.10 Consumer Example

```java
while(true){

	String item = queue.poll();

	if(item != null){

		process(item);

	}

}
```

Notice

No blocking.

The consumer decides how to behave when the queue is empty.

In many applications, a short backoff strategy or integration with another signaling mechanism is preferable to a tight polling loop.

---

# 16.11 Concurrent Producers

Suppose

Thread A

```text
Offer A
```

Thread B

```text
Offer B
```

Execution

```text
Thread A

↓

CAS

↓

Success

--------------------

Thread B

↓

Retry

↓

Success
```

No global lock.

---

# 16.12 Concurrent Consumers

Thread A

```text
Poll
```

Thread B

```text
Poll
```

Both attempt CAS.

Only one removes a given node.

Each element is removed at most once.

---

# 16.13 ConcurrentLinkedQueue vs BlockingQueue

| Feature         | ConcurrentLinkedQueue | BlockingQueue             |
| --------------- | --------------------- | ------------------------- |
| Thread Safe     | ✅                     | ✅                         |
| Lock-Free       | ✅                     | Usually No                |
| Blocks on Empty | ❌                     | ✅ (`take()`)              |
| Blocks on Full  | ❌ (Unbounded)         | Depends on implementation |
| Capacity        | Unbounded             | Bounded or Unbounded      |

---

# 16.14 Throughput

Suppose

100 Threads

continuously add tasks.

Performance trend

```text
LinkedList

↓

synchronized Queue

↓

ConcurrentLinkedQueue
```

Lock-free algorithms generally provide better scalability under high contention, although actual performance depends on workload, hardware, and JVM optimizations.

---

# 16.15 Real Spring Boot Example

Task Dispatcher

```java
@Service
public class TaskDispatcher {

	private final ConcurrentLinkedQueue<Task>
			queue =
			new ConcurrentLinkedQueue<>();

	public void submit(Task task){

		queue.offer(task);

	}

	public Task next(){

		return queue.poll();

	}

}
```

Suitable when consumers periodically poll for work or are triggered by another mechanism.

---

# 16.16 Logging Framework Example

Many asynchronous logging frameworks maintain internal queues.

Conceptually

```text
Application Thread

↓

Log Queue

↓

Logger Thread

↓

File
```

A lock-free queue helps reduce contention when many threads generate log messages simultaneously.

---

# 16.17 Common Interview Questions

### Q1. Is ConcurrentLinkedQueue thread-safe?

Yes.

It is designed for concurrent producers and consumers.

---

### Q2. Does it use locks?

No.

It uses lock-free algorithms based on CAS.

---

### Q3. Does poll() block?

No.

If the queue is empty,

it immediately returns

```text
null
```

---

### Q4. Is it bounded?

No.

It grows as needed until memory becomes a limiting factor.

---

### Q5. When should you use ConcurrentLinkedQueue?

When:

* High throughput is required
* Blocking behavior is unnecessary
* Producers and consumers can tolerate polling or have another coordination mechanism

---

# Production Scenario

**Interviewer:**

> "You need a high-performance task queue where producers should never block, and consumers periodically check for work. Which queue would you choose?"

A strong answer:

* `ConcurrentLinkedQueue`.
* It is lock-free and highly scalable.
* `offer()` and `poll()` do not block.
* If consumers must wait efficiently for work instead of polling, a `BlockingQueue` is a better choice.

---

# Best Practices

✅ Use when blocking behavior is unnecessary.

✅ Consider backoff strategies instead of aggressive busy polling.

✅ Monitor memory usage because the queue is unbounded.

✅ Design consumers to handle temporary empty queues efficiently.

---

# Common Mistakes

❌ Using it when consumers should sleep until work arrives.

❌ Assuming it has a fixed capacity.

❌ Forgetting that continuous polling can waste CPU.

❌ Treating it as a replacement for every `BlockingQueue`.

---

# Chapter Summary

* `ConcurrentLinkedQueue` is a lock-free, thread-safe FIFO queue.
* It is based on the Michael-Scott algorithm and CAS operations.
* `offer()`, `poll()`, and `peek()` never block.
* It is ideal for high-throughput, low-latency systems where producers and consumers do not require blocking coordination.
* For producer-consumer workflows that require waiting, `BlockingQueue` is generally the better choice.

---

# Progress Update

### Part III - Concurrent Collections

* ✅ Chapter 11 - HashMap Internals
* ✅ Chapter 12 - Why HashMap is NOT Thread Safe
* ✅ Chapter 13 - ConcurrentHashMap
* ✅ Chapter 14 - CopyOnWriteArrayList
* ✅ Chapter 15 - BlockingQueue
* ✅ Chapter 16 - ConcurrentLinkedQueue

---

# Next Chapter

## Chapter 17 - Atomic Classes & Compare-And-Swap (CAS)

The next chapter begins **Part IV - Atomic Operations** and covers one of the most important foundations of modern concurrent programming:

* Why `synchronized` is not always the best solution
* Hardware atomic instructions
* Compare-And-Swap (CAS)
* `AtomicInteger`
* `AtomicLong`
* `AtomicBoolean`
* `AtomicReference`
* `LongAdder` and `LongAccumulator`
* ABA Problem
* CAS retry loops
* Lock-free programming concepts
* Production examples (counters, sequence generators, rate limiters)
* Senior interview questions

This chapter forms the foundation for understanding how high-performance classes like `ConcurrentHashMap`, `ConcurrentLinkedQueue`, and many JVM internals achieve thread safety with minimal locking.
