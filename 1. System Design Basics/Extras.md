# BUZZWORDS: EXTRAS

Dive into extra topics to take your system design skills further. We'll explore:

- [1.Cloud Computing](#cloud-computing)

- [2.Logging and Monitoring](#logging-and-monitoring)

- [3.Hashing and Consistent Hashing](#hashing-and-consistent-hashing)

- [4.CAP Theorem](#cap-theorem)

<hr style="border:2px solid gray">

## Cloud Computing
*There is no such thing as the cloud. Servers are always kept in a data center.* 

### Understanding Cloud Computing  

If you try to host your website, you will need servers for that. Instead of buying and maintaining physical servers yourself for your website, why don’t you rent them?  

This is where **Cloud Computing** comes in. With cloud computing, you can rent computing resources from providers like:  

- **AWS (Amazon Web Services)**  
- **Google Cloud**  
- **Microsoft Azure**  

This allows you to focus on your website while they handle the infrastructure.  

![cloud computing](https://static.wixstatic.com/media/99fa54_5773ebfdac1e471caa1ffdeefc80e60d~mv2.png/v1/fill/w_1120,h_420,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_5773ebfdac1e471caa1ffdeefc80e60d~mv2.png)

<hr style="border:2px solid gray">

## Logging & Monitoring

### Logging

Logging is like a computer writing in a diary.  

- It records everything important like errors and key activities.  
- These records are called logs.  
- These logs can be used to fix problems (troubleshooting) and also for data analysis.  

![logging](https://static.wixstatic.com/media/99fa54_ed282e658de446298a056aeb83629b31~mv2.png/v1/fill/w_1120,h_300,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/99fa54_ed282e658de446298a056aeb83629b31~mv2.png)

### Monitoring

Monitoring is like keeping a close watch on a computer.  

- When we monitor, we constantly check that everything is working properly.  
- If there are any issues, we catch them and fix them.  
- It's like having a security camera on a computer.  

![monitoring](https://static.wixstatic.com/media/99fa54_fcad1baf81d5440b98cc9c2789abd4e2~mv2.png/v1/fill/w_1120,h_523,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_fcad1baf81d5440b98cc9c2789abd4e2~mv2.png)

<hr style="border:2px solid gray">

## Hashing and Consistent Hashing

Think of a library where each new book gets a numeric code. The librarian uses this code to quickly put the book on the right shelf.

To find a book, the system uses this code, which is much faster than searching by title.

**Hashing** is very similar. It converts data into a short, random, unique code. This code helps efficiently place and locate data in a system.

![hashing1](https://static.wixstatic.com/media/99fa54_64da032fc3e6470baf517fc0a917d7ba~mv2.png/v1/fill/w_1120,h_489,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_64da032fc3e6470baf517fc0a917d7ba~mv2.png)

#### *The Problem with Reorganization*

Let’s say we need to reorganize our bookshelves. However, if we do so, we would need to change the codes of a lot of books.

#### Example:

- If we remove **shelf number 2**, then:
  - **Shelf 3** becomes the new **shelf 2**.
  - **Shelf 4** becomes the new **shelf 3**.

- Suppose we had a book called *"The Alchemist"* on **shelf 3**, coded as **3B**.
- Now, since our old **shelf 3** is the new **shelf 2**, *"The Alchemist"* should have a new code **2B**.

![hashing2](https://static.wixstatic.com/media/99fa54_6c8ea76f91174f0fb66a4b7c76d3cc04~mv2.png/v1/fill/w_1120,h_680,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_6c8ea76f91174f0fb66a4b7c76d3cc04~mv2.png)

This means we would need to update our system with the new codes for all books. 

### Why is this a problem?
Imagine someone wants to borrow *"The Alchemist"*. If our system isn't updated, it will still show the book at **code 3B**.

- The librarian goes to **shelf 3B** but cannot find *"The Alchemist"* there.
- Instead, she finds a different book.
- The system is now inaccurate, causing confusion.

Therefore, updating all book codes whenever we reorganize shelves is a big hassle.

![hashing3](https://static.wixstatic.com/media/99fa54_9414fe2dbbff4e2ba76bd2c5c660e3ef~mv2.png/v1/fill/w_1120,h_438,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_9414fe2dbbff4e2ba76bd2c5c660e3ef~mv2.png)

### Consistent Hashing

**Consistent Hashing**, a special type of hashing, is a smart algorithm that minimizes these reorganizations.

- Even if shelves change, most books will still keep their original codes.
- Only a **few** books need to be changed, making it much easier to manage.

We won’t go deep into how it works, as that would be out of the scope of this course. Just imagine it as a **magic algorithm** that helps minimize all these reorganization hassles.

<hr style="border:2px solid gray">

## CAP Theorem

Ideally, you would want your system to be both **consistent** and **available**.

### Handling Partitions

Let's say an accident happens that creates a **partition** in our system.  
How will you tolerate the partition?

The **CAP theorem** states that you can either make your system **available** or **consistent**, but you **cannot** have both at the same time.

### Example: SweetBook (A Social Media Company)

Consider there is a social media company called **SweetBook**. They have servers all around the world.

#### The Partition Event

- At **3:00 PM**, an accident happens, and the connection between their **New York** and **San Francisco** servers is lost.  
  They have a **partition** now.
- At **3:30 PM**, your **friend in New York** posts something on social media.

### *Two Possible Scenarios:*

1. **If SweetBook prioritizes availability**  
   - The site remains accessible.  
   - However, you **won't see** the new post from your friend in New York—only posts from local San Francisco users.

2. **If SweetBook prioritizes consistency**  
   - You might see a message like **"Website not available"** when trying to access it from San Francisco.  
   - This ensures that all users see the same, up-to-date data.

![cap theorem1](https://static.wixstatic.com/media/99fa54_2538ff4aa9684b9aab9919dc2f966527~mv2.png/v1/fill/w_1013,h_613,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_2538ff4aa9684b9aab9919dc2f966527~mv2.png)

![cap theorem2](https://static.wixstatic.com/media/99fa54_5f29569774cd434fa383aacbd9c885b6~mv2.png/v1/fill/w_1075,h_613,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_5f29569774cd434fa383aacbd9c885b6~mv2.png)

### *Conclusion*

You **cannot** have both **availability** and **consistency** at the same time in the presence of a partition.
