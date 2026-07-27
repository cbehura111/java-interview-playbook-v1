# Part V - Executor Framework & Asynchronous Programming

# Chapter 21: Executor Framework & ExecutorService

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Asked in:** Amazon, Microsoft, Oracle, Goldman Sachs, Walmart, Visa, Adobe, Atlassian

---

# 1. Why Do Interviewers Ask This?

This topic reveals whether you understand **how Java applications execute tasks in production**.

The interviewer wants to assess whether you understand:

* Why manually creating threads is a bad idea
* Thread lifecycle
* Thread pooling
* Resource management
* Scalability
* Task execution
* Production best practices

Typical interview question:

> **Why should we use ExecutorService instead of creating threads using `new Thread()`?**

---

# 2. 30-Second Interview Answer

> Creating a new thread for every task is expensive because thread creation, scheduling, and destruction consume CPU and memory. `ExecutorService` manages a pool of reusable worker threads, reducing thread creation overhead, controlling concurrency, improving throughput, and providing lifecycle management such as graceful shutdown.

---

# 3. The Problem with `new Thread()`

Junior developers often write:

```java
new Thread(() -> processOrder()).start();
```

Looks simple.

But imagine your REST API receives:

```text
20 requests/sec
```

No problem.

Now imagine:

```text
10,000 requests/sec
```

Now you're creating

```text
10,000 Threads
```

Problems:

* Huge memory consumption
* CPU context switching
* Thread scheduling overhead
* Thread creation cost
* Possible `OutOfMemoryError`

---

# 4. Why is Thread Creation Expensive?

A Java thread is **not just a Java object**.

Creating a thread involves:

```text
Application

↓

JVM

↓

Native Thread

↓

Operating System

↓

Kernel

↓

CPU Scheduler
```

Each thread requires:

* Native OS thread
* Thread stack (typically 1 MB by default, JVM/OS dependent)
* Scheduling metadata
* Context-switch support

Creating thousands of threads is costly.

---

# 5. Production Scenario

Imagine a payment service.

Every payment triggers:

```java
new Thread(() -> sendEmail()).start();
```

Traffic:

```text
50 TPS

↓

500 TPS

↓

5000 TPS
```

Soon:

* Thousands of live threads
* High CPU utilization
* Increased GC pressure
* Slow response times

---

# 6. The Executor Framework

Instead of creating threads,

submit **tasks**.

```text
Application

↓

ExecutorService

↓

Task Queue

↓

Worker Threads

↓

Execution
```

The application no longer manages threads directly.

It delegates thread management to the framework.

---

# 7. Core Interfaces

```text
Executor
		│
		▼
ExecutorService
		│
		▼
ScheduledExecutorService
```

### Executor

Simple interface.

```java
public interface Executor {

	void execute(Runnable command);

}
```

Only executes tasks.

No shutdown.

No result.

---

### ExecutorService

Adds:

* submit()
* Future
* shutdown()
* invokeAll()
* invokeAny()

---

### ScheduledExecutorService

Adds scheduling support.

* Delayed execution
* Fixed-rate execution
* Fixed-delay execution

---

# 8. Creating an ExecutorService

```java
ExecutorService executor =
		Executors.newFixedThreadPool(5);
```

Five worker threads are created.

Suppose you submit 100 tasks.

```text
100 Tasks

↓

Queue

↓

5 Threads

↓

Execution
```

Only five tasks execute concurrently.

The remaining tasks wait in the queue.

---

# 9. execute() vs submit()

### execute()

```java
executor.execute(() -> processOrder());
```

Characteristics:

* No return value
* Exceptions go to the thread's uncaught exception handler

---

### submit()

```java
Future<String> future =
		executor.submit(() -> processOrder());
```

Characteristics:

* Returns a `Future`
* Exceptions are captured and rethrown when calling `future.get()`

---

**Interview Question**

Which one do you prefer?

Answer:

* Use `execute()` for fire-and-forget tasks.
* Use `submit()` when you need a result or exception handling through `Future`.

---

# 10. Runnable vs Callable

### Runnable

```java
Runnable task = () -> {

	processOrder();

};
```

Returns

```text
void
```

Cannot throw checked exceptions directly.

---

### Callable

```java
Callable<Order> task = () -> {

	return processOrder();

};
```

Returns

```text
Order
```

Can throw checked exceptions.

---

# 11. Future

`Future` represents the result of an asynchronous computation.

```java
Future<String> future =
		executor.submit(() -> "SUCCESS");
```

Later:

```java
String result = future.get();
```

Important:

> `future.get()` blocks until the task completes.

---

# 12. Production Example

Invoice generation.

```text
REST Request

↓

Submit Task

↓

ExecutorService

↓

Generate PDF

↓

Store in S3

↓

Return Download Link
```

The REST thread is freed quickly while background processing continues.

---

# 13. Executor Lifecycle

Many candidates forget this.

```text
Created

↓

Running

↓

Shutdown Requested

↓

No New Tasks

↓

Existing Tasks Complete

↓

Terminated
```

---

# 14. shutdown() vs shutdownNow()

### shutdown()

```java
executor.shutdown();
```

* Stops accepting new tasks
* Allows queued/running tasks to finish

---

### shutdownNow()

```java
executor.shutdownNow();
```

* Attempts to interrupt running tasks
* Returns tasks that never started
* Interruption is cooperative-tasks must respond to interrupts

---

**Interview Trap**

Does `shutdownNow()` always stop every thread immediately?

**No.**

A task that ignores interruption may continue running.

---

# 15. Production Best Practices

✅ Prefer dependency-injected executors (for example, in Spring) instead of creating executors throughout the codebase.

✅ Always shut down executors you create manually.

✅ Give worker threads meaningful names.

✅ Monitor queue size and active thread count.

❌ Never create a new executor for every request.

❌ Never use `Executors` factory methods blindly in production without understanding their queueing behavior.

---

# 16. Common Interview Traps

### Is ExecutorService a thread?

❌ No.

It manages a collection of worker threads.

---

### Does submit() create a new thread?

❌ No.

It submits a task.

The pool decides which worker executes it.

---

### Can one thread execute multiple tasks?

✅ Yes.

Worker threads are reused.

---

### Is Future asynchronous?

Not by itself.

The task executes asynchronously, but `Future.get()` is a blocking call.

---

# 17. Senior-Level Follow-up Questions

1. Why is creating threads expensive?
2. What is thread reuse?
3. Difference between execute() and submit()?
4. Runnable vs Callable?
5. What happens if a task throws an exception?
6. How does Future work?
7. Why is Future considered limited compared to CompletableFuture?
8. What happens if you never call shutdown()?
9. Can ExecutorService leak resources?
10. How do you monitor a thread pool in production?

---

# 18. Production Debugging Scenario

### Problem

A Spring Boot application gradually slows down after several days.

### Investigation

* Heap looks normal
* Database is healthy
* CPU is moderate
* Thousands of threads remain active

### Root Cause

Developers created new executors repeatedly:

```java
public void sendEmail() {

	ExecutorService executor =
		Executors.newFixedThreadPool(5);

	executor.submit(...);

}
```

Each invocation creates a new thread pool that is never shut down.

### Fix

* Create a shared executor.
* Reuse it across the application.
* Shut it down gracefully during application shutdown.

---

# 19. Cheat Sheet

| Concept           | Key Point                 |
| ----------------- | ------------------------- |
| `Executor`        | Executes tasks            |
| `ExecutorService` | Manages thread pools      |
| `execute()`       | No return value           |
| `submit()`        | Returns `Future`          |
| `Runnable`        | No result                 |
| `Callable`        | Returns result            |
| `Future.get()`    | Blocking                  |
| `shutdown()`      | Graceful shutdown         |
| `shutdownNow()`   | Attempts interruption     |
| Worker Thread     | Reused for multiple tasks |

---

# 🎯 Interview Quick Revision

**Q:** Why use `ExecutorService` instead of `new Thread()`?

**Answer:**

* Reuses threads
* Controls concurrency
* Reduces thread creation overhead
* Improves scalability
* Provides lifecycle management
* Supports asynchronous task execution and result handling

---

## 🔥 Interviewer's Hidden Question

When an interviewer asks:

> **"Why ExecutorService?"**

They're often really asking:

> **"Do you understand how a production backend handles thousands of concurrent requests without creating thousands of OS threads?"**

Answering that broader question-with discussion of thread reuse, resource management, queueing, and scalability-is what distinguishes a senior engineer from someone who only knows the API.

---

### Next Chapter (Most Important)

**Chapter 22 - ThreadPoolExecutor Internals**

This is one of the highest-value topics in senior interviews. We'll go beyond the `Executors` factory methods and examine:

* Internal architecture of `ThreadPoolExecutor`
* Worker thread lifecycle
* Core pool size vs maximum pool size
* Queue types and their impact
* Thread creation algorithm
* Rejection policies
* Pool sizing strategies for CPU-bound vs I/O-bound workloads
* Spring Boot thread pool configuration
* Real production tuning and debugging scenarios

This chapter is where most candidates struggle, and mastering it gives you a significant advantage in backend interviews.
