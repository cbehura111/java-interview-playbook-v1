# Part V - Executor Framework & Asynchronous Programming

# Chapter 26: Virtual Threads (Project Loom, Java 21) - The Future of Java Concurrency

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Uber, Atlassian, VMware, Modern Java 21 Interviews

---

# 1. Why Do Interviewers Ask This?

Virtual Threads are **the biggest change to Java concurrency since the Executor Framework**.

If you're interviewing for Java 21+, expect questions like:

* What are Virtual Threads?
* Why were they introduced?
* How are they different from platform threads?
* Do they replace thread pools?
* What is thread pinning?
* Can I migrate existing Spring Boot applications?

---

# 2. 30-Second Interview Answer

> Virtual Threads are lightweight threads introduced in Java 21. Unlike platform threads, they are managed primarily by the JVM instead of being permanently tied to an operating system thread. A virtual thread occupies a platform (carrier) thread only while it is actively running. When it blocks on supported operations such as network I/O, the JVM unmounts it so the carrier thread can execute other virtual threads. This enables applications to handle very large numbers of concurrent tasks using the familiar thread-per-request programming model.

---

# 3. The Problem Before Virtual Threads

Traditional Java

```java
new Thread(() -> processRequest()).start();
```

Every Java thread

↓

One OS Thread

```text
Java Thread 1
	  │
	  ▼
 OS Thread 1

Java Thread 2
	  │
	  ▼
 OS Thread 2
```

10,000 requests

↓

10,000 OS Threads

Problems

* Huge memory usage
* Context switching
* Scheduler overhead
* Poor scalability

---

# 4. Platform Threads

Traditional threads are now called

```text
Platform Threads
```

Relationship

```text
1 Java Thread

↓

1 OS Thread
```

Expensive.

---

# 5. Virtual Threads

Now imagine

```text
1,000,000 Virtual Threads
```

Running on

```text
8 Carrier Threads
```

Possible because

Virtual Threads

≠

OS Threads

---

# 6. Architecture

```text
		  Virtual Threads

	  VT1 VT2 VT3 VT4 VT5 ...

			 │

			 ▼

	 JVM Scheduler

			 │

			 ▼

	  Carrier Threads

		PT1   PT2   PT3

			 │

			 ▼

		 Operating System
```

The JVM schedules virtual threads onto a smaller set of carrier (platform) threads.

---

# 7. Creating Virtual Threads

Traditional

```java
Thread thread =
	new Thread(task);

thread.start();
```

Virtual Thread

```java
Thread.startVirtualThread(() -> {

	processOrder();

});
```

Very simple.

---

# 8. Virtual Thread Executor

Instead of

```java
ExecutorService executor =
	Executors.newFixedThreadPool(100);
```

Use

```java
try (ExecutorService executor =
		 Executors.newVirtualThreadPerTaskExecutor()) {

	executor.submit(() -> processOrder());

}
```

Each submitted task gets its own virtual thread.

---

# 9. Why Are They Fast?

Suppose

Request

↓

HTTP Call

↓

Wait 500 ms

Platform Thread

```text
OS Thread

Waiting...
```

The OS thread remains occupied.

Virtual Thread

```text
Virtual Thread

↓

Blocks

↓

Unmounted

↓

Carrier Thread Free
```

Carrier thread immediately executes another virtual thread.

---

# 10. Mounting and Unmounting

Virtual Thread

↓

Running

↓

Mounted

↓

Carrier Thread

When blocking on supported operations

↓

Unmount

↓

Carrier Released

Later

↓

Resume

↓

Mounted Again

This transparent scheduling is the key innovation.

---

# 11. Thread Pinning

One of the favourite Java 21 interview topics.

Sometimes

Virtual Thread

cannot unmount.

It becomes

```text
Pinned
```

Carrier thread

remains occupied.

---

# 12. Common Causes of Pinning

Examples include:

```java
synchronized(lock) {

	callDatabase();

}
```

If the thread blocks while inside a `synchronized` section,

the carrier thread may remain pinned.

Other examples:

* Native/JNI calls
* Some blocking operations that cannot be cooperatively managed

---

# 13. Better Alternative

Instead of

```java
synchronized(lock) {

}
```

Consider

```java
ReentrantLock lock =
		new ReentrantLock();
```

`ReentrantLock` is generally a better fit for code that may block while running on virtual threads, although the best choice still depends on your concurrency requirements.

---

# 14. Spring Boot Support

Spring Boot 3.2+

supports Virtual Threads.

Configuration

```properties
spring.threads.virtual.enabled=true
```

No major application rewrite required for many request-processing workloads.

---

# 15. Where Virtual Threads Shine

Excellent for

* REST APIs
* Database calls
* HTTP clients
* Kafka consumers
* File I/O
* Messaging
* Microservices

Why?

Because these workloads spend much of their time waiting.

---

# 16. Where They Don't Help Much

CPU-intensive tasks

Examples

* Encryption
* Image Processing
* Video Encoding
* AI Model Training

These tasks keep the CPU busy rather than waiting.

Adding millions of virtual threads won't make the CPU execute faster.

---

# 17. Thread Pool vs Virtual Threads

Traditional

```text
100 Tasks

↓

10 Threads

↓

Queue
```

Virtual Threads

```text
100 Tasks

↓

100 Virtual Threads

↓

Scheduler
```

No need for a small worker pool just to limit thread creation overhead.

Resource limits such as database connections still need to be managed separately.

---

# 18. Production Example

Order Service

For every request

Need

* Customer API
* Inventory API
* Payment API

Traditional

Complex async code

↓

CompletableFuture

↓

Thread pools

Virtual Threads

```java
customer();

inventory();

payment();
```

Each blocking call can execute in its own virtual thread, making the code look synchronous while still scaling well for I/O-bound workloads.

---

# 19. Common Interview Traps

### Do Virtual Threads replace CompletableFuture?

❌ No.

They solve different problems.

* Virtual Threads simplify thread management.
* `CompletableFuture` simplifies asynchronous composition and combining results.

Often they complement each other.

---

### Do Virtual Threads replace ThreadPoolExecutor?

Not entirely.

They replace many thread-pool use cases centred on thread reuse.

You may still need executors to:

* Limit concurrency
* Prioritise tasks
* Schedule work
* Isolate workloads

---

### Are Virtual Threads faster?

Not necessarily.

They are **more scalable for blocking workloads**, not inherently faster for CPU-bound computation.

---

### Can I create one million Virtual Threads?

Potentially yes, depending on available memory and workload characteristics.

That does **not** mean one million tasks will execute simultaneously.

---

# 20. Production Debugging Story

Problem

A migration to Java 21 showed little performance improvement.

Investigation

Most processing involved:

```text
Image Compression

Encryption

PDF Rendering
```

CPU utilisation

```text
100%
```

Root Cause

CPU-bound workload.

Virtual Threads cannot eliminate CPU limits.

Fix

Use appropriate parallelism (for example, `ForkJoinPool`) for CPU-intensive work.

---

# 21. Platform Threads vs Virtual Threads

| Feature             | Platform Thread | Virtual Thread                      |
| ------------------- | --------------- | ----------------------------------- |
| Backed by OS thread | Yes             | No (scheduled onto carrier threads) |
| Creation Cost       | High            | Low                                 |
| Memory              | Higher          | Lower                               |
| Millions Possible   | No              | Yes (workload dependent)            |
| Best For            | General purpose | Blocking I/O workloads              |
| Java Version        | All             | Java 21+                            |

---

# 22. Senior-Level Follow-up Questions

1. Why were Virtual Threads introduced?
2. Explain carrier threads.
3. What is mounting and unmounting?
4. What is thread pinning?
5. Why can `synchronized` cause pinning?
6. Are Virtual Threads suitable for CPU-bound work?
7. Do Virtual Threads eliminate the need for connection pools?
8. How would you migrate a Spring Boot application?
9. How would you monitor Virtual Threads in production?
10. When would you still use `CompletableFuture`?

---

# 23. Real Interview Scenario

**Interviewer:**

> "Your Spring Boot application handles 50,000 concurrent HTTP requests, most of which wait on external services. Would you recommend Virtual Threads?"

### Strong Answer

> Yes. This is a classic I/O-bound workload where Virtual Threads are a strong fit. They allow a thread-per-request programming model without requiring tens of thousands of platform threads. I'd still ensure that downstream resources such as database connection pools and HTTP client limits are configured appropriately, because Virtual Threads don't remove those bottlenecks.

---

# 24. Cheat Sheet

| Scenario                 | Recommendation                                 |
| ------------------------ | ---------------------------------------------- |
| REST APIs                | ✅ Virtual Threads                              |
| Database Calls           | ✅ Virtual Threads                              |
| HTTP Clients             | ✅ Virtual Threads                              |
| Kafka Consumers          | ✅ Virtual Threads (evaluate framework support) |
| File I/O                 | ✅ Virtual Threads                              |
| CPU-intensive Processing | ❌ Prefer platform threads/ForkJoinPool         |
| Async Composition        | ✅ CompletableFuture                            |
| Scheduled Jobs           | ✅ ScheduledExecutorService                     |

---

# 🎯 Migration Tips

✅ Use Virtual Threads for blocking I/O.

✅ Avoid holding locks while performing long blocking operations.

✅ Test third-party libraries for Java 21 compatibility.

✅ Continue to size external resources (database pools, HTTP connection pools, etc.) appropriately.

✅ Measure performance before and after migration.

---

## ⭐ Interview Secret

When an interviewer asks:

> **"Should every Java 21 application switch to Virtual Threads?"**

A strong senior answer is:

> "Not automatically. I'd first identify whether the application is I/O-bound or CPU-bound. Virtual Threads provide the biggest benefit for blocking operations such as database access and HTTP calls. For CPU-intensive workloads, they don't improve throughput. I'd also validate library compatibility, watch for thread pinning, and ensure downstream resources like connection pools are tuned appropriately."

This demonstrates balanced engineering judgement rather than treating Virtual Threads as a universal solution.

---

## 📌 Part V Complete

You have now covered:

* ✅ Executor Framework & `ExecutorService`
* ✅ `ThreadPoolExecutor` Internals
* ✅ `CompletableFuture`
* ✅ `ForkJoinPool` & Work-Stealing
* ✅ `ScheduledExecutorService`
* ✅ **Virtual Threads (Java 21)**

These topics represent the core concurrency concepts expected of senior Java backend engineers.

### Next Part: **Part VI - JVM Memory Management & Garbage Collection for Interviews**

We'll shift from concurrency to JVM internals, covering topics such as:

* Runtime Memory Areas
* Heap generations
* Object allocation
* Escape analysis
* G1, ZGC, Shenandoah
* GC tuning
* Memory leaks
* OutOfMemoryError debugging
* Production JVM troubleshooting

This is another area that is heavily tested in senior backend interviews, especially for roles involving performance and large-scale systems.
