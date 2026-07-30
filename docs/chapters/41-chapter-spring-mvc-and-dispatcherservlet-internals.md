# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 41: Spring MVC & DispatcherServlet Internals

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, VMware, Goldman Sachs, JP Morgan, Product Companies

---

# 1. Why Do Interviewers Ask This?

Every HTTP request in a Spring MVC or Spring Boot application passes through the **DispatcherServlet**.

When a client sends:

```http
GET /api/orders/1001
```

many developers think:

```text
Request

↓

Controller

↓

Response
```

But internally, Spring performs many steps:

* Request mapping
* Handler resolution
* Argument binding
* Validation
* Message conversion
* Exception handling
* Response serialization

Understanding this flow is essential for debugging production issues.

Typical interview questions:

* What is DispatcherServlet?
* Explain the Spring MVC request lifecycle.
* What is HandlerMapping?
* What is HandlerAdapter?
* How does `@RequestBody` work?
* How is JSON converted into Java objects?

---

# 2. 30-Second Interview Answer

> DispatcherServlet is the front controller of Spring MVC. Every HTTP request first reaches the DispatcherServlet, which delegates to HandlerMapping to locate the appropriate controller, uses a HandlerAdapter to invoke it, processes request and response bodies through HttpMessageConverters, handles exceptions when necessary, and finally returns the HTTP response to the client.

---

# 3. High-Level Request Flow

```text
Client

↓

DispatcherServlet

↓

HandlerMapping

↓

HandlerAdapter

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Response

↓

DispatcherServlet

↓

Client
```

This is one of the most important Spring interview diagrams.

---

# 4. What is DispatcherServlet?

DispatcherServlet is the **Front Controller** of Spring MVC.

Instead of every controller handling HTTP requests independently,

all requests first arrive here.

```text
Browser

↓

DispatcherServlet

↓

Spring MVC
```

Benefits:

* Centralised request processing
* Uniform exception handling
* Flexible routing
* Extensibility

---

# 5. Example Controller

```java
@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping("/{id}")
    public Order getOrder(
            @PathVariable Long id) {

        return service.findById(id);

    }
}
```

When the request arrives,

Spring must discover

* Which controller?
* Which method?
* What parameter values?

---

# 6. Step 1 – Request Arrives

Client sends

```http
GET /orders/100
```

Tomcat receives it.

↓

Forwards it to

```text
DispatcherServlet
```

---

# 7. Step 2 – HandlerMapping

Interview favourite.

DispatcherServlet asks

```text
Which Controller

Handles

/orders/100 ?
```

HandlerMapping searches registered mappings.

Result

```text
OrderController#getOrder()
```

---

# 8. Step 3 – HandlerAdapter

Interview favourite.

DispatcherServlet knows

which method

must execute.

But

different handler types may exist.

HandlerAdapter knows

how to invoke

the selected handler.

```text
DispatcherServlet

↓

HandlerAdapter

↓

Controller Method
```

---

# 9. Why HandlerAdapter Exists?

Imagine Spring supported

* Annotation Controllers
* Legacy Controllers
* Functional Endpoints

DispatcherServlet doesn't need to understand every style.

Each HandlerAdapter understands its own handler type.

This keeps Spring extensible.

---

# 10. Step 4 – Argument Resolution

Controller

```java
@GetMapping("/{id}")
public Order getOrder(
        @PathVariable Long id) {
```

Spring automatically resolves

```text
@PathVariable

↓

100

↓

Long
```

Other examples:

* `@RequestParam`
* `@RequestHeader`
* `@CookieValue`
* `@RequestBody`

---

# 11. Step 5 – @RequestBody

Interview favourite.

Suppose

Client sends

```json
{
  "name":"Laptop",
  "price":1500
}
```

Controller

```java
@PostMapping
public void create(
        @RequestBody Product product) {
}
```

Spring converts JSON

↓

Java Object

Automatically.

---

# 12. HttpMessageConverter

Who performs JSON conversion?

```text
HttpMessageConverter
```

Flow

```text
JSON

↓

Jackson

↓

Product Object
```

For responses

```text
Product Object

↓

Jackson

↓

JSON
```

Spring Boot configures Jackson automatically if it is on the classpath.

---

# 13. Request Lifecycle

```text
HTTP Request

↓

DispatcherServlet

↓

HandlerMapping

↓

HandlerAdapter

↓

Argument Resolver

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Controller

↓

HttpMessageConverter

↓

JSON Response

↓

Client
```

---

# 14. What Happens After Controller Returns?

Suppose

```java
return order;
```

Spring performs

```text
Order Object

↓

HttpMessageConverter

↓

JSON

↓

HTTP Response
```

No manual JSON conversion required.

---

# 15. Exception Handling

Suppose

```java
throw new OrderNotFoundException();
```

DispatcherServlet delegates to

```text
HandlerExceptionResolver
```

which looks for

* `@ExceptionHandler`
* `@ControllerAdvice`
* Built-in exception resolvers

---

# 16. Example

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ResponseEntity<String> handle(
            OrderNotFoundException ex) {

        return ResponseEntity.notFound().build();

    }
}
```

Spring automatically converts the exception into an HTTP response.

---

# 17. What is ViewResolver?

Traditional Spring MVC

```text
Controller

↓

"home"

↓

ViewResolver

↓

home.jsp
```

For REST APIs,

ViewResolver is generally **not** involved because the response body is written directly using `HttpMessageConverter`.

---

# 18. Complete MVC Architecture

```text
Client

↓

Tomcat

↓

DispatcherServlet

↓

HandlerMapping

↓

HandlerAdapter

↓

Argument Resolver

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

HttpMessageConverter

↓

HTTP Response
```

---

# 19. Production Example

REST API

```http
POST /orders
```

↓

DispatcherServlet

↓

Jackson converts JSON

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Order Object

↓

Jackson converts

↓

JSON Response

↓

Client

---

# 20. Production Debugging Story

Problem

API returns

```text
415 Unsupported Media Type
```

Investigation

Request

```http
Content-Type: text/plain
```

Controller expected

```java
@RequestBody Product
```

Root Cause

Spring couldn't find a suitable `HttpMessageConverter` for the request's content type.

Fix

Client sent

```http
Content-Type: application/json
```

The request succeeded.

---

# 21. Common Interview Traps

### Does DispatcherServlet call controllers directly?

❌ No.

It delegates through HandlerMapping and HandlerAdapter.

---

### Does `@RequestBody` use Reflection?

Indirectly, yes.

Spring uses Jackson, which relies on reflection (and other mechanisms) to create and populate Java objects.

---

### Does every request create a new DispatcherServlet?

❌ No.

Typically, one DispatcherServlet instance handles many requests concurrently.

---

### Does ViewResolver handle REST APIs?

❌ Generally no.

REST responses use `HttpMessageConverter`.

---

### Can DispatcherServlet handle exceptions?

✅ Yes.

Through `HandlerExceptionResolver` implementations.

---

# 22. Senior-Level Follow-up Questions

1. Explain the complete Spring MVC request lifecycle.
2. What is DispatcherServlet?
3. What is HandlerMapping?
4. Why does Spring need HandlerAdapter?
5. How does `@RequestBody` work?
6. What is HttpMessageConverter?
7. How are exceptions handled?
8. What is ViewResolver?
9. How does Jackson integrate with Spring?
10. How would you debug a request that never reaches the controller?

---

# 23. Real Interview Scenario

**Interviewer:**

> "A REST endpoint is returning HTTP 415 (Unsupported Media Type). How would you investigate?"

### Strong Answer

> I'd first verify the request's `Content-Type` header and compare it with what the controller expects. If the endpoint uses `@RequestBody`, Spring requires an appropriate `HttpMessageConverter` for that media type. I'd also check whether Jackson is on the classpath, review any custom message converter configuration, and inspect the application logs to determine why the request couldn't be deserialized.

---

# 24. Cheat Sheet

| Component                | Responsibility                         |
| ------------------------ | -------------------------------------- |
| DispatcherServlet        | Front Controller                       |
| HandlerMapping           | Finds the correct controller method    |
| HandlerAdapter           | Invokes the handler                    |
| Argument Resolver        | Resolves method parameters             |
| HttpMessageConverter     | Converts request/response bodies       |
| HandlerExceptionResolver | Handles exceptions                     |
| ViewResolver             | Resolves views (MVC, not typical REST) |

---

## Request Flow

```text
Client

↓

DispatcherServlet

↓

HandlerMapping

↓

HandlerAdapter

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

HttpMessageConverter

↓

Client
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does a Spring MVC request reach the controller?"**

Don't answer:

> "DispatcherServlet calls the controller."

A senior-level answer is:

> "Every request first reaches the DispatcherServlet, which acts as the Front Controller. It consults a HandlerMapping to identify the appropriate controller method, delegates invocation to a HandlerAdapter, resolves method arguments such as `@PathVariable` and `@RequestBody`, executes the controller, and finally uses HttpMessageConverters to serialize the response. Exceptions are handled through HandlerExceptionResolvers before the response is sent back to the client."

That answer demonstrates a clear understanding of the **complete Spring MVC request pipeline**, rather than only the controller layer.

---

## Next Chapter

**Chapter 42 – Spring Security Internals (Authentication, Authorization & Filter Chain)**

We'll cover:

* Spring Security architecture
* Filter chain internals
* Authentication vs Authorization
* SecurityContext
* AuthenticationManager
* UserDetailsService
* JWT authentication flow
* OAuth2 basics
* Method security
* Production debugging scenarios
* Senior interview questions

This is one of the most frequently asked Spring Security topics in senior backend interviews because almost every enterprise application uses it.
