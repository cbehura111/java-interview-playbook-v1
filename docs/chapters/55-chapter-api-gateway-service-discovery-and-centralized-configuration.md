# Part IX – Enterprise Design & Microservices

# Chapter 55: API Gateway, Service Discovery & Centralized Configuration

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

A system with hundreds of microservices cannot have clients calling each service directly.

Questions arise:

* How does a client know which service to call?
* What if service IP addresses change?
* How are authentication and rate limiting enforced?
* How are configurations managed across services?

This is why **API Gateways**, **Service Discovery**, and **Centralized Configuration** are essential.

Typical interview questions:

* What is an API Gateway?
* Why is service discovery needed?
* What is Eureka?
* Client-side vs Server-side discovery?
* What is Spring Cloud Config?
* How does configuration refresh work?

---

# 2. 30-Second Interview Answer

> An API Gateway acts as the single entry point for client requests, handling routing, authentication, rate limiting, and other cross-cutting concerns. Service Discovery allows services to locate each other dynamically instead of using fixed IP addresses. Centralized Configuration stores application configuration in one place, enabling consistent configuration management across environments and services.

---

# 3. Without API Gateway

```text
Client

↓

User Service

↓

Order Service

↓

Payment Service

↓

Inventory Service

↓

Notification Service
```

Problems:

* Client must know every service URL
* Multiple authentication implementations
* Complex client logic
* Difficult version management

---

# 4. With API Gateway

```text
                Client
                   │
                   ▼
             API Gateway
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
User Service   Order Service  Payment Service
```

Clients communicate only with the gateway.

---

# 5. Responsibilities of an API Gateway

Interview favourite.

An API Gateway typically handles:

* Request routing
* Authentication
* Authorization
* SSL/TLS termination
* Rate limiting
* Load balancing
* Request/response transformation
* Logging
* Monitoring

---

# 6. API Request Flow

```text
Client

↓

API Gateway

↓

Authentication

↓

Routing

↓

Target Service

↓

Response
```

---

# 7. Spring Cloud Gateway

Interview favourite.

Spring Cloud Gateway is the recommended API Gateway solution in the Spring ecosystem.

Features:

* Route configuration
* Path rewriting
* Filters
* Circuit breaker integration
* Rate limiting
* Load balancing
* JWT authentication

---

# 8. Gateway Filters

Gateway filters can intercept every request.

```text
Incoming Request

↓

Authentication Filter

↓

Logging Filter

↓

Rate Limiter

↓

Routing Filter

↓

Target Service
```

Think of filters as middleware for incoming requests.

---

# 9. Why Service Discovery?

Interview favourite.

Suppose the Payment Service runs on:

```text
10.1.5.12:8080
```

After scaling:

```text
10.1.8.42:8080
```

Hardcoded addresses would fail.

Services need dynamic discovery.

---

# 10. Service Registry

```text
Payment Service

↓

Registers

↓

Service Registry

↓

API Gateway Queries Registry
```

A registry keeps track of available service instances.

---

# 11. Netflix Eureka

A popular (though now in maintenance mode) service registry.

Flow:

```text
Payment Service

↓

Register

↓

Eureka Server

↓

Gateway Discovers Service
```

Modern alternatives include Kubernetes Service Discovery, Consul, and cloud-provider-native discovery.

---

# 12. Client-Side Discovery

Interview favourite.

```text
Client

↓

Service Registry

↓

Select Instance

↓

Call Service
```

The client is responsible for selecting a service instance.

Example:

Spring Cloud LoadBalancer.

---

# 13. Server-Side Discovery

```text
Client

↓

Load Balancer/API Gateway

↓

Service Registry

↓

Target Service
```

The client knows only the gateway.

The gateway or load balancer chooses the service instance.

---

# 14. Load Balancing

Suppose three Payment Service instances exist.

```text
Gateway

↓

Payment-1

Payment-2

Payment-3
```

Requests are distributed among them.

Common algorithms:

* Round Robin
* Least Connections
* Weighted Routing
* Random

---

# 15. Centralized Configuration

Interview favourite.

Instead of storing configuration separately in every service:

```text
User Service

application.yml

Order Service

application.yml

Payment Service

application.yml
```

Use:

```text
Spring Cloud Config Server

↓

Git Repository

↓

All Services
```

---

# 16. Benefits of Centralized Configuration

* Single source of truth
* Easier environment management
* Version-controlled configuration
* Simplified updates
* Consistent configuration across services

---

# 17. Configuration Refresh

Suppose a timeout changes from:

```text
5 seconds

↓

15 seconds
```

Instead of redeploying every service:

```text
Git Update

↓

Config Server

↓

Refresh

↓

Updated Configuration
```

Spring supports refresh mechanisms (for example, with Spring Cloud Config and refresh endpoints) depending on the deployment model.

---

# 18. Secrets Management

Never store:

* Passwords
* API keys
* JWT signing keys
* Database credentials

directly in source code.

Use dedicated secret management solutions such as:

* HashiCorp Vault
* AWS Secrets Manager
* Azure Key Vault
* Kubernetes Secrets (with appropriate security controls)

---

# 19. Production Architecture

```text
                   Client
                      │
                      ▼
                API Gateway
                      │
          Service Discovery
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
 User Service    Order Service   Payment Service
      │               │               │
      └───────────────┼───────────────┘
                      │
                      ▼
              Config Server
                      │
                      ▼
                Git Repository
```

---

# 20. Production Example

E-commerce Platform

```text
Customer

↓

API Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service
```

Benefits:

* One public endpoint
* Central authentication
* Dynamic routing
* Easier monitoring

---

# 21. Production Debugging Story

Problem

After scaling the Payment Service, some requests failed.

Investigation

The API Gateway continued routing traffic to a terminated instance.

Root Cause

The service instance had not been removed promptly from the service registry due to delayed health status updates.

Fix

* Corrected health checks
* Tuned registry lease/heartbeat settings
* Improved instance deregistration

Traffic was routed only to healthy instances.

---

# 22. Common Interview Traps

### Is API Gateway mandatory?

❌ No.

Small systems may not require one.

---

### Should microservices communicate through the Gateway?

❌ Usually no.

Internal service-to-service communication generally occurs directly (or through a service mesh or messaging system), while external clients use the gateway.

---

### Can configuration be stored inside Docker images?

❌ Avoid this.

Keep configuration external to the application binary/image.

---

### Is Eureka the only discovery solution?

❌ No.

Kubernetes, Consul, AWS Cloud Map, and other platforms provide service discovery.

---

### Should secrets be stored in Git?

❌ No.

Use dedicated secret management solutions.

---

# 23. Senior-Level Follow-up Questions

1. Why use an API Gateway?
2. What is Spring Cloud Gateway?
3. Client-side vs Server-side discovery?
4. How does Eureka work?
5. What is centralized configuration?
6. How do you refresh configuration?
7. How do you secure secrets?
8. How does load balancing work?
9. How do services register themselves?
10. What happens if the registry is unavailable?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Your Payment Service was scaled from 2 to 10 instances, but users still experience uneven traffic distribution. How would you investigate?"

### Strong Answer

> I'd verify whether all instances are successfully registered in the service registry and passing health checks. Next, I'd examine the API Gateway or load balancer configuration to confirm that it is discovering all healthy instances and applying the expected load-balancing algorithm. I'd also review gateway metrics, service registration logs, and health endpoint responses to identify stale registrations or failed instances.

---

# 25. Cheat Sheet

| Component             | Purpose                   |
| --------------------- | ------------------------- |
| API Gateway           | Single entry point        |
| Spring Cloud Gateway  | Gateway implementation    |
| Service Discovery     | Dynamic service location  |
| Eureka                | Service registry          |
| Load Balancer         | Distributes requests      |
| Config Server         | Centralized configuration |
| Git                   | Configuration versioning  |
| Vault/Secrets Manager | Secure secret storage     |

---

## Request Flow

```text
Client

↓

API Gateway

↓

Authentication

↓

Service Discovery

↓

Target Service

↓

Response
```

---

## Configuration Flow

```text
Git Repository

↓

Config Server

↓

Microservices

↓

Refresh Configuration
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why do we need an API Gateway in microservices?"**

Don't answer:

> "It routes requests."

A senior-level answer is:

> "An API Gateway provides a single entry point for external clients while centralizing cross-cutting concerns such as authentication, authorization, rate limiting, routing, request transformation, logging, and monitoring. Combined with service discovery, it dynamically routes traffic to healthy service instances without exposing internal network topology. This simplifies clients and improves security, scalability, and operational control."

That answer demonstrates an understanding of **enterprise architecture, distributed systems, and operational best practices**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 56 – Resilience Patterns (Circuit Breaker, Retry, Bulkhead & Timeout)**

We'll cover:

* Why distributed systems fail
* Timeouts and retry strategies
* Circuit Breaker pattern
* Bulkhead pattern
* Fallback mechanisms
* Rate limiting
* Resilience4j integration
* Common anti-patterns (retry storms, cascading failures)
* Production debugging stories
* Senior interview questions
