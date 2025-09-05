# UBER CAB SYSTEM DESIGN

- [DECIDING REQUIREMENTS](#deciding-requirements)
    - [1. Functional Requirements](#functional-requirements)
    - [2. Non Functional Requirements](#non-functional-requirements)
- [CAPACITY ESTIMATION](#capacity-estimation)
    - [3. DAU-MAU](#dau-mau-estimation)
    - [4. Throughput](#throughput-estimation)
    - [5. Storage](#storage-estimation)
    - [6. Memory](#memory-estimation)
    - [7. Network and Bandwidth Estimation](#network-and-bandwidth-estimation)
- [API DESIGN](#api-design)
    - [8. User registration](#user-registration)
    - [9. Cab driver registration](#cab-driver-registration)
    - [10. Book a cab](#book-a-cab)
    - [11. Find a cab driver](#find-a-cab-driver)
    - [12. Track the journey](#track-the-journey)
    - [13. Pay for the service](#pay-for-the-service)
    - [14. Service rating system](#service-rating-system)
    - [15. Complaint system](#complaint-system)
- [HIGH LEVEL DESIGN](#high-level-design)
- [DEEP DIVE INSIGHTS](#deep-dive-insights)

<hr style="border:2px solid gray">

# DECIDING REQUIREMENTS

## Functional Requirements

Below is a structured table displaying various requirements and their descriptions.

### User Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>User registration</td>
        <td>User should be able to register using a uber mobile application</td>
    </tr>
    <tr>
        <td>Book a cab</td>
        <td>User should be able to book a Uber cab using a uber mobile application</td>
    </tr>
    <tr>
        <td>Track the trip</td>
        <td>User should be able to track his journey from source to destination using a uber mobile application</td>
    </tr>
    <tr>
        <td>Pay for the trip</td>
        <td>User should be able to pay for his journey after the ride using payment gateway in uber mobile application</td>
    </tr>
    <tr>
        <td>Rate for the trip</td>
        <td>User should be able to rate for his journey after the ride using a uber mobile application</td>
    </tr>
</table>

### Cab Driver Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Cab Driver registration</td>
        <td>Cab driver should be able to register using a uber mobile application</td>
    </tr>
    <tr>
        <td>Accept/decline the booking request</td>
        <td>Cab driver should be able to accept/decline a user booking request using a uber mobile application</td>
    </tr>
    <tr>
        <td>Track the trip</td>
        <td>Cab driver should be able to track his accepted booking journey from source to destination using a uber mobile application</td>
    </tr>
    <tr>
        <td>Payment for the trip</td>
        <td>Cab driver should be able to see the user payment status after completing the trip using uber mobile application</td>
    </tr>
    <tr>
        <td>Rate for the trip</td>
        <td>cab driver should be able to rate for user after the ride using a uber mobile application</td>
    </tr>
</table>

### Uber Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Schedule the trip</td>
        <td>System should be able to schedule the trip according to user's booking request which includes geo-graphical location(s)</td>
    </tr>
    <tr>
        <td>Booking prioritization</td>
        <td>System should be able to prioritize booking for both user and cab driver as per their current rating</td>
    </tr>
    <tr>
        <td>Map service</td>
        <td>System should be able to facilitate the city map of their respective state/country for both user & cab driver using a mobile application</td>
    </tr>
    <tr>
        <td>Payment gateway</td>
        <td>System should be able to provide different ways of payment through payment gateway to the user using a mobile application</td>
    </tr>
</table>

## Non Functional Requirements

### Customer Non Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Availability</strong></td>
        <td>The system should be highly available - <strong>99.99%</strong> uptime</td>
    </tr>
    <tr>
        <td><strong>Scalability</strong></td>
        <td>The system should be able to handle multiple users simultaneously</td>
    </tr>
    <tr>
        <td><strong>Low latency</strong></td>
        <td>The system's turn around time for user's booking request should be very low.</td>
    </tr>
    <tr>
        <td><strong>Customer Experience</strong></td>
        <td>The system should give smooth and seamless experience, if customer's internet is working perfectly</td>
    </tr>
    <tr>
        <td><strong>Security</strong></td>
        <td>The system should provide security with out any data breach</td>
    </tr>
    <tr>
        <td><strong>Storage Reliability</strong></td>
        <td>The system should ensure storage reliability for customer's content by maintaining his/her records and booking history.</td>
    </tr>
</table>

### Cab Driver Non Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Availability</strong></td>
        <td>The system should be highly available - <strong>99.99%</strong> uptime</td>
    </tr>
    <tr>
        <td><strong>Scalability</strong></td>
        <td>The system should be able to handle multiple cab drivers simultaneously</td>
    </tr>
    <tr>
        <td><strong>Low latency</strong></td>
        <td>The system's turn around time for cab driver's booking acceptance/deny should be very low.</td>
    </tr>
    <tr>
        <td><strong>Cab driver Experience</strong></td>
        <td>The system should give smooth and seamless experience, if cab driver's internet is working perfectly</td>
    </tr>
    <tr>
        <td><strong>Security</strong></td>
        <td>The system should provide security with out any data breach of cab driver</td>
    </tr>
    <tr>
        <td><strong>Storage Reliability</strong></td>
        <td>The system should ensure storage reliability for cab driver's content by maintaining his/her records and booking history.</td>
    </tr>
</table>

<hr style="border:2px solid gray">

# CAPACITY ESTIMATION

## DAU MAU ESTIMATION

<strong>How many users are using your software?</strong>
- <strong>Daily Active Users</strong> (DAU) : ```36 million```
- <strong>Monthly Active Users</strong> (MAU) : ```180 million```

## Throughput Estimation

Calculation of write requests and read requests to the system

### Write requests

The possible ways of write requests to the system:
1. Customer/Cab driver details during registration
2. Customer/Cab driver booking acceptance/rejection information
3. Customer payment preference (optional)
4. Customer/Cab driver rating information
5. Customer complaint information

Most of the cases write requests are one time activities or rare scenarios other than booking, payment and rating requests.

<strong>Assumptions</strong>:
- ```90 out of 100``` customers book rides daily.
- ```95 out of 100``` cab drivers accept rides daily.
- ```15 out of 100``` customers do app registrations daily.
- ```20 out of 100``` customers set their payment preferences daily.
- ```60 out of 100``` customers rate for their trip daily
- ```2 out of 100``` customer raise complaints daily

<strong>Calculation</strong>:
- Total DAU: ```36 million```
- Write requests per day:
    - Booking : ```(90/100) times 36,000,000 = 32,400,000 ~ 32.4 million```
    - Ride acceptance : ```(95/100) times 36,000,000 = 34,200,000 ~ 34.2 million```
    - App registrations : ```(15/100) times 36,000,000 = 5,400,000 ~ 5.4 million```
    - Payment preference : ```(20/100) times 36,000,000 = 7,800,000 ~ 7.8 million```
    - Rating : ```(60/100) times 36,000,000 = 21,600,000 ~ 21.6 million```
    - Complaints : ```(2/100) times 36,000,000 = 720,000 ~ 0.72 million```

### Read requests

The possible ways of read requests to the system:
- Trip
    - Preferences
    - Acceptance
    - Scheduling
    - Tracking
    - Fares
    - History
    - Rating
    - Payment
    - Complaint tracking

<strong>Assumptions</strong>:
- ```90 out of 100``` customers read their ride preference(cab type preference e.t.c.) daily.
- ```95 out of 100``` cab drivers read the acceptance request daily.
- ```90 out of 100``` customers read their source and destination while scheduling their ride daily.
- ```55 out of 100``` customers track their journey daily.
- ```85 out of 100``` customers read their trip fare details daily.
- ```10 out of 100``` customers read their trip history daily
- ```20 out of 100``` customers/cab drivers read their user/service ratings daily.
- ```90 out of 100``` customers/cab drivers read the trip payment details after their ride daily.
- ```2 out of 100``` customers/cab drivers track/read trip complaints daily.

<strong>Calculation</strong>:
- Total DAU: ```36 million```
- Read requests per day:
    - Trip
        - Preferences: ```(90/100) times 36,000,000 = 32,400,000 ~ 32.4 million```
        - Acceptance: ```(95/100) times 36,000,000 = 34,200,000 ~ 34.2 million```
        - Scheduling: ```(90/100) times 36,000,000 = 32,400,000 ~ 32.4 million```
        - Tracking: ```(55/100) times 36,000,000 = 19,800,000 ~ 19.8 million```
        - Fares: ```(85/100) times 36,000,000 = 30,600,000 ~ 30.6 million```
        - History: ```(10/100) times 36,000,000 = 3,600,000 ~ 3.6 million```
        - Rating: ```(20/100) times 36,000,000 = 7,200,000 ~ 7.2 million```
        - Payment: ```(90/100) times 36,000,000 = 32,400,000 ~ 32.4 million```
        - Complaint tracking: ```(2/100) times 36,000,000 = 720,000 ~ 0.7 million```

<strong>Summary</strong>

|   Operation                   |   Calculation         |   Result      |
|-------------------------------|-----------------------|---------------|
|   Write                       |(90/100) x 36 million  |	32.4 million|
|                               |(95/100) x 36 million  |	34.2 million|
|                               |(15/100) x 36 million  |	5.4 million |
|                               |(20/100) x 36 million  |	7.8 million |
|                               |(60/100) x 36 million  |	21.6 million|
|                               |(02/100) x 36 million  |	0.72 million|
|Total write request(s) per day |                       | 102.12 million|
|   Read                        |(90/100) x 36 million  |   32.4 million|
|                               |(95/100) x 36 million  |   34.2 million|
|                               |(90/100) x 36 million  |   32.4 million|
|                               |(55/100) x 36 million  |   19.8 million|
|                               |(85/100) x 36 million  |   30.6 million|
|                               |(10/100) x 36 million  |   3.6 million |
|                               |(20/100) x 36 million  |   7.2 million |
|                               |(90/100) x 36 million  |   32.4 million|
|                               |(02/100) x 36 million  |   0.7 million |
|Total read request(s) per day  |                       | 193.3 million |

## Storage Estimation

<strong>Assumptions</strong>

- Average size of a customer record: ```100 MB```
- Daily write operations to the system: ```102.12 million```

<strong>Storage Calculations</strong>

1. <strong>Daily storage requirement</strong>:
    ```100 MB x 102.12 million requests per day = 10.212 PB per day```
2. <strong>Storage requirement for 10-Years</strong>:
    ```10.212 PB per day x 365 days x 10 years = 512.6 PB```

<strong>Summary</strong>
|   Metric          |   Calculation                      |   Result        |
|-------------------|------------------------------------|-----------------|
| Daily Storage     | 100 MB x 102.12 M req/day          |   10.212 PB     |
| 10-Year Storage   | 10.212 PB/day x 365 days x 10 years|    3.727 ZB     |

## Memory Estimation

<strong>Overview</strong>
By memory, we refer to the <strong>cache memory size</strong> required for faster data access.

<strong>Why Cache Memory</strong>
Accessing data directly from the database takes time. To speed up data retrieval, cache memory is used.

<strong>Cache Memory Requirement Calculation</strong>

- <storage>Daily Storage Requirement</storage>: ```10.212 PB```
- <storage>Cache Requirement(1% of Daily Storage)</storage>: ```(1/100) x 10.212 PB = 102.12 TB```

<strong>Scalability</strong>
The memory size should scale as the system grows to accommodate increasing storage and data access demands.

## Network and Bandwidth Estimation

<strong>Overview</strong>
Network/Bandwidth estimation helps us determine the amount of data flowing in and out of the system per second.

<strong>Data Flow Estimations</strong>

<strong>Ingress</strong> (Data flow into the system)

- <strong>Data stored per day</strong>: ```10.212 PB```
- <strong>Calculation</strong>: ```10.212 PB / (24 x 60 x 60) = 118.194 GB/sec```
- <strong>Result:</strong> Incoming Data Flow = ```118.194 GB/sec```

<strong>Egress</strong> (Data flow out of the system)

- <strong>Total read requests per day</strong>: ```193.3 million```
- <strong>Average customer record size</strong>: ```100 MB```
- <strong>Daily Outgoing Data</strong>: ```193.3 million x 100 MB = 19.33 PB/day```
- <strong>Calculation</strong>: ```19.33 PB / (24 x 60 x 60) = 223 GB/sec```
- <strong>Result</strong>: ```223 GB/sec```

<strong>Summary</strong>

|       Type           |        Calculation        |   Result       |
|----------------------|---------------------------|----------------|
|Ingress (Data flow in)| 10.212 PB / (24 x 60 x 60)|118.194 GB/sec  |
|Egress (Data flow out)| 19.33 PB / (24 x 60 x 60) |223 GB/sec      |

<hr style="border:2px solid gray">

# API DESIGN

## User Registration

Lets understand how user register in cab sharing application.

When we ask the server to register a user, we use an API call. This is how computers talk to each other.

We follow a standard way to register a user and will use a REST API for this communication. Here are the technical details.

<!--Include HTTP request picture -->

### HTTP Method
This tells to the server what action to perform. Since we want to create new user on the server, we use the `POST` action.

### Endpoint
This tells the server where to perform that action. Since we are creating a new user, we will use the `/v1/users/customers` endpoint of the server.

**Note:**
```
'v1' means version 1. It is good practice to version your APIs.
```

### HTTP Body
We have told the server to create a user, but we haven't provided the details of the user itself. This information is sent in the request body:

```json
{
    "userName":"Name of the user",
    "userEmailId":"EmailId of the user",
    "userPhoneNumber":"Phone number of the user",
    "userIdentityNumber":"National Identification Number of the user",
    "userNationality":"Nationality of the user"
}
```

## Cab driver registration

Lets understand how cab driver register in cab sharing application.

When we ask the server to register a cab driver, we use an API call. This is how computers talk to each other.

We follow a standard way to register a cab driver and will use a REST API for this communication. Here are the technical details.

<!--Include HTTP request picture -->

### HTTP Method
This tells to the server what action to perform. Since we want to create new cab driver on the server, we use the `POST` action.

### Endpoint
This tells the server where to perform that action. Since we are creating a new cab driver, we will use the `/v1/users/cabDrivers` endpoint of the server.

### HTTP Body
We have told the server to create a cab driver profile, but we haven't provided the details of the cab driver itself. This information is sent in the request body:

```json
{
    "cabDriverName":"Name of the cab driver",
    "cabDriverEmailId":"EmailId of the cab driver",
    "cabDriverPhoneNumber":"Phone number of the cab driver",
    "cabDriverIdentityNumber":"National Identification Number of the cab driver",
    "cabDriverNationality":"Nationality of the cab driver",
    "cabNumber":"Vehicle number of the cab driver",
    "cabDriverLicense":"License number of the cab driver"
}
```

## Book a cab

## Find a cab driver

## Track the journey

## Pay for the service

## Service rating system

## Complaint system

<hr style="border:2px solid gray">

# HIGH LEVEL DESIGN

<hr style="border:2px solid gray">

# DEEP DIVE INSIGHTS

<hr style="border:2px solid gray">