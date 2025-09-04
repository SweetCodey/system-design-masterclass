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
    - [8. Book a cab](#book-a-cab)
    - [9. Find a cab driver](#find-a-cab-driver)
    - [10. Track the journey](#track-the-journey)
    - [11. Pay for the service](#pay-for-the-service)
    - [12. Service rating system](#service-rating-system)
    - [13. User registration](#user-registration)
    - [14. Cab driver registration](#cab-driver-registration)
- [HIGH LEVEL DESIGN](#high-level-design)
- [DEEP DIVE INSIGHTS](#deep-dive-insights)

<hr style="border:2px solid gray">

# <p style="font-size: 24px; font-style: italic; color:red">DECIDING REQUIREMENTS</p>

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

### Uber Service Provider Functional Requirements

<table>
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Schedule the trip</td>
        <td>Uber service provider should be able to schedule the trip according to user's booking request which includes geo-graphical location(s)</td>
    </tr>
    <tr>
        <td>Booking prioritization</td>
        <td>Uber service provider should be able to prioritize booking for both user and cab driver as per their current rating</td>
    </tr>
    <tr>
        <td>Map service</td>
        <td>Uber service provider should be able to facilitate the city map of their respective state/country for both user & cab driver using a uber mobile application</td>
    </tr>
    <tr>
        <td>Payment gateway</td>
        <td>Uber service provider should be able to provide different ways of payment through payment gateway to the user using a uber mobile application</td>
    </tr>
</table>

## Non Functional Requirements

### Uber customer Non Functional Requirements

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

### Uber Cab Driver Non Functional Requirements

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

# <p style="font-size: 24px; font-style: italic; color:red">CAPACITY ESTIMATION</p>

## DAU MAU ESTIMATION

### Daily Active Users (DAU)

### Monthly Active Users (MAU)

## Throughput Estimation

## Storage

## Memory

## Network and Bandwidth Estimation

<hr style="border:2px solid gray">

# <p style="font-size: 24px; font-style: italic; color:red">API DESIGN</p>

<hr style="border:2px solid gray">

# <p style="font-size:24px; font-style:italic; color:red">HIGH LEVEL DESIGN</p>

<hr style="border:2px solid gray">

# <p style="font-size: 24px; font-style:italic; color:red">DEEP DIVE INSIGHTS</p>