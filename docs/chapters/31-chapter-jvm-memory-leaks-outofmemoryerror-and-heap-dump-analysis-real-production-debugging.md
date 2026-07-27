# Part VI – JVM Memory Management & Garbage Collection

# Chapter 31: JVM Memory Leaks, OutOfMemoryError & Heap Dump Analysis (Real Production Debugging)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Visa, Adobe, Atlassian, JVM Performance Interviews

---

# 1. Why Do Interviewers Ask This?

This chapter separates **developers** from **production engineers**.

Almost every senior Java interview includes a question like:

* Have you investigated an OutOfMemoryError?
* How do you analyse a heap dump?
* Can Java have memory leaks?
* What tools have you used?
* What is a ThreadLocal leak?

Typical Interview Question:

> **Java has Garbage Collection. Why do memory leaks still happen?**

---

# 2. 30-Second Interview Answer

> Java can still suffer from memory leaks because the garbage collector only removes unreachable objects. If objects remain strongly referenced—such as through static collections, caches, ThreadLocals, or class loader leaks—the GC considers them live and cannot reclaim their memory. I typically investigate using GC logs, heap dumps, and tools such as Eclipse MAT or VisualVM.

---

# 3. Memory Leak vs OutOfMemoryError

Interview Trap.

Many developers think:

```text
Memory Leak

=

OutOfMemoryError
```

Wrong.

A memory leak

↓

May eventually cause

↓

OutOfMemoryError

But they are different.

---

# 4. What is a Memory Leak?

Definition

> Memory that is **no longer useful** but is still **reachable**.

Example

```java
static List<Employee> employees =
        new ArrayList<>();
```

Every request

```java
employees.add(employee);
```

Never removed.

GC sees

```text
Static Reference

↓

Employee Objects
```

Objects remain alive forever.

---

# 5. Types of OutOfMemoryError

Common interview topic.

### Java Heap Space

```text
OutOfMemoryError:

Java heap space
```

Cause

Heap exhausted.

---

### Metaspace

```text
OutOfMemoryError:

Metaspace
```

Cause

Too many loaded classes

or

ClassLoader leak.

---

### GC Overhead Limit Exceeded

```text
98% GC

2% Progress
```

JVM spends almost all its time collecting garbage but recovers very little memory.

---

### Unable to Create Native Thread

```text
OutOfMemoryError

Unable to create native thread
```

Usually caused by:

* Too many platform threads
* OS limits
* Native memory exhaustion

---

### Direct Buffer Memory

```text
OutOfMemoryError:

Direct buffer memory
```

Often related to

* Netty
* NIO
* ByteBuffer.allocateDirect()

---

# 6. Heap Dump

Heap Dump

↓

Snapshot

↓

Entire Heap

Contains

* Every object
* References
* Class information
* Memory usage

---

# 7. Creating Heap Dumps

Automatically

```text
-XX:+HeapDumpOnOutOfMemoryError
```

Location

```text
-XX:HeapDumpPath=/tmp
```

Production Best Practice

Always enable heap dumps for production JVMs where storage policies allow it.

---

# 8. VisualVM

Useful for

* Heap usage
* Threads
* CPU
* Heap dumps
* Monitoring

Good first investigation tool.

---

# 9. Eclipse Memory Analyzer (MAT)

Industry standard.

Capabilities

* Dominator Tree
* Leak Suspects
* Histogram
* Retained Heap
* Reference Chains

Interviewers like hearing:

> Eclipse MAT

---

# 10. Dominator Tree

One of the favourite interview topics.

Suppose

```text
Cache

↓

Orders

↓

Items

↓

Addresses
```

If Cache disappears

Everything below disappears.

Cache dominates.

Hence

Dominator Tree.

---

# 11. Retained Heap

Interview Question

Difference between

Shallow Heap

and

Retained Heap?

---

Shallow Heap

Memory

of object itself.

---

Retained Heap

Memory

freed

if object disappears.

Example

```text
Cache

↓

1 Million Objects
```

Shallow Heap

```text
32 Bytes
```

Retained Heap

```text
800 MB
```

Huge difference.

---

# 12. Histogram

MAT can show

```text
Employee

5 Million Objects

String

12 Million Objects

HashMap

600000 Objects
```

Useful to identify excessive object creation.

---

# 13. ThreadLocal Leak

Interview favourite.

Example

```java
ThreadLocal<User> context =
        new ThreadLocal<>();
```

Store value

Never remove

```java
context.set(user);
```

No

```java
context.remove();
```

Thread pool reuses the thread.

Old values remain associated with that thread.

---

Production Fix

```java
try {

    context.set(user);

} finally {

    context.remove();

}
```

---

# 14. Static Collection Leak

Very common.

```java
public class Cache {

    static List<Order> orders =
            new ArrayList<>();

}
```

Never cleared.

Heap grows continuously.

---

# 15. ClassLoader Leak

Mostly seen in

* Tomcat
* Application servers
* Plugin systems
* Hot deployment

Old class loaders remain referenced.

Result

```text
Metaspace

Keeps Growing
```

---

# 16. Listener Leak

Suppose

```java
button.addListener(listener);
```

Application forgets

```java
removeListener()
```

Listener remains referenced.

Object never collected.

---

# 17. Cache Leak

Example

```java
Map<String,Object> cache =
        new HashMap<>();
```

Never evicted.

Heap grows.

Production

Prefer

* Caffeine
* Guava Cache
* Redis

with eviction policies.

---

# 18. Production Investigation Workflow

```text
OOM

↓

GC Logs

↓

Heap Dump

↓

MAT

↓

Largest Objects

↓

Reference Chain

↓

Root Cause

↓

Fix
```

This workflow is worth memorising.

---

# 19. Production Debugging Story

Problem

Spring Boot API

Restarted every

```text
48 Hours
```

Heap

```text
95%
```

Heap Dump

↓

MAT

↓

Dominator Tree

↓

Static HashMap

↓

Millions of Orders

Root Cause

Cache never evicted.

Fix

Migrated to

Caffeine

with size-based eviction.

---

# 20. Common Interview Traps

### Can Java have memory leaks?

✅ Yes.

GC only removes unreachable objects.

---

### Does calling `System.gc()` fix a leak?

❌ No.

If objects are still reachable,

GC cannot reclaim them.

---

### Is Heap Dump enough?

❌ No.

You must analyse

* Reference chains
* Dominator Tree
* Retained Heap

---

### Is every large object a leak?

❌ No.

Some objects are legitimately large.

Investigate whether they should still be retained.

---

# 21. Senior-Level Follow-up Questions

1. Explain memory leaks in Java.
2. Difference between leak and OOM?
3. Explain Dominator Tree.
4. Difference between Shallow and Retained Heap?
5. How do ThreadLocal leaks happen?
6. Explain ClassLoader leaks.
7. What causes Metaspace OOM?
8. How do you investigate production OOM?
9. Which tools do you use?
10. How do you read a heap dump?

---

# 22. Real Interview Scenario

**Interviewer:**

> "A Spring Boot application crashes every three days with `OutOfMemoryError: Java heap space`. How would you investigate it?"

### Strong Answer

> I'd first confirm the error type and review GC logs to understand allocation behaviour. If heap dumps are enabled, I'd open the dump in Eclipse MAT, inspect the Leak Suspects report, review the Dominator Tree and Histogram, and identify the objects with the largest retained heap. Then I'd follow the reference chain back to the GC Root to determine why those objects are still strongly reachable. Finally, I'd fix the underlying cause—for example, an unbounded cache, static collection, or ThreadLocal leak—and validate the fix under load.

---

# 23. Cheat Sheet

| Problem           | Typical Cause                              |
| ----------------- | ------------------------------------------ |
| Java Heap Space   | Heap exhausted                             |
| Metaspace OOM     | ClassLoader leak / excessive class loading |
| Native Thread OOM | Too many platform threads                  |
| Direct Buffer OOM | Off-heap buffer exhaustion                 |
| GC Overhead Limit | GC running constantly with little recovery |

---

## Investigation Flow

```text
OutOfMemoryError

↓

GC Logs

↓

Heap Dump

↓

Eclipse MAT

↓

Histogram

↓

Dominator Tree

↓

Retained Heap

↓

Reference Chain

↓

Root Cause
```

---

# 🎯 Interview Secret

When an interviewer asks:

> **"How do you investigate an OutOfMemoryError?"**

Don't answer:

> "I increase the heap."

A senior-level answer is:

> "Increasing the heap may only delay the problem. I'd first determine the type of OutOfMemoryError, analyse GC logs, capture a heap dump, inspect it using Eclipse MAT, identify the largest retained objects and their reference chains, and then fix the underlying cause. Only after understanding the application's memory behaviour would I consider tuning heap sizes."

This demonstrates **systematic production troubleshooting**, which is exactly what senior interviewers look for.

---

## Next Chapter

**Chapter 32 – JVM Performance Tuning & GC Tuning**

We'll cover:

* Heap sizing (`-Xms`, `-Xmx`)
* Young Generation tuning
* GC logging
* G1 tuning parameters
* ZGC tuning basics
* JFR (Java Flight Recorder)
* JMC (Java Mission Control)
* `jstat`, `jcmd`, `jmap`, `jstack`
* Performance tuning workflow
* Real production case studies

This chapter ties together everything you've learned about JVM memory, garbage collection, and production diagnostics into a practical performance engineering guide.
