# PAYMENT SYSTEM

<!-- toc -->

- [Introduction](#introduction)
  * [What is a payment system?](#what-is-a-payment-system)
  * [Why we need a payment system?](#why-we-need-a-payment-system)
- [Glossary](#glossary)
- [Requirements](#requirements)
  * [Functional Requirements](#functional-requirements)
  * [Non-Functional Requirements](#non-functional-requirements)
- [API Design](#api-design)
  * [Initiate](#initiate)
  * [Pay](#pay)
  * [Payment Status](#payment-status)
  * [Refund](#refund)
- [High Level Design](#high-level-design)
  * [Payment Initiation](#payment-initiation)
  * [Payment Execution](#payment-execution)
    + [Payment Registration](#payment-registration)
    + [Payment Authorization](#payment-authorization)
      - [Payment State Machine](#payment-state-machine)
    + [Payment Status Handling](#payment-status-handling)
      - [Authorization vs Settlement](#authorization-vs-settlement)
    + [Refund Processing](#refund-processing)
- [Deep Dive Insights](#deep-dive-insights)
  * [Database Selection](#database-selection)
  * [Database Modelling](#database-modelling)
  * [Audit Payment Transactions](#audit-payment-transactions)
  * [PCI DSS Compliance](#pci-dss-compliance)
  * [Keeping Sensitive Data Secure](#keeping-sensitive-data-secure)
  * [Preventing Payment Data Loss](#preventing-payment-data-loss)

<!-- tocstop -->

## Introduction
### What is a payment system?
Let’s travel back to the early 1990s. Imagine you go shopping at a store. After selecting your items, you go to the checkout counter and pay for them. The most common way to pay is with cash. In some cases, such as large purchases like a car or a house, people use other payment methods like Demand Drafts (DD) or cheques. The payee deposits the DD or cheque in their bank, and the bank transfers the money from the payer’s account to the payee’s account.

![](Resources/Intro_PhysicalPayment.png)

This physical mode of payment worked well when most purchases happened in physical stores. However, with the growth of the internet in the late 1990s, many companies began selling products online without the need for physical stores. For example, Amazon was founded in 1994 and initially sold books online, while Netflix was founded in 1997 and began selling DVDs through the internet. This shift led to the emergence of a digital payment ecosystem that allows customers to pay merchants online without the need for physical money.

### Why we need a payment system?

In offline payments, only a few parties are involved in moving money. For example, in cash-based payments, only the payer (customer) and payee (merchant) participate. In methods like DD or cheque, the banks of the payer and payee are also involved. In theory, a merchant accepting online payments could collect a customer’s bank details and request a transfer through the banking system. However, the online payment ecosystem has grown rapidly, and many different payment methods now exist across the world and each payment method operates differently.

![](Resources/Intro_PaymentSystem.png)

For example, credit and debit card payments require card networks such as Visa or Mastercard. UPI payments involve a UPI application and the infrastructure operated by NPCI (National Payments Corporation of India). Because of these differences, a merchant that wants to accept multiple payment methods would need to integrate with several banks, networks, and financial institutions. To simplify this complexity, online payment systems have evolved. With a simple onboarding process, merchants can integrate with a payment system and accept multiple payment methods when customers make purchases on their website.

---

## Glossary

We will encounter the following terms in the later sections of this article, so familiarizing yourself with them will help in understanding the content.

![](Resources/Glossary.png)

* **Merchant** – The business that sells products or services and receives the payment from customers. *(Example: Amazon, Swiggy)*
* **Issuing Bank** – The bank that issued the customer’s debit or credit card and checks whether the customer has enough funds to approve the payment. *(Example: HDFC Bank issuing a credit card)*
* **Acquiring Bank** – The bank that enables the merchant to accept card payments and receives the funds on behalf of the merchant. *(Example: ICICI Bank providing payment services to a merchant)*
* **Payment Gateway** – The system that collects payment details from the customer and securely sends the payment request to the processor. *(Example: Stripe checkout page)*
* **Payment Processor** – The system that communicates with card networks and banks to process and authorize the payment. *(Example: Stripe processing a card transaction)*
* **Payment Network** – The network that connects issuing banks and acquiring banks and routes card transactions between them. *(Example: Visa, Mastercard)*

---

## Requirements
### Functional Requirements

<table>
  <tr>
    <th>Requirement</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><b>Payment method support</b></td>
    <td>Allow merchants to accept payments via multiple payment methods such as card, netbanking, UPI, etc.</td>
  </tr>
  <tr>
    <td><b>Manage payment transaction</b></td>
    <td>Create a transaction when a user initiates a payment and track its lifecycle (created, auth_pending, authorized, failed, refunded).</td>
  </tr>
  <tr>
    <td><b>Payment authorization</b></td>
    <td>Send payment requests to the appropriate payment networks/banks and receive authorization or rejection responses.</td>
  </tr>
  <tr>
    <td><b>Refunds</b></td>
    <td>Allow merchants to initiate refunds against a successful payment and track the refund lifecycle.</td>
  </tr>
  <tr>
    <td><b>Webhook notifications</b></td>
    <td>Notify merchant backend asynchronously for key payment events (e.g., payment.authorized, payment.failed, payment.refunded) so merchant systems can update order state reliably.</td>
  </tr>
  <tr>
    <td><b>Idempotent write operations</b></td>
    <td>Prevent duplicate charges/duplicate resources when the same request is retried due to network failures or client retries (especially for write operations like initiating or paying).</td>
  </tr>
</table>

### Non-Functional Requirements

<table>
  <tr>
    <th>Requirement</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><b>Consistency</b></td>
    <td>Maintain correct and consistent transaction states. A payment should never result in conflicting states such as both success and failure.</td>
  </tr>
  <tr>
    <td><b>Security</b></td>
    <td>Protect sensitive financial data using strong encryption in transit and at rest, with strict access controls and least-privilege.</td>
  </tr>
  <tr>
    <td><b>Availability</b></td>
    <td>Remain highly available (e.g., 99.99% uptime) so that merchants can continue accepting payments even during peak traffic.</td>
  </tr>
  <tr>
    <td><b>Scalability</b></td>
    <td>Handle large spikes in transaction volume, especially during peak shopping periods or promotional events.</td>
  </tr>
  <tr>
    <td><b>Durability</b></td>
    <td>Guarantee that no transaction record is ever lost when infrastructure fails.</td>
  </tr>
  <tr>
    <td><b>Auditability</b></td>
    <td>Maintain detailed logs and records of all payment activities to support auditing, dispute resolution, and regulatory compliance.</td>
  </tr>
</table>

---

## API Design
### Initiate
This endpoint starts the payment process by creating a transaction record in the gateway and generating a secure checkout URL for the customer.

![](Resources/API_Initiate.png)

#### HTTP Method & Endpoint
We use the **POST** method to create a new payment resource. The endpoint is `/v1/payments`

#### HTTP Request Header
* **Authorization**: Merchant Secret Key (Bearer token). This authenticates the merchant and the payment gateway
* **Idempotency-Key**: A unique string to prevent duplicate payment creation during retries.

#### HTTP Request Body

```json
{
    "orderId": "order123",
    "merchantCustomerId": "customerId123",
    "amount": "90",
    "tax": "10",
    "currency": "INR",
    "productInfo": {
        "name": "Garnier Facewash",
        "quantity": 1
    }
}
```

> Note: `amount` and `tax` are strings intentionally to avoid floating point precision issues. In production systems, money is typically stored/processed as an integer in the smallest currency unit (e.g., paise/cents) or as a fixed-precision decimal (Ex: 19.99 not 19.999999999).

#### HTTP Response
```json
{
    "paymentId": "payment123",
    "paymentPageUrl": "https://payments.com/v1/payments/payment123/payselect?sessionToken=xyz"
}
```
> paymentId - unique identifier of the payment transaction for the checkout.

---

### Pay
#### Register Payment Method

This endpoint securely adds the customer's payment details to the system. For example, for a card payment, we collect and save card number, and expiry.

![](Resources/API_RegisterPayment.png)

**HTTP Method & Endpoint**

We use the **POST** method to securely register a new payment instrument. The endpoint is `/v1/payments/payment-methods`. Note that we didn't use `/v1/payments/{paymentId}/payment-methods` because adding a card is not specifically tied to a checkout flow. The added card can be used in the future for other checkouts as-well.

**HTTP Request Header**

* **sessionToken**: The random string received from the `paymentPageUrl`. This proves the user has an active, valid session.

**HTTP Request Body**

```json
{
    "cardNumber": "4242424242424242",
    "expiry": {
        "month": "08",
        "year": "2027"
    },
    "cvv": "123"
}
```

> For simplicity, card details in the request body are added as plain text. As the card details are sensitive information, the real payment system will encrypt the data using **client-side encryption** before sending it to the server. We will discuss more about this in the [high level design section](#payment-registration).

**HTTP Response**

```json
{
    "paymentMethodId": "paymentMethod123",
    "displayString": "Visa Card ending in 4242",
    "expiry": {
        "month": "08",
        "year": "2027"
    }
}
```

---

#### Make Payment

This endpoint executes the actual payment attempt. It connects the `paymentId` with the chosen `paymentMethodId` and triggers the communication with the bank or card network.

![](Resources/API_Pay.png)

#### HTTP Method & Endpoint

We use the **POST** method to execute the transaction. The endpoint is `/v1/payments/{paymentId}/pay`

#### HTTP Request Header

* **sessionToken**: Required for user authentication.
* **Idempotency-Key**: A unique string to prevent double charge if the client retries this request.

#### HTTP Request Body

```json
{
    "paymentMethodId": "paymentMethod123"
}

```

#### HTTP Response

```json
{
    "paymentId": "payment123",
    "status": "PENDING",
    "nextAction": {
        "type": "REDIRECT",
        "method": "GET",
        "url": "https://hdfcbank.com/netbanking/login?token=bank_auth_999&returnUrl=https://payment.com/v1/payment/redirect",
        "description": "Redirecting customer to HDFC Bank for authentication"
    },
    "metadata": {
        "expiry": "2026-03-14T11:00:00Z",
        "orderId": "order123"
    }
}
```

### Payment Status

This endpoint allows the frontend to verify if a payment was successful after the user returns from the bank redirect.

![](Resources/API_Status.png)

#### HTTP Method & Endpoint

We use the **GET** method to retrieve the current state. The endpoint is `/v1/payments/{paymentId}`

#### HTTP Request Parameter

* **paymentId**: Passed in the URL path to identify the specific transaction.

#### HTTP Request Header

* **sessionToken**: Required to securely access the status of this specific session.

#### HTTP Response

```json
{
    "status": "SUCCESS",
    "paymentId": "payment123"
}

```

---

### Refund

Refunds are initiated by the **merchant backend** (for example from a customer support tool) after a payment has succeeded/authorized. Refund is a critical write operation, so it must be idempotent.

![](Resources/API_Refund.png)

#### HTTP Method & Endpoint

We use the **POST** method to create a refund resource for a payment. The endpoint is `/v1/payments/{paymentId}/refunds`.

#### HTTP Request Header

* **Authorization**: Merchant Secret Key (Bearer token). This authenticates the merchant and the payment gateway.
* **Idempotency-Key**: A unique string to prevent duplicate refunds if the merchant retries the request.

#### HTTP Request Body

```json
{
    "reason": "CUSTOMER_REQUEST"
}
```

#### HTTP Response

```json
{
    "refundId": "refund123",
    "paymentId": "payment123",
    "status": "REFUND_PENDING"
}
```

---

## High Level Design

The payment system can support multiple payment methods such as **cards, UPI, and netbanking**. Each method follows a slightly different workflow and may involve different systems. For example, Cards involve Card Network, UPI involves UPI system, and Netbanking involves direct integration with the bank.

To keep the explanation simple, this article uses **card payments as an example**. The overall system design remains similar for other payment methods, with only some differences in the payment flow.

### Payment Initiation

Payment initiation is the stage where a payment request is created by the merchant when the user starts the checkout process.

![](Resources/HLD_PaymentInitiation.png)

1. User clicks "Buy Now" from the merchant's website. The request goes to the **Merchant Backend**
2. **Merchant Backend** invokes the **Payment Gateway's** `/v1/payments` endpoint to initiate the payment. The **Merchant Backend** passes the Secret Key to authenticate itself with the **Payment Gateway**
3. The **Payments API Gateway** receives the request and routes it to the **Payments Gateway Backend**.
4. The **Payment Gateway** checks in the **Payment Database** if an existing payment session is available for the idempotency key sent by the merchant. If present, it fetches and returns the response immediately.
5. If not present, The **Payment Gateway** creates a payment entry on the **Payment Database** to track the life cycle of the payment for the checkout flow.
6. The **Payments Gateway Backend** creates a random session token and persists it in the **Session Cache**. The session token should be short lived and hence a TTL of 15 minutes is set on the cache entry. The session token will be linked to the paymentId in the session cache.
    * There is a high risk of data loss when Session Cache cluster crash. To avoid this we can have a fallback backup like **Append Only File - AOF** in Redis which adds every cache entry to an append only log file. If the cache cluster crash, it is reconstructed from the AOF.
7. The **Payment Gateway** generates the payment selection URL and returns it to the **Merchant Backend** via the **Payments API Gateway** (Step 7a and 7b).
8. The **Merchant Backend** redirects the user to the payment selection URL sent by the Payment Gateway.

### Payment Execution
When the user is redirected to the payment selection page, the **Payment Gateway** fetches the payment methods configured for the merchant and displays them to the user. It also allows the user to add a new payment method, such as a credit or debit card.

While rendering the page, the **Payment Gateway** also provides a public encryption key to the client. This key is used by the frontend to perform client-side encryption of sensitive card details before sending them to the backend. The corresponding private key is securely stored in the **Payment Processor's** system.

![](Resources/HLD_PaymentFlow.png)

#### Payment Registration

<a id="payment-registration"></a>

The payment registration flow handles the process of securely saving a user’s payment method, such as a credit or debit card. The saved method can be used later to make payments.

![](Resources/HLD_PaymentRegistration.png)

1. User enters the card details and click "Save". The frontend invokes the `/v1/payments/payment-methods` endpoint and passes the card details. The card details are encrypted with the public key.
2. The **Payments API Gateway** receives the request and route it to the **Payments Gateway Backend**.
3. The **Payment Gateway** fetches the session information from the **Session Cache** with the given Session Token in the request. If the token is valid, it authorizes the request
4. The **Payment Gateway** invokes the **Payment Processor** with the encrypted card details. 
5. The **Payment Processor** decrypts the client side encryption with the private key to get card details
6. The **Payment Processor** identifies the card type using Bank Identification Number (BIN), the first 6-8 digits of the card number that identifying the issuing network. Ex: Visa, Master. Once the issuing network is identified, it invokes the respective card network to validate card details
7. Once the card details are verified, the **Payment Processor** encrypts the card details using **Vault Encryption Key**.
8. The **Payment Processor** generates a random **token** string, associate it with the encrypted card details and store it in the **Token Vault**
9. The **Payment Processor** returns the response to the **Payment Gateway** with metadata such as **token**, **card tail**, **expiry**, etc.
10. The **Payment Gateway** stores the returned card data in the **Payment Method Database** along with a unique `paymentMethodId`.
11. The final response is returned to the client with the **Payments API Gateway** (Step 11a and 11b)

**Handling Sensitive Card Data**

In a real system, raw card details should never be sent directly to the payment gateway backend. Instead, the payment page typically loads a secure JavaScript SDK (aka script) provided by the payment processor. This SDK collects the card details and performs client-side encryption before the data leaves the browser.

![](Resources/HLD_HandlingCardData.png)

The encrypted card data (or a temporary token representing the card) is then sent to the payment processor’s secure infrastructure, which operates within a [PCI DSS–compliant environment](#pci-dss-compliance). The payment gateway only receives a token reference rather than the actual card number. This approach significantly reduces the system’s PCI compliance scope and minimizes the risk of exposing sensitive cardholder data.

#### Payment Authorization

Payment authorization is the step where the bank checks the payment request and verifies if the transaction can be approved. The bank may also ask for additional verification such as an OTP. Once the transaction is approved, the funds are reserved.

![](Resources/HLD_Payment.png)

1. User selects a payment method (for example, a saved card) and clicks **Pay**. The frontend calls `/v1/payments/{paymentId}/pay`.
2. The **Payments API Gateway** routes the request to the **Payments Gateway Backend**.
3. The **Payment Gateway** validates the Session Token using the **Session Cache**.
4. The **Payment Gateway** fetches payment details from the **Payment Database** and updates the status to `AUTH_PENDING`.
5. The **Payment Gateway** fetches the payment method `token` from the **Payment Method Database**.
6. The **Payment Gateway** fetches merchant acquiring configuration from the **Merchant Database**:
   * **Acquirer ID** – Identifies the acquiring bank routing the transaction to the card network.
   * **Merchant ID (MID)** – Unique identifier assigned to the merchant by the acquiring bank.
   * **MCC** – 4-digit code representing the merchant’s business category. For example, grocery store, restaurant, electronics store
7. The **Payment Gateway** calls the **Payment Processor** with the `token`, `amount`, merchant identifiers, and `returnUrl`. The `returnUrl` is required for the MFA (3-D Secure) flow so the issuing bank knows where to redirect the user after authentication.
    * **3D Secure** is an extra security step used in card payments to verify that the person making the payment is the real cardholder. The bank asks the user to complete an additional check, such as entering an OTP sent to their phone.
8. The **Payment Processor** retrieves the card from the **Token Vault**, decrypts it, and sends an authorization request to the **Card Network**.
9. The **Card Network** forwards the request to the **Issuing Bank**.
10. The **Issuing Bank** requires additional authentication and returns a **3-D Secure** URL.
11. The **Payment Processor** returns the authentication URL via the **Payment Gateway** and **Payments API Gateway**.
12. The user is redirected to the bank page and enters the OTP.
    * Although the user experiences a simple redirect and OTP verification, several systems — including the payment processor, card network directory server, and the bank’s Access Control Server — coordinate behind the scenes to complete this authentication step.
13. The **Issuing Bank** verifies the OTP and returns the authorization result (`AUTHORIZED` or `DECLINED`).

#### Payment State Machine

Payment transactions move through multiple well-defined states during their lifecycle. For example, a payment may start as `CREATED`, move to `AUTH_PENDING` when the user initiates the payment, and transition to `AUTHORIZED` or `FAILED` after the bank processes the request. Maintaining a clear payment state machine helps the system avoid invalid transitions and ensures that each transaction progresses through a predictable and auditable lifecycle.

![](Resources/HLD_PaymentStateMachine.png)

#### Payment Status Handling
The Payment Status flow tracks the lifecycle of a transaction and exposes the latest state to both the client and merchant systems.

![](Resources/HLD_Payment_Status.png)

1. The **Issuing Bank** after verifying OTP send the response back through the **Card Network** to the **Payment Processor** (Step 1a).  Meanwhile, after completing the authentication step, the user is redirected to the `returnUrl`. The `returnUrl` typically loads an intermediate page waiting for the payment result. (Step 1b and 1c)
2. The **Payment Processor** publishes a payment status event (for example `payment.authorized` or `payment.failed`) to **Payment Event Stream**. To keep it scalable, we can partition the stream at `merchantId` level.
    * For simplicity, this design initially uses `merchantId` as the partition key. This can cause **hot partitions** if a large merchant generates huge traffic. To fix it, the payment event stream can be partitioned using `paymentId` as the partition key. This ensures that all events related to a single payment are processed in order while distributing different payments evenly across multiple partitions for better throughput.
3. The **Payment Event Consumer** running inside the Payment Gateway subscribes to the queue and receives the event.
4. The **Payment Event Consumer** updates the corresponding payment record in the **Payment Database** using the information in the event.
5. The frontend periodically calls `/v1/payments/{paymentId}` to check the payment status.
6. The request is routed to the **Payment Gateway** via **Payments API Gateway**
7. The **Payment Gateway** simply reads the latest payment status from the **Payment Database**
8. The status is returned to the client via the **Payments API Gateway**. (Step 8a and 8b)
9. The payment gateway also sends an asynchronous webhook notification (e.g., payment.succeeded or payment.failed) to the merchant backend so the merchant system can update the order status.

#### Authorization vs Settlement

When a payment is authorized, the issuing bank only places a temporary hold on the customer’s account. The actual transfer of funds happens later during the settlement process, where the issuing bank sends the money through the card network to the acquiring bank.

Payment systems also perform **reconciliation**, where the gateway compares its transaction records with settlement reports received from acquiring banks to ensure that all approved payments are correctly settled and no discrepancies exist.

![](Resources/HLD_Settlement.png)

### Refund Processing

Refund processing reverses funds after a successful payment. It is usually triggered by the merchant backend (returns, cancellations, failed fulfillment), not by the customer browser.

![](Resources/HLD_Refund.png)

1. The **Merchant Backend** calls `POST /v1/payments/{paymentId}/refunds` with `Authorization` and an `Idempotency-Key`.
2. The **Payments API Gateway** routes the request to the **Payments Gateway Backend**.
3. The **Payment Gateway** validates the merchant, verifies the payment is in a refundable state, and creates a refund record in the **Payment Database** with state `REFUND_PENDING`.
4. The **Payment Gateway** returns the response with the reference `refundId` to the merchant via the **Payments API Gateway** (Step 4a and 4b).
5. The **Payment Gateway** calls the **Payment Processor** with the refund request (payment reference, amount, merchant identifiers).
6. The **Payment Processor** submits the refund to the network/bank and publishes a refund event (e.g., `payment.refunded` or `payment.refund_failed`) to the **Payment Event Stream** (Steps 6a, 6b, and 6c).
7. The **Payment Event Consumer** updates the refund record and the payment state in the **Payment Database** (`REFUNDED` / `REFUND_FAILED`) (Steps 7a and 7b).
8. The **Payment Gateway** sends a webhook notification to the merchant backend (e.g., `payment.refunded`) so the merchant system can update order state.

---

## Deep Dive Insights
### Database Selection

Below are general guidelines to build intuition for making database choices and are not absolute rules. The right choice always depends on the specific access patterns, scale, and consistency requirements.

| Guideline                                                                | Recommendation                             |
| ------------------------------------------------------------------------ | ------------------------------------------ |
| When strong consistency is required                                      | Use SQL (Relational)                       |
| When financial transactions must never be partially committed            | Use SQL (ACID guarantees)                  |
| When extremely high read/write throughput is needed with flexible schema | Use NoSQL                                  |
| When the data is mostly key-based lookups                                | Use NoSQL (Key–Value)                      |
| When the data is append-only event streams                               | Use NoSQL (Wide Column / Log-based stores) |
| When temporary session data needs fast access with TTL                   | Use In-Memory DB (Redis / Memcached)       |

Based on the above guidelines, we made the database choices for our payment service.

<table>
    <tr>
        <th>Database</th>
        <th>Deciding Factors</th>
        <th>Decision</th>
    </tr>
    <tr>
        <td>Payment Database</td>
        <td>
            <ul>
                <li><b>Financial Source of Truth</b> – Stores payment transactions.</li>
                <li><b>Strong Consistency</b> – A payment cannot be both success and failure.</li>
                <li><b>Durability</b> – Payment records must never be lost.</li>
            </ul>
        </td>
        <td>Relational (ACID)</td>
    </tr>
    <tr>
        <td>Payment Method Database</td>
        <td>
            <ul>
                <li><b>Stores tokenized card metadata</b> – Card tail, expiry, token reference.</li>
                <li><b>Moderate read/write frequency</b>.</li>
                <li><b>Data integrity important</b>.</li>
            </ul>
        </td>
        <td>Relational</td>
    </tr>
    <tr>
        <td>Merchant Database</td>
        <td>
            <ul>
                <li><b>Merchant configuration</b> such as MID, Acquirer ID.</li>
                <li><b>Strong consistency required</b>.</li>
            </ul>
        </td>
        <td>Relational</td>
    </tr>
    <tr>
        <td>Payment Event Stream</td>
        <td>
            <ul>
                <li><b>Append-only events</b> such as payment.authorized.</li>
                <li><b>High write throughput</b>.</li>
                <li><b>Event-driven architecture</b>.</li>
            </ul>
        </td>
        <td>Log-based system (Kafka / Pulsar)</td>
    </tr>
    <tr>
        <td>Audit / Logging Database</td>
        <td>
            <ul>
                <li><b>Large volume of logs</b>.</li>
                <li><b>Append-only events</b>.</li>
                <li><b>Used for auditing and compliance</b>.</li>
            </ul>
        </td>
        <td>NoSQL (Wide Column, e.g., Cassandra)</td>
    </tr>
</table>

> A log-based streaming system (like Kafka) is an append-only distributed log where producers publish events and consumers read them in order. It fits payments well because it can handle high write throughput, allows replay for system recovery, and decouples event producers (processor) from multiple consumers (gateway, analytics).

### Database Modelling
#### Payment Schema

![Payment Schema](Resources/DiveDeep_PaymentSchema.png)

* **Database Type:** Relational (ACID)
* **Common Queries:**
  * Fetch payment by `paymentId`
  * Fetch payments for a merchant using `merchantId`
  * Check payment status using `paymentId`
* **Indexing:** `paymentId`, `merchantId`

#### Payment Method Schema

![Payment Method Schema](Resources/DiveDeep_PaymentMethodSchema.png)

* **Database Type:** Relational
* **Common Queries:**
  * Fetch saved payment methods by `customerId`
  * Fetch payment method details using `paymentMethodId`
  * Retrieve token reference for processing payment
* **Indexing:** `paymentMethodId`, `customerId`

#### Merchant Schema

![Merchant Schema](Resources/DiveDeep_MerchantSchema.png)

* **Database Type:** Relational
* **Common Queries:**
  * Fetch merchant configuration using `merchantId`
  * Retrieve acquiring bank configuration for payment routing
* **Indexing:** `merchantId`

#### Audit Log Schema

![Audit Log Schema](Resources/DiveDeep_AuditSchema.png)

* **Database Type:** NoSQL (Wide Column / Time-series, e.g., Cassandra)
* **Common Queries:**
  * Retrieve audit logs for a `paymentId`
  * Fetch events within a time range for compliance checks
  * Investigate suspicious activity using `merchantId`
* **Indexing:** `paymentId`, `timestamp`, `merchantId`

Audit logs are stored in an **append-only format** to maintain a permanent record of all payment-related activities.

### Audit Payment Transactions
Assume that a customer claims they were charged ₹500 but never completed the payment. Without proper audit logs, the payment gateway cannot determine whether:
* The user actually initiated the payment
* The bank authorized the transaction
* The payment failed after authorization
* A retry caused a duplicate payment attempt

Auditability ensures that the system maintains a complete and verifiable history of all payment-related activities. This includes when the payment was created, when it was authorized, who initiated the action, and which systems were involved.

![](Resources/DiveDeep_Auditability.png)

### PCI DSS Compliance
Payment systems handle sensitive data such as card numbers, CVV, and expiry dates. If this data leaks, attackers can directly steal money or perform fraudulent transactions. To prevent this, the payment industry follows a global security standard called **Payment Card Industry Data Security Standard**, commonly known as PCI DSS.

PCI DSS focuses on protecting cardholder data such as Card Number, CVV, PIN, etc. PCI DSS enforces several requirements not limited to the below:

* Encryption - Client side encryption, TLS
* Strong Access Control - Only systems who need access to card data should have it.
* Firewalls - Install and maintain network security controls.

### Keeping Sensitive Data Secure
A **Hardware Security Module (HSM)** is a special device that is used to securely store encryption keys. These keys are used to encrypt/decrypt sensitive data such as card numbers. In a normal system, an application might retrieve the encryption key from the storage, use it to encrypt/decrypt data. This means that the key temporarily exists in the application server’s memory, which can be risky if the system is compromised.

With an HSM, the system **never retrieves the key**. Instead, the application sends the data that needs to be encrypted or decrypted to the HSM. The HSM performs the cryptographic operation internally using the key stored inside it and returns the result. The key always remains inside the HSM and is never exposed to the rest of the system.

![](Resources/DiveDeep_HSM.png)

You can think of it like a **secure vault where the key always stays inside**. Normally, we would take the key out of a locker to lock or unlock something. With an HSM, we don’t take the key out. Instead, we bring the item to the vault, the operation happens inside, and you receive the result while the key remains safely inside.

### Preventing Payment Data Loss
Imagine a situation where a customer buys a product for Rs.100 from a merchant website. The flow looks like `User → Merchant → Payment Gateway → Bank`. The bank approves the payment. But right after the approval, the payment gateway server crashes before saving the result. Now the system has a problem: **Bank says payment succeeded** and **Gateway database has no record**

This problem is addressed by making our system **durable**. Durability in a payment system is the promise that once a payment is recorded, it will never disappear, even if servers crash, networks fail, or a data center burns down. In simple terms: when someone pays ₹100, the system must never “forget” that the payment happened.

Durability in a system can be achieved through several mechanisms such as:
* Database Replication
* Write-Ahead Logging (WAL)

#### Database Replication
Replication keeps same data in multiple machines. When a payment record is written it is stored in the primary database and replicated to the replica databases. If the primary server crashes, one replica becomes the new primary. So, the payment record still exists.

![](Resources/DiveDeep_DatabaseReplication.png)

#### Write-Ahead Logging (WAL)
In WAL, before modifying the database, the system first appends the change to a log file. Only after this log entry is safely stored on disk does the database update the actual table. If the database crashes midway, it can replay the log to restore the correct state.

WAL is actually fast because it performs **sequential writes** and they are cheap. In HDD, random disk writes are slow because the disk head has to move. Sequential writes are fast because the disk just keeps writing forward.

![](Resources/DiveDeep_WAL.png)


In addition, this design can recover from the exact “gateway crashed before saving approval” scenario using the **Payment Event Stream** and **reconciliation**:

* The **Payment Processor** publishes an immutable event (e.g., `payment.authorized`) to the Payment Event Stream once it receives the bank/network decision.
* The **Payment Event Consumer** in the gateway is a durable subscriber: if it crashes, it resumes by replaying events from the stream and applies them idempotently to the Payment Database.
* A periodic **reconciliation job** compares gateway records vs processor/acquirer settlement/authorization reports to detect and fix any missing updates (e.g., gateway missed an event due to prolonged outage).