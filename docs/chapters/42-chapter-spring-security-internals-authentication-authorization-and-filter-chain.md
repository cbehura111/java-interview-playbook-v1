# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 42: Spring Security Internals (Authentication, Authorization & Filter Chain)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Banking & FinTech Companies

---

# 1. Why Do Interviewers Ask This?

Nearly every enterprise application requires security.

When you configure:

```java
http.authorizeHttpRequests(auth -> auth
    .anyRequest().authenticated());
```

or

```java
@PreAuthorize("hasRole('ADMIN')")
```

Spring Security performs a large amount of work behind the scenes.

Interviewers want to know whether you understand:

* Authentication
* Authorization
* Security Filter Chain
* JWT Authentication
* SecurityContext
* Method Security

Typical interview questions:

* Explain Spring Security architecture.
* Authentication vs Authorization?
* What is SecurityContext?
* How does JWT work?
* What is the Security Filter Chain?

---

# 2. 30-Second Interview Answer

> Spring Security secures applications using a chain of servlet filters. Every request passes through the Security Filter Chain before reaching Spring MVC. The framework authenticates the user, stores the authentication in the SecurityContext, performs authorization checks, and only then allows the request to reach the controller. Features such as JWT, OAuth2, method security, and session-based authentication all build on this architecture.

---

# 3. Authentication vs Authorization

Interview favourite.

### Authentication

Question:

> Who are you?

Example

```text
Username

+

Password
```

or

```text
JWT Token
```

Result

```text
Identity Verified
```

---

### Authorization

Question:

> What are you allowed to do?

Example

```text
User

↓

Role

↓

ADMIN

↓

Can Delete?
```

---

## Simple Comparison

| Authentication  | Authorization                |
| --------------- | ---------------------------- |
| Verify identity | Verify permissions           |
| Happens first   | Happens after authentication |
| User login      | Access control               |

---

# 4. Spring Security Architecture

```text
Client

↓

Tomcat

↓

Security Filter Chain

↓

DispatcherServlet

↓

Controller

↓

Service

↓

Repository

↓

Database
```

The request never reaches the controller before passing through security.

---

# 5. Security Filter Chain

Interview favourite.

Every request passes through multiple filters.

Example

```text
HTTP Request

↓

CorsFilter

↓

CSRF Filter

↓

Authentication Filter

↓

Authorization Filter

↓

ExceptionTranslationFilter

↓

DispatcherServlet
```

Each filter has a specific responsibility.

---

# 6. Why Filters?

Because security should be applied

Before

Business logic executes.

Example

Without security

```text
Client

↓

Controller
```

Dangerous.

Instead

```text
Client

↓

Security

↓

Controller
```

---

# 7. Authentication Flow

User logs in.

```text
Username

Password

↓

AuthenticationManager

↓

UserDetailsService

↓

Database

↓

Authentication Object

↓

SecurityContext
```

---

# 8. AuthenticationManager

Responsible for

Authenticating credentials.

Simplified flow

```text
Username

Password

↓

AuthenticationManager

↓

Authenticated?
```

If successful

↓

Returns an authenticated `Authentication` object.

---

# 9. UserDetailsService

Interview favourite.

Spring calls

```java
loadUserByUsername(username)
```

Implementation

```text
Database

↓

Find User

↓

Load Password

↓

Load Roles

↓

Return UserDetails
```

---

# 10. Password Encoding

Never store plain passwords.

Example

```text
Password

↓

BCrypt

↓

Hash Stored
```

During login

```text
Entered Password

↓

BCrypt Verify

↓

Match?
```

Spring commonly uses `BCryptPasswordEncoder`.

---

# 11. SecurityContext

Interview favourite.

After successful authentication

Spring stores

```text
Authentication

↓

SecurityContext

↓

Current Request
```

Controllers can access

```java
Authentication authentication
```

or

```java
SecurityContextHolder.getContext()
```

---

# 12. JWT Authentication

Very common interview topic.

Login

↓

Server validates credentials

↓

Generates JWT

↓

Returns token

Client stores token.

---

# 13. JWT Request Flow

```text
Login

↓

JWT Generated

↓

Client Stores JWT

↓

Every Request

↓

Authorization Header

↓

JWT Filter

↓

Validate Token

↓

SecurityContext

↓

Controller
```

No database lookup is required **solely to validate the token**, although applications may still query the database depending on their design (for example, to load current user details or check token revocation).

---

# 14. Authorization Header

Example

```http
Authorization: Bearer eyJhbGciOi...
```

Spring extracts

↓

JWT

↓

Validates signature

↓

Creates Authentication object

---

# 15. Method Security

Example

```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser() {

}
```

Spring checks

```text
Current User

↓

ADMIN?

↓

YES

↓

Execute Method
```

Otherwise

↓

HTTP 403 Forbidden.

---

# 16. Exception Handling

Unauthenticated user

↓

HTTP

```text
401 Unauthorized
```

Authenticated

But insufficient permission

↓

HTTP

```text
403 Forbidden
```

Interview favourite.

---

# 17. Stateless vs Stateful

### Session-Based

```text
Login

↓

Session Created

↓

Server Stores Session

↓

Session Cookie
```

---

### JWT

```text
Login

↓

JWT

↓

Client Stores

↓

Every Request Sends JWT
```

Server does not maintain session state for authentication.

---

# 18. Spring Security Request Flow

```text
HTTP Request

↓

Security Filter Chain

↓

Authentication

↓

SecurityContext

↓

Authorization

↓

DispatcherServlet

↓

Controller

↓

Response
```

---

# 19. Production Example

REST API

```http
GET /accounts
```

↓

JWT Filter

↓

Validate JWT

↓

SecurityContext

↓

Check Role

↓

Controller

↓

Response

---

# 20. Production Debugging Story

Problem

API always returned

```text
403 Forbidden
```

Investigation

JWT validated successfully.

However

Role stored as

```text
ADMIN
```

Application expected

```text
ROLE_ADMIN
```

Root Cause

Spring's default role-based authorization expects the `ROLE_` prefix when using methods like `hasRole()`.

Fix

Store authorities consistently or use `hasAuthority()` where appropriate.

---

# 21. Common Interview Traps

### Does Spring Security protect controllers directly?

❌ No.

It intercepts requests using servlet filters before controllers are invoked.

---

### Is JWT encrypted?

❌ Not necessarily.

A typical signed JWT (JWS) is **signed**, not encrypted. Its payload is Base64URL-encoded and can be read by anyone holding the token, so sensitive data should not be stored in it unless encryption (JWE) is specifically used.

---

### Does Spring automatically store JWT?

❌ No.

The client stores the token (for example, in a secure cookie or other client-side storage strategy).

---

### Authentication vs Authorization?

Authentication verifies identity.

Authorization verifies permissions.

---

### Does every request pass through the Security Filter Chain?

✅ Yes.

Every secured request is processed by the configured filter chain.

---

# 22. Senior-Level Follow-up Questions

1. Authentication vs Authorization?
2. Explain the Security Filter Chain.
3. What is SecurityContext?
4. How does JWT authentication work?
5. What is AuthenticationManager?
6. What is UserDetailsService?
7. Why use BCrypt?
8. Difference between 401 and 403?
9. Session vs JWT?
10. How does `@PreAuthorize` work?

---

# 23. Real Interview Scenario

**Interviewer:**

> "A valid JWT is being sent, but every request still returns HTTP 401. How would you investigate?"

### Strong Answer

> I'd first verify that the JWT filter is actually part of the Security Filter Chain and executes before authorization. Then I'd check whether the token signature, issuer, audience, and expiry are valid. I'd also confirm that the filter creates an authenticated `Authentication` object and stores it in the `SecurityContext`. Finally, I'd review the security configuration and logs to ensure the request matches the intended security rules.

---

# 24. Cheat Sheet

| Component             | Responsibility                  |
| --------------------- | ------------------------------- |
| Security Filter Chain | Intercepts all secured requests |
| AuthenticationManager | Verifies credentials            |
| UserDetailsService    | Loads user information          |
| PasswordEncoder       | Verifies hashed passwords       |
| SecurityContext       | Stores current authentication   |
| JWT Filter            | Validates JWT tokens            |
| `@PreAuthorize`       | Method-level authorization      |

---

## Authentication Flow

```text
Login Request

↓

AuthenticationManager

↓

UserDetailsService

↓

Password Verification

↓

Authentication

↓

SecurityContext
```

---

## JWT Flow

```text
Login

↓

JWT Issued

↓

Client Sends Token

↓

JWT Filter

↓

SecurityContext

↓

Controller
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How does Spring Security authenticate a JWT request?"**

Don't answer:

> "It validates the token."

A senior-level answer is:

> "Every incoming request first passes through the Security Filter Chain. A JWT authentication filter extracts the Bearer token from the `Authorization` header, validates its signature and claims, and if valid, creates an authenticated `Authentication` object. That object is stored in the `SecurityContext`, allowing subsequent authorization filters and controller methods to determine the user's identity and permissions. Only after these checks does the request proceed to the DispatcherServlet."

That answer demonstrates an understanding of **Spring Security's architecture, filter chain, authentication flow, and request lifecycle**, rather than just JWT concepts.

---

## Next Chapter

**Chapter 43 – Spring Boot Exception Handling, Validation & REST Error Design**

We'll cover:

* Exception handling flow
* `@ControllerAdvice`
* `@ExceptionHandler`
* Bean Validation (`@Valid`)
* `MethodArgumentNotValidException`
* Global error handling
* RFC 9457 `ProblemDetail` (Spring Boot 3)
* Custom exceptions
* REST API error response design
* Production debugging scenarios
* Senior interview questions
