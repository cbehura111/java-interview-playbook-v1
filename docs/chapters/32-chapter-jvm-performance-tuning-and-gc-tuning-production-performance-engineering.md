# Part VI – JVM Memory Management & Garbage Collection

# Chapter 32: JVM Performance Tuning & GC Tuning (Production Performance Engineering)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, Visa, Atlassian, Uber, JVM Performance Interviews

---

# 1. Why Do Interviewers Ask This?

Most senior Java developers know GC concepts.

Senior engineers know **how to diagnose and tune JVM performance in production**.

Interviewers typically ask:

* How do you tune JVM performance?
* What JVM flags have you used?
* How do you analyse GC logs?
* Which JVM tools do you use?
* How do you investigate high CPU or memory usage?

This chapter focuses on **real-world production troubleshooting**, not memorising JVM options.

---

# 2. 30-Second Interview Answer

> JVM tuning starts with measuring, not guessing. I first identify whether the bottleneck is CPU, memory, GC, threads, or I/O. I analyse GC logs, thread dumps, heap dumps, and JFR recordings before changing JVM parameters. Heap size, garbage collector selection, and GC tuning should be based on application behaviour and performance goals rather than fixed recommendations.

---

# 3. JVM Performance Tuning Workflow

Never start with changing JVM flags.

Follow this workflow:

```text
Performance Problem

↓

Identify Symptoms

↓

Collect Metrics

↓

Analyse

↓

Find Root Cause

↓

Tune

↓

Measure Again
```

Performance tuning is an iterative process.

---

# 4. Common Performance Symptoms

| Symptom            | Possible Cause                               |
| ------------------ | -------------------------------------------- |
| High CPU           | Infinite loop, excessive computation, GC     |
| High Memory        | Memory leak, oversized cache                 |
| Long Response Time | Slow database, blocking I/O, Full GC         |
| Frequent GC        | High allocation rate, small heap             |
| Application Freeze | Full GC, deadlock, native issue              |
| OutOfMemoryError   | Leak, insufficient heap, excessive retention |

---

# 5. Heap Sizing

Most common JVM options:

```text
-Xms2g
-Xmx2g
```

Where:

* `-Xms` = Initial heap size
* `-Xmx` = Maximum heap size

Example:

```text
-Xms4g
-Xmx4g
```

This avoids heap resizing during runtime.

---

# 6. Should Xms Equal Xmx?

Interview Favourite.

Production recommendation:

For stable server applications,

```text
-Xms = Xmx
```

Benefits:

* Avoids heap expansion pauses
* More predictable performance
* Easier GC tuning

For development environments, smaller initial heaps are often acceptable.

---

# 7. GC Logging

Never tune GC blindly.

Enable logging.

Java 9+

```text
-Xlog:gc*
```

More detailed example:

```text
-Xlog:gc*:file=gc.log
```

GC logs reveal:

* Pause times
* Collection frequency
* Heap occupancy
* Promotion rates

---

# 8. Reading GC Logs

Example

```text
Pause Young (G1 Evacuation Pause)

28 ms
```

Interpretation:

* Minor GC
* Healthy pause
* Normal behaviour

---

Another example

```text
Full GC

15.6 s
```

Investigation required.

Possible causes:

* Memory leak
* Heap too small
* Poor allocation behaviour

---

# 9. G1 GC Tuning

Common parameter

```text
-XX:MaxGCPauseMillis=200
```

Meaning:

Target

```text
200 ms
```

Important:

This is a **pause-time goal**, not a guarantee.

---

Another useful parameter

```text
-XX:InitiatingHeapOccupancyPercent=45
```

Controls when concurrent marking begins.

Lower values may start marking earlier, depending on workload.

---

# 10. ZGC Tuning

Usually requires fewer tuning parameters than older collectors.

Typical configuration:

```text
-XX:+UseZGC
```

Large heaps often require little additional tuning beyond appropriate heap sizing.

---

# 11. Thread Dumps

Interview Favourite.

Generate using

```text
jstack <pid>
```

Contains

* Thread states
* Stack traces
* Locks
* Deadlocks

Useful for investigating:

* Hanging applications
* Deadlocks
* High CPU
* Blocked threads

---

# 12. jstat

Useful command

```text
jstat -gc <pid>
```

Shows:

* Heap usage
* Eden usage
* Survivor usage
* Old Generation usage
* GC count

Good for observing live GC activity.

---

# 13. jmap

Generate heap dump

```text
jmap -dump:live,file=heap.hprof <pid>
```

Analyse later using:

* Eclipse MAT
* VisualVM

---

# 14. jcmd

Modern JVM diagnostic tool.

Example

```text
jcmd <pid> VM.flags
```

Other useful commands:

```text
jcmd <pid> GC.heap_info
```

```text
jcmd <pid> Thread.print
```

```text
jcmd <pid> GC.class_histogram
```

`jcmd` is generally preferred over several older standalone tools because it provides many JVM diagnostic capabilities from a single command.

---

# 15. Java Flight Recorder (JFR)

One of the best production profiling tools.

Records:

* CPU usage
* GC
* Allocation
* Lock contention
* Thread activity
* I/O
* Exceptions

Very low runtime overhead.

---

# 16. Java Mission Control (JMC)

GUI for analysing

* JFR recordings
* CPU hotspots
* Allocation profiles
* GC activity
* Thread behaviour

Frequently used alongside JFR.

---

# 17. Performance Investigation Example

Problem

```text
API latency

8 Seconds
```

Workflow

```text
CPU

↓

Normal

↓

Thread Dump

↓

No Deadlock

↓

GC Logs

↓

Frequent Full GC

↓

Heap Dump

↓

Large Cache

↓

Root Cause
```

---

# 18. Production Tuning Case Study

Application

Spring Boot

Heap

```text
8 GB
```

Problem

```text
Full GC

Every Minute
```

Investigation

GC Logs

↓

Old Generation

98%

Heap Dump

↓

Static Cache

↓

Millions of Products

Fix

* Cache eviction
* Reduced retention
* Appropriate heap sizing

Result

```text
Minor GC

Healthy

↓

No Full GC
```

---

# 19. Common JVM Performance Mistakes

### Increasing Heap Without Investigation

❌ Wrong

Always identify the root cause first.

---

### Ignoring GC Logs

GC logs often provide the quickest insight into memory behaviour.

---

### Using Default Heap Everywhere

Production workloads vary.

Tune based on measurements.

---

### Changing GC Frequently

Changing collectors is not a substitute for fixing application issues.

---

### Ignoring Thread Dumps

Many latency issues are caused by locks, blocking, or deadlocks—not GC.

---

# 20. Performance Investigation Decision Tree

```text
Application Slow

↓

High CPU?

↓

YES

↓

Thread Dump

↓

CPU Profiling

--------------------

NO

↓

High Memory?

↓

YES

↓

Heap Dump

↓

MAT

--------------------

NO

↓

High GC?

↓

GC Logs

↓

Heap Analysis

--------------------

Still Unknown?

↓

JFR

↓

JMC
```

---

# 21. Senior-Level Follow-up Questions

1. How do you tune JVM performance?
2. Why enable GC logging?
3. Difference between JFR and JMC?
4. When would you use `jstack`?
5. What does `jstat` provide?
6. Why is `jcmd` preferred?
7. Should `-Xms` equal `-Xmx`?
8. How do you investigate long GC pauses?
9. Which tools have you used in production?
10. How do you identify memory leaks?

---

# 22. Real Interview Scenario

**Interviewer:**

> "A Java service suddenly becomes slow every few minutes. How would you investigate?"

### Strong Answer

> I'd begin by checking application metrics to determine whether CPU, memory, or I/O is the bottleneck. I'd review GC logs for long pauses, capture thread dumps if the application appears blocked, and use JFR to collect runtime data if the issue persists. If memory pressure is suspected, I'd generate a heap dump and analyse it in Eclipse MAT. I would avoid changing JVM parameters until I had identified the actual root cause.

---

# 23. JVM Tool Summary

| Tool        | Purpose                  |
| ----------- | ------------------------ |
| `jcmd`      | General JVM diagnostics  |
| `jstack`    | Thread dump analysis     |
| `jmap`      | Heap dump generation     |
| `jstat`     | GC and heap statistics   |
| JFR         | Runtime event recording  |
| JMC         | Analyse JFR recordings   |
| Eclipse MAT | Heap dump analysis       |
| VisualVM    | Monitoring and profiling |

---

# 24. Cheat Sheet

| Problem         | First Tool       |
| --------------- | ---------------- |
| High CPU        | `jstack`, JFR    |
| Memory Leak     | Heap Dump + MAT  |
| Frequent GC     | GC Logs, `jstat` |
| Deadlock        | `jstack`         |
| Heap Usage      | `jcmd`, `jstat`  |
| GC Tuning       | GC Logs          |
| Thread Analysis | `jstack`         |
| JVM Diagnostics | `jcmd`           |

---

## Production Performance Workflow

```text
Performance Issue

↓

Metrics

↓

GC Logs

↓

Thread Dump

↓

Heap Dump

↓

JFR

↓

Root Cause

↓

Fix

↓

Validate
```

---

# 🎯 Interview Secret

When an interviewer asks:

> **"How do you tune JVM performance?"**

Don't list JVM flags.

A senior-level answer is:

> "I don't begin by tuning JVM parameters. I first determine whether the bottleneck is CPU, memory, garbage collection, threads, or I/O using metrics and diagnostic tools. I analyse GC logs, thread dumps, heap dumps, and JFR recordings to identify the root cause. Only then do I adjust heap sizing, GC configuration, or application code, and I always validate the impact with performance measurements."

This demonstrates a **data-driven engineering approach**, which is what senior interviewers expect.

---

# ✅ Part VI Complete

You have now covered:

* ✅ JVM Runtime Memory Areas
* ✅ Object Creation & Escape Analysis
* ✅ Garbage Collection Fundamentals
* ✅ Modern Garbage Collectors (G1, ZGC, Shenandoah)
* ✅ Memory Leaks & Heap Dump Analysis
* ✅ JVM Performance & GC Tuning

These topics form the **core JVM knowledge expected of senior Java backend engineers**.

## Next Part: **Part VII – Class Loading, Reflection & Dynamic Proxies**

We'll cover:

* Class Loading Lifecycle
* ClassLoader hierarchy
* Parent Delegation Model
* Custom ClassLoaders
* Reflection API
* Dynamic Proxies (JDK & CGLIB)
* Bytecode manipulation (Byte Buddy, ASM)
* Spring AOP internals
* ClassLoader leaks
* Real production debugging scenarios

This section is especially valuable for understanding **Spring, Hibernate, AOP, plugin architectures, and framework internals**, all of which are common in senior Java interviews.
