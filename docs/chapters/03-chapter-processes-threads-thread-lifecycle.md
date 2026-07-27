# Java Backend Engineering Interview Handbook

## Volume 1 - Java Core & Concurrency

# Chapter 3 - Processes, Threads & Thread Lifecycle

> **"A thread is the unit of execution. Understanding how threads are created, scheduled, paused, blocked, and terminated is essential for writing efficient and correct concurrent applications."**

---

# Learning Objectives

By the end of this chapter, you will understand:

* What is a Process?
* What is a Thread?
* Why Threads are lightweight
* Java Thread Lifecycle
* Thread States
* Context Switching
* Thread Scheduling
* Thread Priorities
* Daemon Threads
* Common Interview Questions

---

# 3.1 What is a Process?

A **Process** is an independent program running in the operating system.

Examples:

* Chrome Browser
* IntelliJ IDEA
* PostgreSQL
* Java Application
* VS Code

Every process has its own:

* Memory
* Heap
* Stack
* File descriptors
* Security Context
* Process ID (PID)

Processes cannot directly access each other's memory.

```text
Operating System

 ├── Chrome (Process)
 │      Heap
 │      Threads
 │
 ├── PostgreSQL (Process)
 │      Heap
 │      Threads
 │
 └── Java Application (Process)
		Heap
		Threads
```

---

# 3.2 What is a Thread?

A **Thread** is the smallest unit of execution inside a process.

A Java application starts with one thread:

```text
main()
```

As the application grows, more threads are created.

Example:

```text
Java Process

	Main Thread

		|

 ┌──────┼────────┐

Worker  DB     Kafka

Thread Thread Thread
```

Each thread performs different work simultaneously.

---

# 3.3 Why Use Threads?

Imagine a Spring Boot application.

One user:

* Login

Another user:

* Fund Transfer

Another user:

* Download Statement

Another user:

* Upload CSV

Without threads...

Every request waits.

```text
User1

↓

User2

↓

User3

↓

User4
```

Total response time becomes huge.

With threads:

```text
User1 ──► Thread-1

User2 ──► Thread-2

User3 ──► Thread-3

User4 ──► Thread-4
```

Requests execute concurrently.

---

# 3.4 Process vs Thread

| Process                  | Thread                          |
| ------------------------ | ------------------------------- |
| Independent program      | Execution unit                  |
| Own memory               | Shares process memory           |
| Heavyweight              | Lightweight                     |
| Slow creation            | Fast creation                   |
| High context switch cost | Low context switch cost         |
| Communication via IPC    | Communication via shared memory |

---

# 3.5 What Resources are Shared?

All threads share:

* Heap
* Objects
* Static Variables
* Database Connections
* Connection Pools
* Files

Each thread has its own:

* Stack
* Program Counter
* Local Variables
* Execution State

Example:

```java
class Bank {

	static int interest = 7;

	Account account = new Account();
}
```

Both Thread-A and Thread-B share:

* interest
* account

But local variables remain private.

```java
public void transfer() {

	int amount = 100;

}
```

Every thread gets its own `amount`.

---

# 3.6 Java Thread Lifecycle

A thread moves through several states.

```text
NEW

↓

RUNNABLE

↓

RUNNING

↓

BLOCKED

↓

WAITING

↓

TIMED_WAITING

↓

RUNNABLE

↓

TERMINATED
```

Let's understand each.

---

# 3.7 NEW

```java
Thread t = new Thread();
```

The thread object exists.

OS thread is not yet created.

State:

```text
NEW
```

---

# 3.8 RUNNABLE

```java
t.start();
```

Now JVM asks OS to schedule it.

The thread is ready.

It may or may not immediately execute.

State:

```text
RUNNABLE
```

---

# 3.9 RUNNING

Java doesn't expose RUNNING separately.

Internally:

Runnable

↓

CPU picks thread

↓

Running

The thread is actively executing instructions.

---

# 3.10 BLOCKED

Suppose:

```java
synchronized(account){

}
```

Another thread already owns the lock.

Current thread waits.

State:

```text
BLOCKED
```

Waiting for monitor lock.

---

# 3.11 WAITING

Examples:

```java
thread.join();

object.wait();
```

The thread waits indefinitely.

Another thread must wake it.

---

# 3.12 TIMED_WAITING

Examples:

```java
Thread.sleep(5000);
```

or

```java
join(1000);
```

The thread waits for a specific duration.

---

# 3.13 TERMINATED

When:

```java
run()
```

finishes,

the thread dies.

State:

```text
TERMINATED
```

Cannot restart.

Calling

```java
thread.start();
```

again throws:

```text
IllegalThreadStateException
```

---

# 3.14 Thread State Diagram

```text
		   NEW

			|

		start()

			|

		RUNNABLE

			|

	  CPU Scheduler

			|

		 RUNNING

	  /      |      \

sleep()   wait() synchronized

 |          |          |

Timed    Waiting   Blocked

Waiting

	  \      |      /

		Runnable

		   |

	  run() Ends

		   |

	 TERMINATED
```

---

# 3.15 Context Switching

Suppose we have:

Thread-A

Thread-B

One CPU.

CPU executes:

```text
A

↓

B

↓

A

↓

B

↓

A
```

This switching is called

**Context Switching**.

During switching, OS saves:

* Registers
* Stack Pointer
* Program Counter

and restores another thread.

---

# 3.16 Why Too Many Threads Hurt Performance

Suppose:

CPU Cores = 8

Threads = 20,000

CPU spends more time switching than executing.

Result:

* High CPU usage
* Poor throughput
* Increased latency
* Memory pressure
* Reduced scalability

This is why modern applications prefer thread pools over creating a new thread per request.

---

# 3.17 Thread Priorities

Java supports priorities:

```java
Thread.MIN_PRIORITY
```

```java
1
```

Default:

```java
5
```

Highest:

```java
10
```

Example:

```java
Thread t=new Thread();

t.setPriority(10);
```

However,

modern operating systems generally treat priorities as hints rather than strict guarantees.

Do not rely on thread priority for application correctness.

---

# 3.18 Daemon Threads

Some threads perform background work.

Examples:

* Garbage Collector
* Scheduler
* Monitoring

Example:

```java
Thread t=new Thread();

t.setDaemon(true);
```

Daemon threads automatically stop when all user threads have finished.

---

# 3.19 Real Spring Boot Example

Incoming request:

```text
Client

↓

Tomcat Thread Pool

↓

Controller

↓

Service

↓

Repository

↓

Database
```

Every HTTP request is processed by a thread borrowed from the server's thread pool. Once the response is sent, the thread returns to the pool for reuse instead of being destroyed.

---

# 3.20 Common Interview Questions

### Q1. Difference between Process and Thread?

A process is an independent execution environment with its own memory. A thread is a lightweight execution unit within a process that shares the process's resources.

---

### Q2. Can we restart a thread?

No.

A thread can be started only once.

---

### Q3. Difference between `start()` and `run()`?

```java
thread.start();
```

Creates a new thread and executes `run()` asynchronously.

```java
thread.run();
```

Is just a normal method call executed on the current thread.

---

### Q4. Why are threads called lightweight?

Because they share the process's memory and resources, making creation and context switching cheaper than processes.

---

### Q5. What is context switching?

It is the operating system saving the execution state of one thread and restoring another so multiple threads can share CPU time.

---

# Production Interview Scenario

**Interviewer:**

> "Our Spring Boot application suddenly has 15,000 active threads and CPU utilization is at 100%. How would you investigate?"

A strong answer would cover:

1. Capture a thread dump (`jstack` or JDK tools).
2. Check for blocked or waiting threads.
3. Review thread pool configurations (Tomcat, executors, async tasks).
4. Identify thread leaks or excessive thread creation.
5. Analyze CPU hotspots with Java Flight Recorder (JFR) or async-profiler.
6. Replace unbounded thread creation with appropriately sized thread pools and tune based on workload.

---

# Chapter Summary

* A process is an isolated program; a thread is a lightweight execution unit within it.
* Threads share heap memory but maintain their own stacks and execution state.
* Java threads transition through well-defined lifecycle states.
* Excessive threads lead to costly context switching and degraded performance.
* Thread pools are the preferred approach for scalable server applications.

---

# Next Chapter

## Chapter 4 - Heap, Stack & CPU Cache

This chapter will answer questions such as:

* Where are objects stored?
* Why are local variables thread-safe?
* Why do shared objects require synchronization?
* How do heap, stack, registers, and CPU caches interact?
* How do these concepts relate to the Java Memory Model and concurrency bugs?

This chapter forms the bridge between thread fundamentals and the synchronization mechanisms (`synchronized`, `volatile`, and locks) covered next.
