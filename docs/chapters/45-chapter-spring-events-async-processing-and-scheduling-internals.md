# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 45: Spring Events, Async Processing & Scheduling Internals

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, VMware, Goldman Sachs, JP Morgan, Product Companies

---

# 1. Why Do Interviewers Ask This?

Modern enterprise applications are **event-driven**.

Instead of tightly coupling services like this:

```text
OrderService

↓

EmailService

↓

InventoryService

↓

NotificationService

↓

AuditService
```

we publish an event.

```text
OrderService

↓

OrderCreatedEvent

↓

Email

Inventory

Audit

Notification
```

This creates a loosely coupled architecture that is easier to extend and maintain.

Typical interview questions:

* What are Spring Events?
* What is `ApplicationEventPublisher`?
* How does `@EventListener` work?
* Difference between synchronous and asynchronous events?
* How does `@Async` work internally?
* How does `@Scheduled` work?

---

# 2. 30-Second Interview Answer

> Spring provides an event-driven programming model using `ApplicationEventPublisher` and `@EventListener`. A publisher emits an event without knowing who will consume it, while listeners react independently. Events are synchronous by default but can be processed asynchronously with `@Async`. Spring also provides task scheduling through `@Scheduled`, backed by configurable executors and schedulers.

---

# 3. Why Use Events?

Without Events

```text
OrderService

↓

EmailService

↓

AuditService

↓

NotificationService
```

Problems:

* Tight coupling
* Difficult to extend
* Hard to test

---

With Events

```text
OrderService

↓

Publish Event

↓

Email Listener

Audit Listener

Inventory Listener

Notification Listener
```

Publisher knows nothing about consumers.

---

# 4. Event Architecture

```text
Publisher

↓

ApplicationEventPublisher

↓

ApplicationEventMulticaster

↓

Listener 1

Listener 2

Listener 3
```

This is the internal architecture used by Spring.

---

# 5. Publishing an Event

Example

```java
@Service
public class OrderService {

    private final ApplicationEventPublisher publisher;

    public OrderService(ApplicationEventPublisher publisher) {
        this.publisher = publisher;
    }

    public void createOrder(Order order) {

        // Save order...

        publisher.publishEvent(
                new OrderCreatedEvent(order));

    }
}
```

The publisher does not know who is listening.

---

# 6. Creating an Event

Since Spring 4.2, any object can be published as an event.

Example

```java
public class OrderCreatedEvent {

    private final Order order;

    public OrderCreatedEvent(Order order) {
        this.order = order;
    }

    public Order getOrder() {
        return order;
    }
}
```

---

# 7. Listening to Events

Example

```java
@Component
public class EmailListener {

    @EventListener
    public void handle(
            OrderCreatedEvent event) {

        // Send email

    }

}
```

Spring automatically registers the listener.

---

# 8. Event Flow

```text
Order Created

↓

publishEvent()

↓

ApplicationEventMulticaster

↓

Email Listener

↓

Inventory Listener

↓

Audit Listener
```

Every matching listener receives the event.

---

# 9. Synchronous Events

Interview favourite.

Default behaviour.

```text
Publisher

↓

Listener A

↓

Listener B

↓

Listener C

↓

Return
```

The publisher waits until all listeners finish.

Advantages:

* Simple
* Same transaction context
* Predictable execution

Disadvantage:

Slow listeners delay the publisher.

---

# 10. Asynchronous Events

Example

```java
@Async
@EventListener
public void handle(
        OrderCreatedEvent event) {

}
```

Flow

```text
Publisher

↓

Thread Pool

↓

Listener A

↓

Listener B

↓

Return Immediately
```

Publisher is no longer blocked.

---

# 11. @EnableAsync

Required to enable async processing.

```java
@Configuration
@EnableAsync
public class AsyncConfig {

}
```

Without it,

`@Async` has no effect.

---

# 12. How @Async Works Internally

Interview favourite.

```text
Caller

↓

Spring Proxy

↓

TaskExecutor

↓

Worker Thread

↓

Method Executes
```

Like `@Transactional` and `@Cacheable`, `@Async` is implemented using **Spring AOP proxies**.

---

# 13. TaskExecutor

Spring delegates asynchronous execution to a `TaskExecutor`.

Common implementation:

```text
ThreadPoolTaskExecutor
```

Benefits:

* Thread reuse
* Queue management
* Configurable pool size
* Better performance

Avoid creating new threads manually.

---

# 14. @Scheduled

Interview favourite.

Example

```java
@Scheduled(fixedRate = 5000)
public void refreshCache() {

}
```

Runs every five seconds (measured from the start of the previous execution).

---

# 15. Scheduling Options

```java
@Scheduled(fixedRate = 5000)
```

Runs every 5 seconds.

---

```java
@Scheduled(fixedDelay = 5000)
```

Runs 5 seconds after the previous execution completes.

---

```java
@Scheduled(cron = "0 0 2 * * *")
```

Runs every day at **2:00 AM**.

---

# 16. @EnableScheduling

Scheduling must be enabled.

```java
@Configuration
@EnableScheduling
public class SchedulerConfig {

}
```

---

# 17. Scheduler Internals

```text
Application Starts

↓

ScheduledAnnotationBeanPostProcessor

↓

Detect @Scheduled

↓

Register Task

↓

TaskScheduler

↓

Execute Periodically
```

Spring discovers scheduled methods during bean post-processing.

---

# 18. Thread Pool Configuration

Example

```java
@Bean
public ThreadPoolTaskExecutor executor() {

    ThreadPoolTaskExecutor executor =
            new ThreadPoolTaskExecutor();

    executor.setCorePoolSize(10);
    executor.setMaxPoolSize(20);
    executor.setQueueCapacity(100);

    return executor;
}
```

Proper sizing prevents excessive thread creation.

---

# 19. @TransactionalEventListener

Interview favourite.

Sometimes an event should be published

Only after

the transaction commits.

Example

```java
@TransactionalEventListener
public void handle(
        OrderCreatedEvent event) {

}
```

Benefits

```text
Database Commit

↓

Event Fired
```

If the transaction rolls back,

the listener is not invoked by default.

---

# 20. Production Example

Order Created

↓

Save Database

↓

Commit Transaction

↓

Publish Event

↓

Email

↓

Audit

↓

Inventory

↓

Notification

No direct coupling between services.

---

# 21. Production Debugging Story

Problem

Customers received confirmation emails.

But

Orders were **not** stored in the database.

Investigation

`publishEvent()` was called

before

the transaction completed.

Later,

the transaction rolled back.

Email had already been sent.

Root Cause

Using a normal `@EventListener` for post-transaction work.

Fix

Replace with

```java
@TransactionalEventListener
```

so the listener executes only after a successful transaction commit.

---

# 22. Common Interview Traps

### Are Spring events asynchronous?

❌ No.

By default, events are synchronous.

---

### Does `@Async` create a new thread every time?

❌ No.

It typically uses a thread pool managed by a `TaskExecutor`.

---

### Can `@Scheduled` methods be private?

❌ No.

Since scheduling relies on proxies, methods should be invocable by the proxy (public is the common and recommended approach).

---

### Does `@TransactionalEventListener` fire on rollback?

❌ Not by default.

The default phase is **AFTER_COMMIT**, though other phases can be configured.

---

### Is `@Async` applied during self-invocation?

❌ No.

Like other proxy-based features, self-invocation bypasses the proxy.

---

# 23. Senior-Level Follow-up Questions

1. Explain Spring Events.
2. How does `ApplicationEventPublisher` work?
3. What is `ApplicationEventMulticaster`?
4. Synchronous vs asynchronous events?
5. How does `@Async` work internally?
6. What is `ThreadPoolTaskExecutor`?
7. How does `@Scheduled` work?
8. Difference between `fixedRate` and `fixedDelay`?
9. What is `@TransactionalEventListener`?
10. When would you use events instead of direct method calls?

---

# 24. Real Interview Scenario

**Interviewer:**

> "A slow email service is delaying your order creation API. How would you improve it?"

### Strong Answer

> I'd decouple email sending from the request flow by publishing an `OrderCreatedEvent`. The order creation transaction would complete first, and an asynchronous listener would process email delivery using a `ThreadPoolTaskExecutor`. If the email should only be sent after a successful database commit, I'd use `@TransactionalEventListener` with the default `AFTER_COMMIT` phase to avoid sending emails for rolled-back transactions.

---

# 25. Cheat Sheet

| Component                     | Responsibility                              |
| ----------------------------- | ------------------------------------------- |
| `ApplicationEventPublisher`   | Publishes events                            |
| `@EventListener`              | Consumes events                             |
| `ApplicationEventMulticaster` | Dispatches events to listeners              |
| `@Async`                      | Executes methods asynchronously             |
| `ThreadPoolTaskExecutor`      | Executes async tasks                        |
| `@Scheduled`                  | Schedules recurring tasks                   |
| `@TransactionalEventListener` | Executes after transaction lifecycle events |

---

## Event Flow

```text
Business Logic

↓

publishEvent()

↓

ApplicationEventMulticaster

↓

Listeners

↓

Business Actions
```

---

## Async Flow

```text
Caller

↓

Spring Proxy

↓

ThreadPoolTaskExecutor

↓

Worker Thread

↓

Business Logic
```

---

## Scheduling Flow

```text
Application Startup

↓

Detect @Scheduled

↓

Register Tasks

↓

TaskScheduler

↓

Periodic Execution
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does `@Async` work internally?"**

Don't answer:

> "It runs the method in another thread."

A senior-level answer is:

> "`@Async` is implemented using Spring AOP. Spring creates a proxy around the target bean. When an external caller invokes an `@Async` method, the proxy submits the invocation to a configured `TaskExecutor`, such as `ThreadPoolTaskExecutor`. The caller returns immediately while a worker thread executes the target method. Because it's proxy-based, self-invocation bypasses asynchronous execution."

That answer demonstrates an understanding of **Spring AOP, proxy mechanics, thread pools, and asynchronous processing**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 46 – Spring Data JPA & Hibernate Internals**

We'll cover:

* JPA architecture
* Hibernate internals
* Entity lifecycle
* Persistence Context
* First-level vs Second-level cache
* Dirty checking
* Lazy vs Eager loading
* N+1 query problem
* Fetch strategies
* Production debugging scenarios
* Senior interview questions

This is one of the **highest-frequency interview topics** because nearly every enterprise Java application uses JPA/Hibernate, and senior engineers are expected to understand its internals-not just use repositories.
