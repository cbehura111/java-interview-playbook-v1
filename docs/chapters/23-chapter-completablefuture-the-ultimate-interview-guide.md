# Part V - Executor Framework & Asynchronous Programming

# Chapter 23: CompletableFuture - The Ultimate Interview Guide

> **Interview Difficulty:** ⭐⭐⭐⭐⭐
>
> **Frequently Asked In:** Amazon, Microsoft, Oracle, Visa, Walmart, Goldman Sachs, Adobe, Atlassian

---

# 1. Why Do Interviewers Ask This?

Almost every modern Java backend application uses asynchronous programming.

If you're working with:

* Spring Boot
* Microservices
* Kafka
* REST APIs
* External services
* Database calls

...you'll eventually use `CompletableFuture`.

The interviewer wants to evaluate whether you understand:

* Asynchronous programming
* Non-blocking workflows
* Parallel execution
* Error handling
* Performance optimization
* API composition

Typical interview question:

> **Why is CompletableFuture better than Future?**

---

# 2. 30-Second Interview Answer

> `Future` only represents the result of an asynchronous computation and forces callers to block using `get()`. `CompletableFuture` extends `Future` by allowing asynchronous task chaining, composition, callbacks, exception handling, and combining multiple tasks without blocking. This makes it ideal for modern microservices and asynchronous workflows.

---

# 3. Why Future Wasn't Enough

Example:

```java
Future<User> future = executor.submit(() -> getUser());

User user = future.get();
```

Problem:

```text
Submit Task

↓

Wait

↓

Wait

↓

Wait

↓

Result
```

`get()` blocks the current thread.

Now imagine:

```text
Service A

↓

Service B

↓

Service C

↓

Service D
```

If each call blocks,

overall latency increases.

---

# 4. Enter CompletableFuture

Instead of waiting:

```text
Task

↓

Complete

↓

Notify Next Stage
```

The next operation starts automatically.

No explicit waiting.

---

# 5. Creating CompletableFuture

### Simple Example

```java
CompletableFuture<String> future =
	CompletableFuture.completedFuture("Hello");
```

Already completed.

---

### Asynchronous Task

```java
CompletableFuture<String> future =
	CompletableFuture.supplyAsync(() -> {

		return "Hello";

	});
```

Runs in a background thread.

---

# 6. Runnable vs Supplier

Interview favourite.

### Runnable

```java
Runnable
```

Returns

```text
void
```

---

### Supplier

```java
Supplier<String>
```

Returns

```text
String
```

Therefore

```java
CompletableFuture.supplyAsync(...)
```

returns a value.

---

# 7. thenApply()

Transforms the result.

```java
CompletableFuture<String> future =
	CompletableFuture
		.supplyAsync(() -> "Java")
		.thenApply(s -> s.toUpperCase());
```

Execution

```text
Java

↓

JAVA
```

Think of it like `map()`.

---

# 8. thenAccept()

Consumes the result.

```java
future.thenAccept(System.out::println);
```

No return value.

Used for:

* Logging
* Notifications
* Metrics

---

# 9. thenRun()

Runs another task.

Ignores previous result.

```java
future.thenRun(() -> {

	System.out.println("Completed");

});
```

---

# 10. thenCompose()

One of the most important interview questions.

Suppose

```text
getUser()

↓

getOrders(user)

↓

getPayments(order)
```

Each returns

```text
CompletableFuture
```

Without `thenCompose`

You'll get

```text
CompletableFuture<CompletableFuture<User>>
```

Nested futures.

Wrong.

Instead

```java
getUser()

.thenCompose(user ->
	getOrders(user))
```

Result

```text
CompletableFuture<Order>
```

### Interview Tip

> **thenCompose() is like `flatMap()` in Streams.**

Remember this.

---

# 11. thenCombine()

Suppose two independent APIs.

```text
User API

Order API
```

Run simultaneously.

```java
CompletableFuture<User> user =
		getUser();

CompletableFuture<Order> order =
		getOrder();
```

Combine

```java
user.thenCombine(order,

	(u,o) -> buildResponse(u,o)

);
```

Execution

```text
User API

		 \

		  Combine

		 /

Order API
```

Huge performance improvement.

---

# 12. allOf()

Suppose

10 APIs.

```text
A

B

C

D

E
```

Run all.

```java
CompletableFuture.allOf(

	future1,

	future2,

	future3

);
```

Waits for all.

---

# 13. anyOf()

Suppose

Three cache servers.

Return first response.

```java
CompletableFuture.anyOf(

	cache1,

	cache2,

	cache3

);
```

Fastest wins.

---

# 14. Exception Handling

### exceptionally()

```java
future.exceptionally(ex -> {

	return "DEFAULT";

});
```

Fallback value.

---

### handle()

```java
future.handle((result,error)->{

});
```

Receives

Both

* Success
* Failure

Useful for unified processing.

---

### whenComplete()

```java
future.whenComplete(

(result,error)->{

}
);
```

Used mainly for:

* Logging
* Cleanup
* Metrics

Doesn't modify the result.

---

# 15. Production Example

Suppose your Order API requires:

```text
Customer

Orders

Payments

Recommendations
```

Sequential

```text
Customer

↓

Orders

↓

Payments

↓

Recommendations
```

Latency

```text
300 ms

+

250 ms

+

400 ms

=

950 ms
```

Parallel

```text
Customer

Orders

Payments

Recommendations

↓

Combine
```

Latency

```text
≈ 400 ms
```

This is exactly why `CompletableFuture` is used in microservices.

---

# 16. Custom Executor

Interview trap.

Many developers write:

```java
CompletableFuture.supplyAsync(...)
```

This uses the **ForkJoinPool.commonPool()** by default.

For business applications, it's often better to provide a dedicated executor:

```java
ExecutorService executor =
	Executors.newFixedThreadPool(10);

CompletableFuture.supplyAsync(
	this::fetchOrders,
	executor
);
```

This avoids contention with unrelated tasks and gives you control over sizing and monitoring.

---

# 17. Common Interview Traps

### Does CompletableFuture always create a new thread?

❌ No.

It schedules work using an executor.

---

### Is thenApply asynchronous?

❌ Not necessarily.

`thenApply()` may execute in the thread that completed the previous stage.

For guaranteed asynchronous execution use:

```java
thenApplyAsync()
```

---

### Difference

```text
thenApply

↓

May use same thread

--------------

thenApplyAsync

↓

Uses Executor
```

---

# 18. Production Debugging Story

Problem

API latency doubled.

Investigation

Developers wrote

```java
future1.get();

future2.get();

future3.get();
```

Even though

they used CompletableFuture,

they blocked after every call.

Result

Sequential execution.

Fix

```java
CompletableFuture.allOf(...)
```

Latency reduced by more than half.

---

# 19. Common Interview Questions

### Why is CompletableFuture better than Future?

* Chaining
* Combining
* Exception handling
* Callbacks
* Parallel execution
* Better composability

---

### thenApply vs thenCompose?

`thenApply`

Transforms value.

```text
A

↓

B
```

`thenCompose`

Flattens nested futures.

```text
Future

↓

Future

↓

Future
```

---

### thenApply vs thenApplyAsync?

`thenApply`

May execute on the completing thread.

`thenApplyAsync`

Schedules the stage asynchronously using an executor (default or custom).

---

# 20. Spring Boot Example

```java
@Service
public class OrderService {

	@Async
	public CompletableFuture<Order> getOrder() {

		return CompletableFuture.completedFuture(

				repository.find()

		);

	}

}
```

Controller

```java
CompletableFuture<Order> order =
		service.getOrder();
```

This pattern is common when integrating asynchronous business operations in Spring.

---

# 21. Senior-Level Follow-up Questions

1. Why was Future insufficient?
2. Explain thenCompose().
3. Explain thenCombine().
4. Difference between allOf() and anyOf().
5. What executor does supplyAsync() use by default?
6. Why avoid blocking with get()?
7. How do you propagate exceptions?
8. When would you use a custom executor?
9. How would you aggregate responses from multiple microservices?
10. What happens if one future in allOf() fails?

---

# 22. Cheat Sheet

| Method          | Purpose                         |
| --------------- | ------------------------------- |
| supplyAsync()   | Async task with return value    |
| runAsync()      | Async task without return value |
| thenApply()     | Transform result                |
| thenCompose()   | Chain async operations          |
| thenCombine()   | Merge two independent futures   |
| allOf()         | Wait for all                    |
| anyOf()         | First completed result          |
| exceptionally() | Recover from failure            |
| handle()        | Process success or failure      |
| whenComplete()  | Side effects after completion   |

---

# 🎯 Real Interview Scenario

**Interviewer:**

> "Your API calls three downstream microservices: Customer, Inventory, and Pricing. Each call takes around 300 ms. How would you reduce the response time?"

### Strong Answer

> Since the calls are independent, I'd execute them in parallel using `CompletableFuture.supplyAsync()` with a dedicated executor. I'd combine the results using `CompletableFuture.allOf()` or `thenCombine()`, avoiding sequential waits. I'd also add timeouts, exception handling with `exceptionally()` or `handle()`, and monitor the executor to ensure it doesn't become a bottleneck.

This answer demonstrates not only knowledge of the API but also an understanding of production concerns such as resilience, latency, and thread management.

---

## ⭐ Chapter Summary

By mastering `CompletableFuture`, you can confidently answer questions about:

* Asynchronous programming
* Parallel API aggregation
* Thread management
* Exception handling
* Performance optimization
* Modern Spring Boot backend design

This is one of the most frequently discussed topics in senior Java backend interviews.

---

### Next Chapter

**Chapter 24 - ForkJoinPool & Work-Stealing**

We'll cover:

* Why `ForkJoinPool` was introduced
* Work-stealing algorithm
* RecursiveTask vs RecursiveAction
* Divide-and-conquer programming
* Relationship with `CompletableFuture`
* Parallel streams internals
* Performance trade-offs
* Production use cases
* Common interview traps
* When **not** to use `ForkJoinPool`

This chapter ties together the Executor Framework and the internals behind many modern Java concurrency features.
