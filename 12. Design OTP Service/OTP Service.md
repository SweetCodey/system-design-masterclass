# OTP Service

## Analogy

When you use your email and password to log into your bank account, it theoretically seems secure because you believe no one else knows your password. However, a password is a non-physical entity, meaning if someone discovers your password, they can use it to access your account from anywhere in the world. Now imagine if your password were a "physical key" instead. If someone has to open your account, they need to have the key with them to open it. This is where MFA comes into play.

Multi-Factor Authentication (MFA) requires you to prove your identity using two or more methods - like **something you know** (password), **something you have** (phone), or **something you are** (fingerprint). It's like needing both your house key and a security code to enter - even if someone steals your password, they still can't get in without the second factor. 

MFA can be performed using several methods such as sending an OTP (One Time Password) via SMS or email, using your fingerprint, or using a physical security key. For simplicity, we will go into detail about a single MFA service called OTP Service that performs MFA via SMS OTP.

## What is an OTP Service?

An OTP service is the backend system that handles phone verification from start to finish. Here's how it works: you try to log into a website, and the service creates a random code, saves it, and texts it to your phone. You type that
code back into the website, and the service checks if it matches. After you successfully verify, that code becomes useless - you can't use it again. It's basically a one-time digital key that self-destructs after use.

## Requirements

### Functional Requirements

| Requirement | Description |
| --- | --- |
| Generate OTP | Generate a random 6-digit code and send it to the user via SMS |
| Validate OTP | Accept the OTP entered by the user and verify if it is valid |
| Rate Limit OTP Attempts | Throttle requests when the user enters 3 invalid OTPs for a session |
| OTP Expiry | Set an expiration time of 10 minutes when the OTP is generated. The attempt should fail if the user enters an expired OTP |

### Non-Functional Requirements

| Requirement | Description |
| --- | --- |
| Availability | The system should be highly available with 99.9999% uptime |
| Latency | The user should receive the OTP within 10 seconds after requesting it |

## Capacity Estimation

### Active Users

- Daily Active Users (DAU) - 100 Million

### Throughput

**Write Operations**

We write to the system whenever new OTP is generated. Since we have 100 Million DAU, we expect **100 Million writes per day.**

**Read Operations**

We read from the system whenever we verify the OTP entered by the users. Since we have 100 Million DAU, we expect **100 Million reads per day.** Also, each verification flow allows 3 retries and if we assume 50% of the users retry, we expect **0.5 x 100 Million = 50 million additional reads**. In total, we have **150 million read operations per day**.

### Memory

We store the OTP in cache (discussed later why cache is preferred) whenever it is generated. Along with OTP we also store additional information such as verification identifier, remaining attempts, and Time-To-Live (TTL)

- **Verification identifier** - Assume we use UUID (Universally Unique Identifier), the V4 version uses 36 characters which is equivalent to **36 bytes**
- **Remaining attempts -** This is an integer and takes **4 bytes**
- **OTP** - This is a 6 digit code and takes **6 bytes** (OTP is stored as string not number)
- TTL - Assuming unix timestamp, occupies **8 bytes**

So, in total we need 36 + 4 + 6 + 8 = 54 bytes to store each OTP entry. Assuming 100 Million writes per day, we require **100 Million x 54 bytes = ~5 GB.**

## API Design

### Generate OTP

Let’s say Stark is logging into Instagram with your username and password. Now Instagram wants to make sure you are the owner of the account. So, it takes you to the next screen for OTP verification. In the mean time, Instagram tells OTP service “Hey, Stark wants to login to Instagram. can you share him an OTP to his mobile number 999-999-999 for additional verification”. Now, the OTP service creates a random 6 digit code, stores it in its systems, sends it to Stark’s mobile via SMS. All these communication between the Instagram Service and OTP Service happens through REST API

**HTTP Method**

This tells server what action to perform. In our case, we generate an OTP we use `POST` method. `POST` method is generally used when the action changes adds something new to the system. In this case, we create and store the OTP, we used `POST`

**Endpoint**

This tells the backend service (Ex: Instagram) where to route the request when an OTP has to be generated. We will use the endpoint `/v1/otp/generate`. Here `v1` means version 1 and is called API Versioning. API versioning allows you to make changes to your API without breaking existing clients by using version numbers like /v1/ or /v2/ in the URL path.

**HTTP Body**

Now we know `/v1/otp/generate`, generates the OTP. But the backend service need to provide information such as the user’s mobile number so that the OTP service can send the OTP via SMS after generating it. This information is sent as request body

```json
{
	"clientId": "instagram",
	"mobile": "999-999-999",
	"purpose": "login"
}
```

OTP service can be used by any backend service (client) for OTP generation and validation. Hence the client has to pass its clientId with the OTP service for identifying the system that invokes it. This helps with things such as auditing, throttling when one client overloads the system with traffic, etc.

**HTTP Response**

After generating the OTP, the service generates the OTP and a unique challengeId to track the verification lifecycle. The challengeId is sent to the backend service so that it will be passed back with OTP during verification

```json
{
	"challengeId": "abcdef"
}
```

### Verify OTP

Now Stark receives the OTP via SMS and enters into the OTP screen which sends it to the OTP Service. The service validates if the OTP entered belongs to Stark. If yes, it allows Stark to access his account. If not, it says the OTP is invalid and asks him to enter the correct OTP again.

**HTTP Method**

We will use `POST` method for validating OTP because it changes the state in the system. Example, it marks the user as logged in. 

**Endpoint**

This tells the backend service (Ex: Instagram) where to route the request when an OTP has to be generated. We will use the endpoint `/v1/otp/verify`

**HTTP Body**

We will pass the challengeId and OTP to the OTP service for verification

```json
{
	"challengeId": "abcdef",
	"otp": "123456"
}
```

**HTTP Response**

The OTP service returns either a success or failure response if the OTP is valid or invalid

```json
{
  "challengeId": "abcdef"
	"verificationStatus": "SUCCESS"
}
```

## High Level Design

### Generate OTP

When the backend service has to verify the user identity, the following steps are executed to generate and send the OTP to the user's mobile. Let's take the account login use-case as an example.

![GenerateOTP](Resources/OTPGenerate.png)


1. When the customer enters their credentials to login to their account, the credentials are sent to the backend service via a POST request.
2. The load balancer of the service receives the request and routes it to the backend service.
3. The backend service validates the credentials. If not valid, it sends a failure response; otherwise, it fetches the user's mobile number from the database and makes a POST call to the OTP service to generate
an OTP.
4. The load balancer of the OTP service receives the request and routes it to the OTP service.
5. The OTP service generates a random 6-digit code using the code generation algorithm/logic
6. The OTP Service stores it in the cache with `attemptsLeft` of 3 and a TTL (Time-To-Live) of 10 minutes
7. The OTP service sends the code as an SMS to the user's mobile number.

**Why use cache instead of database to store OTP?**

OTPs by nature are short-lived codes, meaning they become obsolete after some time. Also, OTP is sensitive data, and there is no reason for someone to see it later.

Databases in general are used for long-lived persistent storage like user information, order history, payment transactions, etc. So, using databases for storing OTP doesn't make sense. 

Let's look at other options. One is cache. Cache naturally fits our use-case because the **OTP has to expire after 10 minutes**, and the **verification of OTP should be faster**. Almost all caching technologies such as Redis come with built-in TTL. When adding something to cache, we specify the TTL, and the entry is automatically removed from cache after the TTL expires. Also, caches are faster (1 - 3 ms) compared to databases (5 - 20 ms), and hence the OTP verification process will be faster.

**How Does the OTP Service Track User-Specific Codes?**

Ever wondered how the OTP service knows which code belongs to a specific user's flow? 

Simple - it can be tracked using a random unique ID called the verificationId. When the OTP service generates a code, it also creates a unique verificationId which is sent to the backend service. The backend service returns the verificationId to the user's device while rendering the OTP page or screen. When the user enters the OTP, it's sent to the backend service along with the verificationId. The OTP service then checks if the verificationId + OTP combination received matches the one stored in the system.

### Verify OTP

The user receives the OTP via SMS, enters into the website for additional verification. The following steps explain the verification process.

![ValidateOTP](Resources/OTPValidate.png)

1. When the customer enters the OTP on the website, it is sent to the backend service via a POST request.
2. The load balancer of the service receives the request and routes it to the backend service.
3. The backend service sends the OTP to the OTP service for verification
4. The load balancer of the OTP service receives the request and routes it to the OTP service.
5. The OTP service first checks whether the token has expired or the user has exceeded the maximum allowed attempts (`attemptsLeft`). If the token has not expired and the limit hasn't been reached, it compares the submitted code against the one stored in cache. When both codes match, it sends a success response. However, if the user has exceeded the attempt limit, the token has expired or if the codes don't match, it sends a failure response.
6. The response from the OTP Service is sent back to the load balancer
7. The load balancer sends back the response to the backend service
8. Backend services returns the response to its load balance
9. The load balancer finally sends the response to the client device.


## Dive Deep Insights

### Cache Selection

We chose cache over database because OTPs are expected to be short-lived and should be invalidated or removed after the expired time. So, the most important requirement is built-in TTL (Time-To-Live) support. We also expect the retrieval to be faster and hence we can choose in-memory caches like Redis. Redis stores data in the RAM (memory) instead of disk for faster access.

But RAM is temporary memory. How to recover lost data in case of failures? The answer is backup. For example, Redis offers periodic backup options like **RDB (Redis Database) Snapshot** and **Append-Only File (AOF)**.

![RedisSnapshot](Resources/RedisSnapshot.png)
- In RDB snapshot, Redis periodically saves the snapshot of the cache at that point in time and writes it to the disk. In case of recovery after failure, Redis reconstructs the entries from the snapshot. One issue with this solution is that the snapshot happens at regular intervals (say 5 minutes) and if there are failures at the 3rd minute after the last backup, we lose that 3-minute data.
- In AOF method, all writes to Redis cache are persisted in an append-only file. So, in case of recovery after failure, Redis reconstructs all the entries from the file. This write happens in a separate thread so that the main thread is not blocked.

### OTP Storage Security

OTP is sensitive data and can be used against the actual user if it gets into the wrong hands, like attackers. So, it is not safe to store as plain text in the system. Since we store OTPs in cache, plain text OTPs can be exposed via log files, network interception of cache traffic, direct user access with admin permissions, etc. So, we will transform the plain text OTP into a secure hashed version so that it cannot be decoded and misused.

To make the OTP secure, we use one-way hashing functions. Think of a one-way hash function as a juicer. You put raw fruits in and get juice out of it. But you cannot reverse the process and bring back the fruits from the juice. 

![OTPStorageSecutrity](Resources/OTPStorageSecutrity.png)

Similarly, in one-way hash functions, you give an input and get an output. But you can never reverse the process to get the original input from the output. One of the most common and secure hash functions is SHA-256 (Secure Hash Algorithm 256). The 256 mentioned here is the output size of 256 bits, meaning for inputs of any size, it always produces a unique output with a fixed size of 256 bits. So, when the OTP service generates the OTP, it converts the OTP into a hashed format using the SHA-256 function and stores it in the cache. When the user enters the OTP and sends it to the OTP service, the service converts the OTP to the hashed format using the same SHA-256 function and compares it against the one in the cache.

### High Availability

We expect the system to be highly available with an uptime of 99.9999% (we allow only 31.5 seconds of outage per year). There is no single solution to keep the system up throughout the year. We should combine multiple strategies discussed below to make our system resilient.

**Load Balancing**

A load balancer acts like a traffic controller that distributes requests across multiple servers to prevent any single server from getting overloaded. If there are 10 hosts, the load balancer checks if all 10 hosts are healthy. If some hosts are unhealthy, it doesn't send the request to those servers; instead, it sends requests to alternate healthy servers. We will place load balancers before the OTP Service to make sure the servers are not overloaded with requests. 

![LoadBalancing](Resources/LoadBalancer.png)

Some of the common load balancing strategies are discussed below:

1. Round Robin - Requests are distributed in order. For example, if there are 11 requests and 10 hosts, each host is given one request and finally the first host gets the 11th request
2. Least Connections - Requests are routed to the server that is currently serving fewer requests.
3. Weighted Routing - Send more traffic to powerful servers with more CPU and memory compared to the other servers.

**Multi-Region Deployment**

Ideally, the service will be deployed on a server placed in a data center in some part of the world. Assume the server is located in the USA. If the data center goes down due to unforeseen circumstances like power outage, natural calamity, or human error, there will be no server to serve the traffic for the OTP service. So, when building a resilient system, we should make sure the service is hosted in multiple physical locations (Ex: other regions like Europe, India, etc.) to consistently serve the traffic even if one data center is brought down due to issues.

![MultiRegion](Resources/MultiRegion.png)

**Auto Scaling**

Auto Scaling automatically increases/decreases the number of servers based on traffic demand. It adds more servers (scale up) when the current servers can't handle the incoming traffic and removes servers (scale down) that are underutilized when traffic comes down. It monitors metrics like CPU, memory usage, etc. to decide if the current servers can handle the incoming traffic. This makes the service highly available to serve incoming traffic spikes without failing them.

![AutoScaling](Resources/AutoScaling.png)

Note that Auto Scaling can also cause issues due to Denial of Wallet (DoW) attacks that target cloud services by generating massive traffic. As the system supports auto scaling, it keeps adding more and more hosts to handle the incoming traffic, resulting in over usage, thus increasing the infrastructure cost. So it is safer to set a upper threshold on the scaling limits like “don’t go beyond 100 servers”.


**Retry Mechanism**

Retry mechanisms automatically retry failed requests without failing the customer. This is very useful to handle transient failures such as network timeouts or temporary service unavailability. For example, in our use case, when the backend service invokes the OTP service to generate the OTP and fails due to transient failures, instead of failing the entire request, it retries generating the OTP 2-3 times.

But this retry mechanism makes the problem even worse if not handled properly. Assume we retry every 1 second in case of failures. This will overload the server more frequently that already couldn't handle the traffic. So, we use **exponential backoff**, a retry mechanism that retries after 1s, 2s, 4s, 8s, and so on (the delay increases exponentially). This gives the failed server ample time to come back to a healthy state.

![RetryMechanism](Resources/RetryMechanism.png)

Exponential backoff also might overload the server because burst traffic is sent to the servers at exponential intervals. For example, if 1000 requests failed on a specific second, all these requests will be retried at seconds 2, 4, 8, and so on. This send burst traffic to the server recovering from outage. To avoid this, we add random delay called Jitter (Ex: random value between 0 to 0.5) to distribute the traffic. For instance, if there are 3 failed request, and the retry delay is 1 second, we add random jitter with the retry time to distribute the load, `req 1: 1 + 0.3s = 1.3s`, `req 2: 1 + 0.1s = 1.1s`, and `req 3: 1 + 0.2s = 1.2s`


**Blue Green Deployment**

Blue-Green deployment maintains two identical production environments, blue and green. Blue represents the current environment serving traffic and green represents the new version being deployed. Any new deployments happen in the green environment, and it will be tested with test data. Once confident, the traffic will be switched from blue to green. If there are issues, the traffic will be switched back from green to blue. If no issues are observed during a certain duration (aka bake time), the blue environment is destroyed.

![BlueGreenDeployment](Resources/BlueGreenDeployment.png)
