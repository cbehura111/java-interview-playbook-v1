# Part IX – Enterprise Design & Microservices

# Chapter 52: Design Patterns Every Senior Java Engineer Should Know

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

Most developers know design pattern definitions.

Senior engineers know:

* When to use them
* When not to use them
* Which patterns Spring Boot already uses
* How patterns solve production problems

Interviewers frequently ask:

* Explain Factory Pattern.
* Difference between Factory and Builder?
* Where does Spring use Proxy?
* How is Strategy used in Spring?
* Which patterns do you use daily?

---

# 2. 30-Second Interview Answer

> Design patterns are proven solutions to recurring software design problems. In enterprise Java, patterns such as Factory, Builder, Strategy, Proxy, Template Method, Observer, Decorator, and Singleton are widely used. Spring Framework internally relies on many of these patterns, especially Factory, Proxy, Strategy, and Template Method, making them essential for senior Java developers.

---

# 3. Design Pattern Categories

The **Gang of Four (GoF)** patterns are grouped into three categories.

| Category   | Purpose            |
| ---------- | ------------------ |
| Creational | Object creation    |
| Structural | Object composition |
| Behavioral | Object interaction |

---

# 4. Creational Patterns

These focus on creating objects.

Common patterns:

* Singleton
* Factory Method
* Abstract Factory
* Builder
* Prototype

---

# 5. Singleton Pattern

Interview favourite.

Ensures only one instance exists.

Example

```java
public class CacheManager {

    private static final CacheManager INSTANCE =
            new CacheManager();

    private CacheManager() { }

    public static CacheManager getInstance() {
        return INSTANCE;
    }
}
```

---

### Where Spring Uses It

Most Spring beans are **singleton-scoped by default**.

Important:

A Spring Singleton is **one instance per ApplicationContext**, **not** the classic GoF JVM-wide Singleton.

---

# 6. Factory Pattern

Interview favourite.

Instead of

```java
new EmailService();
```

Use

```text
Factory

↓

Creates Correct Object
```

Example

```java
interface PaymentProcessor {

    void pay();

}
```

```java
class PaymentFactory {

    PaymentProcessor create(String type) {

        ...

    }

}
```

---

### Spring Example

```text
BeanFactory

↓

Creates Beans
```

Spring's `BeanFactory` and `ApplicationContext` are examples of the Factory Pattern.

---

# 7. Builder Pattern

Interview favourite.

Instead of

```java
User user =
new User(
"Alice",
25,
"London",
...
);
```

Use

```java
User user =
User.builder()
    .name("Alice")
    .age(25)
    .city("London")
    .build();
```

Benefits:

* Readability
* Immutability
* Optional fields
* Cleaner APIs

---

### Spring Example

Common examples include:

* `RestTemplateBuilder`
* `WebClient.Builder`
* `UriComponentsBuilder`

---

# 8. Prototype Pattern

Creates new objects by copying existing ones.

Example

```text
Original Object

↓

Clone

↓

Modified Copy
```

Useful when object creation is expensive.

---

### Spring Example

Prototype bean scope:

```java
@Scope("prototype")
```

A new bean instance is created for each request from the container.

---

# 9. Structural Patterns

These organize classes and objects.

Common patterns:

* Adapter
* Decorator
* Facade
* Proxy
* Composite

---

# 10. Adapter Pattern

Interview favourite.

Allows incompatible interfaces to work together.

```text
Application

↓

Adapter

↓

External API
```

Example:

Converting data from a third-party API into your domain model.

---

### Spring Example

`HandlerAdapter` in Spring MVC adapts different handler types so `DispatcherServlet` can invoke them uniformly.

---

# 11. Decorator Pattern

Adds behaviour without modifying existing code.

```text
Service

↓

Logging Decorator

↓

Caching Decorator

↓

Target Service
```

Unlike inheritance,

behaviour is added dynamically.

---

### Java Example

```text
InputStream

↓

BufferedInputStream
```

---

# 12. Facade Pattern

Provides a simplified interface.

Instead of

```text
Inventory

Payment

Shipping

Notification
```

Expose

```text
OrderFacade

↓

Everything Happens
```

Client code becomes simpler.

---

### Enterprise Example

Order placement APIs often act as facades over multiple internal services.

---

# 13. Proxy Pattern

Interview favourite.

```text
Client

↓

Proxy

↓

Real Object
```

Proxy can add:

* Transactions
* Security
* Logging
* Lazy loading
* Caching

---

### Spring Examples

Spring uses proxies for:

* `@Transactional`
* `@Async`
* `@Cacheable`
* Spring Security method interception
* Spring AOP

---

# 14. Behavioral Patterns

Focus on communication between objects.

Common patterns:

* Strategy
* Observer
* Command
* Template Method
* Chain of Responsibility

---

# 15. Strategy Pattern

Interview favourite.

Instead of

```text
if...

else...

else...
```

Use

```text
Strategy Interface

↓

Card Strategy

UPI Strategy

Wallet Strategy
```

Spring injects the required implementation.

---

### Spring Example

Different `PaymentProcessor` implementations injected by type or qualifier.

---

# 16. Observer Pattern

Objects subscribe to events.

```text
Publisher

↓

Observers

↓

Notification
```

---

### Spring Example

* `ApplicationEventPublisher`
* `@EventListener`

---

# 17. Template Method Pattern

Defines the algorithm structure while allowing subclasses to customize steps.

```text
Template

↓

Step 1

↓

Custom Step

↓

Step 3
```

---

### Spring Example

* `JdbcTemplate`
* `RestTemplate`
* `RedisTemplate`

These provide a fixed workflow while allowing custom callbacks.

---

# 18. Chain of Responsibility

Request passes through multiple handlers.

```text
Request

↓

Filter 1

↓

Filter 2

↓

Filter 3

↓

Controller
```

---

### Spring Examples

* Spring Security Filter Chain
* Servlet Filters
* Handler Interceptors

---

# 19. Design Patterns Used Inside Spring

| Pattern                 | Spring Example                |
| ----------------------- | ----------------------------- |
| Singleton               | Default bean scope            |
| Factory                 | BeanFactory                   |
| Builder                 | WebClient.Builder             |
| Proxy                   | `@Transactional`, AOP         |
| Strategy                | Multiple bean implementations |
| Observer                | Application Events            |
| Template Method         | JdbcTemplate                  |
| Adapter                 | HandlerAdapter                |
| Chain of Responsibility | Security Filter Chain         |

---

# 20. Production Example

Payment System

Instead of

```text
Huge if-else
```

Use

```text
PaymentProcessor

↓

CardProcessor

↓

UPIProcessor

↓

WalletProcessor

↓

CryptoProcessor
```

Adding new payment methods requires creating a new implementation rather than modifying existing code.

---

# 21. Production Debugging Story

Problem

Every new payment method required editing a 600-line method.

Each release introduced regressions.

Root Cause

Business logic depended on a long chain of `if-else` statements.

Fix

Refactored to the Strategy Pattern.

Each payment method became an independent implementation.

Benefits:

* Easier testing
* Better extensibility
* Fewer regressions

---

# 22. Common Interview Traps

### Is Singleton thread-safe?

❌ Not always.

A correctly implemented eager singleton is thread-safe, but singleton **objects** still need thread-safe internal state if accessed concurrently.

---

### Is Factory the same as Builder?

❌ No.

Factory decides **which object** to create.

Builder decides **how to construct** a complex object.

---

### Is Proxy inheritance?

❌ No.

A proxy controls access to another object. JDK dynamic proxies use interfaces, while CGLIB creates subclasses.

---

### Is Strategy just polymorphism?

Strategy uses polymorphism **plus runtime selection of algorithms**.

---

### Does Spring use all GoF patterns?

❌ No.

It uses many extensively, but not every pattern.

---

# 23. Senior-Level Follow-up Questions

1. Which design patterns does Spring use internally?
2. Factory vs Builder?
3. Adapter vs Facade?
4. Proxy vs Decorator?
5. Template Method vs Strategy?
6. Why does Spring use proxies?
7. Which pattern is used in Spring Security?
8. How does `JdbcTemplate` implement Template Method?
9. Where have you used Strategy in production?
10. Which design patterns are overused?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Your application has hundreds of `if-else` statements to determine business behaviour. How would you improve it?"

### Strong Answer

> I'd first determine whether the branching represents interchangeable business rules. If it does, I'd replace the conditional logic with the Strategy Pattern by defining a common interface and separate implementations for each algorithm. Spring's Dependency Injection can manage these implementations, making the code easier to extend, test, and maintain while following the Open/Closed Principle.

---

# 25. Cheat Sheet

| Pattern                 | Purpose                     | Spring Example        |
| ----------------------- | --------------------------- | --------------------- |
| Singleton               | Single instance             | Default bean scope    |
| Factory                 | Object creation             | BeanFactory           |
| Builder                 | Complex object construction | WebClient.Builder     |
| Adapter                 | Interface conversion        | HandlerAdapter        |
| Decorator               | Add behaviour               | BufferedInputStream   |
| Facade                  | Simplified interface        | OrderFacade           |
| Proxy                   | Access control              | `@Transactional`      |
| Strategy                | Multiple algorithms         | PaymentProcessor      |
| Observer                | Event notification          | `@EventListener`      |
| Template Method         | Fixed workflow              | JdbcTemplate          |
| Chain of Responsibility | Sequential processing       | Security Filter Chain |

---

## Pattern Classification

```text
Creational
↓

Singleton
Factory
Builder
Prototype

----------------

Structural
↓

Adapter
Decorator
Facade
Proxy

----------------

Behavioral
↓

Strategy
Observer
Template
Chain
```

---

## Spring Pattern Map

```text
Spring Framework

↓

BeanFactory → Factory

↓

@Transactional → Proxy

↓

JdbcTemplate → Template Method

↓

ApplicationEventPublisher → Observer

↓

HandlerAdapter → Adapter

↓

Security Filters → Chain of Responsibility
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Which design patterns are used in Spring Boot?"**

Don't simply list pattern names.

A senior-level answer is:

> "Spring heavily relies on GoF design patterns. `BeanFactory` implements the Factory Pattern, singleton bean scope reflects the Singleton Pattern, `@Transactional`, `@Async`, and `@Cacheable` are implemented using the Proxy Pattern, `JdbcTemplate` uses the Template Method Pattern, application events implement the Observer Pattern, `HandlerAdapter` follows the Adapter Pattern, and the Spring Security filter chain is an example of the Chain of Responsibility Pattern. These patterns work together with Dependency Injection to build flexible and maintainable enterprise applications."

This answer demonstrates that you understand **not just the theory of design patterns, but also how major enterprise frameworks apply them in practice**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 53 – REST API Design Best Practices**

We'll cover:

* REST principles
* Resource modeling
* HTTP methods and idempotency
* Status codes
* Versioning strategies
* Pagination, filtering, and sorting
* HATEOAS (when and why)
* API security
* API documentation (OpenAPI/Swagger)
* Production API design mistakes
* Senior interview questions
