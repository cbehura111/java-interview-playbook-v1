# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 38: Spring IoC Container & Dependency Injection Internals

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, VMware, Goldman Sachs, JP Morgan, Morgan Stanley, Product Companies

---

# 1. Why Do Interviewers Ask This?

Every Spring Boot application depends on the **IoC (Inversion of Control) Container**.

When you write:

```java
@Service
public class PaymentService {

}
```

or

```java
@Autowired
private OrderRepository repository;
```

many developers simply assume "Spring does the magic."

Senior engineers understand **what actually happens inside the Spring Container**.

Typical interview questions:

* What is IoC?
* What is Dependency Injection?
* How does Spring create beans?
* What is BeanFactory?
* What is ApplicationContext?
* What happens during Spring Boot startup?

---

# 2. 30-Second Interview Answer

> Spring's IoC Container is responsible for creating, configuring, wiring, and managing application objects known as beans. During application startup, Spring scans the classpath, creates bean definitions, instantiates beans, injects dependencies, applies BeanPostProcessors, and stores beans in the ApplicationContext. Dependency Injection is simply the mechanism by which the container provides required dependencies instead of objects creating them manually.

---

# 3. What is Inversion of Control (IoC)?

Without IoC

```java
public class PaymentService {

    private OrderRepository repository =
            new OrderRepository();

}
```

Problems:

* Tight coupling
* Difficult to test
* Hard to replace implementations

---

With IoC

```java
@Service
public class PaymentService {

    @Autowired
    private OrderRepository repository;

}
```

Now

Spring creates

↓

Spring injects

↓

Application uses

Control has been inverted from the application code to the container.

---

# 4. IoC Architecture

```text
Application

↓

Spring Container

↓

Create Objects

↓

Inject Dependencies

↓

Manage Lifecycle

↓

Return Beans
```

---

# 5. What is Dependency Injection (DI)?

Dependency Injection is one implementation of IoC.

Instead of

```java
PaymentService

↓

creates

↓

OrderRepository
```

It becomes

```text
Spring

↓

creates

↓

OrderRepository

↓

injects

↓

PaymentService
```

---

# 6. Types of Dependency Injection

Spring supports

### Constructor Injection

✅ Recommended

```java
@Service
public class PaymentService {

    private final OrderRepository repository;

    public PaymentService(
            OrderRepository repository) {

        this.repository = repository;
    }

}
```

---

### Setter Injection

```java
@Autowired
public void setRepository(
        OrderRepository repository) {

    this.repository = repository;
}
```

Useful for optional dependencies.

---

### Field Injection

```java
@Autowired
private OrderRepository repository;
```

Easy to write, but generally discouraged for new code because it makes testing and immutability harder.

---

# 7. Why Constructor Injection?

Interview Favourite.

Advantages:

* Mandatory dependencies
* Immutable fields
* Easier unit testing
* Detects circular dependencies earlier
* Preferred by Spring documentation

---

# 8. BeanFactory

The most basic Spring container.

Responsibilities:

* Create beans
* Manage bean lifecycle
* Dependency injection

Minimal features.

Rarely used directly in Spring Boot applications.

---

# 9. ApplicationContext

Most commonly used Spring container.

Extends BeanFactory.

Additional features:

* Internationalization (i18n)
* Event publishing
* Resource loading
* Environment abstraction
* Bean post-processing
* AOP integration

Almost every Spring Boot application uses an `ApplicationContext`.

---

# 10. BeanFactory vs ApplicationContext

| BeanFactory                  | ApplicationContext                        |
| ---------------------------- | ----------------------------------------- |
| Basic IoC container          | Full enterprise container                 |
| Lazy bean loading by default | Eager singleton initialization by default |
| Limited features             | Events, AOP, i18n, Environment, etc.      |
| Rarely used directly         | Used in almost all Spring Boot apps       |

---

# 11. Spring Boot Startup

Simplified flow

```text
main()

↓

SpringApplication.run()

↓

Create ApplicationContext

↓

Component Scan

↓

Read Annotations

↓

Create Bean Definitions

↓

Instantiate Beans

↓

Inject Dependencies

↓

BeanPostProcessors

↓

Application Ready
```

---

# 12. Component Scanning

Suppose

```java
@Service
class PaymentService {

}
```

Spring scans packages

↓

Finds

```text
@Service
```

↓

Registers Bean Definition

↓

Creates Bean

---

# 13. Bean Definition

Interview favourite.

Spring does not immediately create beans when scanning.

It first creates metadata.

Example metadata

```text
Bean Name

↓

Class

↓

Scope

↓

Constructor

↓

Dependencies

↓

Lifecycle Methods
```

This metadata is called a **Bean Definition**.

---

# 14. Bean Creation Lifecycle

```text
Scan Class

↓

Bean Definition

↓

Instantiate Object

↓

Inject Dependencies

↓

BeanPostProcessor

↓

Initialization

↓

Ready
```

---

# 15. How Dependency Injection Works

Suppose

```java
@Service
class PaymentService {

    private final OrderRepository repository;

    public PaymentService(
            OrderRepository repository) {

        this.repository = repository;
    }

}
```

Spring

↓

Looks for constructor

↓

Finds `OrderRepository`

↓

Creates repository bean (if needed)

↓

Calls constructor

↓

Stores bean

---

# 16. Circular Dependency

Interview favourite.

Example

```text
ServiceA

↓

depends on

↓

ServiceB

↓

depends on

↓

ServiceA
```

Result

```text
Circular Dependency
```

Constructor injection makes these cycles explicit and typically causes startup failure, encouraging better design.

---

# 17. Bean Scopes

Default

```text
Singleton
```

Other scopes

* Prototype
* Request
* Session
* Application
* WebSocket

---

## Singleton

One bean instance

```text
Application

↓

One PaymentService
```

Default Spring scope.

---

## Prototype

Every request for the bean creates a new instance.

```text
Request

↓

New Object
```

---

## Request Scope

One bean per HTTP request.

Common in Spring MVC.

---

## Session Scope

One bean per user session.

---

# 18. Singleton in Spring vs Singleton Pattern

Interview favourite.

Spring Singleton

```text
One Bean

Per ApplicationContext
```

GoF Singleton Pattern

```text
One Object

Per JVM (conceptually)
```

A Spring application can have multiple `ApplicationContext` instances, each with its own singleton beans.

---

# 19. Lazy Initialization

Normally

Spring eagerly creates singleton beans during startup.

With

```java
@Lazy
```

Creation happens

Only when the bean is first requested.

Useful for expensive or rarely used beans.

---

# 20. Production Example

Application Startup

```text
@SpringBootApplication

↓

Component Scan

↓

@Bean Definitions

↓

Singleton Beans

↓

Dependency Injection

↓

Ready
```

---

# 21. Production Debugging Story

Problem

Application failed during startup.

Error

```text
BeanCurrentlyInCreationException
```

Investigation

```text
PaymentService

↓

OrderService

↓

PaymentService
```

Root Cause

Circular dependency introduced through constructor injection.

Fix

Refactor responsibilities to remove the circular dependency (preferred), or redesign interactions rather than relying on workarounds.

---

# 22. Common Interview Traps

### Is IoC the same as Dependency Injection?

❌ No.

IoC is the design principle.

DI is one technique used to implement IoC.

---

### Does Spring create every bean immediately?

❌ Not every bean.

By default, singleton beans are eagerly initialized, while lazy beans and some scoped beans are created later.

---

### Is BeanFactory obsolete?

❌ No.

`ApplicationContext` builds upon `BeanFactory`; the latter remains the core abstraction.

---

### Is field injection recommended?

❌ Generally no.

Constructor injection is preferred for mandatory dependencies.

---

### Can Spring have multiple ApplicationContexts?

✅ Yes.

For example, parent-child contexts or multiple deployed applications.

---

# 23. Senior-Level Follow-up Questions

1. What is IoC?
2. Explain Dependency Injection.
3. BeanFactory vs ApplicationContext?
4. Why constructor injection?
5. Explain bean scopes.
6. What is a Bean Definition?
7. How does Spring discover beans?
8. What happens during startup?
9. What causes circular dependencies?
10. What is `@Lazy`?

---

# 24. Real Interview Scenario

**Interviewer:**

> "What exactly happens when Spring Boot starts?"

### Strong Answer

> The `main()` method calls `SpringApplication.run()`, which creates an `ApplicationContext`. Spring scans configured packages, identifies candidate components, creates bean definitions, instantiates singleton beans, resolves and injects dependencies, applies BeanPostProcessors and initialization callbacks, and finally publishes startup events before the application begins accepting requests.

---

# 25. Cheat Sheet

| Concept            | Purpose                            |
| ------------------ | ---------------------------------- |
| IoC                | Container controls object creation |
| DI                 | Container injects dependencies     |
| BeanFactory        | Core IoC container                 |
| ApplicationContext | Enterprise Spring container        |
| Bean Definition    | Metadata describing a bean         |
| Singleton          | One bean per ApplicationContext    |
| Prototype          | New bean each lookup               |
| `@Lazy`            | Deferred bean creation             |

---

## Spring Startup Flow

```text
main()

↓

SpringApplication.run()

↓

ApplicationContext

↓

Component Scan

↓

Bean Definitions

↓

Bean Creation

↓

Dependency Injection

↓

Bean Initialization

↓

Application Ready
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"What does the Spring IoC Container actually do?"**

Don't simply answer:

> "It manages beans."

A senior-level answer is:

> "The IoC container is responsible for the complete lifecycle of application objects. It discovers candidate classes, creates bean definitions, instantiates objects, resolves constructor and field dependencies, applies BeanPostProcessors and AOP proxies where required, manages bean scopes and lifecycle callbacks, and exposes fully initialized beans through the `ApplicationContext`. This centralised management enables loose coupling, easier testing, and consistent lifecycle management."

That answer demonstrates a deep understanding of **Spring internals**, not just annotation usage.

---

## Next Chapter

**Chapter 39 – Spring Bean Lifecycle & BeanPostProcessor Internals**

We'll cover:

* Complete bean lifecycle
* `InitializingBean`
* `DisposableBean`
* `@PostConstruct`
* `@PreDestroy`
* BeanPostProcessor
* BeanFactoryPostProcessor
* Configuration class enhancement
* How Spring creates AOP proxies
* Real production debugging scenarios

This is one of the most frequently asked Spring internals topics because it explains **how Spring transforms ordinary Java objects into fully managed beans with transactions, caching, security, and other enterprise features**.
