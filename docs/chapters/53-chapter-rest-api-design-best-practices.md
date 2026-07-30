# Part IX – Enterprise Design & Microservices

# Chapter 53: REST API Design Best Practices

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Google, Oracle, Goldman Sachs, JP Morgan, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

Every backend engineer builds APIs.

A junior engineer focuses on making an API work.

A senior engineer designs APIs that are:

* Easy to understand
* Backward compatible
* Secure
* Scalable
* Consistent
* Easy to maintain

Typical interview questions:

* What makes a good REST API?
* PUT vs PATCH?
* POST vs PUT?
* What is idempotency?
* URI vs Query Parameter?
* How do you version APIs?
* Which HTTP status codes should be returned?

---

# 2. 30-Second Interview Answer

> A well-designed REST API models business resources rather than actions, uses HTTP methods according to their semantics, returns appropriate status codes, supports pagination and filtering, provides consistent request and response formats, and is versioned without breaking existing clients. Security, idempotency, validation, and proper error handling are also essential aspects of enterprise-grade API design.

---

# 3. What is REST?

REST stands for:

**Representational State Transfer**

REST is an architectural style based on:

* Resources
* HTTP methods
* Stateless communication
* Uniform interfaces
* Cacheability

---

# 4. Resource-Oriented Design

Interview favourite.

❌ Poor Design

```text
/getAllUsers

/createUser

/deleteUser
```

Good Design

```text
/users

/users/101

/orders

/orders/2001
```

Resources should be nouns, not verbs.

---

# 5. HTTP Methods

| Method | Purpose          | Idempotent                |
| ------ | ---------------- | ------------------------- |
| GET    | Read data        | ✅ Yes                     |
| POST   | Create resource  | ❌ No                      |
| PUT    | Replace resource | ✅ Yes                     |
| PATCH  | Partial update   | Depends on implementation |
| DELETE | Delete resource  | ✅ Yes                     |

---

# 6. POST vs PUT

Interview favourite.

POST

```text
POST /users
```

Server creates the resource.

---

PUT

```text
PUT /users/101
```

Client specifies the resource identifier and sends the full representation to create or replace it.

---

# 7. PUT vs PATCH

Interview favourite.

PUT

```json
{
  "name":"John",
  "city":"London"
}
```

Replace the entire resource representation.

---

PATCH

```json
{
  "city":"Manchester"
}
```

Update only the specified fields.

---

# 8. Idempotency

Interview favourite.

Definition:

> Performing the same request multiple times produces the same intended result.

Example

DELETE

```text
DELETE /users/100
```

First request

↓

Deleted

Second request

↓

Still deleted

Final state remains unchanged.

---

POST

```text
POST /orders
```

Repeated requests may create multiple orders.

Not idempotent.

---

# 9. HTTP Status Codes

Interview favourite.

| Code | Meaning                                     |
| ---- | ------------------------------------------- |
| 200  | OK                                          |
| 201  | Created                                     |
| 202  | Accepted                                    |
| 204  | No Content                                  |
| 400  | Bad Request                                 |
| 401  | Unauthorized (authentication required)      |
| 403  | Forbidden (authenticated but not permitted) |
| 404  | Not Found                                   |
| 409  | Conflict                                    |
| 422  | Unprocessable Content                       |
| 500  | Internal Server Error                       |
| 503  | Service Unavailable                         |

---

# 10. URI Design

Good

```text
/users/101/orders
```

Bad

```text
/getOrdersByUser?id=101
```

Use path variables for identifying resources.

Use query parameters for filtering.

---

# 11. Query Parameters

Examples

```text
/products?page=1

/products?size=20

/products?sort=name

/products?category=electronics
```

Perfect for:

* Pagination
* Filtering
* Sorting

---

# 12. Pagination

Interview favourite.

Without pagination

```text
GET /orders
```

Returns

500,000 rows

Very slow.

---

Better

```text
GET /orders?page=0&size=20
```

---

# 13. Sorting

```text
/products?sort=name,asc

/products?sort=price,desc
```

---

# 14. Filtering

```text
/products?category=laptop

/products?price<1000
```

A more common REST-friendly approach is:

```text
/products?maxPrice=1000
```

or

```text
/products?priceLt=1000
```

---

# 15. API Versioning

Interview favourite.

Common approaches:

### URI Versioning

```text
/v1/orders

/v2/orders
```

Most common.

---

### Header Versioning

```text
API-Version: 2
```

---

### Media Type Versioning

```text
Accept:

application/vnd.company.v2+json
```

---

# 16. Error Response Design

Bad

```json
{
 "error":"Exception"
}
```

Better

```json
{
  "timestamp":"2026-07-25T10:30:00Z",
  "status":404,
  "error":"Not Found",
  "message":"User not found",
  "path":"/users/101"
}
```

Spring Boot 3 also supports RFC 9457 `ProblemDetail` for standardized error responses.

---

# 17. Validation

Validate requests before business logic.

Example

```java
public class UserRequest {

    @NotBlank
    private String name;

    @Email
    private String email;

}
```

Return validation errors with clear field-level messages.

---

# 18. HATEOAS

Interview favourite.

Response includes related links.

Example

```json
{
  "id":101,
  "name":"John",
  "_links":{
      "orders":"/users/101/orders"
  }
}
```

Useful in some hypermedia-driven APIs, but many public REST APIs do not implement HATEOAS.

---

# 19. API Security

Every production API should consider:

* Authentication
* Authorization
* HTTPS
* Input validation
* Rate limiting
* CORS configuration
* Security headers

Never expose sensitive information in responses.

---

# 20. API Documentation

Use OpenAPI (Swagger).

Benefits:

* Interactive documentation
* Client generation
* Better collaboration
* Easier testing

---

# 21. REST Request Lifecycle

```text
Client

↓

API Gateway

↓

Spring Controller

↓

Service

↓

Repository

↓

Database

↓

JSON Response
```

---

# 22. Production Example

E-commerce

```text
GET /products?page=0&size=20&sort=price,asc
```

Instead of

```text
GET /getAllProducts
```

Supports:

* Pagination
* Sorting
* Scalability

---

# 23. Production Debugging Story

Problem

A mobile application became very slow.

Investigation

API returned

100,000 products

without pagination.

Root Cause

No paging support.

Each request transferred massive amounts of data.

Fix

Added:

* Pagination
* Sorting
* Filtering

Response size reduced dramatically, improving latency and bandwidth usage.

---

# 24. Common Interview Traps

### Should every endpoint return 200?

❌ No.

Use status codes that reflect the outcome.

---

### Is POST idempotent?

❌ No.

Repeated POST requests may create additional resources unless the API explicitly implements idempotency (for example, using idempotency keys).

---

### Is PUT always an update?

❌ Not necessarily.

PUT creates or replaces the resource at the specified URI, depending on API semantics.

---

### Should verbs appear in URIs?

❌ Usually no.

Prefer nouns representing resources.

---

### Should APIs expose database entities directly?

❌ No.

Use DTOs to decouple API contracts from persistence models.

---

# 25. Senior-Level Follow-up Questions

1. Explain REST constraints.
2. PUT vs PATCH?
3. POST vs PUT?
4. What is idempotency?
5. How do you version APIs?
6. Which status code should be returned after resource creation?
7. How would you design pagination?
8. What is HATEOAS?
9. How do you secure REST APIs?
10. How would you design backward-compatible APIs?

---

# 26. Real Interview Scenario

**Interviewer:**

> "Your `/orders` API is taking 12 seconds and returning 300 MB of JSON. How would you improve it?"

### Strong Answer

> I'd first introduce server-side pagination, sorting, and filtering to reduce payload size. I'd review the SQL queries for missing indexes and N+1 issues, use DTO projections instead of returning full entities, enable compression if appropriate, and add caching for frequently requested data. Finally, I'd monitor response times and payload sizes to validate the improvements.

---

# 27. Cheat Sheet

| Topic           | Best Practice                        |
| --------------- | ------------------------------------ |
| Resource Naming | Use nouns                            |
| HTTP Methods    | Follow REST semantics                |
| Status Codes    | Return appropriate responses         |
| Pagination      | Required for large datasets          |
| Versioning      | Prefer URI or header versioning      |
| Validation      | Validate before business logic       |
| Errors          | Consistent structured responses      |
| Security        | HTTPS, Auth, Validation, Rate Limits |
| Documentation   | OpenAPI/Swagger                      |

---

## REST Architecture

```text
Client

↓

API Gateway

↓

Controller

↓

Service

↓

Repository

↓

Database
```

---

## API Design Flow

```text
Resource

↓

HTTP Method

↓

Validation

↓

Business Logic

↓

DTO

↓

JSON Response
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"What makes a good REST API?"**

Don't answer:

> "Use GET, POST, PUT and DELETE."

A senior-level answer is:

> "A well-designed REST API models resources instead of actions, uses HTTP methods according to their semantics, returns meaningful status codes, supports pagination, filtering, and versioning, validates input, secures endpoints with authentication and authorization, and provides consistent error responses and documentation. The API contract should remain stable over time, allowing new features to be introduced without breaking existing clients."

This answer demonstrates an understanding of **API design, scalability, backward compatibility, and enterprise best practices**, which is exactly what senior interviewers expect.

---

## Next Chapter

**Chapter 54 – Microservices Architecture**

We'll cover:

* Monolith vs Microservices
* Service decomposition strategies
* Database per service
* Synchronous vs asynchronous communication
* Event-driven architecture
* Distributed data challenges
* Advantages and trade-offs
* Common production pitfalls
* Real-world architecture examples
* Senior interview questions
