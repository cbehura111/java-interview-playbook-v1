# Part IX – Enterprise Design & Microservices

# Chapter 58: Distributed Transactions (Saga Pattern & Transactional Outbox)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

In a monolithic application, maintaining data consistency is straightforward using a single database transaction.

```text
BEGIN

↓

Update Order

↓

Update Payment

↓

Update Inventory

↓

COMMIT
```

In microservices:

* Order Service has its own database
* Payment Service has its own database
* Inventory Service has its own database

A single ACID transaction cannot span these independent databases.

Typical interview questions:

* Why doesn't `@Transactional` work across microservices?
* What is the Saga Pattern?
* Choreography vs Orchestration?
* What is a Compensating Transaction?
* What is the Transactional Outbox Pattern?
* How do you ensure eventual consistency?

---

# 2. 30-Second Interview Answer

> Traditional ACID transactions are limited to a single transactional resource and do not naturally span independent microservices. Instead, microservices commonly use the Saga Pattern, where each service performs a local transaction and, if necessary, executes compensating actions to undo business effects. The Transactional Outbox Pattern ensures reliable event publishing by storing business data and outbound events in the same local database transaction before asynchronously publishing those events.

---

# 3. Why Distributed Transactions are Difficult

Imagine an order placement.

```text
Order Service

↓

Create Order

↓

Payment Service

↓

Charge Customer

↓

Inventory Service

↓

Reserve Stock
```

Suppose:

* Order succeeds ✅
* Payment succeeds ✅
* Inventory fails ❌

How do we recover?

---

# 4. Why Not Use One Database Transaction?

Interview favourite.

Each service owns its database.

```text
Order DB

Payment DB

Inventory DB
```

A single local database transaction cannot coordinate all of them.

Protocols like **Two-Phase Commit (2PC)** exist, but they introduce coordination overhead, reduce availability, and are generally avoided in many modern microservice architectures.

---

# 5. Local Transactions

Each service performs its own transaction.

```text
Order Service

↓

Commit Order

---------------

Payment Service

↓

Commit Payment

---------------

Inventory Service

↓

Commit Inventory
```

Each transaction succeeds independently.

---

# 6. What is a Saga?

Interview favourite.

A Saga is a sequence of local transactions.

```text
Order

↓

Payment

↓

Inventory

↓

Shipping
```

If one step fails,

previous successful steps are compensated.

---

# 7. Compensating Transaction

Instead of database rollback,

execute a business rollback.

Example

```text
Payment Success

↓

Inventory Failed

↓

Refund Payment
```

Notice:

The payment record still exists.

A refund is a **new business action**, not a database rollback.

---

# 8. Saga Architecture

```text
Order Created

↓

Payment Completed

↓

Inventory Reserved

↓

Shipment Created
```

If Shipment fails

↓

Release Inventory

↓

Refund Payment

↓

Cancel Order

---

# 9. Choreography Saga

Interview favourite.

No central coordinator.

Services communicate through events.

```text
Order Service

↓

OrderCreated Event

↓

Payment Service

↓

PaymentCompleted Event

↓

Inventory Service

↓

InventoryReserved Event
```

Every service reacts independently.

---

# 10. Advantages of Choreography

* Loose coupling
* No central controller
* Easy to add consumers
* Good for event-driven systems

---

# 11. Disadvantages

As services increase:

```text
Order

↓

Payment

↓

Inventory

↓

Shipping

↓

Loyalty

↓

Analytics

↓

Notification
```

Event flows become difficult to understand.

This is often called **event choreography complexity**.

---

# 12. Orchestration Saga

Interview favourite.

A central orchestrator controls the workflow.

```text
Saga Orchestrator

↓

Order

↓

Payment

↓

Inventory

↓

Shipping
```

The orchestrator decides what happens next.

---

# 13. Orchestration Example

```text
Orchestrator

↓

Create Order

↓

Payment Success?

↓

Reserve Inventory

↓

Shipment

↓

Complete Order
```

If Payment fails

↓

Cancel Order

---

# 14. Choreography vs Orchestration

| Choreography         | Orchestration              |
| -------------------- | -------------------------- |
| Event-driven         | Central coordinator        |
| Loosely coupled      | Easier workflow visibility |
| Harder to trace      | Easier to debug            |
| No single controller | Central decision maker     |

---

# 15. Transactional Outbox Pattern

Interview favourite.

Problem:

```text
Update Order

↓

Publish Kafka Event
```

What if the database commit succeeds,

but Kafka is unavailable?

The order exists,

but no event is published.

---

# 16. Outbox Solution

```text
Business Table

↓

Outbox Table

↓

Same Database Transaction

↓

Commit
```

Business data and event are committed together.

---

# 17. Outbox Flow

```text
Order Service

↓

Save Order

↓

Save Outbox Event

↓

Commit

↓

Outbox Publisher

↓

Kafka
```

If Kafka is temporarily unavailable,

the event remains in the Outbox table until successfully published.

---

# 18. Outbox Benefits

* No lost events
* Reliable publishing
* Eventual consistency
* Independent retries
* No distributed transaction required

---

# 19. Idempotency

Interview favourite.

Suppose Kafka delivers the same event twice.

```text
PaymentCompleted

↓

Consumer

↓

Duplicate Event
```

Consumers should process duplicate events safely.

Common techniques:

* Event ID
* Business key
* Deduplication table

---

# 20. Eventual Consistency

Unlike ACID transactions,

updates may not be visible immediately.

Example

```text
Order Created

↓

Payment Pending

↓

Inventory Updating

↓

Eventually

↓

Everything Consistent
```

The system reaches a consistent state over time.

---

# 21. Production Architecture

```text
Order Service

↓

Order DB

↓

Outbox Table

↓

Kafka

↓

Inventory Service

↓

Inventory DB
```

---

# 22. Production Example

Customer places an order.

```text
Customer

↓

Order Service

↓

Save Order

↓

Save Outbox Event

↓

Kafka

↓

Payment Service

↓

Inventory Service

↓

Shipping Service
```

No distributed database transaction is required.

---

# 23. Production Debugging Story

Problem

Orders were successfully created.

However,

Inventory Service never received some `OrderCreated` events.

Investigation

The application crashed after committing the Order record but before sending the Kafka event.

Root Cause

Business data and event publishing were separate operations.

Fix

Implemented the Transactional Outbox Pattern.

Now:

* Order
* Outbox Event

are committed atomically.

A background publisher retries until Kafka acknowledges the event.

No events are lost.

---

# 24. Common Interview Traps

### Can `@Transactional` span multiple microservices?

❌ No.

It manages local transactions within a transactional resource, not distributed business workflows across independent services.

---

### Does Saga provide ACID consistency?

❌ No.

Saga provides **eventual consistency** using local transactions and compensating actions.

---

### Is compensation the same as rollback?

❌ No.

Compensation is a new business operation that reverses the business effect.

---

### Does the Outbox Pattern guarantee immediate delivery?

❌ No.

It guarantees reliable publication, not immediate delivery.

---

### Can duplicate events still occur?

✅ Yes.

Consumers should always be idempotent.

---

# 25. Senior-Level Follow-up Questions

1. Why don't ACID transactions scale across microservices?
2. Explain Saga Pattern.
3. Choreography vs Orchestration?
4. What is a compensating transaction?
5. What is eventual consistency?
6. Explain the Transactional Outbox Pattern.
7. How do you prevent duplicate processing?
8. What happens if Kafka is unavailable?
9. Why is idempotency important?
10. When would you choose orchestration over choreography?

---

# 26. Real Interview Scenario

**Interviewer:**

> "An order was created successfully, but no payment event reached Kafka because the application crashed immediately after the database commit. How would you prevent this?"

### Strong Answer

> I'd implement the Transactional Outbox Pattern. During the same local database transaction that saves the order, I'd also write an event record into an Outbox table. A separate publisher process would reliably read pending Outbox records and publish them to Kafka, retrying if necessary. This ensures the business data and event publication remain consistent without requiring distributed transactions.

---

# 27. Cheat Sheet

| Concept              | Purpose                         |
| -------------------- | ------------------------------- |
| Local Transaction    | Transaction within one service  |
| Saga                 | Sequence of local transactions  |
| Compensation         | Business action to undo effects |
| Choreography         | Event-driven workflow           |
| Orchestration        | Central workflow controller     |
| Outbox               | Reliable event publishing       |
| Eventual Consistency | Data converges over time        |
| Idempotency          | Safe duplicate handling         |

---

## Saga Flow

```text
Order

↓

Payment

↓

Inventory

↓

Shipping

↓

Completed

OR

Compensating Actions
```

---

## Transactional Outbox

```text
Save Business Data

↓

Save Outbox Event

↓

Commit

↓

Publisher

↓

Kafka
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why not use `@Transactional` across all microservices?"**

Don't answer:

> "`@Transactional` doesn't work."

A senior-level answer is:

> "`@Transactional` provides local transaction management within a single transactional resource. In a microservices architecture, each service owns its own database and commits independently, so a single ACID transaction isn't practical across services. Instead, I'd use patterns such as Saga for business workflow coordination and the Transactional Outbox Pattern for reliable event publishing, accepting eventual consistency while ensuring the system can recover safely from failures."

That answer demonstrates an understanding of **distributed systems, data consistency, reliability, and enterprise architecture**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 59 – Distributed Caching & Session Management**

We'll cover:

* Local cache vs distributed cache
* Redis architecture
* Cache invalidation strategies
* Cache consistency
* Session replication
* Sticky sessions vs stateless authentication
* Redis clustering
* Cache warming
* Production debugging stories
* Senior interview questions
