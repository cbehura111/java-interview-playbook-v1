# Part IX – Enterprise Design & Microservices

# Chapter 51: SOLID Principles Revisited for Enterprise Applications

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

Many developers can **recite the SOLID principles**, but far fewer can **apply them effectively in large enterprise systems**.

Interviewers are evaluating whether you can:

* Design maintainable systems
* Reduce code coupling
* Improve extensibility
* Build testable applications
* Refactor legacy code

Typical interview questions:

* Explain SOLID with real examples.
* Which SOLID principle is violated here?
* How does Spring Boot support SOLID?
* How do Design Patterns relate to SOLID?
* When can SOLID be overused?

---

# 2. 30-Second Interview Answer

> SOLID is a set of five object-oriented design principles that improve maintainability, flexibility, and testability. In Spring Boot, Dependency Injection naturally supports the Dependency Inversion Principle, interfaces help achieve the Open/Closed Principle, and small focused services follow the Single Responsibility Principle. Applying SOLID correctly results in loosely coupled, highly cohesive systems that are easier to extend and test.

---

# 3. What is SOLID?

SOLID consists of five principles:

| Principle | Meaning                         |
| --------- | ------------------------------- |
| S         | Single Responsibility Principle |
| O         | Open/Closed Principle           |
| L         | Liskov Substitution Principle   |
| I         | Interface Segregation Principle |
| D         | Dependency Inversion Principle  |

Think of SOLID as **guidelines**, not strict rules.

---

# 4. S — Single Responsibility Principle (SRP)

> **A class should have only one reason to change.**

Bad example:

```java
public class OrderService {

    public void createOrder() { }

    public void sendEmail() { }

    public void generateInvoice() { }

    public void writeAuditLog() { }

}
```

Problems:

* Business logic
* Email
* Reporting
* Auditing

All mixed together.

---

# 5. Better Design

```text
OrderService
      │
      ├── EmailService
      ├── InvoiceService
      └── AuditService
```

Each service has one clear responsibility.

---

# 6. Enterprise Example

Instead of

```text
OrderService
```

doing everything,

Split into

```text
OrderService

↓

InventoryService

↓

PaymentService

↓

NotificationService

↓

AuditService
```

Much easier to maintain.

---

# 7. O — Open/Closed Principle (OCP)

> **Software should be open for extension but closed for modification.**

Bad example

```java
if(paymentType.equals("CARD")) {

}

else if(paymentType.equals("UPI")) {

}

else if(paymentType.equals("PAYPAL")) {

}
```

Every new payment method requires modifying existing code.

---

# 8. Better Design

```java
public interface PaymentProcessor {

    void pay();

}
```

Implementations

```text
CardPayment

UPIPayment

PayPalPayment
```

Spring injects the required implementation.

Adding Apple Pay?

Create another implementation.

Existing code remains unchanged.

---

# 9. L — Liskov Substitution Principle (LSP)

> **Subtypes should be replaceable for their base type without changing program correctness.**

Example

```java
interface NotificationService {

    void send();

}
```

Implementations

```text
EmailNotification

SMSNotification

PushNotification
```

The caller should work correctly regardless of which implementation is injected.

Violation occurs when a subclass changes expected behaviour or throws unsupported-operation exceptions.

---

# 10. I — Interface Segregation Principle (ISP)

> **Clients should not depend on methods they do not use.**

Bad example

```java
interface Worker {

    void work();

    void eat();

    void sleep();

}
```

A robot worker should not be forced to implement `eat()` or `sleep()`.

Better:

```text
Workable

Eatable

Sleepable
```

Small, focused interfaces.

---

# 11. D — Dependency Inversion Principle (DIP)

Interview favourite.

High-level modules should depend on **abstractions**, not concrete implementations.

Bad

```java
OrderService service =
    new OrderService(
        new EmailService());
```

Good

```java
@Service
public class OrderService {

    private final NotificationService notificationService;

    public OrderService(
        NotificationService notificationService) {

        this.notificationService = notificationService;

    }

}
```

Spring injects the implementation.

---

# 12. How Spring Boot Supports SOLID

| SOLID | Spring Feature                    |
| ----- | --------------------------------- |
| SRP   | Service-based architecture        |
| OCP   | Interfaces + Bean implementations |
| LSP   | Bean substitution                 |
| ISP   | Small service interfaces          |
| DIP   | Dependency Injection              |

Spring naturally encourages SOLID when used correctly.

---

# 13. SOLID in a Typical Spring Boot Application

```text
Controller

↓

Service Interface

↓

Service Implementation

↓

Repository Interface

↓

Database
```

Each layer has a focused responsibility.

---

# 14. Common SOLID Violations

### God Class

```text
OrderService

↓

2,500 lines

↓

Everything happens here
```

Hard to maintain and test.

---

### Tight Coupling

```java
new EmailService()
```

inside business logic.

Hard to replace or mock.

---

### Fat Interfaces

```java
interface PaymentService {

    30 methods

}
```

Most implementations use only a few methods.

---

### Business Logic in Controllers

Controllers should coordinate requests, not contain business rules.

---

# 15. SOLID and Unit Testing

Good SOLID design makes testing easier.

```java
@Mock
NotificationService notificationService;

@InjectMocks
OrderService orderService;
```

Because dependencies are injected, they can easily be mocked.

---

# 16. SOLID and Design Patterns

SOLID often works together with design patterns.

| Principle | Common Pattern                 |
| --------- | ------------------------------ |
| SRP       | Facade                         |
| OCP       | Strategy                       |
| LSP       | Template Method                |
| ISP       | Adapter                        |
| DIP       | Factory + Dependency Injection |

Patterns help implement SOLID principles effectively.

---

# 17. Production Example

Payment System

Instead of

```text
PaymentService

↓

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

New payment types require no changes to existing processors.

---

# 18. Production Debugging Story

Problem

A new payment method was introduced.

Developers modified a large `if-else` block in `PaymentService`.

An existing payment type stopped working because of an unintended change.

Root Cause

Violation of the Open/Closed Principle.

Fix

Refactor to a `PaymentProcessor` interface with one implementation per payment type.

Future additions required only new implementations.

---

# 19. Common Interview Traps

### Does SOLID mean more classes?

❌ Not necessarily.

The goal is maintainability, not maximizing the number of classes.

---

### Should every class have an interface?

❌ No.

Use interfaces where multiple implementations, testing, or abstraction provide value.

---

### Is Dependency Injection the same as Dependency Inversion?

❌ No.

Dependency Injection is a technique.

Dependency Inversion is a design principle.

---

### Can SOLID be overused?

✅ Yes.

Over-abstraction can make simple code unnecessarily complex.

---

# 20. Senior-Level Follow-up Questions

1. Explain each SOLID principle with a Spring example.
2. How does Spring support DIP?
3. When should interfaces be avoided?
4. How do SOLID and Design Patterns complement each other?
5. What is a God Class?
6. How do you refactor legacy code using SOLID?
7. Which SOLID principle is most commonly violated?
8. Does microservices architecture automatically enforce SOLID?
9. Can SOLID reduce technical debt?
10. When would you intentionally break a SOLID principle?

---

# 21. Real Interview Scenario

**Interviewer:**

> "Your `OrderService` has grown to 3,000 lines and every new feature requires modifying it. How would you refactor it?"

### Strong Answer

> I'd first identify distinct responsibilities such as payment, inventory, notifications, pricing, and auditing. I'd extract each into focused services, introduce interfaces where multiple implementations are expected, and use constructor injection to decouple dependencies. This applies the Single Responsibility, Open/Closed, and Dependency Inversion principles while making the code easier to test and extend without modifying existing business logic.

---

# 22. Cheat Sheet

| Principle | Key Idea                       |
| --------- | ------------------------------ |
| SRP       | One responsibility per class   |
| OCP       | Extend without modifying       |
| LSP       | Subtypes must be substitutable |
| ISP       | Small, focused interfaces      |
| DIP       | Depend on abstractions         |

---

## SOLID Architecture

```text
Controller

↓

Service Interface

↓

Implementation

↓

Repository

↓

Database
```

---

## Dependency Inversion

```text
OrderService

↓

NotificationService (Interface)

↓

EmailService

SMSService

PushService
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does Spring Boot implement SOLID?"**

Don't answer:

> "Spring uses Dependency Injection."

A senior-level answer is:

> "Spring's constructor-based Dependency Injection naturally supports the Dependency Inversion Principle by depending on abstractions rather than concrete implementations. Interfaces and multiple bean implementations make systems open for extension, while separating controllers, services, repositories, and infrastructure components encourages the Single Responsibility Principle. Combined with patterns like Strategy and Factory, Spring enables highly modular, testable, and maintainable enterprise applications."

This answer demonstrates that you understand **both the design principles and how they're applied in real Spring Boot systems**, which is what senior interviewers expect.

---

## Next Chapter

**Chapter 52 – Design Patterns Every Senior Java Engineer Should Know**

We'll cover:

* Creational, Structural, and Behavioral patterns
* Singleton, Factory, Builder, Prototype
* Adapter, Decorator, Facade, Proxy
* Strategy, Observer, Command, Template Method
* Which patterns Spring Boot uses internally
* Real production examples
* Interview scenarios from FAANG and top product companies
