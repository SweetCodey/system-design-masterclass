# CACHING STRATEGIES

- [1.Caching Strategies:Read](#caching-strategies-read)

- [2.Caching Strategies:Write](#caching-strategies-write)

- [3.Read Caching Strategies :Pros and Cons](#read-caching-strategies-pros-and-cons)

- [4.Write Caching Strategies :Pros and Cons](#write-caching-strategies-pros-and-cons)

<hr style="border:2px solid gray">

## Caching Strategies :Read

Here are two common methods to read data from a cache:

### *Cache Aside Strategy*
- When data is requested, we first look in the cache.
- If it's not there, we retrieve it from the database.
- The retrieved data is then saved in the cache for future requests.

![Cache Aside](https://static.wixstatic.com/media/99fa54_6d8c7d722dfb453d867001fb4e422b93~mv2.png/v1/fill/w_1103,h_680,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_6d8c7d722dfb453d867001fb4e422b93~mv2.png)

### *Read Through Strategy*
- When data is requested, we first look in the cache.
- If it’s not there, the cache itself fetches the data from the database.
- The cache then saves the data for future requests.

This is called **"Read Through"** because we are reading the data **through the cache**.

![Read Through](https://static.wixstatic.com/media/99fa54_fbf91cfe5d184d6b8a70b51ae17ed0ab~mv2.png/v1/fill/w_1078,h_690,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/99fa54_fbf91cfe5d184d6b8a70b51ae17ed0ab~mv2.png)

<hr style="border:2px solid gray">

## Caching Strategies :Write

Here are the three common strategies to write the data in the cache:

### *Write Aside Strategy*

![Write Aside Strategy](https://static.wixstatic.com/media/99fa54_7f8ee752c26847949940018b0ed0c853~mv2.png/v1/fill/w_783,h_357,al_c,lg_1,q_85,enc_auto/99fa54_7f8ee752c26847949940018b0ed0c853~mv2.png)

In this write strategy, data is written directly to the database, bypassing the cache.

You might wonder, “How does the cache get updated?” This happens during the read process! When the data is read, the system first checks the cache. If there’s a cache miss (meaning the data isn’t there), it fetches the data from the database and then updates the cache.

Basically, the cache gets updated reactively (on-demand) rather than proactively. This is why this approach is also known as **lazy caching**.

### *Write Through Strategy*

![Write Through](https://static.wixstatic.com/media/99fa54_f777481de61b47a6887692975078031f~mv2.png/v1/fill/w_781,h_277,al_c,lg_1,q_85,enc_auto/99fa54_f777481de61b47a6887692975078031f~mv2.png)

In this strategy, every time data is written, it’s first written to the cache. Then, the cache immediately updates the database.

This process happens **synchronously**—meaning that only after the database is updated does the application get confirmation of the write.

### *Write Behind Strategy*

![Write Behind](https://static.wixstatic.com/media/99fa54_9c246cc0fac243f2be735a862948a163~mv2.png/v1/fill/w_781,h_268,al_c,lg_1,q_85,enc_auto/99fa54_9c246cc0fac243f2be735a862948a163~mv2.png)

In this strategy, when data is written, it’s also first written to the cache, and the cache then updates the database.

The key difference here is that the database update happens **asynchronously**. The application receives a confirmation as soon as the data is written to the cache, and the database is updated in the background / asynchronously.

<hr style="border:2px solid gray">

## Read Caching Strategies :Pros and Cons

### Cache-Aside Strategy

![Cache Aside](https://static.wixstatic.com/media/99fa54_edb470b6176b42e082f1f1382d1a7d83~mv2.png/v1/fill/w_775,h_364,al_c,lg_1,q_85,enc_auto/99fa54_edb470b6176b42e082f1f1382d1a7d83~mv2.png)

### *Pros:*
- **Fault Tolerance:**  
  If the cache fails for any reason, the system doesn’t break. We can still read data directly from the database, even though it may be a bit slower. Basically, the cache is kept separate (hence “cache-aside”), so it doesn’t impact uptime if it goes down.

- **Flexible Schemas:**  
  Since the application controls the cache, we have more flexibility in how we store data. The cache and database can have different data structures. For example, the cache might only store commonly accessed details, like a user’s name and contact details, while the database holds the full profile.

### *Cons:*
- **Stale Data:**  
  Let’s say a user record (e.g., `user4`) is initially only in the database, not in the cache. When a read request comes in, the cache misses, so we fetch `user4` from the database and save it to the cache. Now, future requests for `user4` will be served from the cache.  

  But if `user4`’s record in the database is updated (say their address changes), the cache still holds the old address since it wasn’t refreshed. If we get another request for `user4`, it will still serve the outdated address from the cache.  

  To avoid this, we need to periodically remove old data from the cache—a process called **cache invalidation**.  

  After invalidation, the next request for `user4` will miss the cache and fetch the updated info from the database.

### Read-Through Strategy

![Read Through](https://static.wixstatic.com/media/99fa54_d4c518f9b20f4b09bbf2a24d3375af19~mv2.png/v1/fill/w_788,h_277,al_c,lg_1,q_85,enc_auto/99fa54_d4c518f9b20f4b09bbf2a24d3375af19~mv2.png)

### *Pros:*
- **No Stale Data (with Write-Through):**  
  If we pair the Read-Through strategy with Write-Through, data in the cache stays fresh. Every update (like a change in `user4`’s address) is written to both the cache and database at the same time. So, whenever we read data from the cache, it’s guaranteed to be up-to-date.

### *Cons:*
- **Cache Failure Causes Downtime:**  
  If the cache fails, the application can’t read data directly from the database because, in this strategy, all reads go through the cache. So, a cache failure could make the whole system unavailable.

- **Non-Flexible Schema:**  
  In this approach, the cache and database need to have the same data structure. This limits flexibility since we can’t customize what’s stored in the cache.

<hr style="border:2px solid gray">

## Write Caching Strategies :Pros and Cons

### **Write-Aside Strategy**

![Write Aside](https://static.wixstatic.com/media/99fa54_7f8ee752c26847949940018b0ed0c853~mv2.png/v1/fill/w_784,h_356,al_c,lg_1,q_85,enc_auto/99fa54_7f8ee752c26847949940018b0ed0c853~mv2.png)

### **Pros:**
- **Faster Writes:** Data is written directly to the database, skipping the cache. Since we only write once (to the database), writes are faster, making it ideal for write-heavy systems where immediate cache updates aren't required.
- **Cache Independence:** The cache operates separately from the write process. If the cache fails, it doesn't impact database writes, ensuring system reliability.

### **Cons:**
- **Slower Reads:** Since the cache is bypassed during writes, data won't be in the cache immediately. Reads may result in a cache miss, requiring a fetch from the database before updating the cache, slowing down the process.
- **Risk of Stale Data:** If a user's address is updated in the database but the cache isn’t refreshed, it may still contain the old data. Until the cache expires and removes stale data, users may see outdated information.

### **Write-Through Strategy**

![Write Through](https://static.wixstatic.com/media/99fa54_f777481de61b47a6887692975078031f~mv2.png/v1/fill/w_781,h_277,al_c,lg_1,q_85,enc_auto/99fa54_f777481de61b47a6887692975078031f~mv2.png)

### **Pros:**
- **No Stale Data:** Every write updates both the cache and the database simultaneously. This ensures that updates, like a user’s address change, are immediately reflected in both locations.
- **Faster Reads:** Since data is always available in the cache, reads are quick and do not rely on cache misses to update.

### **Cons:**
- **Slower Writes:** Writes take longer since they update both the cache and the database. Unlike the Write-Around strategy, this approach introduces extra latency.
- **Cache Dependency:** Since all writes go through the cache, a cache failure can prevent writes from reaching the database, potentially causing system downtime.

### **Write Behind Strategy**

![Write Behind](https://static.wixstatic.com/media/99fa54_9c246cc0fac243f2be735a862948a163~mv2.png/v1/fill/w_781,h_269,al_c,lg_1,q_85,enc_auto/99fa54_9c246cc0fac243f2be735a862948a163~mv2.png)

### **Pros:**
- **Faster Writes:** Data is first written to the cache, and the application receives a confirmation instantly. The cache then updates the database asynchronously in the background, improving write performance.
- **Faster Reads:** Since data is stored in the cache, read operations are quick and don’t need to access the database.

### **Cons:**
- **Risk of Data Loss:** The asynchronous database update can fail. If the background update doesn’t go through, data won't be stored in the database, raising durability concerns.
- **Cache Dependency:** Since every write depends on the cache, a cache failure could prevent writes from being stored in the database, leading to system downtime.
