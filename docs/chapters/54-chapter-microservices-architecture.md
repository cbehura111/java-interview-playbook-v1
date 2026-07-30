# Part IX – Enterprise Design & Microservices

# Chapter 54: Microservices Architecture

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

Almost every modern enterprise application uses **Microservices Architecture**.

Interviewers want to assess whether you understand:

* Why companies moved away from monoliths
* When microservices are appropriate
* Their advantages and trade-offs
* Communication patterns
* Distributed system challenges
* Real production issues

Typical interview questions:

* Monolith vs Microservices?
* How do microservices communicate?
* What is Database per Service?
* Why are distributed transactions difficult?
* How do you handle failures between services?

---

# 2. 30-Second Interview Answer

> Microservices architecture decomposes an application into small, independently deployable services, each responsible for a specific business capability. Every service owns its data and communicates with other services through APIs or asynchronous messaging. This improves scalability, independent deployment, and team autonomy, but introduces challenges such as distributed transactions, network latency, service discovery, and observability.

---

# 3. What is a Monolith?

A monolithic application contains all business functionality in a single deployable unit.

```text
+--------------------------------------+
|            Monolithic App            |
|--------------------------------------|
| User Module                          |
| Order Module                         |
| Payment Module                       |
| Inventory Module                     |
| Notification Module                  |
+--------------------------------------+
                 │
                 ▼
            Single Database
```

Everything is deployed together.

---

# 4. Problems with Monoliths

As applications grow:

* Slow deployments
* Large codebases
* Difficult scaling
* Tight coupling
* Higher release risk
* Technology lock-in

Example:

A small change in the Notification module requires redeploying the entire application.

---

# 5. What are Microservices?

Instead of one application:

```text
User Service

Order Service

Payment Service

Inventory Service

Notification Service
```

Each service:

* Owns one business capability
* Can be deployed independently
* Has its own codebase
* Owns its own data

---

# 6. Microservices Architecture

```text
                    Client
                      │
                      ▼
                API Gateway
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
 User Service    Order Service   Product Service
      │               │               │
      ▼               ▼               ▼
 User DB         Order DB       Product DB
                      │
                      ▼
              Payment Service
                      │
                      ▼
                 Payment DB
```

---

# 7. Characteristics of Microservices

* Small, focused services
* Independent deployment
* Independent scaling
* Database ownership
* Technology flexibility (where appropriate)
* Fault isolation
* Team autonomy

---

# 8. Database per Service

Interview favourite.

Each service owns its own database.

```text
Order Service
      │
      ▼
Order Database

Payment Service
      │
      ▼
Payment Database

Inventory Service
      │
      ▼
Inventory Database
```

No service should directly access another service's database.

---

# 9. Why Database per Service?

Benefits:

* Loose coupling
* Independent schema evolution
* Independent scaling
* Better ownership
* Improved security boundaries

---

# 10. Service Communication

Microservices communicate using:

### Synchronous

* REST
* gRPC

### Asynchronous

* Kafka
* RabbitMQ
* Amazon SQS

---

# 11. REST Communication

```text
Order Service

↓

HTTP Request

↓

Payment Service

↓

HTTP Response
```

Simple.

Easy to understand.

Can increase latency because services wait for responses.

---

# 12. Event-Driven Communication

Interview favourite.

```text
Order Created

↓

Kafka

↓

Inventory Service

↓

Notification Service

↓

Analytics Service
```

Producer and consumers are loosely coupled.

---

# 13. Benefits of Event-Driven Architecture

* Better scalability
* Loose coupling
* Improved resilience
* Easier integration
* Independent consumers

Trade-off:

Eventual consistency instead of immediate consistency.

---

# 14. Independent Deployment

One service can be upgraded without deploying others.

Example:

```text
Payment Service

Version 2

↓

Deploy

↓

No change to Order Service
```

---

# 15. Independent Scaling

High traffic?

Scale only the affected service.

Example

```text
Payment Service

10 Instances

Inventory Service

2 Instances
```

Much more efficient than scaling an entire monolith.

---

# 16. Challenges of Microservices

Interview favourite.

* Network latency
* Partial failures
* Distributed transactions
* Monitoring
* Security
* Service discovery
* Data consistency
* Increased operational complexity

---

# 17. Distributed Data Problem

Order Service

↓

Create Order

↓

Payment Service

↓

Payment Failed

Now what?

Unlike a monolith, there is no single local database transaction across services.

Solutions include:

* Saga Pattern
* Compensating Transactions
* Outbox Pattern

(These are covered in later chapters.)

---

# 18. Microservices Request Flow

```text
Client

↓

API Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service

↓

Notification Service
```

Every additional network call introduces latency and potential failure points.

---

# 19. Production Example

E-commerce Platform

```text
Customer

↓

Order Service

↓

Payment Service

↓

Inventory Service

↓

Shipping Service

↓

Notification Service
```

Each service is independently deployable and scalable.

---

# 20. Monolith vs Microservices

| Feature                | Monolith           | Microservices        |
| ---------------------- | ------------------ | -------------------- |
| Deployment             | Single             | Independent          |
| Scaling                | Entire application | Individual service   |
| Database               | Usually shared     | Database per service |
| Codebase               | Single             | Multiple             |
| Fault Isolation        | Lower              | Higher               |
| Operational Complexity | Lower              | Higher               |
| Team Ownership         | Shared             | Independent          |

---

# 21. Production Debugging Story

Problem

Users reported that orders were created but payment confirmations were missing.

Investigation

Distributed traces showed:

```text
Order Service

↓

Payment Service

↓

Timeout
```

The Order Service created the order successfully, but the synchronous call to the Payment Service timed out.

Root Cause

A temporary database issue caused slow responses in the Payment Service.

Fix

* Added request timeouts
* Implemented retries with backoff where appropriate
* Added a circuit breaker
* Moved confirmation notifications to asynchronous events

The system became more resilient to downstream failures.

---

# 22. Common Interview Traps

### Are microservices always better?

❌ No.

They introduce significant operational complexity and are not suitable for every application.

---

### Should all services share one database?

❌ No.

Each service should own its data.

---

### Can one service directly update another service's database?

❌ No.

Communication should occur through APIs or events.

---

### Is REST the only communication mechanism?

❌ No.

gRPC, Kafka, RabbitMQ, and other messaging systems are common choices.

---

### Do microservices guarantee high availability?

❌ No.

High availability requires resilient design, redundancy, monitoring, and fault handling.

---

# 23. Senior-Level Follow-up Questions

1. Monolith vs Microservices?
2. When should you choose microservices?
3. Why database per service?
4. Synchronous vs asynchronous communication?
5. What is eventual consistency?
6. How do services discover each other?
7. How do you handle partial failures?
8. How do you secure service-to-service communication?
9. What are the biggest operational challenges?
10. How do you monitor hundreds of services?

---

# 24. Real Interview Scenario

**Interviewer:**

> "A company with a simple CRUD application wants to migrate immediately to 50 microservices. Would you recommend it?"

### Strong Answer

> Not necessarily. Microservices solve organisational and scalability challenges but also introduce distributed systems complexity, including network failures, service discovery, observability, and data consistency concerns. For a small application with a single team and modest scaling needs, a well-structured modular monolith is often a better choice. I'd migrate to microservices only when there is a clear business or technical justification.

---

# 25. Cheat Sheet

| Concept                | Key Idea                        |
| ---------------------- | ------------------------------- |
| Monolith               | Single deployable application   |
| Microservice           | Independent business capability |
| Database per Service   | Each service owns its data      |
| REST                   | Synchronous communication       |
| Kafka/RabbitMQ         | Asynchronous communication      |
| Independent Deployment | Deploy services separately      |
| Independent Scaling    | Scale only what needs it        |
| Eventual Consistency   | Data converges over time        |

---

## Microservices Architecture

```text
Client

↓

API Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service

↓

Notification Service
```

---

## Database Ownership

```text
User Service
     │
 User DB

Order Service
     │
 Order DB

Payment Service
     │
 Payment DB
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why do companies move from monoliths to microservices?"**

Don't answer:

> "Because microservices are more scalable."

A senior-level answer is:

> "Microservices enable independent deployment, scaling, and ownership of business capabilities, allowing teams to work autonomously and release features faster. However, they also introduce distributed systems challenges such as network latency, partial failures, observability, and data consistency. That's why microservices should be adopted only when their benefits outweigh the added operational complexity."

This answer demonstrates an understanding of **architecture trade-offs rather than simply advocating microservices**, which is what senior interviewers look for.

---

## Next Chapter

**Chapter 55 – API Gateway, Service Discovery & Centralized Configuration**

We'll cover:

* Why API Gateways are needed
* Spring Cloud Gateway
* Netflix Eureka and service discovery concepts
* Client-side vs server-side discovery
* Load balancing
* Centralized configuration with Spring Cloud Config
* Dynamic configuration refresh
* Secrets management
* Production architecture and debugging stories
* Senior interview questions
