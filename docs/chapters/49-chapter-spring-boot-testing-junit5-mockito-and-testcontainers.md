# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 49: Spring Boot Testing (JUnit 5, Mockito & Testcontainers)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Goldman Sachs, JP Morgan, VMware, Walmart Global Tech, Product Companies

---

# 1. Why Do Interviewers Ask This?

Writing code is only half the job.

Writing **reliable, maintainable, and testable code** is what distinguishes a senior engineer.

Interviewers want to know:

* Can you write effective unit tests?
* Do you know when to mock dependencies?
* How do you test databases?
* What is the difference between unit and integration testing?
* Why use Testcontainers instead of H2?

---

# 2. 30-Second Interview Answer

> Spring Boot supports multiple levels of testing. Unit tests validate individual classes using JUnit 5 and Mockito, while integration tests verify interactions between application components using `@SpringBootTest`. Testcontainers provides production-like testing by running real services such as PostgreSQL or Redis inside Docker containers, improving test reliability compared to in-memory databases.

---

# 3. Testing Pyramid

Interview favourite.

```text
           E2E Tests
          (Few, Slow)

     Integration Tests
      (Some, Medium)

        Unit Tests
     (Many, Very Fast)
```

A healthy project contains:

* Many Unit Tests
* Some Integration Tests
* Few End-to-End Tests

---

# 4. Types of Testing

| Test Type        | Purpose                             |
| ---------------- | ----------------------------------- |
| Unit Test        | Test one class in isolation         |
| Integration Test | Test interaction between components |
| End-to-End Test  | Test complete application workflow  |
| Performance Test | Measure scalability and latency     |
| Contract Test    | Validate API compatibility          |

---

# 5. Unit Testing

Example

```java
class Calculator {

    int add(int a, int b) {
        return a + b;
    }

}
```

Test

```java
@Test
void shouldAddNumbers() {

    Calculator calculator = new Calculator();

    assertEquals(5,
            calculator.add(2,3));

}
```

No Spring Context.

Very fast.

---

# 6. JUnit 5

Interview favourite.

Common annotations

| Annotation           | Purpose                       |
| -------------------- | ----------------------------- |
| `@Test`              | Test method                   |
| `@BeforeEach`        | Before every test             |
| `@AfterEach`         | After every test              |
| `@BeforeAll`         | Before all tests              |
| `@AfterAll`          | After all tests               |
| `@DisplayName`       | Friendly test name            |
| `@Nested`            | Group related tests           |
| `@ParameterizedTest` | Run test with multiple inputs |

---

# 7. Mockito

Mockito creates mock objects.

Instead of

```text
Service

↓

Real Database
```

Use

```text
Service

↓

Mock Repository
```

Fast

Predictable

Isolated

---

# 8. @Mock

Example

```java
@Mock
private UserRepository repository;
```

Mockito creates a fake implementation.

---

# 9. @InjectMocks

Example

```java
@InjectMocks
private UserService service;
```

Mockito injects all mocks into the service.

---

# 10. Mock Behaviour

Example

```java
when(repository.findById(1L))
        .thenReturn(Optional.of(user));
```

Repository never calls the database.

---

# 11. Verify Behaviour

Example

```java
verify(repository)
        .save(user);
```

Confirms that the expected interaction occurred.

---

# 12. Mock vs Spy

Interview favourite.

### Mock

Everything is fake.

Methods return default values unless stubbed.

---

### Spy

Wraps a real object.

Real methods execute unless explicitly stubbed.

---

| Mock          | Spy                        |
| ------------- | -------------------------- |
| Fake object   | Real object wrapper        |
| No real logic | Real logic executes        |
| Faster        | Useful for partial mocking |

---

# 13. @SpringBootTest

Loads the complete Spring Context.

```java
@SpringBootTest
class UserServiceTest {

}
```

Suitable for integration testing.

Slower than unit tests.

---

# 14. @MockBean vs @Mock

Interview favourite.

### @Mock

Mockito only.

Spring knows nothing about it.

---

### @MockBean

Spring replaces an existing bean in the Application Context with a Mockito mock.

Useful for integration tests.

---

# 15. Slice Testing

Spring Boot provides focused test annotations.

| Annotation        | Tests              |
| ----------------- | ------------------ |
| `@WebMvcTest`     | Controllers        |
| `@DataJpaTest`    | JPA repositories   |
| `@JsonTest`       | JSON serialization |
| `@JdbcTest`       | JDBC components    |
| `@RestClientTest` | REST clients       |

These load only the required Spring components.

---

# 16. Testcontainers

Interview favourite.

Instead of using H2:

```text
Application

↓

H2 Database
```

Use

```text
Application

↓

Docker

↓

PostgreSQL
```

Tests run against the same database engine used in production.

---

# 17. Why Testcontainers?

Benefits:

* Real database behaviour
* Production-like environment
* No manual setup
* Automatic cleanup
* Supports PostgreSQL, MySQL, Redis, Kafka, RabbitMQ, Elasticsearch, etc.

---

# 18. Example

```java
@Testcontainers
@SpringBootTest
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");

}
```

Container starts automatically before tests.

---

# 19. Why Not H2?

Interview favourite.

H2 behaves differently from PostgreSQL.

Examples:

* SQL syntax
* JSON support
* Sequences
* Index behaviour
* Locking
* Data types

Tests may pass on H2 but fail in production.

---

# 20. Integration Test Flow

```text
JUnit

↓

Spring Context

↓

Repository

↓

Hibernate

↓

PostgreSQL Container

↓

Assertions
```

---

# 21. Production Example

CI Pipeline

↓

Start PostgreSQL Container

↓

Run Liquibase

↓

Run Repository Tests

↓

Run Service Tests

↓

Destroy Container

This provides consistent, isolated test environments.

---

# 22. Production Debugging Story

Problem

All tests passed.

Production failed immediately after deployment.

Investigation

Tests used H2.

Production used PostgreSQL.

Root Cause

Application relied on PostgreSQL-specific SQL and JSON operators unsupported by H2.

Fix

Replace H2 integration tests with Testcontainers running PostgreSQL.

The issue was detected before future deployments.

---

# 23. Common Interview Traps

### Is `@SpringBootTest` suitable for every test?

❌ No.

Use it only when the full Spring Context is required.

---

### Should repositories be mocked in repository tests?

❌ No.

Repository tests should use a real database.

---

### Is H2 always a good replacement for PostgreSQL applications?

❌ No.

Behaviour can differ significantly.

---

### Can Mockito mock final classes?

Yes.

Modern Mockito supports mocking final classes when properly configured.

---

### Does `verify()` check returned values?

❌ No.

It verifies interactions, not business results.

---

# 24. Senior-Level Follow-up Questions

1. Unit vs Integration testing?
2. Why JUnit 5?
3. Mockito vs Spring MockBean?
4. Mock vs Spy?
5. Why Testcontainers?
6. Why avoid H2 for PostgreSQL applications?
7. What is slice testing?
8. When should `@SpringBootTest` be used?
9. How do you test asynchronous methods?
10. How would you improve test execution speed?

---

# 25. Real Interview Scenario

**Interviewer:**

> "Your integration tests pass locally but fail in production because of SQL issues. How would you improve your testing strategy?"

### Strong Answer

> I'd replace in-memory database tests with Testcontainers using the same database engine as production. I'd execute Liquibase/Flyway migrations during test startup to validate schema compatibility, keep unit tests isolated with Mockito, and reserve `@SpringBootTest` for scenarios that require the full application context. This provides faster feedback while ensuring production parity.

---

# 26. Cheat Sheet

| Component         | Purpose                       |
| ----------------- | ----------------------------- |
| JUnit 5           | Test framework                |
| Mockito           | Mocking framework             |
| `@Mock`           | Create mock object            |
| `@InjectMocks`    | Inject mocks                  |
| `@MockBean`       | Replace Spring bean with mock |
| `@SpringBootTest` | Full application context      |
| `@DataJpaTest`    | Repository testing            |
| Testcontainers    | Real infrastructure in Docker |

---

## Testing Pyramid

```text
E2E Tests

↓

Integration Tests

↓

Unit Tests
```

---

## Integration Test Architecture

```text
JUnit

↓

Spring Boot

↓

Repository

↓

Hibernate

↓

PostgreSQL Testcontainer
```

---

# 🎯 Interview Secret

When the interviewer asks:

> **"Why are Testcontainers preferred over H2?"**

Don't answer:

> "Because they're more realistic."

A senior-level answer is:

> "Testcontainers run the same infrastructure components used in production, such as PostgreSQL, Redis, or Kafka. This eliminates discrepancies caused by in-memory databases like H2, which may differ in SQL syntax, transaction behaviour, locking, data types, and database-specific features. As a result, integration tests become far more reliable and closely reflect production behaviour."

This answer demonstrates an understanding of **test reliability, production parity, CI/CD practices, and enterprise-quality testing**, which is what senior interviewers expect.

---

## Next Chapter

**Chapter 50 – Spring Boot Performance Tuning & Production Best Practices**

We'll cover:

* JVM tuning for Spring Boot
* Connection pool tuning (HikariCP)
* Thread pool optimisation
* HTTP client tuning
* Database performance
* Caching strategies
* Memory leak detection
* GC tuning
* Startup optimisation
* Production deployment best practices
* Senior interview questions

This chapter concludes **Part VIII** and lays the foundation for **Part IX – Enterprise Design & Microservices**.
