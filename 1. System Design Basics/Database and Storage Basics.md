# BUZZWORDS :DATABASE AND STORAGE

In this section, let's explore the **data layer** in our system design. We will learn about:

[1.Relational Databases or SQL](#relational-database-or-sql-database)

[2.Non Relational Database or NOSQL](#non-relational-database-or-nosql)

[3.SQL vs NOSQL](#sql-vs-nosql)

[4.Object Storage](#object-storage)

[5.Database Sharding and Database Replication](#database-sharding-and-database-replication)

[6.Cache](#cache)

[7.CDN](#cdn)

These techniques improve **data access, performance, and fault tolerance** for our **data layer**.

<hr style="border:2px solid gray">
 
## Relational Database or SQL Database

A relational database stores data in **tables**, which are similar to spreadsheets with **rows and columns**.

### When to Use  
Relational databases are ideal for storing **well-structured data**, such as **user data**.

#### Why is User Data Structured?  
User data is considered structured because it is organized into predefined fields, such as:  
- **Name**  
- **Email**  
- **Phone Number**  
- **Address**  

### Examples of Relational / SQL Databases  
Some popular relational databases include:  
- **MySQL**  
- **PostgreSQL**

![Relational Database](https://static.wixstatic.com/media/99fa54_3bc83820d2c04414a8f97b27d601a861~mv2.png/v1/fill/w_1120,h_498,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_3bc83820d2c04414a8f97b27d601a861~mv2.png)

<hr style="border:2px solid gray">

## Non Relational Database or NoSQL

Imagine saving social media posts in a table with columns for text, images, and videos.

- If a post has only text, the image and video columns remain empty.  
- Similarly, a post with only a video leaves the text and image columns empty.  

This leads to many empty spaces in the table, which is inefficient and wastes resources.

![Nosql1](https://static.wixstatic.com/media/99fa54_3624485a97ce4a8a957094108c22895e~mv2.png/v1/fill/w_1120,h_430,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_3624485a97ce4a8a957094108c22895e~mv2.png)

### Why Use NoSQL?  

This is where we use **NoSQL databases**. They are ideal for storing data that doesn’t have a fixed structure.  

#### Examples of Popular NoSQL Databases:  
- MongoDB  
- Cassandra  
- DynamoDB  

### Types of NoSQL Databases  

NoSQL databases come in various types, each suited to different needs:  

1. **Key-Value Stores**  
2. **Document Databases**  
3. **Graph Databases**  
4. **Wide-Column Databases**  
5. **Time-Series Databases**  


![Nosql2](https://static.wixstatic.com/media/99fa54_a75ac091f5ed47bfa1ca95b23760e62c~mv2.png/v1/fill/w_864,h_786,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_a75ac091f5ed47bfa1ca95b23760e62c~mv2.png)

<hr style="border:2px solid gray">

## SQL vs NoSQL

The natural question that arises here is how to choose between SQL vs NoSQL database.

Here are some general guidelines that you can follow, but **DO REMEMBER** it’s not always black and white. A lot depends on the project needs.

<table border="1">
  <tr>
    <th>Criteria</th>
    <th>SQL</th>
    <th>NoSQL</th>
  </tr>
  <tr>
    <td>Fast Data Access</td>
    <td>Slower compared to NoSQL</td>
    <td>Faster</td>
  </tr>
  <tr>
    <td>Scalability</td>
    <td>Less scalable for large-scale data</td>
    <td>Performs better at large scale</td>
  </tr>
  <tr>
    <td>Data Structure</td>
    <td>Fixed schema (structured data)</td>
    <td>Flexible schema (unstructured/semi-structured data)</td>
  </tr>
  <tr>
    <td>Query Complexity</td>
    <td>Best for complex queries</td>
    <td>Better for simple queries</td>
  </tr>
  <tr>
    <td>Data Evolution</td>
    <td>Rigid structure, harder to modify</td>
    <td>Flexible, supports frequent changes</td>
  </tr>
</table>

<hr style="border:2px solid gray">

## Object Storage

In Object Storage, we store objects.

### What is an Object?
Each object is either a photo, video, audio, or file. Effectively, they are simply units of data composed of bits/bytes.

### Why Use Object Storage?
This type of storage is perfect for keeping large amounts of data that don't follow a regular structure, such as:
- Pictures
- Videos
- Music
- Documents
- Backups

### Examples of Object Storage Services
Some popular object storage services include:
- **Amazon S3**
- **Google Cloud Storage**
- **Microsoft Azure Blob Storage**

![object storage](https://static.wixstatic.com/media/99fa54_5436c42cbe4d485582cb07d6a204410c~mv2.png/v1/fill/w_714,h_811,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_5436c42cbe4d485582cb07d6a204410c~mv2.png)

<hr style="border:2px solid gray">

## Database Sharding and Database Replication

### Database Sharding

Database sharding splits a large database into smaller sections called **shards**.

- Each shard stores a part of the data.
- This speeds up searches and reduces stress on any single server.
- If one shard has a problem and stops working, the other shards keep functioning.
- This ensures that the whole system doesn’t go down, making the database more reliable.

![Database sharding](https://static.wixstatic.com/media/99fa54_7715d98a7c134410b13152fb9fcf5c32~mv2.png/v1/fill/w_1120,h_459,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_7715d98a7c134410b13152fb9fcf5c32~mv2.png)

### Database Replication

Database replication is the process of making copies of a database so that if one fails, others can take over.

- This enhances **fault tolerance** and **availability**.
- Replication ensures **data redundancy**, improving disaster recovery.

![Database replication](https://static.wixstatic.com/media/99fa54_aab9677d24844e9799da70b992038a21~mv2.png/v1/fill/w_1120,h_488,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_aab9677d24844e9799da70b992038a21~mv2.png)


## Cache

Accessing data from a database takes a long time. But if we want to access it faster, we use a cache.

Accessing from a cache is **~50 to 100 times faster** than accessing from a database.

### What is Cache?

Cache is a type of memory that is **super fast** but has **limited capacity** (much less compared to a database).  
That is why we use cache to store **frequently accessed data**.

#### Analogy:
It is like **keeping snacks close to you at your desk (cache)** while you study.  
Instead of walking to the **kitchen (database)** each time you're hungry, you simply grab a snack from your desk.

### Cache Hit and Cache Miss

- **Cache Hit:** When the data is found in the cache.
- **Cache Miss:** When the data is not found in the cache.

### Examples

- **Cache Hit:**  
  User1's data is found in the cache, so it is quickly fetched from the cache without the need for accessing the database.

![Cache hit](https://static.wixstatic.com/media/99fa54_bb94d13f244f4b2f986e6130d9c09f77~mv2.png/v1/fill/w_671,h_643,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_bb94d13f244f4b2f986e6130d9c09f77~mv2.png)

- **Cache Miss:**  
  User4's data isn't in the cache initially. It's fetched from the **database (slow)** and the cache is updated.

![Cache Miss](https://static.wixstatic.com/media/99fa54_f86ea614a7134505b10414cd4eb08102~mv2.png/v1/fill/w_616,h_633,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_f86ea614a7134505b10414cd4eb08102~mv2.png) 

  The **next request for User4** is quickly served from the cache because User4's data is now in the cache.

![Cache Hit2](https://static.wixstatic.com/media/99fa54_c16946b9d82e4085b7291ee874c34117~mv2.png/v1/fill/w_658,h_655,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_c16946b9d82e4085b7291ee874c34117~mv2.png) 

## CDN - Content Delivery Network

Let's say **Sweet Codey** has all its servers in the **US**. A user from **India** tries to open `sweetcodey.com`.

### The Problem

The website assets (**Images, Videos, etc.**) are bulky content. This bulky content has to travel a long distance, which increases **latency** significantly.

### The Solution: CDN

A **CDN (Content Delivery Network)** comes in handy in this case.

It stores copies of your website’s **static content** (static content = data that doesn’t change too often) at various locations around the world.

### Benefits of CDN:
- **Reduced Latency** – The user gets content from the nearest server.
- **Faster Load Times** – No need to fetch data from the original US server.
- **Efficient Bandwidth Usage** – Less strain on the main server.

## How It Works

Now, the user can quickly access static content (**images, videos, etc.**) directly from a **CDN server closer** to them.

![CDN](https://static.wixstatic.com/media/99fa54_bf1080d30bae43fd9b68d6d0fd0e7a2d~mv2.png/v1/fill/w_1120,h_598,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_bf1080d30bae43fd9b68d6d0fd0e7a2d~mv2.png) 
