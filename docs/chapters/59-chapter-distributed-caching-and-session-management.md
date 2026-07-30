# Part IX – Enterprise Design & Microservices

# Chapter 59: Distributed Caching & Session Management

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

As applications grow, databases become one of the biggest bottlenecks.

Common production problems:

* Slow APIs
* High database CPU
* Repeated queries
* Session loss after scaling
* Increased response time

Caching and proper session management help solve these issues.

Typical interview questions:

* Local Cache vs Distributed Cache?
* Why Redis?
* Cache Aside vs Write Through?
* What is Cache Invalidation?
* Sticky Session vs Stateless JWT?
* Redis Cluster?
* Cache Stampede?

---

# 2. 30-Second Interview Answer

> Distributed caching stores frequently accessed data in a shared cache like Redis, reducing database load and improving response times across multiple application instances. Session management can be achieved using sticky sessions, shared session stores such as Redis, or stateless authentication using JWT. A well-designed caching strategy balances performance with data consistency and cache invalidation.

---

# 3. Why Caching?

Without cache

```text
Client

↓

Spring Boot

↓

Database

↓

Response
```

Every request hits the database.

---

With cache

```text
Client

↓

Spring Boot

↓

Redis

↓

Database (Only on Cache Miss)
```

Much faster.

---

# 4. Local Cache

Interview favourite.

```text
Application

↓

Caffeine Cache
```

Examples:

* Caffeine
* ConcurrentHashMap
* Ehcache (local mode)

Advantages:

* Extremely fast
* No network call
* Easy to implement

---

Problems

```text
Instance A

↓

Product Updated

---------------

Instance B

↓

Old Value Still Cached
```

Each instance has its own cache.

---

# 5. Distributed Cache

Interview favourite.

```text
App A

↓

Redis

↑

App B

↑

App C
```

Every instance shares the same cache.

---

Advantages

* Shared cache
* Consistent data across instances
* Better scaling
* Session sharing

---

# 6. Why Redis?

Interview favourite.

Redis is:

* In-memory
* Very fast
* Distributed
* Persistent (optional)
* Highly available
* Supports multiple data structures

Typical structures:

* String
* Hash
* List
* Set
* Sorted Set
* Stream

---

# 7. Cache-Aside Pattern

Interview favourite.

Most common.

Flow

```text
Request

↓

Redis

↓

Cache Hit?

↓

YES

↓

Return

---------------

NO

↓

Database

↓

Update Cache

↓

Return
```

Application controls the cache.

---

# 8. Write-Through Cache

```text
Application

↓

Cache

↓

Database
```

Every write updates:

* Cache
* Database

Advantages

* Cache always up-to-date

Disadvantages

* Higher write latency

---

# 9. Write-Behind (Write-Back)

```text
Application

↓

Cache

↓

Immediate Response

↓

Background Update

↓

Database
```

Very fast writes.

Risk:

If the cache fails before flushing pending writes, data may be lost unless durability mechanisms are in place.

---

# 10. Read-Through Cache

```text
Application

↓

Cache

↓

Database
```

The cache automatically loads missing data.

Applications don't explicitly query the database on cache misses.

---

# 11. Cache Eviction

Interview favourite.

When should cache be removed?

Common strategies:

* TTL
* Manual Eviction
* LRU
* LFU

---

# 12. TTL (Time To Live)

Example

```text
User Cache

↓

Expires

↓

10 Minutes
```

After expiry,

fresh data is loaded.

---

# 13. LRU (Least Recently Used)

When cache is full,

remove

```text
Least Recently Used Item
```

Most common eviction strategy.

---

# 14. Cache Invalidation

Interview favourite.

The two hardest problems are often jokingly said to be:

* Cache invalidation
* Naming things

Example

```text
Update Product

↓

Delete Redis Entry

↓

Next Read

↓

Database

↓

Fresh Cache
```

---

# 15. Cache Consistency

Problem

```text
Database Updated

↓

Redis Not Updated

↓

Old Data Returned
```

Solutions:

* TTL
* Event-driven invalidation
* Cache eviction
* Versioning (where appropriate)

---

# 16. Cache Stampede

Interview favourite.

```text
Popular Product

↓

TTL Expired

↓

1000 Requests

↓

Database Hit 1000 Times
```

Database becomes overloaded.

---

Solutions

* Cache warming
* Request coalescing/single-flight
* Distributed locking
* Staggered TTLs

---

# 17. Cache Penetration

```text
Invalid Product ID

↓

Cache Miss

↓

Database

↓

Repeated Forever
```

Solutions:

* Cache null values briefly
* Bloom filters
* Input validation

---

# 18. Cache Avalanche

```text
Millions of Keys

↓

Expire Together

↓

Database Overloaded
```

Solution

Add random TTL values to avoid simultaneous expiry.

---

# 19. Redis Cluster

Interview favourite.

```text
Redis Node 1

Redis Node 2

Redis Node 3
```

Benefits:

* High availability
* Horizontal scaling
* Data partitioning (sharding)

---

# 20. Session Management

Traditional session

```text
Client

↓

Server Memory

↓

Session
```

Works only for one server.

---

# 21. Scaling Problem

```text
Load Balancer

↓

Server A

↓

Session Exists

---------------

Server B

↓

Session Missing
```

User appears logged out.

---

# 22. Sticky Sessions

Interview favourite.

```text
User

↓

Always Routed

↓

Server A
```

Simple,

but limits flexibility and resilience.

---

# 23. Distributed Session

Better approach

```text
Load Balancer

↓

Server A

↓

Redis Session

↑

Server B
```

All servers share session data.

Spring Session commonly integrates with Redis for this purpose.

---

# 24. Stateless Authentication

Modern microservices often prefer:

```text
JWT

↓

No Server Session
```

Every request carries authentication information.

Advantages:

* Horizontal scaling
* No session replication
* Simpler load balancing

Trade-offs:

* Token revocation is more complex
* Token size increases request size
* Sensitive data should not be stored in JWTs

---

# 25. Production Architecture

```text
             Client
                │
                ▼
          Load Balancer
                │
     ┌──────────┴──────────┐
     ▼                     ▼
 Spring Boot A       Spring Boot B
     │                     │
     └──────────┬──────────┘
                ▼
             Redis Cluster
                │
                ▼
             Database
```

---

# 26. Production Example

E-commerce

```text
Product API

↓

Redis

↓

Database
```

Frequently viewed products are served directly from Redis.

Database load drops significantly.

---

# 27. Production Debugging Story

Problem

During a flash sale,

database CPU reached 100%.

Investigation

A hot product cache expired.

Thousands of requests hit the database simultaneously.

Root Cause

Cache stampede.

Fix

* Added distributed locking
* Warmed cache before sale
* Introduced randomized TTL
* Added request coalescing

Database remained stable during future sales.

---

# 28. Common Interview Traps

### Is Redis only a cache?

❌ No.

Redis can also be used for sessions, distributed locks, pub/sub, streams, rate limiting, and more.

---

### Is local cache always faster?

✅ Yes.

But it may become inconsistent across multiple application instances.

---

### Should every query be cached?

❌ No.

Frequently changing data may not benefit from caching.

---

### Is sticky session recommended for cloud-native systems?

❌ Generally no.

Stateless authentication or distributed session storage is usually preferred.

---

### Does cache guarantee consistency?

❌ No.

Applications must define and implement an appropriate consistency strategy.

---

# 29. Senior-Level Follow-up Questions

1. Local cache vs Redis?
2. Why Redis instead of Memcached?
3. Explain Cache-Aside.
4. Cache Stampede vs Cache Avalanche?
5. How do you invalidate cache?
6. Sticky Session vs Redis Session?
7. JWT vs Server Session?
8. How does Redis Cluster work?
9. How would you cache product catalogues?
10. How do you debug stale cache problems?

---

# 30. Real Interview Scenario

**Interviewer:**

> "Your product API is suddenly generating 10 times more database traffic, even though Redis is enabled. How would you investigate?"

### Strong Answer

> I'd first check cache hit and miss metrics to confirm whether requests are bypassing Redis. I'd verify key expiry settings, cache invalidation logic, and whether a recent deployment changed cache keys. If a large number of keys expired simultaneously, I'd investigate a cache stampede. I'd also review Redis health, latency, and application logs before deciding whether to adjust TTLs, warm the cache, or introduce request coalescing.

---

# 31. Cheat Sheet

| Concept                | Purpose                            |
| ---------------------- | ---------------------------------- |
| Local Cache            | Per-instance cache                 |
| Distributed Cache      | Shared cache across instances      |
| Redis                  | Distributed in-memory datastore    |
| Cache-Aside            | Read from cache first              |
| Write-Through          | Update cache and database together |
| Write-Behind           | Cache first, database later        |
| TTL                    | Automatic expiry                   |
| Cache Stampede         | Many requests after cache expiry   |
| Cache Avalanche        | Many keys expire simultaneously    |
| Sticky Session         | Same server handles requests       |
| Spring Session + Redis | Shared sessions                    |
| JWT                    | Stateless authentication           |

---

## Cache Flow

```text
Request

↓

Redis

↓

Hit?

↓

YES → Return

NO

↓

Database

↓

Update Redis

↓

Return
```

---

## Distributed Session

```text
Load Balancer

↓

Spring Boot A

↓

Redis Session Store

↑

Spring Boot B
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why use Redis instead of just increasing the database size?"**

Don't answer:

> "Redis is faster."

A senior-level answer is:

> "Scaling the database alone doesn't eliminate repeated reads or reduce query execution costs. Redis serves frequently accessed data directly from memory with very low latency, reducing database load and improving response times. I'd use Redis selectively for read-heavy workloads while defining a clear cache invalidation strategy, monitoring cache hit ratios, and choosing an appropriate consistency model based on business requirements."

That answer demonstrates an understanding of **performance engineering, scalability, and distributed caching trade-offs**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 60 – Production Debugging & System Design Case Studies (Grand Finale)**

We'll cover:

* End-to-end production debugging methodology
* High CPU, memory leaks, and thread dumps
* Slow APIs and database bottlenecks
* OutOfMemoryError investigation
* Deadlocks and thread starvation
* Kafka consumer lag debugging
* Distributed tracing in microservices
* Real production incidents
* Complete system design case studies
* Senior interview strategy for FAANG and product companies

This final chapter will bring together everything covered throughout the series into a comprehensive production engineering and system design playbook.
