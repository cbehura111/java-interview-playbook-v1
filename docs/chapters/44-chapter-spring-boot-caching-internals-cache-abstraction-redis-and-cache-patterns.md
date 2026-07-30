# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 44: Spring Boot Caching Internals (Cache Abstraction, Redis & Cache Patterns)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Product Companies

---

# 1. Why Do Interviewers Ask This?

Performance is one of the most important aspects of enterprise applications.

Imagine an API that executes the following every request:

```text
Client

↓

Controller

↓

Service

↓

Database

↓

Return Result
```

If the same data is requested thousands of times, repeatedly querying the database wastes CPU, I/O, and increases latency.

Caching solves this problem.

Typical interview questions:

* What is Spring Cache?
* How does `@Cacheable` work?
* Difference between `@CachePut` and `@CacheEvict`?
* What is Redis?
* Explain Cache-Aside Pattern.
* What is Cache Stampede?

---

# 2. 30-Second Interview Answer

> Spring Cache provides a cache abstraction that separates application code from the underlying cache implementation. Developers use annotations such as `@Cacheable`, `@CachePut`, and `@CacheEvict`, while a `CacheManager` coordinates cache operations. Redis is commonly used as the backing store for distributed caching. Effective caching strategies reduce database load, improve response times, and increase system scalability.

---

# 3. What is Caching?

Caching stores frequently accessed data in fast storage.

Instead of

```text
API

↓

Database

↓

20 ms
```

Use

```text
API

↓

Cache

↓

1 ms
```

Only if the cache misses

↓

Query the database.

---

# 4. Spring Cache Architecture

```text
Client

↓

Controller

↓

Service

↓

Spring Cache

↓

CacheManager

↓

Redis / Caffeine / Ehcache

↓

Database (if cache miss)
```

---

# 5. CacheManager

Interview favourite.

`CacheManager` is the central abstraction.

Responsibilities:

* Create caches
* Locate caches
* Store cache entries
* Remove cache entries

Common implementations:

* ConcurrentMapCacheManager
* CaffeineCacheManager
* RedisCacheManager
* JCacheCacheManager

---

# 6. @Cacheable

Most commonly used annotation.

Example

```java
@Cacheable("products")
public Product getProduct(Long id) {

    return repository.findById(id);

}
```

Flow

```text
Method Called

↓

Cache Lookup

↓

Found?

↓

YES

↓

Return Cached Value

---------------

NO

↓

Execute Method

↓

Store Result

↓

Return Result
```

---

# 7. Example

First call

```text
getProduct(100)

↓

Database

↓

Cache Result
```

Second call

```text
getProduct(100)

↓

Cache

↓

Return Immediately
```

Database is not queried.

---

# 8. @CachePut

Interview favourite.

Unlike `@Cacheable`

The method always executes.

After execution

↓

Cache is updated.

Example

```java
@CachePut(value="products",
          key="#product.id")
public Product update(Product product) {

    return repository.save(product);

}
```

Use when updating data.

---

# 9. @CacheEvict

Removes entries.

Example

```java
@CacheEvict(value="products",
            key="#id")
public void delete(Long id) {

    repository.deleteById(id);

}
```

Flow

```text
Delete Database Record

↓

Remove Cache Entry
```

Prevents stale data.

---

# 10. Cache Lifecycle

```text
Client

↓

@Cacheable

↓

Cache Hit?

↓

YES

↓

Return Cache

---------------

NO

↓

Database

↓

Store Cache

↓

Return Result
```

---

# 11. Redis

Interview favourite.

Redis is an in-memory data store.

Characteristics:

* Extremely fast
* Supports key-value storage
* Optional persistence
* Distributed
* TTL support
* Pub/Sub
* Data structures (Lists, Sets, Hashes, Streams, etc.)

Commonly used as the cache provider in Spring Boot.

---

# 12. Why Redis Instead of Local Cache?

Local Cache

```text
Server A

↓

Own Cache
```

Server B

↓

Different Cache

Problem

Different application instances may see different data.

Redis

```text
Server A

↓

Redis

↑

Server B
```

All application instances share the same cache.

---

# 13. Cache-Aside Pattern

Interview favourite.

Most common strategy.

Flow

```text
Read Request

↓

Cache

↓

Hit?

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

# 14. Write-Through Cache

Flow

```text
Write

↓

Cache

↓

Database
```

Cache and database are updated together.

Advantages

* Data consistency
* Simpler reads

Disadvantage

* Higher write latency

---

# 15. Write-Behind (Write-Back)

Flow

```text
Write

↓

Cache

↓

Immediate Response

↓

Database Later
```

Advantages

* Very fast writes

Disadvantages

* Risk of data loss if the cache fails before persistence
* More complex consistency handling

---

# 16. Cache Stampede

Interview favourite.

Suppose

Cache expires.

Suddenly

```text
10,000 Requests

↓

Cache Miss

↓

Database
```

Database becomes overloaded.

Solutions

* Mutex/locking
* Request coalescing
* Staggered expiry (TTL jitter)
* Background refresh

---

# 17. Cache Penetration

Requests for data that does not exist.

Example

```text
Product ID

999999999
```

Every request

↓

Database

↓

No Result

↓

Repeat

Solutions

* Cache null/negative results briefly
* Bloom Filters
* Input validation

---

# 18. Cache Avalanche

Many cache entries expire simultaneously.

```text
Thousands Expire

↓

Database Flood
```

Solutions

* Randomised TTL
* Warm-up
* Multi-level cache

---

# 19. TTL (Time To Live)

Example

```text
Product Cache

↓

10 Minutes

↓

Automatically Removed
```

TTL helps prevent stale data.

Choose TTL based on how frequently the underlying data changes.

---

# 20. Production Example

E-Commerce

Without Cache

```text
Product API

↓

Database

↓

50 ms
```

With Redis

```text
Product API

↓

Redis

↓

2 ms
```

Database traffic drops significantly.

---

# 21. Production Debugging Story

Problem

Users updated product prices.

However

Old prices continued appearing.

Investigation

Redis contained stale values.

Root Cause

Update API used

```java
@Cacheable
```

instead of updating or evicting the cache.

Fix

Use

```java
@CachePut
```

or

```java
@CacheEvict
```

depending on the update strategy.

---

# 22. Common Interview Traps

### Does `@Cacheable` always execute the method?

❌ No.

If a cache entry exists, the method is skipped.

---

### Does `@CachePut` skip execution?

❌ No.

It always executes the method and updates the cache.

---

### Does `@CacheEvict` update cache values?

❌ No.

It removes entries.

---

### Is Redis only a cache?

❌ No.

Redis is an in-memory data store that can be used for caching, messaging, distributed locking, rate limiting, and more.

---

### Can local cache replace Redis?

It depends.

For a single application instance, local caches (e.g., Caffeine) are often sufficient.

For distributed deployments, Redis provides a shared cache across instances.

---

# 23. Senior-Level Follow-up Questions

1. Explain Spring Cache architecture.
2. What does `@Cacheable` do internally?
3. Difference between `@CachePut` and `@CacheEvict`?
4. What is CacheManager?
5. Why Redis?
6. Explain Cache-Aside.
7. What is Cache Stampede?
8. Cache Penetration vs Cache Avalanche?
9. How would you choose TTL values?
10. How do you prevent stale cache data?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Your database CPU suddenly spikes after a cache deployment. What could be the reason?"

### Strong Answer

> I'd investigate cache hit ratios, expiry patterns, and whether cache entries are being evicted too aggressively. A sudden spike often indicates cache stampede or cache avalanche, where many requests simultaneously miss the cache and hit the database. I'd review TTL configuration, enable staggered expirations, verify Redis availability, and consider request coalescing or background refresh to reduce database load.

---

# 25. Cheat Sheet

| Annotation/Concept | Purpose                            |
| ------------------ | ---------------------------------- |
| `@Cacheable`       | Read from cache or populate it     |
| `@CachePut`        | Always execute and update cache    |
| `@CacheEvict`      | Remove cache entry                 |
| CacheManager       | Manages cache instances            |
| Redis              | Distributed in-memory cache        |
| Cache-Aside        | Application manages cache          |
| TTL                | Automatic cache expiry             |
| Cache Stampede     | Many simultaneous cache misses     |
| Cache Penetration  | Repeated requests for missing data |
| Cache Avalanche    | Many keys expire together          |

---

## Spring Cache Flow

```text
Client

↓

@Cacheable

↓

Cache Hit?

↓

YES

↓

Return Cache

---------------

NO

↓

Database

↓

Store Cache

↓

Return
```

---

## Distributed Cache

```text
App Instance A

↓

Redis

↑

App Instance B

↑

App Instance C
```

All application instances use the same cache.

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does `@Cacheable` work internally?"**

Don't answer:

> "It stores the result in Redis."

A senior-level answer is:

> "`@Cacheable` is implemented using Spring AOP. When a proxied method is invoked, Spring intercepts the call, generates a cache key, and checks the configured `CacheManager`. If a cached value exists, it returns that value without executing the target method. On a cache miss, Spring invokes the method, stores the returned result in the cache, and then returns it to the caller. The application code remains unaware of the underlying cache implementation."

This answer demonstrates an understanding of **Spring AOP, proxy-based interception, cache abstraction, and distributed caching**, which is what interviewers typically look for.

---

## Next Chapter

**Chapter 45 – Spring Events, Async Processing & Scheduling Internals**

We'll cover:

* Spring Event architecture
* `ApplicationEventPublisher`
* `@EventListener`
* Transactional event listeners
* `@Async` internals
* `@EnableAsync`
* `@Scheduled` internals
* Thread pools for async execution
* Production event-driven patterns
* Senior interview questions
