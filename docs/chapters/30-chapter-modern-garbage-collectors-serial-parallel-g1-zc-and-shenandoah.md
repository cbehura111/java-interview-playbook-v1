# Part VI – JVM Memory Management & Garbage Collection

# Chapter 30: Modern Garbage Collectors (Serial, Parallel, G1, ZGC & Shenandoah)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Visa, Uber, Atlassian, JVM Performance Interviews

---

# 1. Why Do Interviewers Ask This?

Most senior Java interviews eventually include questions like:

* Which GC are you using?
* Why G1 instead of Parallel GC?
* When should you use ZGC?
* How does Shenandoah differ from G1?
* How do you choose a garbage collector?

The interviewer wants to know whether you understand **real production JVM tuning**, not just Java syntax.

Typical interview question:

> **Which Garbage Collector would you choose for a Java 21 Spring Boot application and why?**

---

# 2. 30-Second Interview Answer

> Modern JVMs provide multiple garbage collectors optimized for different workloads. Parallel GC maximizes throughput, G1 GC balances throughput with predictable pause times and is the default in modern JDKs, while ZGC and Shenandoah focus on extremely low pause times for very large heaps. The right choice depends on the application's latency, throughput, heap size, and SLA requirements.

---

# 3. Evolution of Java Garbage Collectors

```text
Serial GC

↓

Parallel GC

↓

CMS

↓

G1 GC

↓

ZGC

↓

Shenandoah
```

Every new collector aimed to reduce pause times while maintaining throughput.

---

# 4. Serial GC

Architecture

```text
Application

↓

Stop The World

↓

Single GC Thread

↓

Resume
```

Characteristics

* Single-threaded
* Simple implementation
* Long pauses
* Suitable for small applications

---

## When to Use

* Small desktop applications
* Embedded environments
* Small heaps

Not recommended for modern backend servers.

---

# 5. Parallel GC

Architecture

```text
Stop The World

↓

GC Thread1

GC Thread2

GC Thread3

GC Thread4
```

Instead of one GC thread,

multiple threads collect simultaneously.

---

## Goal

Maximize

```text
Throughput
```

Not

```text
Lowest Pause Time
```

---

## Best For

* Batch processing
* Analytics
* Scientific computation

---

# 6. CMS (Concurrent Mark Sweep)

Historical collector.

Purpose

Reduce application pauses.

Flow

```text
Initial Mark

↓

Concurrent Mark

↓

Remark

↓

Concurrent Sweep
```

Problem

Memory fragmentation.

CMS was deprecated and later removed in favour of newer collectors such as G1.

---

# 7. G1 GC (Garbage First)

Most important interview topic.

G1 is the default garbage collector in modern Java releases.

---

## Traditional Heap

```text
Young

↓

Old
```

---

## G1 Heap

Instead of generations only,

Heap becomes

```text
Region1

Region2

Region3

Region4

...

RegionN
```

Small equal-sized regions.

---

# 8. Why Regions?

Instead of collecting

Entire Young Generation

or

Entire Old Generation

G1 collects

Only

```text
Highest Garbage Regions
```

Hence

Garbage

First

---

# 9. G1 Collection

```text
Heap

□□□□□□□□□□□□□□□□

Collect

■■

Only

```

Much smaller pause.

---

# 10. Concurrent Marking

Instead of stopping everything

```text
Application Running

↓

Concurrent Mark

↓

Application Continues
```

G1 performs much of its work concurrently.

Only some phases require stop-the-world pauses.

---

# 11. Pause Time Goal

One of G1's biggest advantages.

Example

```text
Target

200 ms
```

Configuration

```text
-XX:MaxGCPauseMillis=200
```

This is a **goal**, not a strict guarantee.

---

# 12. ZGC

One of Java's newest collectors.

Primary goal

```text
Ultra Low Latency
```

Pause times are typically designed to remain very low, even with large heaps, though exact pauses depend on workload and hardware.

---

## Architecture

```text
Application Running

↓

GC Running

↓

Application Continues
```

Most work happens concurrently.

---

## Best For

* Trading systems
* Banking
* Large APIs
* Large heaps
* Latency-sensitive services

---

# 13. Shenandoah

Very similar objective.

Focus

```text
Low Pause

Large Heap
```

Like ZGC,

most work happens concurrently.

---

# 14. G1 vs ZGC vs Shenandoah

| Feature                    | G1        | ZGC       | Shenandoah |
| -------------------------- | --------- | --------- | ---------- |
| Default GC                 | ✅         | ❌         | ❌          |
| Throughput                 | High      | Good      | Good       |
| Low Pause                  | Good      | Excellent | Excellent  |
| Large Heap                 | Good      | Excellent | Excellent  |
| Mature Enterprise Adoption | Excellent | Growing   | Growing    |

---

# 15. Stop-The-World (STW)

Interview favourite.

During STW

```text
Application Threads

↓

Paused
```

GC performs critical work.

Every collector has some STW phases.

The difference is

How long?

---

# 16. Throughput vs Latency

Throughput

```text
Maximum Work Completed
```

Latency

```text
Fast Response Time
```

Interview Tip

A collector optimized for throughput isn't necessarily best for latency-sensitive systems.

---

# 17. Choosing a Collector

### Small Application

```text
Serial GC
```

---

### Batch Jobs

```text
Parallel GC
```

---

### Typical Spring Boot Application

```text
G1 GC
```

---

### Large Financial Platform

```text
ZGC
```

or

```text
Shenandoah
```

---

# 18. Production Example

Spring Boot

Heap

```text
16 GB
```

Requirement

```text
API <100 ms
```

Choice

```text
G1
```

If pause times become unacceptable even after tuning,

evaluate

```text
ZGC
```

---

# 19. Reading GC Logs

Typical log

```text
Pause Young (G1 Evacuation Pause)

25 ms
```

Good.

---

Another

```text
Full GC

12.5 s
```

Danger.

Investigate

* Heap sizing
* Memory leaks
* Allocation rate
* Collector tuning

---

# 20. Production Debugging Story

Problem

API latency

```text
15 Seconds
```

CPU

```text
25%
```

GC Logs

```text
Full GC

14 Seconds
```

Heap Dump

↓

Large cache

↓

Old Generation

95% Full

Fix

* Reduce retained objects.
* Tune heap sizes.
* Optimise cache policies.
* Evaluate a more suitable collector if necessary.

---

# 21. Common Interview Traps

### Is G1 always the fastest?

❌ No.

It balances throughput and pause times.

---

### Does ZGC eliminate all pauses?

❌ No.

It dramatically reduces pause times but still has brief stop-the-world phases.

---

### Is Parallel GC obsolete?

❌ No.

It remains an excellent choice for throughput-oriented workloads.

---

### Can changing the collector fix a memory leak?

❌ No.

A memory leak is an application problem.

Changing collectors may change symptoms but won't remove the leak.

---

### Is CMS still recommended?

❌ No.

It has been removed from modern JDKs.

---

# 22. Senior-Level Follow-up Questions

1. Why was CMS replaced?
2. Why is G1 called "Garbage First"?
3. Explain heap regions.
4. Why does G1 reduce pause times?
5. Difference between throughput and latency?
6. Why does ZGC scale well with large heaps?
7. How would you choose a collector?
8. How do you analyse GC logs?
9. What causes Full GC?
10. How would you investigate long GC pauses?

---

# 23. Real Interview Scenario

**Interviewer:**

> "Your Java 21 microservice has a 64 GB heap. Users complain about occasional multi-second pauses. Which collector would you consider?"

### Strong Answer

> I'd first analyse GC logs to confirm that garbage collection is the cause of the pauses. If the application is latency-sensitive and pause times remain unacceptable after tuning G1, I'd evaluate ZGC because it is designed to keep pause times very low on large heaps. I'd also verify allocation rates, object retention, and whether the heap is appropriately sized before changing collectors.

---

# 24. Cheat Sheet

| Collector   | Best For                             |
| ----------- | ------------------------------------ |
| Serial GC   | Small applications                   |
| Parallel GC | Maximum throughput                   |
| CMS         | Historical (removed)                 |
| G1 GC       | General-purpose server applications  |
| ZGC         | Very large heaps & ultra-low latency |
| Shenandoah  | Very low pause times                 |

---

## Selection Guide

```text
Small App
    ↓
 Serial GC

Batch Processing
    ↓
 Parallel GC

Spring Boot APIs
    ↓
 G1 GC

Large Heap + Low Latency
    ↓
 ZGC / Shenandoah
```

---

# 🎯 Interview Secret

When an interviewer asks:

> **"Which GC should we use?"**

Avoid giving a one-word answer like:

> "Use G1."

A senior-level answer is:

> "The choice depends on business requirements. If throughput is the priority, Parallel GC may be appropriate. For most server applications, G1 is a strong default because it balances throughput and pause times. If the application has very large heaps and strict latency SLAs, I'd evaluate ZGC or Shenandoah. Before switching collectors, I'd always analyse GC logs and profile the application because the collector isn't always the root cause of performance problems."

That demonstrates an understanding of **trade-offs, performance engineering, and production diagnostics** rather than memorising JVM options.

---

## Next Chapter

**Chapter 31 – JVM Memory Leaks, OutOfMemoryError & Heap Dump Analysis**

We'll cover:

* Why Java can still have memory leaks
* Different types of `OutOfMemoryError`
* Heap dump generation
* Eclipse MAT
* VisualVM
* Dominator Tree
* Retained Heap
* ClassLoader leaks
* ThreadLocal leaks
* Static collection leaks
* Production troubleshooting workflow

This is one of the most practical and frequently discussed JVM topics in senior backend interviews because it directly reflects real-world production debugging experience.
