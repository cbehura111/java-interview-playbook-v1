# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 43: Spring Boot Exception Handling, Validation & REST Error Design

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Product Companies

---

# 1. Why Do Interviewers Ask This?

In production systems, **handling failures correctly is just as important as implementing business logic**.

A well-designed REST API should:

* Return meaningful HTTP status codes
* Avoid exposing internal implementation details
* Provide consistent error responses
* Validate requests before business logic executes
* Log errors appropriately

Interviewers frequently ask:

* How does Spring handle exceptions?
* What is `@ControllerAdvice`?
* How does `@Valid` work?
* Difference between `400`, `401`, `403`, `404`, `409`, and `500`?
* How should REST APIs return errors?

---

# 2. 30-Second Interview Answer

> Spring handles exceptions through the `HandlerExceptionResolver` mechanism. `@ControllerAdvice` provides centralized exception handling across controllers, while `@ExceptionHandler` maps specific exceptions to HTTP responses. Request validation is typically performed using Jakarta Bean Validation with `@Valid`, and Spring Boot 3 supports RFC-compliant error responses using `ProblemDetail`. A good REST API returns consistent, meaningful error responses with appropriate HTTP status codes.

---

# 3. Exception Flow

```text
HTTP Request

↓

DispatcherServlet

↓

Controller

↓

Service

↓

Exception

↓

HandlerExceptionResolver

↓

@ControllerAdvice

↓

HTTP Response
```

The exception does **not** go directly back to the client.

---

# 4. Default Spring Behaviour

Example

```java
@GetMapping("/{id}")
public Order getOrder(Long id) {

    throw new RuntimeException();

}
```

Without custom handling

↓

Spring returns

```text
HTTP 500

Internal Server Error
```

Often with a generic error body.

---

# 5. @ExceptionHandler

Handles specific exceptions.

Example

```java
@ExceptionHandler(
        OrderNotFoundException.class)
public ResponseEntity<String> handle(
        OrderNotFoundException ex) {

    return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body("Order not found");
}
```

Only handles exceptions matching the declared type.

---

# 6. @ControllerAdvice

Interview favourite.

Instead of duplicating exception handling

inside every controller,

Spring provides

```java
@ControllerAdvice
```

for centralized handling.

---

# 7. Example

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(
            OrderNotFoundException.class)

    public ResponseEntity<String> handle(
            OrderNotFoundException ex) {

        return ResponseEntity.notFound().build();

    }

}
```

Now

Every controller

uses the same exception handler.

---

# 8. Why Use Global Exception Handling?

Benefits:

* Consistent error format
* Less duplicate code
* Easier maintenance
* Centralised logging
* Better client experience

---

# 9. Common HTTP Status Codes

| Code | Meaning                                                                    |
| ---- | -------------------------------------------------------------------------- |
| 200  | Success                                                                    |
| 201  | Created                                                                    |
| 204  | No Content                                                                 |
| 400  | Bad Request                                                                |
| 401  | Unauthorized (authentication required or failed)                           |
| 403  | Forbidden (authenticated but not permitted)                                |
| 404  | Not Found                                                                  |
| 409  | Conflict                                                                   |
| 422  | Unprocessable Content (used by some APIs for semantic validation failures) |
| 500  | Internal Server Error                                                      |

---

# 10. Request Validation

Interview favourite.

Example

```java
public class CreateOrderRequest {

    @NotBlank
    private String customer;

    @Positive
    private Integer quantity;

}
```

Controller

```java
@PostMapping
public void create(

    @Valid

    @RequestBody
    CreateOrderRequest request) {

}
```

Spring validates the request

Before

the controller executes.

---

# 11. Bean Validation

Common annotations

| Annotation        | Purpose                     |
| ----------------- | --------------------------- |
| `@NotNull`        | Cannot be null              |
| `@NotBlank`       | Non-empty string            |
| `@NotEmpty`       | Collection/String not empty |
| `@Positive`       | Value > 0                   |
| `@PositiveOrZero` | Value ≥ 0                   |
| `@Negative`       | Value < 0                   |
| `@Size`           | Length constraints          |
| `@Email`          | Email validation            |
| `@Pattern`        | Regular expression          |

These come from **Jakarta Bean Validation**.

---

# 12. Validation Flow

```text
JSON Request

↓

@RequestBody

↓

@Valid

↓

Bean Validation

↓

Valid?

↓

YES

↓

Controller

---------------

NO

↓

Validation Exception

↓

@ControllerAdvice

↓

400 Response
```

---

# 13. MethodArgumentNotValidException

Interview favourite.

Thrown when

```java
@Valid
```

fails.

Example

```json
{
  "quantity": -5
}
```

↓

Validation fails

↓

`MethodArgumentNotValidException`

↓

HTTP 400

---

# 14. Returning Validation Errors

Instead of

```text
Validation Failed
```

Return something useful.

Example

```json
{
  "timestamp": "...",
  "status": 400,
  "errors": [
    "quantity must be positive",
    "customer must not be blank"
  ]
}
```

This is far more helpful to API consumers.

---

# 15. Custom Business Exceptions

Example

```java
public class
OrderAlreadyExistsException
        extends RuntimeException {

}
```

Handler

```java
@ExceptionHandler(
        OrderAlreadyExistsException.class)
```

Return

```text
409 Conflict
```

Appropriate for resource conflicts.

---

# 16. ProblemDetail (Spring Boot 3)

Interview favourite.

Spring Framework 6 / Boot 3 introduced

```java
ProblemDetail
```

Based on

```text
RFC 9457
```

Example

```java
ProblemDetail detail =
    ProblemDetail.forStatus(
        HttpStatus.NOT_FOUND);

detail.setTitle("Order Not Found");

detail.setDetail(
    "Order 1001 does not exist.");
```

Provides a standardised error response structure.

---

# 17. Example Response

```json
{
  "type": "about:blank",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order 1001 does not exist"
}
```

Much more structured than plain text.

---

# 18. Logging Exceptions

Interview favourite.

Don't do

```java
catch(Exception e) {

}
```

Exception disappears.

Instead

```java
log.error(
    "Unable to process order {}",
    orderId,
    ex);
```

Log the exception with context and let the global handler produce the HTTP response where appropriate.

---

# 19. Production Example

Client

↓

POST

```json
{
  "quantity": -10
}
```

↓

Validation

↓

Fails

↓

Global Exception Handler

↓

HTTP 400

↓

Structured JSON Response

---

# 20. Production Debugging Story

Problem

Client always received

```text
500 Internal Server Error
```

Investigation

Business exception

```java
OrderNotFoundException
```

had no matching exception handler.

Spring treated it as an unhandled exception.

Fix

Add

```java
@ControllerAdvice
```

with

```java
@ExceptionHandler(
    OrderNotFoundException.class)
```

Now

↓

HTTP 404

Correct response.

---

# 21. Common Interview Traps

### Is `@ControllerAdvice` mandatory?

❌ No.

But it is strongly recommended for centralized exception handling.

---

### Does `@Valid` execute inside the controller?

❌ No.

Validation occurs before the controller method is invoked.

---

### Is every exception HTTP 500?

❌ No.

Return the status code that best matches the problem.

---

### Should stack traces be returned to clients?

❌ No.

Log them on the server.

Return safe, user-friendly error responses.

---

### Should validation be performed in controllers or services?

Validate request structure at the API boundary. Business rule validation often belongs in the service layer.

---

# 22. Senior-Level Follow-up Questions

1. How does Spring handle exceptions?
2. What is `@ControllerAdvice`?
3. What is `@ExceptionHandler`?
4. How does `@Valid` work?
5. What is `MethodArgumentNotValidException`?
6. What is `ProblemDetail`?
7. Difference between `400` and `422`?
8. Difference between `401` and `403`?
9. How would you design REST error responses?
10. What should never be returned in production error responses?

---

# 23. Real Interview Scenario

**Interviewer:**

> "Your REST API always returns HTTP 500, even for business validation failures. How would you improve it?"

### Strong Answer

> I'd identify the different categories of errors and map them to appropriate HTTP status codes. Validation failures should return 400 (or 422 if that's the API standard), missing resources should return 404, conflicts should return 409, and authorization failures should return 401 or 403 as appropriate. I'd centralize this logic using `@ControllerAdvice` and `@ExceptionHandler`, return a consistent error format—such as `ProblemDetail`—and log the underlying exceptions without exposing stack traces to clients.

---

# 24. Cheat Sheet

| Component                         | Responsibility              |
| --------------------------------- | --------------------------- |
| `@ExceptionHandler`               | Handle specific exceptions  |
| `@ControllerAdvice`               | Global exception handling   |
| `@Valid`                          | Trigger bean validation     |
| `MethodArgumentNotValidException` | Validation failure          |
| `ProblemDetail`                   | Standardized error response |
| Bean Validation                   | Validate request data       |

---

## Exception Flow

```text
Request

↓

Controller

↓

Exception

↓

@ControllerAdvice

↓

ProblemDetail

↓

HTTP Response
```

---

## Validation Flow

```text
JSON

↓

@RequestBody

↓

@Valid

↓

Validation

↓

Success

OR

↓

400 Response
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How do you design exception handling for enterprise REST APIs?"**

Don't answer:

> "I use `@ControllerAdvice`."

A senior-level answer is:

> "I separate infrastructure errors, validation errors, and business exceptions, mapping each to appropriate HTTP status codes. I centralize exception handling with `@ControllerAdvice`, use `@ExceptionHandler` for domain-specific exceptions, return a consistent error format such as `ProblemDetail`, avoid exposing internal implementation details or stack traces, and log enough contextual information for production troubleshooting. This approach provides both a better developer experience for API consumers and easier operational support."

That answer demonstrates an understanding of **REST design, Spring internals, and production engineering**, rather than just annotation usage.

---

## Next Chapter

**Chapter 44 – Spring Boot Caching Internals (Cache Abstraction, Redis & Cache Patterns)**

We'll cover:

* Spring Cache abstraction
* `@Cacheable`, `@CachePut`, `@CacheEvict`
* CacheManager internals
* Redis integration
* Cache-aside, write-through, and write-behind patterns
* Cache stampede and cache penetration
* TTL strategies
* Distributed caching
* Production debugging scenarios
* Senior interview questions
