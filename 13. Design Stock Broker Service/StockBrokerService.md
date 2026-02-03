# Stock Broker Service

<!-- toc -->

- [Introduction](#introduction)
  * [What is a Stock Market](#what-is-a-stock-market)
  * [What a Stock Broker Actually Does](#what-a-stock-broker-actually-does)
- [Requirements](#requirements)
  * [Functional Requirements](#functional-requirements)
  * [Non-Functional Requirements](#non-functional-requirements)
- [Terminology](#terminology)
- [API Design](#api-design)
  * [Stock Watchlist](#stock-watchlist)
  * [Order Management](#order-management)
  * [Place Order](#place-order)
  * [Fetch Order Status](#fetch-order-status)
  * [View Portfolio](#view-portfolio)
  * [Price Tracker](#price-tracker)
- [High Level Design](#high-level-design)
  * [Note](#note)
  * [Watchlist](#watchlist)
  * [Order Management (Buy/Sell Shares)](#order-management-buysell-shares)
  * [Portfolio](#portfolio)
- [Deep Dive Insights](#deep-dive-insights)
  * [Database Selection](#database-selection)
  * [Database Modelling](#database-modelling)
  * [Connection Choices](#connection-choices)
  * [Fan-out Scaling](#fan-out-scaling)
  * [Security](#security)
  * [Order State Machine](#order-state-machine)
  * [Reliability & Failure Scenarios](#reliability--failure-scenarios)

<!-- tocstop -->

## Introduction

### What is a Stock Market

Think of the stock market as a regular marketplace. Assume there are multiple sellers selling apples and multiple buyers with money. Each seller might sell apples at different prices, and each buyer is willing to pay different prices for apples. A trade happens when a buyer finds a seller whose price matches what the buyer is willing to pay.

![Introduction](Resources/StockBroker-Introduction.png)

The stock market works the same way. Instead of apples, sellers offer shares of companies, and buyers are willing to pay money to buy those shares. There are many buyers and many sellers quoting different prices at the same time. A trade happens when a buyer's price matches a seller's price.

### What a Stock Broker Actually Does

In a real marketplace, buyers and sellers meet directly. A buyer can walk up to a seller, negotiate a price, and buy apples for money. But in the stock market, buyers and sellers are spread across cities and never meet each other.

This is where a stock broker comes in. Think of a stock broker as a middleman for both buyers and sellers. Buyers tell the broker what to buy and at what price. Similarly, sellers tell the broker what to sell and at what price. The broker takes these requests and places them into a common marketplace called the **stock exchange**. The stock exchange (for example, NSE or BSE) is like an organized bazaar that keeps all buy and sell offers in one place and decides when a buyer and seller match.

![StockBroker](Resources/StockBroker-Introduction_StockBroker.png)

In simple terms, the broker's role is to sit between buyers, sellers, and the stock exchange, and make sure the outcome of the trade is accurately reflected for both sides.

---

## Requirements

### Functional Requirements

#### Pre-Trade
* **Create/view watchlist** - User should be able to create and view the watchlist
* **Add/remove stocks on watchlist** - User should be able to add or remove stocks on their watchlist
* **Stream live price updates** - Users should receive real-time price ticks for watchlist and portfolio stocks

#### Trade
* **Place orders (Buy/Sell)** - Users should be able to place BUY/SELL orders with the broker
* **Track order status** - Users should be able to fetch order status until completion

#### Post-Trade
* **View Portfolio** - Users should be able to fetch their holdings and positions as a portfolio snapshot

### Non-Functional Requirements

* **Real-time updates** - Price ticks should be delivered with minimal delay to provide a responsive watchlist/portfolio experience
* **Security** - APIs must enforce authentication/authorization, encrypt traffic (TLS), and protect against abuse (rate limiting)
* **Availability** - Broker APIs and streaming endpoints should remain available during market hours and peak traffic periods
* **Consistency** - Order state must be strongly consistent from the broker's perspective

---

## Terminology

* **Holding**: Stocks you own and keep in your account.
* **Position**: Stocks you are currently trading (bought/sold today).
* **Portfolio**: A full view of all the stocks you own (holding) and trade (position), along with their profit or loss.
* **Symbol**: The short name used to identify a stock on the exchange, like `INFY`.
* **Side**: Whether you are buying or selling a stock.
* **Tick**: A small update showing the latest price change of a stock.

![Terminology](Resources/StockBroker-Terminology.png)

---
## API Design

We have listed the APIs for our design based on our functional requirements. In reality, additional systems and APIs may be required for a fully functional stock broker service.

### Stock Watchlist

A stock watchlist allows users to save stocks they are interested in. This helps them quickly track prices in one place. It is like a bookmark list for stocks. In the watchlist screen, the user can: 1) create a watchlist, 2) add stocks to the watchlist, 3) remove stocks from the watchlist, and 4) view live prices.

![Stock Watchlist UI](Resources/StockBroker-IntroWatchlist.png)

#### Create Watchlist

This API allows the user to create a watchlist with the given watchlist name and stock symbols. 
We use REST because watchlist creation is a simple request–response operation. 
It doesn’t need real-time updates or two-way (bidirectional) communication. Unlike price streaming and order updates, latency isn’t critical for this flow. A stateless HTTP API fits this use case well.

![Create Watchlist](Resources/StockBroker-API_WatchList_Create.png)

**HTTP Method & Endpoint**

This tells the server what action to perform. In our case, we want to create a watchlist, so we use the `POST` method. The `POST` method is generally used when the request creates something new in the system. We will use the endpoint `/v1/watchlists`. Here, `v1` means version 1 and is called API versioning. API versioning allows you to make changes to your APIs without breaking existing clients by using version numbers like `/v1/` or `/v2/` in the URL path.

**HTTP Body**

This section provides the necessary information to the server to create a watchlist. This information is sent as the request body.

```json
{
  "name": "MyWatchlist"
}
```

**HTTP Response**

The server creates the watchlist, adds the given stocks, and returns a unique id for the created watchlist.

```json
{
  "watchlistId": "MyWatchlist123",
  "name": "MyWatchlist"
}
```

#### Add Stocks to Watchlist

This API allows the user to add stocks to an existing watchlist.

![Add to Watchlist](Resources/StockBroker-API_WatchList_Add.png)

**HTTP Method & Endpoint**

This tells the server what action to perform. In our case, we want to add stocks to an existing watchlist, so we use the `POST` method. We will use the endpoint `/v1/watchlists/{watchlistId}/symbol:add`.

**HTTP Body**

This section provides the necessary information to the server to add stocks to an existing watchlist. This information is sent as the request body.

```json
{
  "symbols": ["INFY", "HCLTECH"]
}
```

**HTTP Response**

For this API, the response can be minimal and simply state whether the operation succeeded.

```json
{
  "watchlistId": "MyWatchlist123",
  "symbolsAdded": ["INFY", "HCLTECH"],
  "symbolsIgnored": [],
  "status": "success"
}
```

#### Remove Stocks from Watchlist

This API allows the user to remove stocks from an existing watchlist.

![Remove from Watchlist](Resources/StockBroker-API_WatchList_Remove.png)

**HTTP Method & Endpoint**

This tells the server what action to perform. In our case, we want to remove stocks from an existing watchlist, so we use the `POST` method. We will use the endpoint `/v1/watchlists/{watchlistId}/symbol:remove`.

> Why not use DELETE instead of POST?
>
> Some network systems remove data from DELETE requests because they expect DELETE to work like GET requests (which only need a URL). This means you can't send a list of items to delete in the request body - some systems will ignore or remove that data.

**HTTP Body**

This section provides the necessary information to the server to remove stocks from an existing watchlist. This information is sent as the request body.

```json
{
  "symbols": ["INFY", "HCLTECH"]
}
```

**HTTP Response**

For this API, the response can be minimal and simply state whether the operation succeeded.

```json
{
  "watchlistId": "MyWatchlist123",
  "symbolsRemoved": ["INFY", "HCLTECH"],
  "symbolsIgnored": [],
  "status": "success"
}
```

#### Fetch Stocks from Watchlist

This endpoint fetches the user's stocks from their watchlist.

![Fetch from Watchlist](Resources/StockBroker-API_WatchList_Fetch.png)

**HTTP Method & Endpoint**

This tells the server what action to perform. In our case, we want to fetch stocks from an existing watchlist, so we use the `GET` method. We will use the endpoint `/v1/watchlists/{watchlistId}`.

**HTTP Body**

`GET` requests do not need a body because they are used only to fetch information.

**HTTP Response**

The response contains the symbols of all stocks from the user's watchlist.

```json
{
  "watchlistId": "MyWatchlist123",
  "watchlistName": "MyWatchlist",
  "symbols": ["INFY", "HCLTECH"]
}
```

### Order Management

This API allows the user to place a BUY/SELL order with the broker service. The broker service talks to the exchange to place the order.

![Order UI](Resources/StockBroker-IntroOrderPlacement.png)

We need two APIs for order placement:

1. Place Order
2. Fetch Order Status

![Place Order & Fetch Order Status](Resources/StockBroker-API_PlaceOrder.png)

### Place Order

**HTTP Method & Endpoint**

This tells the server what action to perform. Since we want to place an order, we use the `POST` method. The endpoint for this API would be `/v1/orders`.

**HTTP Body**

```json
{
  "clientId": "c_12345",
  "symbol": "INFY",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 10
}
```

**HTTP Response**

```json
{
  "orderId": "ord_789",
  "status": "PENDING_EXCHANGE"
}
```

### Fetch Order Status

**HTTP Method & Endpoint**

This tells the server what action to perform. Since we want to fetch the order status, we use the `GET` method. We use `GET` because this action doesn't alter any state in the system and is read-only. The endpoint for this API would be `/v1/orders/{orderId}`.

**HTTP Body**

`GET` requests do not need a body because they are used only to fetch information.

**HTTP Response**

```json
{
  "orderId": "ord_789",
  "clientId": "c_12345",
  "symbol": "INFY",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 10,
  "status": "SUCCESS",
  "avgPrice": 1542.30
}
```

### View Portfolio

![Portfolio UI](Resources/StockBroker-IntroPortfolio.png)

This API provides portfolio details (holdings and positions) with data such as price, quantity, etc.

![View Portfolio](Resources/StockBroker-API_Portfolio_Fetch.png)

#### HTTP Method & Endpoint

We use the `GET` method since we only want to retrieve details from the system. The endpoint would be `/v1/portfolio`.

#### HTTP Body

`GET` requests do not need a body because they are used only to fetch information.

#### HTTP Response

```json
{
  "holdings": [
    {
      "symbol": "INFY",
      "quantity": 20,
      "avgBuyPrice": 1480.25,
      "investedValue": 29605.00
    }
  ],
  "positions": [
    {
      "symbol": "HCLTECH",
      "netQuantity": -5,
      "avgPrice": 1320.10,
      "product": "INTRADAY"
    }
  ]
}
```

### Price Tracker

In both **watchlist** and **portfolio**, along with the stocks, we display the current stock price being traded in the market. We need a mechanism that delivers live price updates to the client. We want the best user experience, where the user doesn't have to refresh the page to view the latest trading price of their watchlist/portfolio stocks.

To stream live price updates to the client, we use a special protocol called **Server-Sent Events (SSE)**. SSE is a one-way streaming connection where:

1. The client opens an HTTP connection with the server.
2. The server keeps the connection open for the client-specified duration.
3. The server continuously pushes events through the same connection.

![PriceTrackerSSE](Resources/StockBroker-API_PriceTracker_SSE.png)

We used SSE because it is well-suited for **live feed** style updates and is built on HTTP, which works on most modern browsers. We use `text/event-stream` as the content type for SSE requests. There are other ways to achieve the same result using **WebSockets** and long polling. Refer to the deep dive section [Connection Choices](#connection-choices) for more details.

![Price Tracker](Resources/StockBroker-API_PriceTracker.png)

**HTTP Method & Endpoint**

This tells the server to start a live stream of price updates for the client. We use the `GET` method and the endpoint `/v1/marketdata/stream`. We use SSE to invoke this endpoint.

**HTTP Body**

`GET` requests do not need a body because they are used only to fetch information.

**HTTP Response**

```json
event: price_tick
data: {"symbol":"INFY","ltp":1542.35,"change":12.10,"changePct":0.79,"ts":"2026-01-17T10:45:01Z"}

event: price_tick
data: {"symbol":"HCLTECH","ltp":1320.10,"change":-5.20,"changePct":-0.39,"ts":"2026-01-17T10:45:02Z"}
```

**Did you notice the FIX Protocol?**

You must have noticed that the Broker Service and the Stock Exchange don't communicate through HTTP or SSE. Instead, they use a special protocol called FIX (Financial Information eXchange). FIX is a standard messaging protocol used in trading systems to exchange information such as placing orders, cancelling/modifying orders, and subscribing to market data. The syntax for FIX messages is `tag=value|tag=value|tag=value|...`.

**Why use FIX protocol? Why not HTTP?**

Before FIX, the trading systems misunderstood each other because everyone communicated in different formats. FIX created one clear, standard way to communicate so machines don't guess or misinterpret. It exists to make trading fast, correct, and predictable.

**Features of FIX Protocol**
* Standard message format – Every message is sent in a well-defined structure, so systems don't misinterpret.
* Session reliability – It uses sequence numbers and resends to ensure no messages are lost or duplicated.
* Low latency & high throughput – Lightweight text-based messages designed for fast machine-to-machine trading.

---
## High Level Design

Before diving deep into the high-level design of each component, we will first understand the different services involved in a stock broker system.

* **Stock Broker Service** - The main backend API that the app talks to for placing orders, viewing the portfolio, and managing watchlists.
* **Order Management Service (OMS)** - Creates and tracks orders from start to finish.
* **Price Tracker Service (PTS)** - Continuously receives live stock prices and provides the latest price updates to the app.
* **Order Executor Service (OES)** - Takes submitted orders and sends them to the stock exchange.
* **Funds Service** - Manages user balance and margin by blocking funds for orders.

### Note

Throughout this high-level design, we will discuss several backend services such as the Broker Service, Funds Service, and Stock Exchange. In a real system, each service typically sits behind an **API Gateway and a Load Balancer**, which receive incoming requests and route them to the appropriate backend servers. To keep the diagrams simple, I haven't shown these components explicitly, but you can assume they exist in front of every backend service.

![API Gateway Note](Resources/StockBroker-Note_API_Gateway.png)

### Watchlist

The watchlist flow allows users to save a set of stocks and fetch them. For live tracking, the broker streams real-time price ticks for those symbols to the user via SSE.

![Watchlist Design](Resources/StockBroker-HLD_Watchlist.png)

1. The Price Tracker Service subscribes to the Stock Exchange market feed using the FIX protocol. This creates a long-lived connection so the service can continuously receive real-time market prices.
2. The Stock Exchange continuously sends price updates (*ticks*) to the Price Tracker Service. A *tick* is a single market update for a symbol, such as "INFY price changed to 1542.35 at this timestamp".
3. Instead of sending price updates directly to the broker service, the Price Tracker Service writes them to an **event stream**. Interested services (consumers) can read the price ticks from the `Price Events Stream`.
  * The event stream keeps the updates in order so multiple consumers can read them independently. This makes the system scalable and ensures no price updates are missed if a consumer is slow or temporarily unavailable.
  * The stream is also logically partitioned by symbol (e.g., INFY). So, a surge in incoming events of one symbol doesn't affect the other and allows the system to scale horizontally. For example, if INFY has a surge in price ticks, we only scale its stream.
4. The user device calls `GET /v1/watchlists/{watchlistId}` on the Stock Broker Service to fetch watchlist stocks.
5. The Stock Broker Service fetches the watchlist symbols from the Watchlist cache (for faster retrieval). The cache is updated wherever the data is updated in the database. The cache stores only the user's watchlist configuration (symbols, order, name), not live prices.
6. The Stock Broker Service returns the watchlist symbols back to the user device.
7. The user device opens an SSE connection using `GET /v1/marketdata/stream` for live prices. SSE keeps the HTTP connection open so the server can push price ticks continuously without polling.
8. The Stock Broker Service consumes live ticks from the `Price Events Stream` and filters them by watchlist symbols. Only ticks for symbols present in the watchlist are selected.
9. The Stock Broker Service streams matching ticks back to the user device via SSE (fan-out). Fan-out means one tick like `INFY → 1542.35` can be sent to many connected users who are subscribed to INFY at the same time.

**Note**

We didn't go deep into watchlist features like **create**, **add stock**, or **remove stock** because they are mostly simple CRUD operations with predictable behavior. The real complexity in watchlist comes from streaming live price updates, so we focused on the price feed flow.

### Order Management (Buy/Sell Shares)

The following steps are executed when a user buys or sells shares using the broker app/website.

![Order Management Design](Resources/StockBroker-HLD_OrderManagement.png)

1. The user places an order (`POST /v1/orders`) from the broker app to buy or sell shares.
2. The request reaches the **Stock Broker Service**, which performs basic validations (for example, session/auth checks) and then forwards the request to the **Order Management Service (OMS)**.
3. Before processing the order, **OMS** calls the **Funds Service** to verify that the user has sufficient balance and to block (reserve) the required amount.
4. The **Funds Service** receives the request, checks the user's funds from the **Funds Database**, and blocks the funds so that the user cannot withdraw during an active order.
5. The **Funds Service** returns the response to **OMS**.
6. **OMS** validates that the user has sufficient funds. If the balance is sufficient, it creates a new order record in the **Order Database** (Step 6a) with a unique `orderId` to track the order. The `orderId` should be idempotent, so that retries with the same id shouldn't create duplicate orders. The order is also added to the **Order Cache** (Step 6b). We use a cache to store the latest order status so frequent user polling can be served quickly without repeatedly hitting the database.
7. **OMS** publishes the order to the **Order Execution Queue** for asynchronous execution.
8. After publishing to the queue, **OMS** returns an acknowledgement to the user device with the generated `orderId` so the user can track the order status. This is shown in steps 8a and 8b.
9. The **Order Executor Service (OES)** consumes the order from the queue.
10. **OES** sends the order to the **Stock Exchange** for execution.
11. **OES** and the **Stock Exchange** communicate over the **FIX protocol** and receive ongoing updates about the order state.
12. Whenever **OES** receives order updates/events from the Stock Exchange, it publishes them to the **Order Events Stream**.
13. **OMS** consumes these events from the **Order Events Stream**.
14. **OMS** updates the order status in the **Order Database** (Step 14a) based on the received events. The order status is also updated in the **Order Cache** (Step 14b).
15. After placing the order, the user device periodically queries the system to fetch the latest order status.

  1. The user device polls the **Stock Broker Service** (`GET /v1/orders/{orderId}`) at regular intervals. The broker service routes the request to **OMS**.
  2. **OMS** fetches the latest order status from the **Order Cache**.
  3. **OMS** returns the response to the broker service, which then sends it back to the user device.

### Portfolio

The portfolio flow allows users to view their holdings and positions. Similar to watchlist, we use the Price Tracker Service to stream live prices for portfolio stocks.

![Portfolio Design](Resources/StockBroker-HLD_Portfolio.png)

1. The Price Tracker Service subscribes to the Stock Exchange market feed using the FIX protocol.
2. The Stock Exchange continuously sends price updates (*ticks*) to the Price Tracker Service.
3. The Price Tracker Service publishes each tick to the `Price Events Stream`.
4. The user device calls `GET /v1/portfolio` on the Stock Broker Service to fetch portfolio stocks.
5. The Stock Broker Service fetches the holding and position symbols from the Portfolio cache (for faster retrieval). The cache is updated wherever the data is updated in the database.
6. The Stock Broker Service returns the portfolio symbols back to the user device.
7. The user device opens an SSE connection using `GET /v1/marketdata/stream` for live prices.
8. The Stock Broker Service consumes live ticks from the `Price Events Stream` and filters them by portfolio symbols.
9. The Stock Broker Service streams matching ticks back to the user device via SSE (fan-out).

---
## Deep Dive Insights

### Database Selection

We cannot make a "single database" choice for the entire stock broker system. Each functionality of the system will have a specific database choice based on the requirement.

| Guideline                                                     | Recommendation       |
|---------------------------------------------------------------|----------------------|
| When eventual consistency is not accepted                     | Use SQL (Relational) |
| When eventual consistency is accepted                         | Use NoSQL            |
| When you need faster access                                   | Prefer NoSQL         |
| When data correctness is critical (no partial failures)       | Use SQL              |
| When row level locking is required to block concurrent writes | Use SQL              |
| When it is read-heavy                                         | Prefer NoSQL         |
| When you have simpler queries                                 | 	NoSQL works well    |

Based on the above guidelines, we made the database choices for our stock broker service.
<table>
    <tr>
        <th>Database</th>
        <th>Deciding Factors</th>
        <th>Decision</th>
    </tr>
    <tr>
        <td>Fund DB</td>
        <td>
            <ul>
                <li><b>Critical Money State</b> - Stores user's available balance that directly controls order placement.</li>
                <li><b>Immediate Blocking</b> - Funds should be blocked the moment a BUY order is placed.</li>
                <li><b>Concurrent Orders</b> - Two simultaneous orders must not overspend the same balance.</li>
                <li><b>Row-Level Locking</b> - Requires SELECT FOR UPDATE style locking to prevent race conditions.</li>
                <li><b>Atomic Updates</b> - Balance deduction must be all-or-nothing.</li>
            </ul>
        </td>
        <td>Relational (ACID)</td>
    </tr>
    <tr>
        <td>Watchlist DB</td>
        <td>
            <ul>
                <li><b>Non-Critical Data</b> - Stores user preferences; temporary inconsistency causes no loss.</li>
                <li><b>Read Heavy</b> - Users view watchlist far more than they modify it.</li>
                <li><b>High Scalability</b> - Needs to serve millions of fast reads.</li>
                <li><b>Eventual Consistency Acceptable</b> - Minor delays are tolerable.</li>
            </ul>
        </td>
        <td>NoSQL (Key–Value / Document)</td>
    </tr>
    <tr>
        <td>Portfolio DB</td>
        <td>
            <ul>
                <li><b>Legal Source of Truth</b> - Represents actual share ownership of the user.</li>
                <li><b>Atomic State Change</b> - Quantity, avg price, and P&amp;L must update together or not at all.</li>
                <li><b>SELL Validation</b> - Used to validate whether a SELL order is allowed.</li>
                <li><b>Consistency Critical</b> - Stale data can allow overselling or wrong rejection.</li>
            </ul>
        </td>
        <td>Relational (ACID)</td>
    </tr>
    <tr>
        <td>Order DB</td>
        <td>
            <ul>
                <li><b>State Machine Behavior</b> - Orders transition through multiple states rapidly.</li>
                <li><b>Frequent Updates</b> - Same row updated many times during market hours.</li>
                <li><b>Strong Ordering Needed</b> - State transitions must occur in exact sequence.</li>
                <li><b>UI &amp; Trade Safety</b> - Inconsistency leads to ghost orders or duplicate fills.</li>
            </ul>
        </td>
        <td>Relational (ACID)</td>
    </tr>
</table>

### Database Modelling
#### Funds Schema
* Database Type: Relational Database
* Common Queries: Read and block funds for `BUY` order
* Indexing: `userId`

![FundsSchema](Resources/StockBroker-DIVEDEEP_DB_FUNDS.png)

#### Watchlist Schema
* Database Type: NoSQL
* Common Queries: Read the symbols in the user's watchlist
* Indexing: `watchlistId`

![WatchlistSchema](Resources/StockBroker-DIVEDEEP_DB_WATCHLIST.png)

#### Portfolio Schema
* Database Type: Relational Database
* Common Queries: Read the user's holdings and positions
* Indexing: `userId` + `symbol`
* We query the database with the userId to fetch all the holdings and positions of the user

![PortfolioSchema](Resources/StockBroker-DIVEDEEP_DB_PORTFOLIO.png)

#### Order Schema
* Database Type: Relational Database
* Common Queries: Read the order details of the users
* Indexing: `orderId` (to fetch specific order) and `userId` (to fetch all orders of the user)

![OrdersSchema](Resources/StockBroker-DIVEDEEP_DB_ORDERS.png)

### Connection Choices

Every broker app faces the same problem: **prices change constantly**, but HTTP was originally designed for "request → response → done". Markets don't behave like that. So we need a way to push updates to the client without making the user hit refresh every second. There are three common approaches. They all work, but in different ways.

![Dive Deep for Connection Choices](Resources/StockBroker-DIVEDEEP_Connection.png)

#### Long Polling

In long polling, the client keeps calling the server for updates, but the server doesn't respond immediately. The server waits until there's some data or until a timeout, and then returns the response. The client instantly makes the next request.

**Where it works**

* The implementation is simple.
* Update frequency is low.

**Where it hurts**

* Lots of repeated HTTP requests are made.
* Scaling becomes expensive with many concurrent users.
* Not great for high-frequency changes.

#### WebSocket

WebSockets start as HTTP and then upgrade into a persistent two-way connection. After that, both the client and server can send messages at any time. With WebSockets, the client connects once via a handshake and the server pushes updates continuously.

**Where it works**

* Bidirectional communication between the client and server is required.
* Handles high-frequency data well.

#### Server-Sent Events (SSE)

SSE is basically long polling done in a cleaner way. The client makes a single HTTP request, and the server keeps that connection open and pushes events whenever updates arrive. With SSE, the client opens an HTTP `GET` connection with the server, the server replies once and keeps streaming events, and the client keeps receiving updates without making repeated requests.

**Where it works**

* Only the server needs to communicate continuously.
* It is built on HTTP, so it works well with standard infrastructure.

**Where it hurts**

* Slow consumption can lead to backpressure.
* Requires heartbeats to keep connections healthy.

| Feature            | Long Polling            | SSE                        | WebSockets                       |
|--------------------|-------------------------|----------------------------|----------------------------------|
| Connection style   | Repeated HTTP requests  | One long-lived HTTP stream | One upgraded persistent socket   |
| Direction          | Mostly request/response | Server → Client only       | Two-way                          |
| Real-time feel     | Medium                  | High                       | Highest                          |
| Overhead           | High                    | Low                        | Low                              |
| Reconnect handling | Manual                  | Built-in                   | Manual                           |
| Best for           | Simple updates          | Live feeds                 | Live feeds + interactive control |

#### Verdict

For a stockbroker app, we need real-time price updates without complicating the system. **Long polling** works but wastes resources because it repeatedly opens HTTP requests. **WebSockets** are the most powerful option, but they add complexity and are worth choosing only when we need two-way communication. **SSE** is the best default for watchlists and portfolios since it provides a clean, lightweight server-to-client live feed over HTTP.

### Fan-out Scaling

It's 9:15 AM and the market opens. Everyone logs in to the app and starts monitoring their interested stocks (say, INFY). The Price Tracker Service receives price ticks from the exchange, and the stock broker service pushes them to users using Server-Sent Events (SSE).

But the same tick isn't meant for just one user. It needs to go to everyone who is interested in INFY. So the broker service asks, "Who is watching INFY right now?" and the answer is, "a lot". This is called **fan-out**. Fan-out means one incoming update turns into many outgoing updates.

![Dive Deep for Fanout Scaling](Resources/StockBroker-DIVEDEEP_Fanout.png)

#### Problem 1 - Finding the right users

If the broker service tries to scan all users every time a tick arrives, it will overload the CPU. So the broker keeps a map such as `INFY -> [client1, client2, client3, ...]`. We can store this data in a key-value store like DynamoDB fronted by Redis cache for faster retrieval. Now, when INFY ticks, the broker knows who to notify. To handle this safely, the broker service doesn't push every tick to users immediately. Instead, it uses a **Push Scheduler** that sends only the latest price updates at a steady pace. This prevents the system from getting overloaded when thousands of users are watching the same fast-moving stock.

#### Problem 2 - Insane tick rates

Assume INFY is actively trading in the market and there are many ticks per second. If we push every single tick to the user, we will waste resources. So the broker service, instead of sending every tick, keeps only the newest tick and reduces client updates to one or two per second.

#### Problem 3 - Slow clients

Not all clients are fast. Some users have weak networks, background apps, and slow devices. The broker service pushes data, but for some clients the writes are very slow, and this leads to backpressure. Backpressure means the backend service receives updates faster than it can deliver them to clients. This results in growing server buffers, memory spikes, and latency spikes.

Backpressure is handled by not buffering every tick. Instead, keep only the **latest price per symbol** and push updates at a fixed rate. If a client still can't keep up, drop intermediate updates or disconnect the slow stream to protect the system.

### Security

A stock broker system deals with money, trades, and sensitive user data, so security is very important. The goal is to ensure that only authorized actions are allowed, and the system stays protected even when someone tries to abuse it.

![Dive Deep for Security](Resources/StockBroker-DIVEDEEP_Security.png)

#### Authentication and Authorization

Every API request must be authenticated with user credentials. Once authenticated, the system must also verify authorization to ensure the user can only access their own watchlists, portfolio, and orders. For example, even if a user knows another watchlist id like `wl_123`, the broker service must still validate that `wl_123` belongs to the current user before returning any data.

#### Transport Security

All communication between the user device and broker services should happen over HTTPS using TLS (Transport Layer Security). This prevents attackers from reading or modifying requests in transit, especially on public Wi-Fi networks.

#### Rate Limiting and Abuse Protection

Broker systems are easy targets for abuse because market data endpoints can be opened for long durations and order APIs can be spammed. To prevent this, we enforce rate limits such as:

* maximum order placement requests per minute per user
* maximum number of active SSE connections per user
* maximum number of symbols per stream subscription

#### Securing SSE Streams

Streaming endpoints also need protection similar to REST APIs. The SSE connection should validate authentication during connection setup, and the server must ensure that the user only receives ticks for symbols they subscribed to. If the client disconnects and reconnects frequently, the broker service should also apply reconnect limits to prevent stream abuse.

#### Audit Logging

All critical actions, like placing orders, cancelling orders, and modifying orders, should have audit logs stored with details such as user id, request id, timestamp, and action type. This helps during debugging, fraud investigations, and compliance requirements.

![Audit Logging](Resources/StockBroker-DIVEDEEP_AuditLogs.png)

### Order State Machine

An order looks like a single step, but it isn't. After a user buys or sells shares, the order goes through multiple stages before it is completed. A **state machine** is a controlled way to represent those stages so we always know exactly what's happening.

If we treat status like a random string that gets overwritten (`"open"`, `"done"`, `"cancelled"`), the system becomes inconsistent at scale. For example, the UI may show "Cancelled" while the exchange already filled it. A state machine avoids these contradictions by allowing only valid transitions. Below are the valid states in order management:

* **PENDING_EXCHANGE** - Broker accepted the order and queued it for exchange submission.
* **OPEN** - Exchange acknowledged the order and it's live in the market.
* **PARTIALLY_FILLED** - Some quantity is executed, but not all.
* **FILLED** - Entire quantity executed. This is a terminal state.
* **CANCELLED** - Order was cancelled before it fully executed. This is a terminal state.
* **REJECTED** - Order failed either due to broker checks or exchange rejection. This is a terminal state.

![Order State Machine](Resources/StockBroker-DIVEDEEP_OrderStateMachine.png)

A simple order lifecycle is: **User places order → OMS stores it → Executor sends to the exchange → Exchange updates → OMS updates status**. The typical transitions are:

* `PENDING_EXCHANGE → OPEN`
* `OPEN → PARTIALLY_FILLED → FILLED`

### Reliability & Failure Scenarios

Distributed systems rarely fail in a predictable way. They often fail in the middle of a process leaving the system in a partially updated state. For example, an order got executed at the exchange, but OMS crashes before saving the update, leaving the system showing the wrong order status.

So the real question is not *"Will something fail?"*. It is *"When it fails, does the system still behave correctly?"*

Below are some of the important failure scenarios in a broker system and how the design protects itself.

<table>
  <tr>
    <th>Scenario</th>
    <th>What Happens</th>
    <th>Risk</th>
    <th>Recovery Mechanism</th>
  </tr>
  <tr>
    <td>Order executed but OMS didn't update</td>
    <td>Stock Exchange executes the order, but OMS is down and does not record the update.</td>
    <td>Order status, portfolio, and funds become inconsistent.</td>
    <td>Execution events are stored in the event stream. When OMS recovers, it replays missed events and corrects the order state.</td>
  </tr>
  <tr>
    <td>Client retries <b>"Place Order"</b> due to timeout</td>
    <td>User retries the same request because the response was not received.</td>
    <td>Duplicate orders, double fund blocking, and double execution.</td>
    <td>`orderId` acts as an idempotency key and OMS returns the existing order instead of creating a new one.</td>
  </tr>
  <tr>
    <td>Funds blocked but order never reached the exchange</td>
    <td>OMS blocks funds but crashes before publishing the order to the queue.</td>
    <td>User funds remain stuck without an active order.</td>
    <td>Scheduled cleanup job detects long-pending orders and releases funds while marking the order as REJECTED.</td>
  </tr>
  <tr>
    <td>OES crashes after sending order</td>
    <td>OES sends the order to the exchange but crashes before publishing the event.</td>
    <td>OMS never receives the exchange update.</td>
    <td>FIX protocol's session recovery uses sequence numbers to fetch missed messages when OES reconnects and republishes events.</td>
  </tr>
  <tr>
    <td>Cache failure during market hours</td>
    <td>Redis/cache crashes and loses all cached data.</td>
    <td>Increased load on databases and slower responses.</td>
    <td>System continues to work correctly because the database is the source of truth. Cache is rebuilt gradually.</td>
  </tr>
  <tr>
    <td>User sees stale order status</td>
    <td>User polling reads slightly outdated data from cache.</td>
    <td>UI shows delayed order status.</td>
    <td>Write-through cache (cache is updated first and then the database) keeps data fresh, and eventual consistency is acceptable for UI reads.</td>
  </tr>
</table>
