# Introduction to Concurrency

---

## 1.1 Why Concurrency Matters

Imagine you have built an online banking application.

At **9:00 AM**, salary credits begin.

Suddenly,

* 2 million users log in.
* Balance enquiries increase.
* Fund transfers start.
* Statement downloads begin.
* UPI requests flood the system.

If your application processes one request at a time, every customer waits for the previous request to complete.

A single transfer taking **500 ms** would cause a million users to wait for days.

Modern applications therefore execute multiple tasks simultaneously using **concurrency**.

Concurrency enables applications to:

* Handle multiple users simultaneously.
* Improve responsiveness.
* Maximize CPU utilization.
* Increase throughput.
* Scale efficiently on multi-core processors.

Without concurrency, modern backend systems such as banking platforms, e-commerce websites, ride-sharing applications, or logistics systems would not be practical.

---

## 1.2 What Is Concurrency?

Concurrency is the ability of a program to make progress on multiple tasks during overlapping periods of time.

A key point is that concurrency does **not necessarily mean** that multiple tasks are executing at the exact same instant. On a single CPU core, the operating system rapidly switches between tasks, creating the illusion that they are running together.

For example, while one thread waits for a database query to complete, another thread can process a different user's request.

This improves overall responsiveness and resource utilization.

---

## 1.3 Concurrency vs Parallelism

These terms are often confused, but they describe different concepts.

| Concurrency                        | Parallelism                                        |
| ---------------------------------- | -------------------------------------------------- |
| Deals with managing multiple tasks | Deals with executing multiple tasks simultaneously |
| Can occur on a single CPU core     | Requires multiple CPU cores                        |
| Focuses on task coordination       | Focuses on simultaneous execution                  |
| Improves responsiveness            | Improves throughput                                |

### Example

Suppose a restaurant has one chef preparing three dishes.

The chef alternates between chopping vegetables, boiling pasta, and grilling vegetables. The dishes progress together even though only one task is active at a given instant. This is **concurrency**.

If three chefs prepare the three dishes at the same time, that is **parallelism**.

Backend servers use both. They coordinate thousands of requests concurrently, and on multi-core machines many of those requests also execute in parallel.

---

## 1.4 Process vs Thread

Understanding the difference between a process and a thread is fundamental.

### Process

A process is an independent program in execution with its own memory space and system resources.

Examples:

* Chrome browser
* IntelliJ IDEA
* PostgreSQL
* Java application

Each process has its own:

* Heap memory
* Native resources
* File descriptors
* Security context

Processes are isolated from each other.

---

### Thread

A thread is the smallest unit of execution within a process.

Threads share:

* Heap memory
* Open files
* Database connection pools
* Static variables

Each thread has its own:

* Program counter
* Stack
* Local variables

This shared-memory model makes communication efficient but introduces the possibility of race conditions if shared data is not protected.

---

## 1.5 Why Backend Engineers Need Concurrency

Every incoming HTTP request in a Spring Boot application is typically handled by a thread from a server-managed thread pool.

A single request may involve:

1. Authenticating the user.
2. Reading data from Redis.
3. Querying PostgreSQL.
4. Calling external services.
5. Publishing a Kafka event.
6. Returning a response.

Handling many such requests efficiently requires careful concurrency management to avoid bottlenecks, deadlocks, and inconsistent data.

---

## 1.6 Common Concurrency Problems

As systems become concurrent, several classes of bugs emerge:

* **Race conditions:** Multiple threads modify the same data unexpectedly.
* **Deadlocks:** Two or more threads wait indefinitely for each other.
* **Livelocks:** Threads remain active but make no useful progress.
* **Starvation:** Some threads never receive the resources they need.
* **Visibility issues:** One thread cannot observe another thread's updates because of caching or reordering.

These issues often appear only under load, making them difficult to reproduce and diagnose.

---

## 1.7 Learning Outcomes

By the end of this volume, you will be able to:

* Explain concurrency fundamentals clearly.
* Understand how the Java Memory Model governs visibility and ordering.
* Choose appropriate synchronization mechanisms.
* Use concurrent collections effectively.
* Design scalable multithreaded backend applications.
* Debug production concurrency issues with confidence.

---

## Chapter Summary

* Concurrency is about managing multiple tasks that make progress together.
* Parallelism is about executing tasks simultaneously.
* Processes are isolated execution environments.
* Threads share process resources and therefore require synchronization.
* Concurrency is essential for modern backend applications but introduces new correctness and performance challenges.

---

## Next Chapter

**Chapter 2 - Java Memory Model (JMM)**

In the next chapter, we'll explore one of the most important topics for senior Java interviews: how Java guarantees (and sometimes does not guarantee) visibility, ordering, and atomicity across threads. Understanding the JMM is the foundation for mastering `volatile`, `synchronized`, locks, and the concurrent utilities that follow.

---

### Handbook Progress

* ✅ Volume 1 structure defined
* ✅ Chapter 1: Introduction to Concurrency
* ⏳ Chapter 2: Java Memory Model (next)
* ⏳ PDF & Markdown generation after the next few completed chapters, so the first edition is substantial rather than just a single chapter.
