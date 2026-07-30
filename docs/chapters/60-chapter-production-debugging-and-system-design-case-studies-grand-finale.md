# Part IX – Enterprise Design & Microservices

# Chapter 60: Production Debugging & System Design Case Studies (Grand Finale)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Google, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Uber, Netflix, Product Companies

---

# 1. Why Do Interviewers Ask This?

At senior levels, companies care less about whether you can write a REST API and more about whether you can **keep a production system running**.

Typical questions:

* An API suddenly became slow. What would you do?
* CPU reached 100%. How do you investigate?
* Memory keeps increasing every day.
* Kafka consumer lag is growing.
* Orders are getting duplicated.
* Database is healthy but users still complain.
* Design a scalable payment system.

They want to understand your **debugging approach**, not just your knowledge of frameworks.

---

# 2. 30-Second Interview Answer

> Production debugging starts by identifying symptoms through metrics, logs, traces, and alerts. I first determine what changed, isolate the affected component, gather evidence using monitoring tools, thread dumps, heap dumps, and SQL analysis, identify the root cause, validate the fix in a controlled environment, deploy safely, and monitor post-deployment. The goal is to solve the actual problem, not just the visible symptom.

---

# 3. Senior Debugging Mindset

Never start with assumptions.

Always follow:

```text
Observe

↓

Collect Evidence

↓

Form Hypothesis

↓

Verify

↓

Fix

↓

Monitor
```

This avoids chasing false leads.

---

# 4. Production Investigation Checklist

Whenever an incident occurs, ask:

* What changed recently?
* Is the issue affecting everyone or only some users?
* Is it reproducible?
* Which service is affected?
* Is the database healthy?
* Is an external dependency failing?
* Is the issue regional?
* Are infrastructure metrics normal?

---

# 5. High CPU Investigation

Interview favourite.

Possible causes:

* Infinite loops
* Poor algorithms
* Excessive object creation
* Excessive GC
* Busy-waiting
* Thread contention
* Expensive SQL processing

Investigation flow:

```text
CPU High

↓

Application?

↓

Thread Dump

↓

Hot Threads

↓

Root Cause
```

Useful tools:

* `top`
* `htop`
* `jstack`
* Java Flight Recorder (JFR)
* VisualVM

---

# 6. Memory Leak Investigation

Symptoms:

* Memory steadily increases
* Frequent Full GC
* Eventually `OutOfMemoryError`

Flow:

```text
Heap Usage Rising

↓

Heap Dump

↓

MAT Analysis

↓

Retained Objects

↓

Memory Leak
```

Common causes:

* Static collections
* Unbounded caches
* Listener leaks
* ThreadLocal misuse
* Large object graphs
* Objects unintentionally retained

Useful tools:

* Eclipse MAT
* VisualVM
* JFR
* `jmap`

---

# 7. Thread Dump Analysis

Interview favourite.

When:

* Application hangs
* APIs stop responding
* CPU spikes
* Deadlocks suspected

Generate thread dump:

```bash
jstack <PID>
```

Look for:

* BLOCKED threads
* WAITING threads
* Deadlocks
* Long-running SQL calls
* Thread pool exhaustion

---

# 8. Deadlock Investigation

Example:

```text
Thread A

Lock User

↓

Wait Order

---------------

Thread B

Lock Order

↓

Wait User
```

Result:

Neither thread proceeds.

Java detects monitor deadlocks in many cases, and thread dumps often identify the involved threads and locks.

---

# 9. Database Bottleneck

Symptoms:

* Slow APIs
* Database CPU high
* Connection pool exhausted

Check:

* Slow query logs
* Missing indexes
* Execution plans
* Lock contention
* Long-running transactions
* Connection pool metrics

---

# 10. Connection Pool Exhaustion

Interview favourite.

```text
Application

↓

HikariCP

↓

Maximum Connections Reached

↓

Requests Waiting
```

Causes:

* Connection leaks
* Slow SQL
* Pool too small
* Database slowdown

Never increase pool size without understanding the root cause.

---

# 11. Slow API Investigation

Flow:

```text
Client

↓

Gateway

↓

Application

↓

Database

↓

External API
```

Measure latency at each step.

Never assume the application is responsible.

---

# 12. Logging Strategy

Good logs contain:

* Correlation ID
* Request ID
* User ID (where appropriate and privacy-compliant)
* Timestamp
* Service name
* Error details
* Duration

Avoid:

* Logging passwords
* Secrets
* Tokens
* Sensitive personal information

---

# 13. Distributed Tracing

Interview favourite.

Example:

```text
Client

↓

Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service
```

Each request carries a **Trace ID**.

Popular tools:

* OpenTelemetry
* Jaeger
* Zipkin
* Grafana Tempo

---

# 14. Metrics vs Logs vs Traces

| Tool    | Best For                          |
| ------- | --------------------------------- |
| Metrics | Trends, latency, CPU, error rates |
| Logs    | Detailed events and errors        |
| Traces  | Request journey across services   |

All three complement each other.

---

# 15. Kafka Consumer Lag

Symptoms:

```text
Producer

↓

Kafka

↓

Consumer
```

Consumer falls behind.

Possible causes:

* Slow processing
* Too few consumers
* Large messages
* External API delays
* Database bottlenecks

---

# 16. OutOfMemoryError Investigation

Interview favourite.

Possible reasons:

* Heap too small
* Memory leak
* Huge collections
* Large file loading
* Infinite caching

Never solve every `OutOfMemoryError` by simply increasing heap size.

---

# 17. Real Production Incident #1

### Problem

Checkout API suddenly slowed from:

```text
200 ms

↓

12 seconds
```

Investigation

* Database healthy
* CPU normal
* Memory normal

Distributed tracing showed:

```text
Payment API

↓

Third-party Bank API

↓

11 seconds
```

Root Cause

Bank API latency increased.

Fix

* Added timeout
* Circuit breaker
* Retry with exponential backoff
* Fallback response

---

# 18. Real Production Incident #2

### Problem

Memory usage increased daily.

Restart fixed the issue temporarily.

Investigation

Heap dump revealed:

```text
ConcurrentHashMap

↓

50 Million Entries
```

Root Cause

Cache never expired.

Fix

* Added TTL
* Maximum cache size
* Eviction policy

---

# 19. Real Production Incident #3

### Problem

Orders duplicated.

Investigation

Kafka consumer restarted before committing offsets.

Messages were reprocessed.

Root Cause

Consumer was not idempotent.

Fix

* Event ID tracking
* Idempotent processing
* Offset commit after successful processing

---

# 20. Real Production Incident #4

### Problem

After a deployment, all instances became unhealthy.

Investigation

Health checks failed because a new dependency was mandatory during startup.

Root Cause

Application configuration error.

Fix

* Improved startup validation
* Made non-critical dependency optional
* Added deployment health verification before shifting traffic

---

# 21. System Design Case Study 1 – URL Shortener

Requirements:

* Generate short URLs
* Redirect quickly
* High availability

Architecture

```text
Client

↓

API Gateway

↓

URL Service

↓

Redis

↓

Database
```

Key concepts:

* Cache popular URLs
* Unique ID generation
* Database sharding (large scale)
* CDN for global reach
* Analytics asynchronously

---

# 22. System Design Case Study 2 – E-commerce Checkout

```text
Client

↓

Gateway

↓

Order Service

↓

Kafka

↓

Payment

↓

Inventory

↓

Shipping

↓

Notification
```

Patterns used:

* Saga
* Outbox
* Redis
* Circuit Breaker
* Retry
* Distributed Tracing

---

# 23. System Design Case Study 3 – Notification System

Requirements:

* SMS
* Email
* Push Notification

Architecture

```text
Client

↓

Notification API

↓

Kafka

↓

Email Worker

SMS Worker

Push Worker
```

Benefits:

* Independent scaling
* Fault isolation
* Easy retries
* DLQ support

---

# 24. Common Interview Traps

### CPU is high. Increase server size?

❌ No.

Investigate before scaling.

---

### Memory leak? Increase heap?

❌ Temporary workaround.

Find retained objects first.

---

### Slow API means slow database?

❌ Not always.

Measure each dependency.

---

### Kafka duplicates mean Kafka is broken?

❌ No.

Design consumers to be idempotent.

---

### More threads always improve performance?

❌ No.

Too many threads can increase context switching and contention.

---

# 25. Senior-Level Follow-up Questions

1. How do you investigate high CPU?
2. How do you analyse a heap dump?
3. How do you identify deadlocks?
4. How do you debug thread pool exhaustion?
5. Explain distributed tracing.
6. How would you debug Kafka consumer lag?
7. How do you debug slow SQL?
8. How do you identify connection leaks?
9. What metrics would you monitor in production?
10. Describe your most challenging production issue.

---

# 26. Real Interview Scenario

**Interviewer:**

> "Your CEO says the application is slow. Where do you start?"

### Strong Answer

> I wouldn't assume the application is the cause. I'd first determine the scope of the issue and check dashboards for latency, error rates, CPU, memory, and database health. Then I'd use distributed tracing to identify where request time is being spent. Based on the evidence, I'd investigate the slow component—whether it's the application, database, cache, or an external dependency—before implementing and validating a fix.

---

# 27. Senior Production Checklist

```text
✓ Metrics

✓ Logs

✓ Traces

✓ Thread Dumps

✓ Heap Dumps

✓ SQL Analysis

✓ GC Logs

✓ Connection Pools

✓ Kafka Lag

✓ Cache Hit Ratio

✓ Health Checks

✓ Deployment History
```

---

# 28. FAANG Interview Strategy

A senior engineer should demonstrate:

* Trade-off analysis
* Scalability thinking
* Reliability engineering
* Failure handling
* Cost awareness
* Observability
* Security considerations
* Performance optimisation

Avoid saying:

> "I would restart the server."

Instead explain:

* How you would diagnose
* How you would isolate
* How you would validate
* How you would prevent recurrence

---

# 29. Complete Enterprise Architecture

```text
                 Client
                    │
                    ▼
              API Gateway
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Order Service  User Service  Product Service
      │             │             │
      └──────┬──────┴──────┬──────┘
             ▼             ▼
           Kafka         Redis
             │             │
             ▼             ▼
     Notification     Distributed Cache
        Service
             │
             ▼
         Database(s)

Observability:
Metrics + Logs + Traces
```

---

# 30. Grand Cheat Sheet

| Area          | Key Takeaway                                               |
| ------------- | ---------------------------------------------------------- |
| High CPU      | Analyse hot threads before scaling                         |
| Memory Leak   | Capture and inspect heap dumps                             |
| Slow API      | Measure each dependency                                    |
| Deadlock      | Analyse thread dumps                                       |
| Kafka         | Design idempotent consumers                                |
| Redis         | Monitor cache hit ratio and TTLs                           |
| Database      | Optimise queries before adding hardware                    |
| Microservices | Build for failure and eventual consistency                 |
| Observability | Combine metrics, logs, and traces                          |
| System Design | Optimise for reliability, scalability, and maintainability |

---

# 🎯 Final Interview Secret

The biggest difference between a **mid-level** and a **senior** engineer is not writing more code.

A mid-level engineer says:

> "The API is slow because the database is slow."

A senior engineer says:

> "Let's verify that with metrics and traces before drawing conclusions."

A mid-level engineer focuses on **implementing features**.

A senior engineer focuses on:

* Designing resilient systems
* Understanding trade-offs
* Debugging production issues methodically
* Building observable services
* Preventing incidents from recurring

That mindset is what interviewers at top product companies look for.

---

# 🎉 Congratulations!

You have completed the **60-Chapter Senior Java Backend Interview Playbook**, covering:

* Java Fundamentals
* OOP & Collections
* Java 8+ Features
* Multithreading & Concurrency
* JVM Internals
* Class Loading & Reflection
* Spring Boot & Spring Internals
* Hibernate & JPA
* Security
* Testing
* Performance Tuning
* Design Patterns
* REST APIs
* Microservices
* Distributed Systems
* Kafka & RabbitMQ
* Distributed Transactions
* Redis & Caching
* Production Debugging
* System Design

This forms a strong foundation for **Senior Java Developer**, **Lead Engineer**, and many **FAANG/product-company** backend interviews.

## Suggested Bonus Volume

If you want to go beyond senior level and prepare for **Staff Engineer/Principal Engineer** interviews, the next volume could cover:

1. Advanced JVM Performance (GC tuning, JIT, JFR)
2. Advanced Kafka Internals (ISR, Leader Election, KRaft)
3. Kubernetes for Java Developers
4. Docker Deep Dive
5. CI/CD and GitOps
6. Cloud Architecture (AWS/Azure/GCP)
7. Event Sourcing & CQRS
8. Domain-Driven Design (DDD)
9. Hexagonal/Clean Architecture
10. Low-Level Design (LLD) with Java
11. High-Level Design (HLD) for Product Companies
12. Machine Coding Interview Preparation

These topics are commonly expected for Staff/Principal-level backend engineering roles.
