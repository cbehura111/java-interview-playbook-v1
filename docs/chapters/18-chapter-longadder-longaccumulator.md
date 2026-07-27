# Part IV - Atomic Operations

# Chapter 18: LongAdder & LongAccumulator

> **Interview Difficulty:** ⭐⭐⭐⭐☆ (Senior Java Developer)
>
> **Asked In:** Amazon, Oracle, Walmart, Visa, JPMorgan, Goldman Sachs, Microsoft, Flipkart, Adobe

---

# 1. Why Do Interviewers Ask This?

The interviewer is **not** checking whether you know the API.

They want to assess whether you understand:

* High contention scenarios
* Lock-free programming
* CAS bottlenecks
* JVM concurrent utilities
* Performance optimization
* Choosing the right data structure based on workload

**Typical Interview Question:**

> We have an API receiving 200K requests/sec, and we need to maintain a request counter. Would you use `AtomicLong` or `LongAdder`? Why?

---

# 2. 30-Second Interview Answer

> `AtomicLong` stores the value in a single memory location. Every thread competes to update that location using CAS, which becomes a bottleneck under high contention. `LongAdder` distributes updates across multiple internal counters (cells), allowing different threads to update different cells concurrently. This significantly improves write throughput. The trade-off is that reading the value requires summing all cells, making reads slightly more expensive.

---

# 3. Interviewer's Expectation

After your 30-second answer, be prepared for:

* Why does `AtomicLong` become slow?
* What is CAS?
* What are Cells?
* What is `Striped64`?
* How many Cells are created?
* Is `sum()` atomic?
* When should you NOT use `LongAdder`?

---

# 4. The Problem with AtomicLong

Imagine 10 threads incrementing the same counter.

```text
AtomicLong

		 +-------------+
Thread1 ----\
Thread2 -----\
Thread3 -------> Counter (100)
Thread4 -----/
Thread5 ----/
		 +-------------+
```

Every thread tries to update **one memory location**.

Internally:

```java
counter.incrementAndGet();
```

becomes

```java
while(true){

   long current = value;

   long next = current + 1;

   if(compareAndSet(current,next))
	   return;

}
```

If another thread modifies the value before CAS succeeds:

* CAS fails
* Retry
* Retry
* Retry

More contention → More retries → Lower throughput.

---

# 5. Production Scenario

Suppose you're building:

```
Payment Service

↓

Every payment increments

paymentsProcessed++
```

Traffic:

```
100 TPS

↓

500 TPS

↓

10,000 TPS

↓

200,000 TPS
```

With `AtomicLong`, every request competes for the same counter.

CPU spends more time retrying CAS than performing useful work.

---

# 6. Enter LongAdder

Instead of one counter:

```
Cell0

Cell1

Cell2

Cell3

Cell4
```

Threads spread across multiple cells.

```
Thread1 → Cell0

Thread2 → Cell1

Thread3 → Cell2

Thread4 → Cell3

Thread5 → Cell0
```

Each thread updates a different memory location.

Much less contention.

---

# 7. Internal Architecture

```
LongAdder
	  │
	  │
	  ▼
+----------------------+
|      Striped64       |
+----------------------+
		  │
		  │
   +------+------+ 
   |             |
 base        Cell[]
			   │
	 +----+----+----+
	 |    |    |    |
   Cell Cell Cell Cell
```

`LongAdder` extends **Striped64**, an internal JDK class that manages contention by dynamically creating multiple counters.

---

# 8. What is Striped64?

`Striped64` is the foundation for:

* LongAdder
* LongAccumulator
* DoubleAdder
* DoubleAccumulator

It contains:

```java
volatile long base;

volatile Cell[] cells;
```

Initially:

```
base = 0

cells = null
```

When contention is low:

```
Thread

↓

base++
```

Fast and memory-efficient.

---

# 9. What Happens Under Contention?

When CAS on `base` starts failing repeatedly:

```
CAS Failed

↓

Create Cell[]

↓

Distribute threads

↓

Retry
```

Example:

```
base

↓

CAS failure

↓

cells[2]

↓

cells[4]

↓

cells[1]
```

The JDK automatically expands the number of cells as contention increases.

---

# 10. How Does a Thread Pick a Cell?

Each thread has a pseudo-random probe value.

```
probe = 5

↓

5 % cells.length

↓

Cell5
```

Another thread:

```
probe = 12

↓

Cell4
```

This reduces the chance of multiple threads updating the same cell.

---

# 11. Dynamic Expansion

Suppose:

```
2 Cells
```

are not enough.

More contention occurs.

The JDK automatically expands:

```
2

↓

4

↓

8

↓

16

↓

32
```

Expansion stops when additional cells no longer improve throughput or when it reaches an implementation-defined limit (often related to available processors).

---

# 12. Reading the Value

Unlike `AtomicLong`:

```java
counter.get();
```

`LongAdder` must compute:

```
base

+

Cell0

+

Cell1

+

Cell2

+

Cell3
```

Internally:

```java
long total = base;

for(Cell c : cells){

	total += c.value;

}
```

Therefore:

Writes → Very Fast

Reads → Slightly Slower

---

# 13. Is sum() Atomic?

Interview favorite.

**Answer: No.**

Suppose:

```
Cell0 = 10

Cell1 = 20
```

While `sum()` is reading:

```
Thread

updates

Cell1 = 21
```

Possible result:

```
30

or

31
```

depending on timing.

For metrics and statistics, this is acceptable.

For banking balances, it is **not**.

---

# 14. When Should You Use LongAdder?

| Use Case               | LongAdder? | Reason                      |
| ---------------------- | ---------- | --------------------------- |
| API Request Counter    | ✅          | Heavy writes                |
| Prometheus Metrics     | ✅          | Eventual accuracy is fine   |
| Kafka Consumer Metrics | ✅          | High throughput             |
| Login Counter          | ✅          | Many increments             |
| Bank Balance           | ❌          | Exact value required        |
| Inventory Stock        | ❌          | Strong consistency required |
| Wallet Balance         | ❌          | Precise reads required      |

---

# 15. LongAccumulator

`LongAccumulator` generalizes `LongAdder` by allowing a custom accumulation function.

Example:

```java
LongAccumulator maxAccumulator =
	new LongAccumulator(Long::max, Long.MIN_VALUE);

maxAccumulator.accumulate(120);
maxAccumulator.accumulate(250);
maxAccumulator.accumulate(180);

System.out.println(maxAccumulator.get()); // 250
```

Other examples include tracking minimum values or combining values with custom associative operations.

Use it when addition is **not** the operation you need.

---

# 16. LongAdder vs AtomicLong

| Feature           | AtomicLong      | LongAdder                  |
| ----------------- | --------------- | -------------------------- |
| Updates           | Single variable | Multiple cells             |
| Write Performance | Good            | Excellent under contention |
| Read Performance  | Excellent       | Good (needs aggregation)   |
| CAS Contention    | High            | Low                        |
| Memory Usage      | Low             | Higher                     |
| Best For          | Frequent reads  | Frequent writes            |

---

# 17. Production Example

### Spring Boot Request Counter

```java
@Component
public class ApiMetrics {

	private final LongAdder requestCounter = new LongAdder();

	public void increment() {
		requestCounter.increment();
	}

	public long getCount() {
		return requestCounter.sum();
	}
}
```

Every incoming request:

```java
metrics.increment();
```

Periodic metrics export:

```java
metrics.getCount();
```

This pattern is common in monitoring systems where write throughput is far more important than perfectly synchronized reads.

---

# 18. Common Interview Traps

### ❓ Is LongAdder always better?

❌ No.

If reads are much more frequent than writes, `AtomicLong` may be a better choice because reads are just a single volatile access.

---

### ❓ Is LongAdder lock-free?

✅ Yes. It relies primarily on CAS and avoids traditional locks in normal operation.

---

### ❓ Does LongAdder guarantee perfectly consistent reads?

❌ No.

`sum()` provides a best-effort snapshot, not a transactional read.

---

### ❓ Why not synchronize everything?

Locks serialize updates, reducing concurrency under heavy write loads.

---

# 19. Senior-Level Follow-up Questions

1. Why does CAS fail under contention?
2. What problem does `Striped64` solve?
3. How are cells allocated?
4. Why is `base` still present?
5. Why does `sum()` iterate over all cells?
6. Is `LongAdder` linearizable?
7. How does false sharing affect performance?
8. When would `AtomicLong` outperform `LongAdder`?
9. Why is `LongAdder` widely used in metrics libraries?
10. What is the difference between `LongAdder` and `LongAccumulator`?

---

# 20. Cheat Sheet

### Remember

* ✅ `AtomicLong` → Single memory location.
* ✅ `LongAdder` → Multiple cells to reduce contention.
* ✅ Built on `Striped64`.
* ✅ Heavy writes → `LongAdder`.
* ✅ Frequent reads with exact values → `AtomicLong`.
* ✅ `sum()` is **not** an atomic snapshot.
* ✅ Commonly used in metrics, monitoring, and high-throughput counters.

---

In the next chapter, we'll cover **AtomicReference, AtomicStampedReference, and the ABA Problem**, including how lock-free algorithms use CAS on object references, why the ABA problem occurs, and how the JDK solves it using version stamps-topics that frequently appear in senior backend interviews.
