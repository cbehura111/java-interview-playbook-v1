# Java Backend Engineering Interview Handbook

# Volume 1 - Java Core & Concurrency

# Part III - Concurrent Collections

# Chapter 11 - HashMap Internals (Source Code to Production)

> **"HashMap is one of the most frequently used classes in Java, yet one of the least understood. Every senior Java interview eventually reaches the question: 'How does HashMap work internally?'"**

This chapter goes far beyond basic usage. We'll explore the internal implementation, performance characteristics, common pitfalls, and why `HashMap` becomes dangerous in multithreaded applications.

---

# Learning Objectives

After this chapter, you will understand:

* Internal structure of `HashMap`
* Buckets
* Hash Function
* Index Calculation
* Collision Handling
* Linked List vs Red-Black Tree
* Load Factor
* Capacity
* Resize (Rehashing)
* Java 7 vs Java 8
* Performance Analysis
* Production Best Practices

---

# 11.1 Why HashMap?

Imagine an e-commerce website.

Every request needs to quickly find:

* Product
* User
* Order
* Configuration
* Session

Searching sequentially in a list:

```text
User1

↓

User2

↓

User3

↓

User4
```

Time Complexity

```text
O(n)
```

With `HashMap`:

```text
Hash(Key)

↓

Bucket

↓

Value
```

Time Complexity

```text
Average O(1)
```

This is why `HashMap` is one of the most important data structures in backend development.

---

# 11.2 Internal Structure

A `HashMap` is **not** a giant table of key-value pairs.

Internally, it stores an array of buckets.

```text
Bucket Array

+----+----+----+----+----+----+

0    1    2    3    4    5

+----+----+----+----+----+----+
```

Each bucket may contain:

* Nothing
* One Entry
* Multiple Entries

---

# 11.3 Node Structure

Internally each entry looks like:

```java
static class Node<K,V>{

	final int hash;

	final K key;

	V value;

	Node<K,V> next;

}
```

Every node stores:

* Hash
* Key
* Value
* Pointer to next node

---

# 11.4 What Happens During `put()`?

Suppose:

```java
map.put("A",100);
```

Steps:

```text
Key

↓

hashCode()

↓

Hash()

↓

Bucket Index

↓

Store Node
```

The key itself is never used to locate the bucket directly; its hash value determines the bucket index.

---

# 11.5 Hash Calculation

Example:

```java
"A".hashCode()
```

Suppose

```text
63215
```

HashMap further spreads the bits internally before calculating the index to reduce collisions.

Conceptually:

```text
Hash

↓

Spread Bits

↓

Bucket Index
```

---

# 11.6 Bucket Index

Suppose

Capacity

```text
16
```

Bucket calculation

```text
hash & (capacity - 1)
```

Example

```text
63215 & 15

↓

Bucket 7
```

Using a bitwise AND is faster than the modulo operator, which is why HashMap capacities are powers of two.

---

# 11.7 Collision

Suppose

"A"

and

"B"

both map to Bucket 7.

```text
Bucket 7

↓

A

↓

B
```

This is called

**Collision**.

Collisions are normal and expected.

A good hash function minimizes them but cannot eliminate them entirely.

---

# 11.8 Collision Handling

Before Java 8

```text
Bucket

↓

Node

↓

Node

↓

Node
```

A linked list.

Searching:

```text
O(n)
```

for that bucket.

---

# 11.9 Java 8 Improvement

If a bucket becomes too large,

Linked List

↓

Red-Black Tree

```text
	  20

	/    \

   10    30

  /        \

 5         40
```

Search becomes

```text
O(log n)
```

instead of

```text
O(n)
```

This significantly improves performance when many collisions occur.

---

# 11.10 Treeification

HashMap converts a linked list into a Red-Black Tree when:

* Bucket size exceeds **8**
* Table capacity is at least **64**

If the table is still small, HashMap prefers resizing instead of treeifying.

---

# 11.11 Load Factor

Default:

```text
0.75
```

Meaning:

```text
Capacity = 16

↓

Threshold

16 × 0.75

↓

12
```

After inserting the 13th element,

HashMap resizes.

---

# 11.12 Resize (Rehashing)

Old Capacity

```text
16
```

New Capacity

```text
32
```

Every existing entry is redistributed into the new bucket array based on the new capacity.

```text
Old Table

↓

Recalculate Bucket

↓

Move Node

↓

New Table
```

Resizing is an expensive operation, so frequent resizing should be avoided by choosing an appropriate initial capacity.

---

# 11.13 Why Capacity is Always a Power of Two

Possible capacities:

```text
16

32

64

128

256
```

Reason:

Fast bucket calculation using

```text
hash & (capacity - 1)
```

instead of modulo.

This optimization is one of the reasons `HashMap` is so efficient.

---

# 11.14 Time Complexity

| Operation | Average | Worst Case                                   |
| --------- | ------- | -------------------------------------------- |
| Put       | O(1)    | O(n)                                         |
| Get       | O(1)    | O(n) (or O(log n) with tree bins in Java 8+) |
| Remove    | O(1)    | O(n) (or O(log n) with tree bins)            |

Average performance is excellent because collisions are usually low when keys have a good hash distribution.

---

# 11.15 equals() and hashCode()

One of the most common interview topics.

If two objects are equal,

```java
obj1.equals(obj2)
```

returns

```text
true
```

Then

their

```java
hashCode()
```

**must be equal**.

Otherwise,

HashMap may fail to retrieve stored values correctly.

---

# Example

```java
class Employee {

	private int id;

}
```

If you override

```java
equals()
```

you should also override

```java
hashCode()
```

to maintain the general contract.

---

# 11.16 Immutable Keys

Good Key

```java
String
```

Bad Key

```java
class Employee{

	int id;

}
```

Changing

```java
id
```

after inserting into the map changes the logical identity of the key.

Retrieval may fail because the object now hashes differently than when it was inserted.

**Best Practice:** Use immutable objects as keys.

---

# 11.17 Real Production Example

Spring Boot Cache

```java
Map<String,User> cache =
		new HashMap<>();
```

Lookup

```java
cache.get(userId);
```

Average

```text
O(1)
```

This makes `HashMap` ideal for in-memory caches **when only one thread is accessing it**.

---

# 11.18 Common Interview Questions

### Q1. Why is HashMap fast?

Because it uses hashing to compute a bucket index, providing average O(1) lookup and insertion.

---

### Q2. Why is the capacity always a power of two?

To enable efficient bucket calculation using bitwise AND instead of modulo.

---

### Q3. What is Load Factor?

The threshold that determines when the HashMap resizes.

Default value:

```text
0.75
```

---

### Q4. Why convert LinkedList into Red-Black Tree?

To improve lookup performance from O(n) to O(log n) when a bucket becomes heavily populated.

---

### Q5. What happens during resize?

A new bucket array is created (typically double the capacity), and existing entries are redistributed into new buckets.

---

# Production Scenario

**Interviewer:**

> "Your application stores one million records in a `HashMap`, but performance suddenly degrades. What would you investigate?"

A strong answer:

* Check whether the initial capacity was too small, causing repeated resizing.
* Examine the quality of `hashCode()` implementations for excessive collisions.
* Determine whether many entries are ending up in the same bucket.
* Use profiling tools to identify hotspots.
* Consider whether another data structure or caching strategy is more appropriate.

---

# Best Practices

✅ Provide good `hashCode()` implementations.

✅ Always override `equals()` and `hashCode()` together.

✅ Use immutable keys.

✅ Set an appropriate initial capacity when the expected size is known.

✅ Avoid unnecessary resizing.

---

# Common Mistakes

❌ Using mutable objects as keys.

❌ Overriding `equals()` without `hashCode()`.

❌ Assuming collisions never occur.

❌ Ignoring initial capacity for large maps.

---

# Chapter Summary

* `HashMap` stores data in an array of buckets.
* Hash values determine the bucket index.
* Collisions are handled using linked lists or Red-Black Trees.
* Java 8 introduced treeification for better worst-case performance.
* Load factor and capacity directly influence performance.
* Correct implementations of `equals()` and `hashCode()` are essential.

---

# Next Chapter (One of the Most Important in the Book)

## Chapter 12 - Why HashMap is NOT Thread Safe (Deep Dive)

This chapter will cover the **first scenario-based interview question** from your original list in depth:

> **"What happens if multiple threads access a HashMap concurrently?"**

We'll explore:

* Race conditions during `put()`
* Lost updates
* Concurrent resize problems
* The infamous Java 7 infinite loop issue
* Memory corruption scenarios
* Why `ConcurrentHashMap` was introduced
* `Collections.synchronizedMap()` vs `ConcurrentHashMap`
* Source code walkthroughs
* Production debugging examples
* Senior-level interview answers

This will be one of the most detailed and interview-focused chapters in the entire handbook.
