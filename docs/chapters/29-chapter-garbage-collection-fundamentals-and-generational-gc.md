# Part VI – JVM Memory Management & Garbage Collection

# Chapter 29: Garbage Collection Fundamentals & Generational GC (The Foundation of JVM Memory Management)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Visa, Walmart, Adobe, Atlassian

---

# 1. Why Do Interviewers Ask This?

Garbage Collection (GC) is one of the most frequently discussed JVM topics in senior Java interviews.

The interviewer wants to evaluate whether you understand:

* How the JVM reclaims memory
* Why memory leaks still occur in Java
* Object lifecycle
* Young vs Old Generation
* Minor, Major, and Full GC
* Object promotion
* Performance implications

Typical interview question:

> **Explain how Garbage Collection works in Java.**

---

# 2. 30-Second Interview Answer

> Java uses Garbage Collection (GC) to automatically reclaim memory occupied by objects that are no longer reachable. The JVM identifies live objects starting from GC Roots using reachability analysis. Most new objects are allocated in the Young Generation and reclaimed during Minor GC. Objects that survive multiple collections are promoted to the Old Generation, where they are collected less frequently because they are expected to live longer.

---

# 3. Why Do We Need Garbage Collection?

Imagine writing:

```java
Employee emp = new Employee();
```

After the method finishes:

```java
emp = null;
```

Who frees the memory?

Without GC:

```text
Application

↓

Create Objects

↓

Memory Keeps Growing

↓

Out Of Memory
```

GC automatically removes unused objects.

---

# 4. What is Garbage?

Garbage means:

> **Objects that are no longer reachable by the application.**

Example

```java
Employee e = new Employee();

e = null;
```

Now

```text
Employee Object

❌ No References
```

Eligible for garbage collection.

---

# 5. Reachability Analysis

Modern JVMs do **not** simply count references.

Instead, they perform **reachability analysis**.

```text
GC Roots

↓

Follow References

↓

Reachable Objects

↓

Live Objects
```

Anything **not reachable** is eligible for collection.

---

# 6. What Are GC Roots?

GC starts from a set of well-known root references.

Common GC Roots include:

* Local variables in stack frames
* Active thread references
* Static fields
* JNI references

Example

```text
Stack Variable

↓

Employee

↓

Address

↓

City
```

All remain reachable.

---

# 7. Generational Hypothesis

One of the most important JVM concepts.

Observation:

> **Most objects die young.**

Examples

* DTOs
* Request objects
* JSON objects
* Temporary Strings

Therefore,

the JVM separates memory into generations.

---

# 8. Heap Structure

```text
                 Heap

────────────────────────────────────

Young Generation

   Eden

 Survivor S0

 Survivor S1

────────────────────────────────────

Old Generation
```

Most new objects begin in **Eden**.

---

# 9. Object Lifecycle

```text
new Object()

↓

Eden

↓

Minor GC

↓

Survivor

↓

Minor GC

↓

Survivor

↓

Promotion

↓

Old Generation
```

Objects that survive several young collections are promoted to the Old Generation.

---

# 10. Minor GC

Occurs when:

```text
Eden

██████████

Full
```

Process

```text
Minor GC

↓

Dead Objects Removed

↓

Live Objects

↓

Survivor Space
```

Minor GCs are usually frequent and relatively fast.

---

# 11. Survivor Spaces

There are two survivor spaces.

```text
Eden

↓

S0

↓

S1

↓

Old Generation
```

Objects move between survivor spaces across collections before promotion.

---

# 12. Object Promotion

Suppose

```text
Object

↓

Minor GC

↓

Survives

↓

Minor GC

↓

Survives

↓

Promoted
```

Eventually

```text
Old Generation
```

Promotion depends on JVM heuristics and collector configuration.

---

# 13. Major GC

Targets

```text
Old Generation
```

Characteristics

* Less frequent
* More expensive
* Longer pause times (collector dependent)

---

# 14. Full GC

Interview Favourite.

Full GC generally involves collecting the entire heap and may also reclaim other JVM-managed memory such as class metadata depending on the collector and JVM implementation.

It is usually the most expensive type of collection.

---

# 15. Minor vs Major vs Full GC

| Feature          | Minor GC | Major GC | Full GC |
| ---------------- | -------- | -------- | ------- |
| Young Generation | ✅        | ❌        | ✅       |
| Old Generation   | ❌        | ✅        | ✅       |
| Usually Fast     | ✅        | ❌        | ❌       |
| Frequent         | ✅        | ❌        | ❌       |

---

# 16. Weak References

```java
WeakReference<Employee> ref =
        new WeakReference<>(employee);
```

If only a weak reference remains,

the object is eligible for collection during the next GC.

Typical use:

* WeakHashMap
* Certain cache implementations

---

# 17. Soft References

```java
SoftReference<Image> image =
        new SoftReference<>(obj);
```

Softly reachable objects may remain available until the JVM needs memory.

Useful for memory-sensitive caches.

---

# 18. Phantom References

Rare interview topic.

Used for:

* Advanced resource cleanup
* Tracking object reclamation
* Integration with `ReferenceQueue`

Not used to access the object itself.

---

# 19. System.gc()

Interview Trap.

```java
System.gc();
```

Does this force GC?

**No.**

It is only a request to the JVM.

The JVM is free to ignore it or schedule collection later.

---

# 20. Production Example

REST API

1000 requests/sec

Each request creates

```text
DTO

Response

JSON

Validation Objects
```

Most die within milliseconds.

They are reclaimed during Minor GC.

---

# 21. Common Interview Traps

### Does GC immediately remove an unreachable object?

❌ No.

The object becomes **eligible** for collection.

The JVM decides when to reclaim it.

---

### Does `null` immediately free memory?

❌ No.

It only removes one reference.

The object is collected later if it is no longer reachable.

---

### Can Java have memory leaks?

✅ Yes.

Example:

```java
static List<Object> cache =
        new ArrayList<>();
```

If objects remain referenced indefinitely,

GC cannot reclaim them.

---

### Does Full GC always mean the application has a memory leak?

❌ No.

Frequent Full GCs may indicate memory pressure, poor tuning, allocation patterns, or a leak. Investigation is required before drawing conclusions.

---

# 22. Production Debugging Story

Problem

Application pauses every few minutes.

Logs

```text
Full GC

12 Seconds
```

Investigation

Heap Dump

↓

Large

```text
HashMap
```

holding millions of unused objects.

Root Cause

Application cache grew without bounds.

Fix

* Introduce eviction policies.
* Limit cache size.
* Monitor memory usage.

---

# 23. Senior-Level Follow-up Questions

1. Explain Garbage Collection.
2. What is the Generational Hypothesis?
3. What are GC Roots?
4. Explain Reachability Analysis.
5. Difference between Minor and Major GC?
6. What triggers object promotion?
7. Difference between Soft and Weak References?
8. Does `System.gc()` force GC?
9. Why do Java memory leaks still happen?
10. How would you investigate frequent Full GCs?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Your application throws `OutOfMemoryError`, but Garbage Collection is running frequently. How is that possible?"

### Strong Answer

> Frequent GC doesn't necessarily mean memory can be reclaimed. If objects are still strongly reachable—for example, because of an unbounded cache, a static collection, or a class loader leak—the garbage collector cannot free them. I'd analyse GC logs and inspect a heap dump with tools like Eclipse MAT or VisualVM to identify the dominant retained objects and reference chains.

---

# 25. Cheat Sheet

| Concept         | Key Point                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Garbage         | Unreachable object                                                                             |
| GC Roots        | Starting points for reachability analysis                                                      |
| Eden            | Initial allocation area                                                                        |
| Survivor Spaces | Temporary holding area for surviving objects                                                   |
| Old Generation  | Long-lived objects                                                                             |
| Minor GC        | Collects Young Generation                                                                      |
| Major GC        | Collects Old Generation                                                                        |
| Full GC         | Collects the entire heap (and may reclaim other JVM-managed memory depending on the collector) |
| Weak Reference  | Collected eagerly once only weakly reachable                                                   |
| Soft Reference  | Retained longer under memory pressure                                                          |

---

## Object Lifecycle

```text
new Object()

↓

Eden

↓

Minor GC

↓

Survivor

↓

Promotion

↓

Old Generation

↓

Major / Full GC
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why is Java Garbage Collection efficient?"**

A senior-level answer is:

> "The JVM is based on the Generational Hypothesis that most objects die young. By focusing frequent collections on the Young Generation, where short-lived objects are created, the JVM avoids repeatedly scanning long-lived objects in the Old Generation. This significantly reduces GC overhead for typical enterprise applications."

That answer demonstrates an understanding of **JVM design decisions**, not just terminology.

---

## Next Chapter

**Chapter 30 – Modern Garbage Collectors (Serial, Parallel, G1, ZGC & Shenandoah)**

We'll cover:

* Serial GC
* Parallel GC
* CMS (historical context)
* G1 GC internals
* ZGC
* Shenandoah
* Region-based collection
* Concurrent marking
* Pause-time goals
* Collector selection strategies
* Production tuning
* GC log interpretation
* Senior interview scenarios

This is one of the highest-value JVM topics for senior backend interviews, especially for Java 17 and Java 21 roles.
