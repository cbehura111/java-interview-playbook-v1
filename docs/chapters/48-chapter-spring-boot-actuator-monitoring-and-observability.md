# Part VIII – Spring Boot Internals & Enterprise Architecture

# Chapter 48: Spring Boot Actuator, Monitoring & Observability

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Goldman Sachs, Oracle, JP Morgan, VMware, Product Companies

---

# 1. Why Do Interviewers Ask This?

Writing code is only half the job of a backend engineer.

Once an application is deployed, engineers need to answer questions like:

* Is the application healthy?
* Why is CPU usage suddenly high?
* Why are requests becoming slower?
* How many requests are failing?
* Which downstream service is causing latency?

This is where **Monitoring** and **Observability** become essential.

Typical interview questions:

* What is Spring Boot Actuator?
* What endpoints does Actuator provide?
* What is Micrometer?
* Difference between monitoring and observability?
* How do Prometheus and Grafana work?
* What are distributed traces?
* What is MDC?

---

# 2. 30-Second Interview Answer

> Spring Boot Actuator provides production-ready endpoints for monitoring and managing applications. It integrates with Micrometer to collect metrics, which can be exported to systems like Prometheus and visualized in Grafana. Combined with structured logging and distributed tracing using OpenTelemetry, it provides comprehensive observability into application health, performance, and request flow.

---

# 3. Monitoring vs Observability

Interview favourite.

### Monitoring

Tells you

> **Something is wrong.**

Example

```text
CPU = 95%
```

---

### Observability

Helps answer

> **Why is it wrong?**

It combines:

* Metrics
* Logs
* Traces

to diagnose issues.

---

# 4. Spring Boot Actuator

Actuator adds production endpoints.

```text
Application

↓

Actuator

↓

Health

Metrics

Info

Beans

Env

Thread Dump

Heap Dump
```

---

# 5. Common Actuator Endpoints

| Endpoint               | Purpose                      |
| ---------------------- | ---------------------------- |
| `/actuator/health`     | Application health           |
| `/actuator/info`       | Build/application info       |
| `/actuator/metrics`    | Metrics                      |
| `/actuator/prometheus` | Prometheus metrics           |
| `/actuator/env`        | Environment properties       |
| `/actuator/beans`      | Spring beans                 |
| `/actuator/threaddump` | Thread dump                  |
| `/actuator/heapdump`   | JVM heap dump                |
| `/actuator/loggers`    | Runtime log level management |

---

# 6. Health Endpoint

Interview favourite.

Example

```text
GET

/actuator/health
```

Response

```json
{
  "status": "UP"
}
```

Possible statuses:

* UP
* DOWN
* OUT_OF_SERVICE
* UNKNOWN

---

# 7. Custom Health Indicator

Example

```java
@Component
public class DatabaseHealthIndicator
        implements HealthIndicator {

    @Override
    public Health health() {

        if(databaseAvailable()) {

            return Health.up().build();

        }

        return Health.down()
                .withDetail(
                    "Database",
                    "Unavailable")
                .build();
    }

}
```

Useful for checking external dependencies.

---

# 8. Actuator Architecture

```text
Application

↓

Actuator

↓

Health Contributors

↓

Metrics Registry

↓

Management Endpoints
```

---

# 9. Micrometer

Interview favourite.

Micrometer is Spring Boot's metrics facade.

Think of it as

```text
SLF4J

↓

Logging Frameworks
```

Similarly,

```text
Micrometer

↓

Prometheus

Datadog

CloudWatch

New Relic
```

One API

Multiple monitoring systems.

---

# 10. Common Metrics

Examples:

* JVM Memory
* Heap Usage
* CPU Usage
* Request Count
* Request Latency
* Active Threads
* Database Connections
* GC Activity

---

# 11. Custom Metric

Example

```java
Counter counter =
    meterRegistry.counter(
        "orders.created");

counter.increment();
```

Each successful order increases the metric.

---

# 12. Prometheus

Interview favourite.

Prometheus periodically **pulls** metrics.

```text
Prometheus

↓

GET

/actuator/prometheus

↓

Spring Boot
```

Metrics are exposed in Prometheus format.

---

# 13. Grafana

Grafana visualizes collected metrics.

```text
Spring Boot

↓

Prometheus

↓

Grafana Dashboard
```

Typical dashboards:

* CPU
* Memory
* Response Time
* Error Rate
* JVM Threads
* Database Pool

---

# 14. Request Metrics

Example

```text
Request

↓

Controller

↓

Timer Starts

↓

Business Logic

↓

Timer Stops

↓

Micrometer Records Duration
```

Helps identify slow APIs.

---

# 15. Logging

Metrics tell **what** is happening.

Logs explain **what happened**.

Good logs include:

* Timestamp
* Level
* Correlation ID
* Thread
* Request ID
* Message

Avoid logging sensitive information such as passwords, tokens, or personal data.

---

# 16. MDC (Mapped Diagnostic Context)

Interview favourite.

MDC stores request-specific context.

Example

```text
Request

↓

Correlation ID

↓

MDC

↓

Every Log Contains Same ID
```

This makes it easy to trace all log entries for a single request.

---

# 17. Distributed Tracing

Modern systems use multiple services.

```text
Client

↓

API Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service
```

Tracing links these calls together.

---

# 18. Trace IDs & Span IDs

Example

```text
Trace ID

12345

↓

Order Service

↓

Payment Service

↓

Inventory Service
```

Each service creates its own **Span**, but all spans share the same **Trace ID**.

This allows end-to-end request tracking.

---

# 19. OpenTelemetry

Interview favourite.

OpenTelemetry is the industry standard for:

* Metrics
* Logs
* Traces

Spring Boot integrates with it through Micrometer Observability and tracing libraries.

---

# 20. Production Example

Customer reports:

> "Checkout is taking 8 seconds."

Investigation:

```text
Grafana

↓

High Latency

↓

Trace

↓

Payment Service

↓

Slow Database Query
```

Problem identified within minutes.

---

# 21. Production Debugging Story

Problem

Users experienced intermittent delays.

Health endpoint remained **UP**.

Investigation

Metrics showed a sudden increase in request latency.

Distributed traces revealed:

```text
Order Service

↓

Inventory Service

↓

External Supplier API

↓

12 Second Delay
```

Root Cause

External API timeout.

Fix

Added:

* Timeouts
* Retry policy
* Circuit breaker

Latency returned to normal.

---

# 22. Common Interview Traps

### Is Actuator only for health checks?

❌ No.

It provides health, metrics, environment details, thread dumps, heap dumps, loggers, and more.

---

### Does Grafana collect metrics?

❌ No.

Grafana visualizes data.

Prometheus (or another backend) collects metrics.

---

### Does Prometheus push metrics?

❌ No.

Prometheus generally **pulls** metrics from applications.

---

### Are logs enough for observability?

❌ No.

Observability combines metrics, logs, and traces.

---

### Should every Actuator endpoint be exposed publicly?

❌ No.

Sensitive endpoints such as `/env`, `/heapdump`, and `/beans` should be secured or disabled in production.

---

# 23. Senior-Level Follow-up Questions

1. What is Spring Boot Actuator?
2. Explain Micrometer architecture.
3. What is Prometheus?
4. How does Grafana work?
5. Monitoring vs Observability?
6. What is MDC?
7. What are Trace IDs and Span IDs?
8. Explain distributed tracing.
9. How would you monitor JVM performance?
10. Which Actuator endpoints should never be publicly exposed?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Your application is healthy according to `/actuator/health`, but users complain that responses are taking 15 seconds. How would you investigate?"

### Strong Answer

> The health endpoint indicates basic availability, not performance. I'd examine Micrometer metrics for request latency, thread pool utilisation, JVM memory, and database connection pools. Then I'd use distributed tracing to identify which service or external dependency is causing the delay. I'd correlate traces with logs using the Trace ID or Correlation ID and review dashboards in Grafana for spikes or anomalies around the reported time.

---

# 25. Cheat Sheet

| Component            | Purpose                                |
| -------------------- | -------------------------------------- |
| Spring Boot Actuator | Production monitoring endpoints        |
| Micrometer           | Metrics abstraction                    |
| Prometheus           | Metrics collection                     |
| Grafana              | Metrics visualization                  |
| MDC                  | Log correlation                        |
| Trace ID             | End-to-end request identifier          |
| Span                 | Single operation within a trace        |
| OpenTelemetry        | Standard for metrics, logs, and traces |

---

## Monitoring Architecture

```text
Spring Boot

↓

Actuator

↓

Micrometer

↓

Prometheus

↓

Grafana
```

---

## Distributed Tracing

```text
Client

↓

API Gateway

↓

Order Service

↓

Payment Service

↓

Inventory Service

↓

Database
```

(All linked by the same Trace ID.)

---

# 🎯 Interview Secret

When the interviewer asks:

> **"How would you monitor a production Spring Boot application?"**

Don't answer:

> "I'd use Actuator."

A senior-level answer is:

> "I'd expose only the required Actuator endpoints and secure them appropriately. I'd use Micrometer to publish JVM, HTTP, database, and custom business metrics to Prometheus, visualize them in Grafana, and configure alerts for latency, error rates, and resource usage. For request diagnostics, I'd enable distributed tracing with OpenTelemetry and include correlation IDs in structured logs using MDC. Together, metrics, logs, and traces provide full observability into the system."

That answer demonstrates knowledge of **production operations, monitoring, observability, and enterprise support**, which distinguishes senior engineers.

---

## Next Chapter

**Chapter 49 – Spring Boot Testing (JUnit 5, Mockito & Testcontainers)**

We'll cover:

* Testing pyramid
* Unit, integration, and end-to-end testing
* JUnit 5 features
* Mockito internals
* Mock vs Spy
* `@MockBean` vs `@Mock`
* `@SpringBootTest`
* Testcontainers
* Embedded databases vs real containers
* Production testing strategies
* Senior interview questions
