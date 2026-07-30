# Part VII – Class Loading, Reflection & Dynamic Proxies

# Chapter 37: Custom ClassLoaders, Plugin Architectures & ClassLoader Leaks

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Oracle, VMware, Red Hat, Atlassian, Spring, Tomcat, JVM Performance Interviews

---

# 1. Why Do Interviewers Ask This?

ClassLoaders are one of the least understood parts of the JVM.

However, they're heavily used by:

* Spring Boot
* Tomcat
* IntelliJ IDEA
* Maven
* Jenkins
* Kafka Connect
* Plugin frameworks
* OSGi

Understanding ClassLoaders helps explain:

* Hot deployment
* Plugin architectures
* Metaspace leaks
* Multiple versions of the same library
* Application server internals

Typical interview questions:

* What is a Custom ClassLoader?
* Why do plugin systems use ClassLoaders?
* What is a ClassLoader leak?
* How does Tomcat isolate applications?
* Can two versions of the same class exist?

---

# 2. 30-Second Interview Answer

> A ClassLoader is responsible for loading Java classes into the JVM. While the JVM provides Bootstrap, Platform, and Application ClassLoaders, applications can create Custom ClassLoaders to load classes from different sources such as plugins, remote locations, or encrypted JARs. Each ClassLoader creates its own namespace, allowing multiple versions of the same class to coexist. Improper management of ClassLoaders can lead to Metaspace memory leaks.

---

# 3. Why Do We Need Custom ClassLoaders?

Normally

```text
Application

↓

Application ClassLoader

↓

Application Classes
```

But suppose

Users can install

```text
Plugins
```

at runtime.

The Application ClassLoader cannot automatically load new JARs added after startup.

Need

```text
Custom ClassLoader
```

---

# 4. Plugin Architecture

```text
Main Application

        │

        ▼

Plugin Manager

        │

 ┌──────┴────────┐

 ▼               ▼

Plugin A     Plugin B

ClassLoader  ClassLoader
```

Each plugin has its own ClassLoader.

---

# 5. Why Separate ClassLoaders?

Suppose

Plugin A

uses

```text
Jackson 2.15
```

Plugin B

uses

```text
Jackson 2.18
```

Normally

↓

Conflict.

With separate ClassLoaders

↓

No conflict.

Each plugin loads its own version.

---

# 6. Class Namespace

Interview favourite.

The JVM identifies a class by:

```text
(ClassLoader, Fully Qualified Class Name)
```

Not simply

```text
com.example.Employee
```

Therefore

```text
Plugin1

↓

Employee.class
```

and

```text
Plugin2

↓

Employee.class
```

are considered different classes if loaded by different ClassLoaders.

---

# 7. Custom ClassLoader Example

Simplified example

```java
public class PluginClassLoader
        extends ClassLoader {

    @Override
    protected Class<?> findClass(String name)
            throws ClassNotFoundException {

        // Read class bytes

        return defineClass(
                name,
                bytes,
                0,
                bytes.length);

    }

}
```

Most custom loaders override `findClass()` while allowing the normal delegation process to remain intact.

---

# 8. Parent-First Loading

Default Java behaviour.

```text
Application Loader

↓

Platform Loader

↓

Bootstrap

↓

Found?

↓

Yes → Return

↓

No

↓

Load Yourself
```

Safe.

Reliable.

Prevents core classes from being replaced.

---

# 9. Child-First Loading

Some plugin systems prefer

```text
Child First

↓

Parent Later
```

Why?

Plugin wants

its own library

instead of

application library.

Used carefully because it increases the risk of version conflicts.

---

# 10. Parent-First vs Child-First

| Parent First                    | Child First                      |
| ------------------------------- | -------------------------------- |
| Java default                    | Used by some plugin systems      |
| Better security                 | Better version isolation         |
| Prevents overriding JDK classes | Allows plugin-specific libraries |
| Simpler                         | More complex                     |

---

# 11. Tomcat ClassLoader Architecture

Interview favourite.

Simplified hierarchy

```text
Bootstrap

↓

Platform

↓

Common

↓

Web App 1

Web App 2

Web App 3
```

Each deployed application gets its own Web Application ClassLoader.

---

# 12. Why Tomcat Uses Multiple ClassLoaders

Suppose

Application A

uses

```text
Spring 6.0
```

Application B

uses

```text
Spring 6.2
```

Both can run inside the same Tomcat instance because each web application has its own ClassLoader.

---

# 13. Spring Boot Executable JAR

Spring Boot packages dependencies inside

```text
BOOT-INF/lib
```

At startup,

Spring Boot uses a specialised launcher and ClassLoader to load nested JARs, since the standard Java launcher cannot directly load JARs nested inside another JAR.

---

# 14. Hot Deployment

Example

```text
Deploy v1

↓

Users Working

↓

Deploy v2

↓

Old Classes Unloaded

↓

New Classes Loaded
```

Requires the old ClassLoader and all associated classes to become unreachable.

---

# 15. ClassLoader Leak

One of the most important interview topics.

Suppose

```text
Old Application

↓

Old ClassLoader
```

Application is undeployed.

But

A static reference still points to an object loaded by the old ClassLoader.

Result

```text
Old ClassLoader

Still Reachable
```

GC cannot reclaim it.

---

# 16. Why Is This Dangerous?

Old ClassLoader

↓

Cannot be collected

↓

Classes remain loaded

↓

Metaspace grows

↓

Eventually

```text
OutOfMemoryError:

Metaspace
```

---

# 17. Common Causes of ClassLoader Leaks

* Static collections
* ThreadLocal values not removed
* Threads that continue running after undeploy
* JDBC drivers not deregistered
* Logging framework references
* Caches holding application classes

---

# 18. Production Example

Tomcat

Application

↓

Undeployed

↓

Background thread

Still running

↓

Thread references application classes

↓

ClassLoader retained

↓

Metaspace leak

---

# 19. Production Debugging Story

Problem

Tomcat server

↓

Applications redeployed daily

↓

Memory usage increased every day

Eventually

```text
OutOfMemoryError:

Metaspace
```

Investigation

Heap dump

↓

MAT

↓

Reference chain

↓

Background scheduler thread

↓

Old WebApp ClassLoader

Root Cause

Thread never stopped during application shutdown.

Fix

* Properly shut down executors.
* Deregister resources.
* Release ThreadLocal values.
* Ensure application shutdown hooks clean up resources.

---

# 20. OSGi (High-Level)

OSGi is a module system where:

* Each bundle has its own ClassLoader.
* Bundles can be installed or removed dynamically.
* Different bundle versions can coexist.
* Services are shared through defined interfaces.

You don't need deep OSGi knowledge for most interviews, but knowing why it exists is useful.

---

# 21. Common Interview Traps

### Can the same class exist twice?

✅ Yes.

If loaded by different ClassLoaders.

---

### Can two versions of the same library coexist?

✅ Yes.

With separate ClassLoaders.

---

### Is ClassLoader memory stored in the Heap?

❌ Not primarily.

Class metadata resides in **Metaspace**, while ClassLoader objects themselves are ordinary Java objects stored on the heap.

---

### Can GC unload classes?

✅ Yes.

But only when the associated ClassLoader is no longer reachable.

---

### Does undeploying a WAR automatically free Metaspace?

❌ Not always.

Only if all references to the application's ClassLoader have been released.

---

# 22. Senior-Level Follow-up Questions

1. Why use a Custom ClassLoader?
2. What is a plugin architecture?
3. Explain ClassLoader namespaces.
4. Parent-first vs Child-first loading?
5. Why does Tomcat use multiple ClassLoaders?
6. What causes ClassLoader leaks?
7. How do you debug Metaspace leaks?
8. Why can two versions of the same class exist?
9. How does Spring Boot load nested JARs?
10. When are classes unloaded?

---

# 23. Real Interview Scenario

**Interviewer:**

> "A Tomcat server runs fine initially, but after several application redeployments it throws `OutOfMemoryError: Metaspace`. What would you investigate?"

### Strong Answer

> I'd suspect a ClassLoader leak. I'd verify whether application threads, ThreadLocal values, static caches, JDBC drivers, or logging frameworks are retaining references to the old Web Application ClassLoader after undeployment. I'd analyse a heap dump with Eclipse MAT, inspect the reference chain to the ClassLoader, and ensure all application resources are properly cleaned up during shutdown.

---

# 24. Cheat Sheet

| Concept            | Key Point                             |
| ------------------ | ------------------------------------- |
| Custom ClassLoader | Loads classes from custom sources     |
| Parent-First       | Default Java delegation model         |
| Child-First        | Common in plugin systems              |
| Plugin ClassLoader | Isolates plugin dependencies          |
| Tomcat ClassLoader | Isolates deployed applications        |
| Spring Boot Loader | Loads nested JARs                     |
| ClassLoader Leak   | Prevents class unloading              |
| Metaspace OOM      | Often caused by retained ClassLoaders |

---

## ClassLoader Hierarchy

```text
Bootstrap

↓

Platform

↓

Application

↓

Custom / Plugin
```

---

## Plugin Architecture

```text
Application

↓

Plugin Manager

↓

Plugin A Loader

Plugin B Loader

↓

Independent Libraries
```

---

## 🎯 Interview Secret

When the interviewer asks:

> **"Why does Tomcat use a separate ClassLoader for each web application?"**

Don't simply answer:

> "To load the application."

A senior-level answer is:

> "Each web application gets its own ClassLoader to isolate dependencies and allow multiple applications with different library versions to run in the same Tomcat instance. It also enables independent deployment and undeployment. However, this design requires careful resource cleanup because lingering references can prevent the ClassLoader from being garbage collected, leading to Metaspace leaks."

That answer demonstrates an understanding of **JVM internals, application server architecture, and real production troubleshooting**.

---

# ✅ Part VII Complete

You have now covered:

* ✅ JVM Class Loading Lifecycle
* ✅ Reflection API
* ✅ Dynamic Proxies (JDK Proxy & CGLIB)
* ✅ Java Annotations & Annotation Processing
* ✅ Custom ClassLoaders & ClassLoader Leaks

These topics provide a strong understanding of how Java frameworks such as **Spring Boot, Hibernate, Tomcat, and plugin-based systems** work internally.

## Next Part: **Part VIII – Spring Boot Internals & Enterprise Architecture**

We'll dive into:

* Spring IoC Container
* Bean Lifecycle
* Dependency Injection Internals
* Spring Boot Auto-Configuration
* DispatcherServlet Internals
* Spring MVC Request Lifecycle
* Spring Security Internals
* Spring Boot Starter Design
* Spring Events
* Enterprise design patterns
* Production debugging scenarios

This is one of the most valuable sections for **Senior Java Backend** interviews because it bridges JVM knowledge with real-world Spring Boot architecture.
