# Part VII – Class Loading, Reflection & Dynamic Proxies

# Chapter 36: Java Annotations, Annotation Processing & Spring Boot Internals

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, VMware, Spring Boot, Product Companies

---

# 1. Why Do Interviewers Ask This?

Modern Java development revolves around annotations.

Almost everything in Spring Boot is annotation-driven:

* `@SpringBootApplication`
* `@Component`
* `@Service`
* `@Repository`
* `@Controller`
* `@Transactional`
* `@Autowired`
* `@Configuration`
* `@Bean`

Interviewers want to know:

* What are annotations?
* How does Spring process them?
* What is annotation processing?
* How does Lombok work?
* What is MapStruct?
* Runtime vs compile-time annotations?

Typical interview question:

> **How does Spring discover and process annotations like `@Service` or `@Autowired`?**

---

# 2. 30-Second Interview Answer

> Java annotations provide metadata about classes, methods, fields, and parameters. By themselves, annotations do nothing—they require a framework or tool to interpret them. Spring processes annotations at runtime using reflection and classpath scanning, while tools like Lombok and MapStruct process annotations at compile time using the Annotation Processing Tool (APT) to generate source code.

---

# 3. What Are Annotations?

Annotations provide

```text
Metadata
```

They describe code rather than changing Java language behaviour by themselves.

Example

```java
@Service
public class PaymentService {

}
```

`@Service`

does not execute any code on its own.

Spring interprets it.

---

# 4. Why Were Annotations Introduced?

Before annotations

Configuration was often written in XML.

Example

```xml
<bean id="paymentService"
      class="com.example.PaymentService"/>
```

Modern Spring

```java
@Service
public class PaymentService {

}
```

Cleaner.

Less configuration.

---

# 5. Where Can Annotations Be Used?

Annotations can be applied to:

* Classes
* Methods
* Fields
* Constructors
* Parameters
* Packages
* Local variables
* Type uses (Java 8+)

Example

```java
class Employee {

    @NotNull
    private String name;

}
```

---

# 6. Built-in Java Annotations

Common examples

| Annotation             | Purpose                         |
| ---------------------- | ------------------------------- |
| `@Override`            | Verify overridden methods       |
| `@Deprecated`          | Mark deprecated APIs            |
| `@SuppressWarnings`    | Suppress compiler warnings      |
| `@FunctionalInterface` | Ensure a single abstract method |

---

# 7. Custom Annotation

Example

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Audit {

}
```

Usage

```java
@Audit
public void transfer() {

}
```

The annotation itself performs no action until code processes it.

---

# 8. Meta-Annotations

Meta-annotations define the behaviour of other annotations.

Most important ones:

* `@Target`
* `@Retention`
* `@Inherited`
* `@Documented`
* `@Repeatable`

---

# 9. @Target

Specifies where an annotation can be used.

Example

```java
@Target(ElementType.METHOD)
```

Only methods may be annotated.

Other common targets:

* TYPE
* FIELD
* PARAMETER
* CONSTRUCTOR

---

# 10. @Retention

Interview favourite.

Controls how long the annotation is retained.

Three options.

---

## SOURCE

```text
Compiler

↓

Annotation Removed
```

Example

```java
@Override
```

The compiler uses it, but it is not available at runtime.

---

## CLASS

Stored in the `.class` file but not retained for runtime reflection.

Used by some tools and bytecode processors.

---

## RUNTIME

Available through reflection.

Required by Spring.

Example

```java
@Service

@Transactional

@Autowired
```

---

# 11. @Inherited

If applied to a class annotation,

subclasses inherit it.

Example

```text
Parent

↓

Child
```

Only applies to class-level annotations.

---

# 12. @Documented

Indicates the annotation should appear in generated Javadoc.

---

# 13. @Repeatable

Allows multiple instances of the same annotation.

Example

```java
@Role("ADMIN")
@Role("AUDITOR")
```

---

# 14. Runtime Annotation Processing

Spring startup

```text
Scan Classes

↓

Reflection

↓

Read Annotations

↓

Create Beans

↓

Dependency Injection
```

This happens every time the application starts.

---

# 15. Reflection Example

```java
Class<?> clazz =
    PaymentService.class;

boolean exists =
    clazz.isAnnotationPresent(Service.class);
```

Spring performs similar operations internally.

---

# 16. Compile-Time Annotation Processing

Interview favourite.

Instead of runtime,

processing occurs

during compilation.

```text
Java Source

↓

Compiler

↓

Annotation Processor

↓

Generated Source

↓

Compile
```

---

# 17. Annotation Processing Tool (APT)

Java Compiler

↓

APT

↓

Generated Code

↓

Final Compilation

APT is part of the Java compiler toolchain.

---

# 18. Lombok

Example

```java
@Getter
@Setter
public class Employee {

    private String name;

}
```

You never write

```java
getName()

setName()
```

Lombok generates them during compilation.

No runtime reflection required.

---

# 19. MapStruct

Example

```java
@Mapper
public interface EmployeeMapper {

}
```

During compilation

↓

Implementation generated

↓

No reflection

↓

Fast execution

One reason MapStruct is often preferred over reflection-based mapping libraries.

---

# 20. Spring Boot Startup

Simplified flow

```text
@SpringBootApplication

↓

Component Scan

↓

Reflection

↓

Read Annotations

↓

Create Bean Definitions

↓

Dependency Injection

↓

Application Ready
```

---

# 21. How @Autowired Works

Suppose

```java
@Service
class PaymentService {

    @Autowired

    OrderRepository repository;

}
```

Spring

↓

Reads field

↓

Finds matching bean

↓

Injects dependency

All driven by annotation metadata.

---

# 22. How @SpringBootApplication Works

Interview favourite.

It is itself a combination of annotations.

Equivalent to

```java
@SpringBootConfiguration

@EnableAutoConfiguration

@ComponentScan
```

This is called a **composed (meta-)annotation**.

---

# 23. Common Interview Traps

### Do annotations execute code?

❌ No.

Frameworks execute code based on annotations.

---

### Does Java understand `@Service`?

❌ No.

Only Spring interprets it.

---

### Does Lombok use Reflection?

❌ No.

It generates code during compilation using annotation processing.

---

### Does MapStruct use Reflection?

❌ No.

It generates mapper implementations at compile time.

---

### Why must Spring annotations use `RetentionPolicy.RUNTIME`?

Because Spring discovers them using reflection at runtime.

---

# 24. Production Example

Application Startup

```text
@ComponentScan

↓

Find Classes

↓

@Service

@Repository

@Controller

↓

Reflection

↓

Bean Creation

↓

Dependency Injection
```

Thousands of annotations may be processed during startup.

---

# 25. Production Debugging Story

Problem

Developer created

```java
@Audit
```

Spring ignored it.

Investigation

Annotation definition

```java
@Retention(RetentionPolicy.CLASS)
```

Root Cause

The annotation was not retained at runtime, so Spring's reflection-based processing could not see it.

Fix

```java
@Retention(RetentionPolicy.RUNTIME)
```

Application worked correctly.

---

# 26. Common Frameworks Using Annotation Processing

| Framework | Technique          |
| --------- | ------------------ |
| Spring    | Runtime reflection |
| Hibernate | Runtime reflection |
| Jackson   | Runtime reflection |
| Lombok    | Compile-time APT   |
| MapStruct | Compile-time APT   |
| Dagger    | Compile-time APT   |

---

# 27. Senior-Level Follow-up Questions

1. What are annotations?
2. Explain `@Target`.
3. Explain `@Retention`.
4. Difference between SOURCE, CLASS, and RUNTIME retention?
5. Why does Spring require runtime retention?
6. How does Lombok work?
7. How does MapStruct work?
8. What is APT?
9. Does Java execute annotations automatically?
10. How does `@SpringBootApplication` work?

---

# 28. Real Interview Scenario

**Interviewer:**

> "Why is MapStruct generally faster than reflection-based object mappers?"

### Strong Answer

> MapStruct generates plain Java mapping code during compilation using the Annotation Processing Tool. At runtime, it performs direct method calls instead of inspecting classes and fields through reflection. This reduces runtime overhead and allows the JIT compiler to optimise the generated code more effectively.

---

# 29. Cheat Sheet

| Annotation    | Purpose                         |
| ------------- | ------------------------------- |
| `@Target`     | Where annotation can be used    |
| `@Retention`  | How long annotation is retained |
| `@Inherited`  | Allow inheritance by subclasses |
| `@Documented` | Include in Javadoc              |
| `@Repeatable` | Allow multiple instances        |

---

## Runtime vs Compile-Time

| Runtime   | Compile-Time |
| --------- | ------------ |
| Spring    | Lombok       |
| Hibernate | MapStruct    |
| Jackson   | Dagger       |

---

## Annotation Lifecycle

```text
Source Code

↓

Annotation

↓

Compiler

↓

CLASS File

↓

JVM

↓

Reflection (if RUNTIME)

↓

Framework Processing
```

---

# 🎯 Interview Secret

When an interviewer asks:

> **"How does Spring process annotations?"**

Don't answer:

> "It uses reflection."

A senior-level answer is:

> "During application startup, Spring scans the classpath for candidate classes, reads runtime-retained annotations using reflection, creates bean definitions, resolves dependencies, and builds the application context. The annotations themselves contain only metadata—the Spring container interprets that metadata to decide how beans should be created, wired, and managed."

This demonstrates an understanding of **annotations, reflection, dependency injection, and the Spring container lifecycle**, rather than viewing annotations as "magic."

---

# ✅ Part VII Progress

Completed:

* ✅ Chapter 33 – JVM Class Loading Lifecycle & ClassLoader Architecture
* ✅ Chapter 34 – Reflection API
* ✅ Chapter 35 – Dynamic Proxies & Spring AOP
* ✅ Chapter 36 – Java Annotations, Annotation Processing & Spring Boot Internals

## Next Chapter

**Chapter 37 – Custom ClassLoaders, Plugin Architectures & ClassLoader Leaks**

We'll cover:

* Custom ClassLoaders
* Child-first vs Parent-first loading
* Plugin architectures
* Hot deployment
* Tomcat ClassLoader hierarchy
* OSGi basics
* Spring Boot executable JAR loading
* ClassLoader leaks
* Production debugging scenarios
* Senior interview questions

This chapter is particularly valuable for understanding **application servers, Spring Boot internals, plugin systems, and Metaspace-related production issues**, all of which frequently appear in senior Java interviews.
