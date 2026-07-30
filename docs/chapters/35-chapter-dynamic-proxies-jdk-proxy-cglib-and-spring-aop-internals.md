# Part VII – Class Loading, Reflection & Dynamic Proxies

# Chapter 35: Dynamic Proxies (JDK Proxy, CGLIB & Spring AOP Internals)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, VMware, Spring Framework, Banking Product Companies

---

# 1. Why Do Interviewers Ask This?

Almost every Spring Boot application uses Dynamic Proxies.

Examples:

* `@Transactional`
* `@Cacheable`
* `@Async`
* `@Retryable`
* `@Validated`
* Spring Security
* Logging AOP

Most developers use these annotations daily without understanding what happens internally.

Typical interview questions:

* What is a Dynamic Proxy?
* Why does Spring create proxies?
* JDK Proxy vs CGLIB?
* Why doesn't `@Transactional` work sometimes?
* What is self-invocation?

---

# 2. 30-Second Interview Answer

> A Dynamic Proxy is an object generated at runtime that wraps another object and intercepts method calls. Spring uses proxies to implement Aspect-Oriented Programming (AOP), enabling features such as transactions, caching, logging, and security without modifying business logic. Spring uses JDK Dynamic Proxies for interface-based beans and CGLIB proxies for class-based beans.

---

# 3. Why Do We Need Proxies?

Suppose we have

```java
public class PaymentService {

    public void transfer() {

        // Business Logic

    }

}
```

Now we need

* Logging
* Security
* Transactions
* Monitoring
* Audit

Without proxies

```java
public void transfer() {

    startTransaction();

    log();

    authenticate();

    // Business Logic

    commit();

}
```

Business code becomes cluttered.

---

# 4. Solution

Separate

Business Logic

from

Cross-Cutting Concerns

Using

```text
Proxy
```

---

# 5. Proxy Architecture

```text
          Client

             │

             ▼

        Proxy Object

             │

     Before Advice

             │

             ▼

      Real Object

             │

      After Advice
```

The client talks to the proxy instead of the real object.

---

# 6. Static Proxy

Manually written.

Example

```java
class PaymentProxy
        implements PaymentService {

    private PaymentService target;

    public void transfer() {

        log();

        target.transfer();

    }

}
```

Problems

* Too much boilerplate
* Difficult to maintain
* Doesn't scale

---

# 7. Dynamic Proxy

Generated automatically at runtime.

No handwritten proxy class required.

JVM generates the proxy.

---

# 8. JDK Dynamic Proxy

Works

Only

for

Interfaces.

Example

```java
public interface PaymentService {

    void transfer();

}
```

Implementation

```java
public class PaymentServiceImpl
        implements PaymentService {

}
```

Spring creates

```text
PaymentService Proxy

↓

PaymentServiceImpl
```

---

# 9. JDK Proxy Flow

```text
Client

↓

Proxy

↓

InvocationHandler

↓

Real Object
```

Every method call passes through the `InvocationHandler`.

---

# 10. InvocationHandler

Core interface.

```java
public Object invoke(

    Object proxy,

    Method method,

    Object[] args

)
```

This method intercepts every invocation.

---

# 11. Example

```java
public Object invoke(...) {

    System.out.println("Before");

    Object result =
        method.invoke(target,args);

    System.out.println("After");

    return result;

}
```

This is the foundation of many AOP frameworks.

---

# 12. Limitation of JDK Proxy

Interview Favourite.

Suppose

```java
public class PaymentService {

}
```

No interface.

JDK Proxy

❌ Cannot create a proxy.

Need

```text
CGLIB
```

---

# 13. CGLIB

CGLIB creates a **subclass** at runtime.

Example

```text
PaymentService

↓

Generated Subclass

↓

Intercept Methods
```

Unlike JDK proxies,

it doesn't require interfaces.

---

# 14. CGLIB Architecture

```text
Client

↓

Generated Subclass

↓

Original Class
```

Method interception happens in the generated subclass.

---

# 15. Limitations of CGLIB

Cannot proxy

```java
final class PaymentService
```

because

```text
Final Class

↓

Cannot Extend
```

Similarly,

```java
final void transfer()
```

cannot be overridden,

so it cannot be intercepted.

---

# 16. Spring Proxy Selection

Interview Favourite.

If bean implements

Interface

↓

Use

```text
JDK Dynamic Proxy
```

Otherwise

↓

Use

```text
CGLIB
```

> **Note:** Modern Spring versions can also be configured to use CGLIB even when interfaces exist (for example, with `proxyTargetClass=true`).

---

# 17. Spring AOP Flow

Suppose

```java
@Transactional

public void transfer()
```

Execution

```text
Client

↓

Spring Proxy

↓

Begin Transaction

↓

Business Method

↓

Commit

↓

Return
```

The business method never manages the transaction directly.

---

# 18. How @Transactional Works

Internally

```text
Method Called

↓

Proxy Intercepts

↓

Open Transaction

↓

Execute Method

↓

Commit

↓

Rollback (If Needed)
```

Exactly the same idea applies to:

* `@Cacheable`
* `@Async`
* `@Retryable`

---

# 19. Self-Invocation Problem

One of the most common Spring interview questions.

Example

```java
@Service

class PaymentService {

    public void methodA() {

        methodB();

    }

    @Transactional

    public void methodB() {

    }

}
```

Question

Will transaction start?

Answer

❌ No.

---

# 20. Why?

Because

```text
methodA()

↓

Direct Call

↓

methodB()
```

The call never goes through

```text
Spring Proxy
```

No interception.

No transaction.

---

# 21. Correct Flow

```text
Client

↓

Proxy

↓

methodB()
```

Proxy intercepts.

Transaction starts.

---

# 22. Common Solutions

* Move the transactional method to another Spring bean.
* Call through the Spring proxy instead of `this`.
* Use AspectJ weaving when proxy-based AOP is insufficient.

The first option is usually the cleanest.

---

# 23. Performance

Interview Question

Are proxies slow?

Generally,

No.

The overhead is small compared to:

* Database calls
* HTTP requests
* Disk I/O

Avoid using proxy-based interception inside extremely performance-sensitive tight loops.

---

# 24. Byte Buddy

Modern runtime code generation library.

Used by

* Mockito
* Hibernate (in some scenarios)
* Various Java agents
* Instrumentation frameworks

Advantages

* Modern API
* Flexible bytecode generation
* Easier than ASM for many use cases

---

# 25. JDK Proxy vs CGLIB

| Feature                | JDK Proxy                     | CGLIB            |
| ---------------------- | ----------------------------- | ---------------- |
| Requires Interface     | ✅ Yes                         | ❌ No             |
| Works with Classes     | ❌ No                          | ✅ Yes            |
| Creates                | Proxy implementing interfaces | Runtime subclass |
| Can Proxy Final Class  | ❌ No                          | ❌ No             |
| Can Proxy Final Method | ❌ No                          | ❌ No             |

---

# 26. Production Example

Spring Boot Request

```text
Controller

↓

Service Proxy

↓

Transaction Starts

↓

Business Logic

↓

Repository

↓

Commit

↓

Return Response
```

Developers see only

```java
@Transactional
```

Spring handles everything else.

---

# 27. Production Debugging Story

Problem

Developer reports:

```text
@Transactional

Not Working
```

Investigation

Code

```java
methodA()

↓

methodB()
```

Both methods

inside

same class.

Root Cause

Self-invocation bypassed the Spring proxy.

Fix

Move `methodB()` to another Spring-managed bean so that the call goes through the proxy.

---

# 28. Common Interview Traps

### Does Spring modify your original class?

❌ No.

Spring creates a proxy around it.

---

### Is every Spring bean proxied?

❌ No.

Only beans requiring proxy-based features (AOP, transactions, caching, async, security, etc.) are proxied.

---

### Does JDK Proxy require interfaces?

✅ Yes.

---

### Can CGLIB proxy a final class?

❌ No.

---

### Why does self-invocation fail?

Because the call bypasses the proxy.

---

# 29. Senior-Level Follow-up Questions

1. What is a Dynamic Proxy?
2. Difference between Static and Dynamic Proxy?
3. JDK Proxy vs CGLIB?
4. How does `@Transactional` work?
5. Explain self-invocation.
6. Why can't CGLIB proxy final classes?
7. Why does Spring use proxies?
8. What is `InvocationHandler`?
9. What is Byte Buddy?
10. How would you debug a transaction that isn't starting?

---

# 30. Real Interview Scenario

**Interviewer:**

> "A method annotated with `@Transactional` isn't starting a transaction. What would you check?"

### Strong Answer

> First, I'd verify that the bean is managed by Spring and that transaction management is enabled. Then I'd check whether the method is being called through the Spring proxy. A common issue is self-invocation, where one method in a class directly calls another `@Transactional` method using `this`, bypassing the proxy. I'd also verify the method's visibility, transaction configuration, and logs to ensure the proxy is actually being created.

---

# 31. Cheat Sheet

| Concept           | Purpose                                 |
| ----------------- | --------------------------------------- |
| Dynamic Proxy     | Runtime method interception             |
| JDK Proxy         | Interface-based proxy                   |
| CGLIB             | Subclass-based proxy                    |
| InvocationHandler | Handles intercepted method calls        |
| Spring AOP        | Implements cross-cutting concerns       |
| `@Transactional`  | Transaction management via proxies      |
| Self-invocation   | Bypasses proxy, so advice isn't applied |

---

## Proxy Flow

```text
Client

↓

Proxy

↓

Before Advice

↓

Business Method

↓

After Advice
```

---

## Spring Decision

```text
Interface?

↓

YES

↓

JDK Proxy

---------------

NO

↓

CGLIB
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does `@Transactional` work internally?"**

Don't simply answer:

> "Spring starts a transaction."

A senior-level answer is:

> "Spring creates a proxy around the bean. When a client invokes a `@Transactional` method through that proxy, the proxy delegates to a transaction interceptor, which starts a transaction before invoking the target method. Depending on the outcome, it commits or rolls back the transaction. Because this mechanism is proxy-based by default, internal self-invocation bypasses the proxy and prevents transaction interception."

That answer demonstrates a solid understanding of **Spring AOP, proxy internals, and transaction management**, which is exactly what senior Java backend interviewers expect.

---

## Next Chapter

**Chapter 36 – Java Annotations, Annotation Processing & Spring Boot Internals**

We'll cover:

* Built-in annotations
* Meta-annotations (`@Target`, `@Retention`, `@Inherited`, `@Documented`, `@Repeatable`)
* Custom annotations
* Runtime annotation processing
* Compile-time annotation processing (APT)
* How Spring scans annotations
* How Lombok works
* How MapStruct generates code
* Production use cases
* Senior interview questions
