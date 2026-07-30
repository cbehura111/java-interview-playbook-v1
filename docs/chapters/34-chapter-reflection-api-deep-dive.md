# Part VII – Class Loading, Reflection & Dynamic Proxies

# Chapter 34: Reflection API (Deep Dive)

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, Microsoft, Goldman Sachs, VMware, Spring Framework, Hibernate Interviews

---

# 1. Why Do Interviewers Ask This?

Reflection powers almost every major Java framework.

Examples:

* Spring Boot
* Spring DI
* Spring MVC
* Hibernate
* Jackson
* JUnit
* Mockito
* Lombok (partially, alongside annotation processing)
* Dependency Injection frameworks

If you've worked with Spring, you've indirectly used Reflection thousands of times.

Typical interview questions:

* What is Reflection?
* Why is Reflection slower?
* How does Spring create beans?
* Can Reflection access private fields?
* What are Method Handles?

---

# 2. 30-Second Interview Answer

> Reflection is a Java API that allows programs to inspect and manipulate classes, methods, fields, constructors, and annotations at runtime without knowing their details at compile time. Frameworks such as Spring, Hibernate, and Jackson rely heavily on Reflection for dependency injection, object creation, serialization, and annotation processing. Reflection is flexible but generally slower than direct method invocation because many compile-time optimisations cannot be applied.

---

# 3. What is Reflection?

Normally we write

```java
Employee employee = new Employee();

employee.calculateSalary();
```

Compiler already knows

* Class
* Method
* Fields

Everything is fixed.

Reflection allows us to discover them at runtime.

---

# 4. Reflection Architecture

```text
          Employee.class

                │

                ▼

        Reflection API

        ├──────────────┐
        ▼              ▼

    Fields          Methods

        ▼              ▼

   Constructors   Annotations
```

---

# 5. Getting a Class Object

Three common approaches.

### Using `.class`

```java
Class<Employee> clazz = Employee.class;
```

---

### Using an Object

```java
Employee employee = new Employee();

Class<?> clazz = employee.getClass();
```

---

### Using Class Name

```java
Class<?> clazz =
    Class.forName("com.example.Employee");
```

Useful when the class name is only known at runtime.

---

# 6. Reading Class Information

Example

```java
Class<?> clazz = Employee.class;

System.out.println(clazz.getName());

System.out.println(clazz.getSimpleName());

System.out.println(clazz.getPackageName());
```

Output

```text
com.example.Employee

Employee

com.example
```

---

# 7. Accessing Fields

Example

```java
public class Employee {

    private String name;

}
```

Reflection

```java
Field field =
    Employee.class.getDeclaredField("name");

System.out.println(field.getName());
```

---

# 8. Reading Private Fields

Example

```java
Employee employee =
    new Employee();
```

Reflection

```java
Field field =
    Employee.class.getDeclaredField("name");

field.setAccessible(true);

System.out.println(field.get(employee));
```

Private fields can be accessed.

This is why Reflection should be used carefully.

---

# 9. Updating Private Fields

```java
field.set(employee, "John");
```

Now

```java
employee.getName();
```

returns

```text
John
```

---

# 10. Calling Methods Dynamically

Example

```java
Method method =
    Employee.class.getMethod("calculateSalary");

method.invoke(employee);
```

The method name is resolved at runtime.

---

# 11. Calling Private Methods

Example

```java
Method method =
    Employee.class.getDeclaredMethod("calculate");

method.setAccessible(true);

method.invoke(employee);
```

Again,

Reflection bypasses normal access checks (subject to Java's module system and security restrictions in modern JDKs).

---

# 12. Constructors

Reflection can create objects.

```java
Constructor<Employee> constructor =
    Employee.class.getConstructor();

Employee employee =
    constructor.newInstance();
```

This is how many frameworks instantiate classes.

---

# 13. Reading Annotations

Suppose

```java
@Service
public class EmployeeService {

}
```

Reflection

```java
Class<?> clazz =
    EmployeeService.class;

boolean present =
    clazz.isAnnotationPresent(Service.class);
```

Spring heavily relies on this.

---

# 14. Listing Methods

```java
Method[] methods =
    Employee.class.getDeclaredMethods();
```

Frameworks inspect methods this way.

Example

```text
save()

delete()

findById()

calculateSalary()
```

---

# 15. Reflection Performance

Interview favourite.

Direct call

```java
employee.calculateSalary();
```

Reflection

```java
method.invoke(employee);
```

Reflection is slower because:

* Method lookup and invocation happen at runtime.
* The JVM has fewer optimisation opportunities than with direct calls.
* Access checks and additional indirection add overhead.

For most framework startup or configuration tasks, this overhead is acceptable.

---

# 16. Method Handles

Modern alternative.

Package

```text
java.lang.invoke
```

Example

```java
MethodHandles.Lookup lookup =
    MethodHandles.lookup();
```

Advantages

* Better performance than traditional Reflection in many scenarios.
* Designed to cooperate more closely with JVM optimisations.
* Widely used in modern frameworks and language features.

---

# 17. Reflection in Spring

Spring startup

```text
@ComponentScan

↓

Find Classes

↓

Read Annotations

↓

Find Constructors

↓

Create Beans

↓

Inject Dependencies
```

Reflection is used throughout the container lifecycle.

---

# 18. Reflection in Hibernate

Hibernate

↓

Reads

```text
@Entity

@Id

@Column
```

↓

Creates SQL Mapping

↓

Loads Objects

Reflection accesses entity fields and constructors without requiring handwritten mapping code.

---

# 19. Reflection in Jackson

Suppose

```java
public class Employee {

    private String name;

}
```

Jackson

↓

Reads Fields

↓

Creates Object

↓

Sets Values

Reflection enables automatic JSON serialization and deserialization.

---

# 20. Common Interview Traps

### Does Reflection break encapsulation?

✅ Yes.

It can access private members when permitted.

---

### Is Reflection always slow?

❌ No.

It is slower than direct invocation, but for many framework operations the overhead is insignificant because those operations are not on performance-critical paths.

---

### Does Spring use Reflection?

✅ Yes.

Spring uses Reflection extensively for bean creation, dependency injection, annotation scanning, and method invocation.

---

### Is Reflection compile-time or runtime?

✅ Runtime.

---

### Can Reflection create objects?

✅ Yes.

Using constructors discovered at runtime.

---

# 21. Production Example

Spring Boot Startup

```text
@Component

↓

Reflection

↓

Constructor Found

↓

Object Created

↓

Dependency Injected
```

Without Reflection,

Spring would require manual wiring of every bean.

---

# 22. Production Debugging Story

Problem

A Spring Boot application failed during startup.

Error

```text
NoSuchMethodException
```

Investigation

A framework attempted to instantiate an entity using Reflection.

The entity no longer had a no-argument constructor.

Root Cause

Hibernate could not create the object reflectively.

Fix

Add a suitable constructor (or configure the framework appropriately for the chosen constructor strategy).

---

# 23. Senior-Level Follow-up Questions

1. What is Reflection?
2. Why is Reflection slower?
3. How does Spring use Reflection?
4. How does Hibernate use Reflection?
5. Can Reflection access private fields?
6. Difference between `getMethod()` and `getDeclaredMethod()`?
7. Difference between `getField()` and `getDeclaredField()`?
8. What are Method Handles?
9. When should Reflection be avoided?
10. What are the security implications of Reflection?

---

# 24. Real Interview Scenario

**Interviewer:**

> "Spring creates beans without you explicitly calling constructors. How?"

### Strong Answer

> During startup, Spring scans the classpath for annotated classes such as `@Component`, `@Service`, and `@Repository`. Using Reflection, it inspects constructors, creates object instances, resolves dependencies, and injects them into the appropriate fields or constructors. Reflection allows Spring to perform this dynamically without compile-time knowledge of the application's classes.

---

# 25. Cheat Sheet

| Reflection API | Purpose          |
| -------------- | ---------------- |
| `Class`        | Class metadata   |
| `Field`        | Access fields    |
| `Method`       | Invoke methods   |
| `Constructor`  | Create objects   |
| `Annotation`   | Read annotations |

---

## Reflection Flow

```text
Class

↓

Reflection

↓

Fields

Methods

Constructors

Annotations

↓

Dynamic Access
```

---

## Framework Usage

| Framework | Reflection Used For                                     |
| --------- | ------------------------------------------------------- |
| Spring    | Bean creation, DI, AOP, annotation scanning             |
| Hibernate | Entity mapping, object creation                         |
| Jackson   | Serialization/deserialization                           |
| JUnit     | Test discovery and execution                            |
| Mockito   | Mock generation (alongside proxies/bytecode generation) |

---

# 🎯 Interview Secret

When an interviewer asks:

> **"Why does Spring use Reflection?"**

Don't answer:

> "To call methods dynamically."

A senior-level answer is:

> "Reflection enables Spring to discover application classes at runtime, inspect annotations, instantiate beans, inject dependencies, and invoke lifecycle methods without compile-time knowledge of the application's structure. This flexibility is what allows Spring's dependency injection and auto-configuration features to work."

This demonstrates that you understand not only the Reflection API but also **how enterprise frameworks are built**.

---

## Next Chapter

**Chapter 35 – Dynamic Proxies (JDK Proxy, CGLIB & Spring AOP Internals)**

We'll cover:

* Why Dynamic Proxies exist
* JDK Dynamic Proxy internals
* CGLIB proxies
* Byte Buddy overview
* Spring AOP internals
* Transaction management (`@Transactional`)
* Proxy limitations
* Self-invocation problem
* Performance considerations
* Real production debugging scenarios

This is one of the most frequently asked Spring internals topics in senior Java backend interviews because it connects **Reflection, AOP, transactions, and framework design**.
