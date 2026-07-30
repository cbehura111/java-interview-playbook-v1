# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 47: Spring Transaction Management & `@Transactional` Internals

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Product Companies

---

# 1. Why Do Interviewers Ask This?

Transactions are the backbone of every enterprise application.

Consider a money transfer:

```text
Account A

↓

Debit £100

↓

Credit Account B
```

If the debit succeeds but the credit fails,

the banking system becomes inconsistent.

Transactions guarantee that either **all operations succeed or none of them do**.

Typical interview questions:

* What is `@Transactional`?
* How does Spring implement transactions?
* What is transaction propagation?
* What are isolation levels?
* Why does `@Transactional` sometimes not work?
* What causes `UnexpectedRollbackException`?

---

# 2. 30-Second Interview Answer

> Spring manages transactions using AOP proxies. When a method annotated with `@Transactional` is invoked through the Spring proxy, a transaction is started before the method executes. If the method completes successfully, the transaction is committed. If a rollback-triggering exception occurs, the transaction is rolled back. Spring also supports propagation rules and isolation levels to control how transactions behave across method calls.

---

# 3. What is a Transaction?

A transaction is a logical unit of work.

Example

```text
Transfer Money

↓

Debit Account

↓

Credit Account

↓

Commit
```

If anything fails

↓

Rollback

---

# 4. ACID Properties

Interview favourite.

### A — Atomicity

All operations succeed

OR

None succeed.

---

### C — Consistency

Database remains valid before and after the transaction.

---

### I — Isolation

Concurrent transactions should not interfere improperly with one another.

---

### D — Durability

Once committed,

data survives crashes and restarts.

---

# 5. Transaction Flow

```text
Method Call

↓

Transaction Begins

↓

Business Logic

↓

SQL Operations

↓

Commit

OR

Rollback
```

---

# 6. @Transactional

Example

```java
@Service
public class PaymentService {

    @Transactional
    public void transfer() {

        debit();

        credit();

    }

}
```

Spring manages the transaction automatically.

---

# 7. How @Transactional Works Internally

Interview favourite.

```text
Caller

↓

Spring Proxy

↓

Begin Transaction

↓

Target Method

↓

Commit

OR

Rollback
```

Like `@Async` and `@Cacheable`, transaction management is implemented using **Spring AOP proxies**.

---

# 8. Transaction Manager

Spring delegates transaction management to a `PlatformTransactionManager`.

Common implementations:

* `DataSourceTransactionManager`
* `JpaTransactionManager`
* `JtaTransactionManager`
* `R2dbcTransactionManager`

Responsibilities:

* Begin transaction
* Commit
* Rollback
* Suspend/resume transactions

---

# 9. Propagation

Interview favourite.

Propagation defines

**what happens when a transactional method calls another transactional method**.

---

# 10. REQUIRED (Default)

```java
@Transactional
```

Behaviour

```text
Existing Transaction?

↓

YES

↓

Join It

---------------

NO

↓

Create New Transaction
```

Most commonly used.

---

# 11. REQUIRES_NEW

Creates a completely new transaction.

```text
Outer Transaction

↓

Suspend

↓

New Transaction

↓

Commit

↓

Resume Outer Transaction
```

Useful for:

* Audit logging
* Notification history
* Independent operations

---

# 12. SUPPORTS

```text
Transaction Exists?

↓

YES

↓

Join

---------------

NO

↓

Execute Without Transaction
```

Suitable for read operations that can work with or without a transaction.

---

# 13. MANDATORY

```text
Transaction Exists?

↓

YES

↓

Continue

---------------

NO

↓

Throw Exception
```

---

# 14. NEVER

```text
Transaction Exists?

↓

YES

↓

Throw Exception

---------------

NO

↓

Execute Normally
```

---

# 15. NOT_SUPPORTED

```text
Transaction Exists?

↓

Suspend

↓

Execute Without Transaction

↓

Resume
```

Useful when transactional overhead is unnecessary.

---

# 16. Propagation Summary

| Propagation   | Behaviour                    |
| ------------- | ---------------------------- |
| REQUIRED      | Join existing or create new  |
| REQUIRES_NEW  | Always new transaction       |
| SUPPORTS      | Join if available            |
| MANDATORY     | Must already exist           |
| NEVER         | Fail if transaction exists   |
| NOT_SUPPORTED | Suspend existing transaction |

---

# 17. Isolation Levels

Interview favourite.

Isolation controls

how concurrent transactions interact.

---

### READ_UNCOMMITTED

May read uncommitted changes.

Fastest

Least safe.

---

### READ_COMMITTED

Can only read committed data.

Default in many databases.

Prevents dirty reads.

---

### REPEATABLE_READ

Reading the same row twice returns the same committed value within the transaction.

Prevents dirty reads and non-repeatable reads.

---

### SERIALIZABLE

Highest isolation.

Transactions behave as if executed one after another.

Safest

Slowest.

---

# 18. Common Concurrency Problems

### Dirty Read

Transaction A reads

Uncommitted data

from Transaction B.

---

### Non-Repeatable Read

Same query

↓

Different result

because another transaction updated the row.

---

### Phantom Read

Query

```sql
SELECT * FROM orders
```

Later

Same query

↓

Additional rows appear because another transaction inserted matching data.

---

# 19. Rollback Rules

Interview favourite.

By default

Spring rolls back for:

* `RuntimeException`
* `Error`

It does **not** automatically roll back for checked exceptions.

Example

```java
@Transactional(
    rollbackFor = Exception.class
)
```

Customises rollback behaviour.

---

# 20. Self Invocation Problem

Interview favourite.

```java
public void process() {

    save();

}
```

```java
@Transactional
public void save() {

}
```

Problem

```text
Same Class

↓

No Proxy

↓

No Transaction
```

Solution

Call the method through another Spring bean (or otherwise ensure the proxy is used).

---

# 21. Transaction Lifecycle

```text
Client

↓

Spring Proxy

↓

Begin Transaction

↓

Business Logic

↓

Flush

↓

Commit

↓

Release Connection
```

---

# 22. Production Example

Money Transfer

↓

Begin Transaction

↓

Debit Account

↓

Credit Account

↓

Commit

If credit fails

↓

Rollback debit.

---

# 23. Production Debugging Story

Problem

Audit records were saved

even though

the main business transaction rolled back.

Investigation

Audit service used

```java
@Transactional(
    propagation = REQUIRES_NEW
)
```

Root Cause

Audit operations executed in an independent transaction.

The audit committed successfully while the outer transaction rolled back.

Fix

Decide whether audit logs should be independent (keep `REQUIRES_NEW`) or part of the main business transaction (use the default `REQUIRED`).

---

# 24. Common Interview Traps

### Does `@Transactional` always work?

❌ No.

It works only when the method is invoked through the Spring proxy.

---

### Does every exception trigger rollback?

❌ No.

By default, only unchecked exceptions (`RuntimeException` and `Error`) trigger rollback.

---

### Can private methods be transactional?

❌ Generally no.

Proxy-based transaction management cannot intercept private methods.

---

### Does `REQUIRES_NEW` join an existing transaction?

❌ No.

It suspends the current transaction and starts a new one.

---

### Is `SERIALIZABLE` always the best choice?

❌ No.

It offers the strongest isolation but can significantly reduce throughput due to locking and contention.

---

# 25. Senior-Level Follow-up Questions

1. How does `@Transactional` work internally?
2. What is `PlatformTransactionManager`?
3. Explain transaction propagation.
4. Explain isolation levels.
5. Dirty read vs non-repeatable read vs phantom read?
6. Why doesn't `@Transactional` work during self-invocation?
7. Why do checked exceptions not roll back by default?
8. What is `UnexpectedRollbackException`?
9. When would you use `REQUIRES_NEW`?
10. How would you debug transaction issues?

---

# 26. Real Interview Scenario

**Interviewer:**

> "Your `@Transactional` method is updating the database even after an exception is thrown. How would you investigate?"

### Strong Answer

> I'd first determine whether the exception is checked or unchecked, because Spring rolls back only for unchecked exceptions by default. Next, I'd verify that the method is being invoked through the Spring proxy rather than via self-invocation. I'd also check for custom rollback rules (`rollbackFor` or `noRollbackFor`), transaction propagation settings, and application logs to confirm whether the transaction actually committed or was marked rollback-only.

---

# 27. Cheat Sheet

| Concept                      | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| `@Transactional`             | Declarative transaction management       |
| `PlatformTransactionManager` | Begins, commits, rolls back transactions |
| REQUIRED                     | Join existing or create new              |
| REQUIRES_NEW                 | Independent transaction                  |
| READ_COMMITTED               | Prevents dirty reads                     |
| REPEATABLE_READ              | Prevents dirty and non-repeatable reads  |
| SERIALIZABLE                 | Highest isolation                        |
| `rollbackFor`                | Configure rollback rules                 |

---

## Transaction Flow

```text
Client

↓

Spring Proxy

↓

Begin Transaction

↓

Business Logic

↓

Commit

OR

Rollback
```

---

## Propagation

```text
Outer Transaction

↓

Inner Method

↓

Join Existing

OR

Create New

OR

Suspend
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does `@Transactional` actually work?"**

Don't answer:

> "Spring starts a transaction."

A senior-level answer is:

> "`@Transactional` is implemented using Spring AOP. Spring creates a proxy around the target bean. When a transactional method is invoked through that proxy, it delegates transaction management to a `PlatformTransactionManager`, which begins a transaction before the business method executes. When the method completes, Spring either commits or rolls back the transaction based on the outcome and configured rollback rules. Because it's proxy-based, self-invocation and private methods are common reasons why transactions don't behave as expected."

That answer demonstrates a deep understanding of **Spring AOP, transaction lifecycle, propagation, isolation, and proxy mechanics**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 48 – Spring Boot Actuator, Monitoring & Observability**

We'll cover:

* Spring Boot Actuator internals
* Health indicators
* Metrics with Micrometer
* Prometheus integration
* Grafana dashboards
* Distributed tracing (Micrometer Tracing/OpenTelemetry)
* Logging correlation IDs (MDC)
* Custom health indicators
* Production monitoring best practices
* Senior interview questions
