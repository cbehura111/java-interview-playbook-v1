# Part V - Executor Framework & Asynchronous Programming

# Chapter 22: ThreadPoolExecutor Internals (The Most Important Concurrency Topic)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, Visa, Walmart, Adobe, Atlassian

---

# 1. Why Do Interviewers Ask This?

This is one of the **highest-value** topics in Senior Java interviews.

The interviewer isn't checking whether you've used:

```java
Executors.newFixedThreadPool(10);
```

They want to know if you understand:

* How thread pools work internally
* How tasks are scheduled
* How queues affect throughput
* Why applications become slow
* How to tune thread pools
* How to debug production issues

Typical interview question:

> **Explain what happens internally when I call `executor.submit(task)`**

If you can answer that confidently, you're already ahead of many candidates.

---

# 2. 30-Second Interview Answer

> `ThreadPoolExecutor` manages a pool of reusable worker threads. When a task is submitted, it first tries to use an idle core thread. If all core threads are busy, the task is queued. If the queue is full and the pool hasn't reached its maximum size, new threads are created. Once both the queue and maximum threads are exhausted, the task is rejected using the configured rejection policy.

---

# 3. The Architecture

```text
			    submit()

				  │
				  ▼

		   ThreadPoolExecutor

	   ┌──────────┬──────────┐
	   │          │          │
	   ▼          ▼          ▼

  Core Threads   Task Queue  Extra Threads

				  │

				  ▼

			Worker Threads

				  │

				  ▼

			 Execute Task
```

Think of `ThreadPoolExecutor` as a **manager**.

It decides:

* Should an existing thread execute?
* Should I queue the task?
* Should I create another thread?
* Should I reject the task?

---

# 4. Constructor

The real constructor is:

```java
ThreadPoolExecutor(
    int corePoolSize,
    int maximumPoolSize,
    long keepAliveTime,
    TimeUnit unit,
    BlockingQueue<Runnable> workQueue,
    ThreadFactory threadFactory,
    RejectedExecutionHandler handler
)
```

Every interview eventually revolves around these **seven parameters**.

---

# 5. Core Pool Size

Example:

```java
corePoolSize = 5
```

Means

```text
Maximum permanent workers

↓

5
```

If fewer than 5 threads exist,

new tasks immediately create new workers.

Example

Task1

↓

Thread1

Task2

↓

Thread2

...

Task5

↓

Thread5

---

# 6. What Happens After Core Threads?

Suppose

```text
Core Threads = 5
```

All five are busy.

Task6 arrives.

What happens?

Most candidates answer:

> New thread is created.

❌ Wrong.

The executor first checks the queue.

---

# 7. Task Queue

Suppose

```text
Queue Capacity = 100
```

Now

```text
Thread1 Busy

Thread2 Busy

Thread3 Busy

Thread4 Busy

Thread5 Busy
```

Task6

↓

Queue

Task7

↓

Queue

Task8

↓

Queue

No new thread yet.

This is an important interview point.

---

# 8. Maximum Pool Size

Suppose

```text
Core = 5

Max = 10
```

Queue becomes full.

Now

Task101 arrives.

Executor creates

```text
Thread6
```

Next task

↓

Thread7

Until

```text
Thread10
```

Only after the queue is full do additional threads get created.

---

# 9. Thread Creation Algorithm

This is one of the most frequently asked interview questions.

```text
New Task

	 │

	 ▼

Core Threads Available?

	 │

 Yes ─────────► Create Core Thread

	 │

 No

	 ▼

Queue Full?

	 │

 No ─────────► Add To Queue

	 │

 Yes

	 ▼

Maximum Threads Reached?

	 │

 No ─────────► Create Extra Thread

	 │

 Yes

	 ▼

Reject Task
```

Memorize this flow.

---

# 10. Worker Thread Lifecycle

Worker

↓

Take Task

↓

Execute

↓

Take Next Task

↓

Execute

↓

Repeat

Workers are **reused**.

That's why thread pools are efficient.

---

# 11. Keep Alive Time

Example

```java
keepAlive = 60 seconds
```

Suppose

Thread9

finished work.

If idle for

```text
60 seconds
```

Executor removes it.

Core threads usually remain alive by default.

Extra threads are removed.

---

# 12. Queue Types

One of the highest-value interview topics.

## 1. LinkedBlockingQueue

```text
Task1

Task2

Task3

Task4
```

Characteristics

* Large (often effectively unbounded by default)
* Good throughput
* Can lead to unbounded queue growth if producers outpace consumers

---

## 2. ArrayBlockingQueue

Fixed size.

```text
100 Capacity

↓

Full

↓

Reject
```

Predictable memory usage.

Common in production systems.

---

## 3. SynchronousQueue

No storage.

Task

↓

Direct handoff

↓

Worker

No waiting.

Used by

```java
Executors.newCachedThreadPool()
```

---

# 13. Executors Factory Methods

### Fixed Thread Pool

```java
Executors.newFixedThreadPool(10)
```

Internally

```text
Core = 10

Max = 10

Queue = LinkedBlockingQueue
```

Good for stable workloads.

---

### Cached Thread Pool

```java
Executors.newCachedThreadPool()
```

Internally

```text
Core = 0

Max = Integer.MAX_VALUE

Queue = SynchronousQueue
```

Can create many threads.

Useful for short-lived asynchronous tasks but risky if task submission is uncontrolled.

---

### Single Thread Executor

```java
Executors.newSingleThreadExecutor()
```

Only one worker.

Tasks execute sequentially.

---

# 14. Rejection Policies

Suppose

Everything is full.

What happens?

The executor invokes a `RejectedExecutionHandler`.

---

## AbortPolicy

Default.

Throws

```text
RejectedExecutionException
```

---

## CallerRunsPolicy

```text
Application Thread

↓

Runs Task
```

Acts as natural back-pressure because the submitting thread becomes busy.

---

## DiscardPolicy

Silently ignores task.

Dangerous.

---

## DiscardOldestPolicy

Remove oldest queued task.

Insert newest.

Useful only for specific workloads.

---

# 15. CPU-bound vs IO-bound Thread Pools

### CPU-bound

Examples

* Encryption
* Image Processing
* JSON Parsing

Recommended size

```text
Number of CPU cores
or
CPU cores + 1
```

Reason

Extra threads mostly increase context switching.

---

### IO-bound

Examples

* Database
* HTTP Calls
* Kafka
* Redis

Since threads spend time waiting,

you can use more threads than CPU cores.

A common starting point is to size the pool based on expected wait time vs compute time, then measure and tune under production-like load rather than relying on a fixed formula.

---

# 16. Production Spring Boot Example

```java
@Configuration
public class ExecutorConfig {

    @Bean
    public ThreadPoolTaskExecutor orderExecutor() {

	   ThreadPoolTaskExecutor executor =
			 new ThreadPoolTaskExecutor();

	   executor.setCorePoolSize(10);
	   executor.setMaxPoolSize(30);
	   executor.setQueueCapacity(200);
	   executor.setThreadNamePrefix("order-");

	   executor.initialize();

	   return executor;
    }

}
```

Then

```java
@Async("orderExecutor")
public void processOrder() {

}
```

This is a much better practice than relying on Spring Boot's default executor for every asynchronous task.

---

# 17. Production Debugging Story

Problem

API latency suddenly increased.

Metrics

```text
CPU = 30%

Memory = OK

DB = OK
```

Yet requests waited 20 seconds.

Investigation

```text
Thread Pool

Queue Size

↓

10000
```

Root Cause

```text
Core = 5

Queue = 10000

Max = 10
```

Since the queue was huge,

the executor never created additional threads.

Everything waited in the queue.

Fix

```text
Queue

↓

200

Core

↓

20

Max

↓

50
```

Latency dropped significantly.

---

# 18. Common Interview Traps

### Is a larger thread pool always better?

❌ No.

Too many threads increase context switching, memory usage, and scheduler overhead.

---

### Does FixedThreadPool create all threads immediately?

❌ No.

Threads are created lazily as tasks arrive, up to the core pool size.

---

### Why shouldn't I always use CachedThreadPool?

Because it can create a very large number of threads if tasks arrive faster than they complete, potentially exhausting system resources.

---

### Why is a huge queue dangerous?

It can hide overload by letting requests pile up, increasing latency and memory usage instead of applying back-pressure.

---

# 19. Senior-Level Follow-up Questions

1. Explain the task execution algorithm.
2. When does the executor create new threads?
3. Why use `SynchronousQueue`?
4. Why is `LinkedBlockingQueue` risky in production?
5. How does `keepAliveTime` work?
6. Which rejection policy would you choose for a payment system?
7. How would you size a thread pool?
8. Why can a large queue hurt latency?
9. How do you monitor a thread pool in production?
10. Why does Spring recommend custom executors for different workloads?

---

# 20. Cheat Sheet

| Parameter                  | Purpose                        |
| -------------------------- | ------------------------------ |
| `corePoolSize`             | Permanent worker threads       |
| `maximumPoolSize`          | Maximum workers allowed        |
| `keepAliveTime`            | Idle timeout for extra threads |
| `workQueue`                | Stores waiting tasks           |
| `ThreadFactory`            | Creates worker threads         |
| `RejectedExecutionHandler` | Handles overload               |

---

## Decision Tree

```text
Task Submitted

↓

Core Thread Available?

↓

YES → Execute

↓

NO

↓

Queue Full?

↓

NO → Queue Task

↓

YES

↓

Max Threads Reached?

↓

NO → Create New Thread

↓

YES

↓

Reject Task
```

---

# 🎯 Real Interview Scenario

**Interviewer:**

> "Our Spring Boot application becomes slow every evening. CPU is only 40%, but requests take 15 seconds. Where would you look?"

### Strong Answer

> I'd first inspect the application's thread pools. I'd check the active thread count, queue size, completed task count, and rejection metrics. A very large work queue can cause tasks to wait a long time even when the CPU isn't saturated. I'd also verify whether the pool size is appropriate for the workload (CPU-bound vs I/O-bound) and whether long-running tasks are blocking worker threads.

This answer demonstrates that you think in terms of **diagnosis, measurement, and tuning**, which is exactly what interviewers expect from a senior backend engineer.

---

## ⭐ Chapter Rating

If you master this chapter, you'll be able to answer a significant portion of thread pool questions asked in senior Java interviews.

---

### Next Chapter

**Chapter 23 - CompletableFuture: The Complete Interview Guide**

We'll cover:

* Why `Future` is limited
* `CompletableFuture` internals
* Chaining vs composition
* `thenApply`, `thenCompose`, `thenCombine`
* Exception handling
* Parallel API aggregation
* Spring Boot integration
* Performance pitfalls
* Real microservice use cases
* Senior interview scenarios

This is another must-know topic for modern Java backend development.
