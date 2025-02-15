# BUZZWORDS :NETWORKING

In this section, we'll cover the foundational networking concepts essential for system design. We'll explore:

- [1.IP Addresses](#ip-address)

- [2.DNS:Domain Name Server](#dns-domain-name-server)

- [3.Client and Server](#client-and-server)

- [4.Protocols:TCP,UDP,HTTP,Websockets](#protocols-tcp-udp-http-websocket)

- [5.Forward and Reverse Proxy](#forward-proxy-and-reverse-proxy)
## Forward and Reverse Proxies

Press **continue** to dive into these key networking concepts!

<hr style="border:2px solid gray">

## IP Address

Just as every person in this world is known by their name, each computer on the internet is known by its **IP address**.

An IP address looks something like this:  

- **IPv4 Example:** `172.217.22.14`  
- **IPv6 Example:** `2001:db8:3333:4444:5555:6666:7777:8888`  

Well, that’s a very horrible name!


![Ip address](https://static.wixstatic.com/media/99fa54_4f27b97a08794537954daa1ad66116a2~mv2.png/v1/fill/w_673,h_410,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/99fa54_4f27b97a08794537954daa1ad66116a2~mv2.png)

<hr style="border:2px solid gray">

## DNS :Domain Name Server

When you type **sweetcodey.com** in your browser, your browser requests sweetcodey’s home page from servers.

### How Does the Browser Find the Server?

But how does your browser know where sweetcodey’s servers are?

That’s the purpose of **DNS**.

### What is DNS?

**DNS (Domain Name System)** is a service that takes the website name (like **sweetcodey.com**) and provides the **IP address** of the server.

### How Does It Work?

1. The user types **sweetcodey.com** in the browser.
2. The browser requests the **IP address** of **sweetcodey.com** from a DNS server.
3. The DNS server responds with the correct **IP address**.
4. Now, the browser knows **sweetcodey’s IP address** and fetches the homepage from it.

![DNS](https://static.wixstatic.com/media/99fa54_c4ee0eabdc86439680025786ce4f32c5~mv2.png/v1/fill/w_1120,h_519,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_c4ee0eabdc86439680025786ce4f32c5~mv2.png)

<hr style="border:2px solid gray">

## Client and Server

### Client  
A computer that requests information.

### Server  
A computer that serves the requested information from the client.

### Examples  

- **Your Smart TV requests movies (aka streaming) from Netflix**  
  - Your Smart TV is the **client** requesting information from the **Netflix Server**.

- **Your phone gets directions from Google Maps**  
  - Your phone is the **client** requesting information from the **Google Maps Server**.

![Client & Server](https://static.wixstatic.com/media/99fa54_217a22ee8c4248f98f40daee7fd715ee~mv2.png/v1/fill/w_1120,h_413,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_217a22ee8c4248f98f40daee7fd715ee~mv2.png)

<hr style="border:2px solid gray">

## Protocols :TCP UDP HTTP Websocket

Just as people use grammatical rules to communicate, computers also follow certain rules while communicating.

The rules that computers follow are **Protocols**.

Based on what the task is, we use different rules/protocols for it.

**Example:**  
If the task is to perform common web interactions like sending and receiving web pages or updating content, we use the **HTTP** protocol.  
Similarly, if the task is to transfer files, we use the **FTP** protocol.

![Protocols](https://static.wixstatic.com/media/99fa54_32dce5940d944f59a6b8b27fdfd2c563~mv2.png/v1/fill/w_1120,h_435,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_32dce5940d944f59a6b8b27fdfd2c563~mv2.png)

### TCP (Transmission Control Protocol)

Let's say you are streaming a movie, and after the first scene, you see the climax directly. That's confusing, right?

Well, **TCP prevents this from happening**.

TCP ensures your **data packets are delivered in the correct sequence**, so you watch the movie in the proper order.

Whenever proper ordering is necessary, like in **email** or **streaming video**, **TCP is used**.

![TCP](https://static.wixstatic.com/media/99fa54_0728a2c18df948218ac7a0a8434222e7~mv2.png/v1/fill/w_1120,h_370,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_0728a2c18df948218ac7a0a8434222e7~mv2.png)

### UDP (User Datagram Protocol)

Imagine you're watching a **live football game**. You want it to feel live with barely any delay.

**UDP helps with this!**  

It sends video **fast**, though sometimes a few pieces might get lost.

- **UDP is very fast** but **doesn't guarantee** the delivery of all data packets.
- It is **perfect for tasks where speed is more important than reliability**.

**Key Difference:**  
- Unlike **UDP**, which prioritizes **speed** and might **skip some data**,  
- **TCP** focuses on **reliability**, ensuring **everything is complete and in order**—so you don’t miss any part of your movie.

![UDP](https://static.wixstatic.com/media/99fa54_24b0b9bc32c64e02908fd9ef03a1a175~mv2.png/v1/fill/w_1120,h_485,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_24b0b9bc32c64e02908fd9ef03a1a175~mv2.png)

### HTTP (Hypertext Transfer Protocol)

**HTTP is the most commonly used protocol on the internet.**

It operates on a simple principle:  
> **You request something from the server, and the server responds.**  

### Example:
Consider **shopping online**.  
Each time you click on a product, your browser (**client**) sends a **request** to the store's **server** for product details.  
The server then fetches this information from its **database** and sends it back to your **browser** as a **webpage**.

![HTTP](https://static.wixstatic.com/media/99fa54_411008b1032743cd9dcfcd0095fa0ef5~mv2.png/v1/fill/w_1120,h_284,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/99fa54_411008b1032743cd9dcfcd0095fa0ef5~mv2.png)

### Websockets

In standard protocols like **HTTP**, the interaction is **one-directional**.  
- The **client** sends a request, and then the **server** responds.  
- Without a **request** from the client, the **server cannot** initiate sending data.

### Websockets change this!

With **Websockets**, both the **client and the server can send data to each other at any time**. This makes the communication **bi-directional**.

### Example:
Consider a **live chat application**.  
Your device **can’t constantly send requests to the server every second**, asking:  
*"Do you have a new message?"*—That would be **inefficient**.

With **Websockets**, whenever a **message arrives** for a client, the **server immediately sends it** to that client.  
This makes it **very efficient**.

![WEBSOCKETS](https://static.wixstatic.com/media/99fa54_9ae0040aa32c46d2afc225bb1f63c7c5~mv2.png/v1/fill/w_1064,h_425,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_9ae0040aa32c46d2afc225bb1f63c7c5~mv2.png)

This is how different protocols serve different purposes based on the task at hand.

<hr style="border:2px solid gray">

## Forward Proxy and Reverse Proxy

### Forward Proxy
A **Forward Proxy** is like a personal assistant for your outdoor requests.

- Whenever you need something from outside, you just tell your assistant what you need, and they go get it for you.
- Similarly, a forward proxy sits between you (the client) and the internet.
- You send your requests to the proxy, and it fetches the information from the internet on your behalf.

![Forward proxy](https://static.wixstatic.com/media/99fa54_15ae9486f1c540edaf9015ace72f2860~mv2.png/v1/fill/w_1014,h_775,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_15ae9486f1c540edaf9015ace72f2860~mv2.png)

### Reverse Proxy
A **Reverse Proxy** is like a personal assistant for your family.

- Instead of people contacting your family directly, they go through your assistant.
- The assistant filters the messages/calls and forwards only the important ones to your family members.
- Similarly, a reverse proxy sits between the internet and your services (a collection of servers specializing in a task).
- It receives requests from clients and forwards those requests to the appropriate service.

![Reverse proxy](https://static.wixstatic.com/media/99fa54_27096e87b7c04447bbe86b5c69b798d1~mv2.png/v1/fill/w_995,h_863,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_27096e87b7c04447bbe86b5c69b798d1~mv2.png)

### Example:
- If a user sends a **login request**, the reverse proxy routes it to the **Authentication Service**.
- If a user requests **content**, the reverse proxy routes it to the **Content Service**.


