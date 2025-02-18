# 📚 Database Indexing 🗂️

![01.png](img/01.png)

## 🎬 Introduction

1. **❓ What exactly is database indexing?**
2. **🛠️ How do we create indexes?**
3. **🤖 Does the database automatically add indexes?**
4. **🚫 Should we use indexing everywhere?**

---

## 🧐 What is Database Indexing? 📖

![02.png](img/02.png)
Database indexing is akin to the **index page in a book**. Imagine searching for a recipe in a cookbook. Instead of flipping through every page, you use the index to find the exact page number instantly. Similarly, database indexing helps locate specific rows without scanning every record.

#### For example:  

![03.png](img/03.png)
- Consider a `users` table with columns for **ID**, **username**, and **email**. If you want to find a user named "Adam," indexing allows you to access the relevant row almost instantly, much like using a book's index to find a recipe.

---

## 🛠️ Creating Indexes 🔧

### 🏗️ How Indexes are Created

![04.png](img/04.png)

Indexes are created on **specific columns** of a table. For instance, if we create an index on the `username` column, it creates a **shortcut** based on usernames. This shortcut maps each username to a **pointer** that directs to the corresponding row in the table.

### 🗄️ Storage of Indexes

![05.png](img/05.png)

Indexes are typically stored using data structures like **B-trees** 🌳 or **hash tables** 🗃️. B-trees store data in a **hierarchical, sorted structure**, allowing efficient searching, insertion, and deletion. Hash tables, on the other hand, are useful for **exact match queries**.

### ⚡ Query Optimization

![06.png](img/06.png)

Indexes significantly optimize queries. For example, a query like `SELECT * FROM users WHERE username = 'Partha'` can be executed swiftly if an index exists on the `username` column. The database uses the index to directly locate the row without scanning the entire table.

### 🔍 Sorted Searches

![07.png](img/06.png)

Indexes also aid in **sorted searches**. For instance, if you have an index on the `age` column organized in a B-tree, you can efficiently perform **range queries**, such as finding all users aged between 30 and 40.

---

## 🤖 Automatic Indexing 🤔

![08.png](img/08.png)

Most databases **automatically create indexes** on primary key columns, known as **primary key indexes**. However, **manual indexing** is also possible based on query patterns. For example, if you frequently query the `email` column, you might manually create an index on it using a command like:

```sql
CREATE INDEX idx_name ON users (username);
```

This command creates an index named `idx_name` on the `username` column of the `users` table.

---

## 🚫 The Downsides of Indexing ⚠️

While indexing is powerful, it's not without drawbacks:

![09.png](img/09.png)

1. **💾 Storage Overhead**: Each index consumes additional disk space.
2. **✍️ Write Performance**: Insert, update, and delete operations require updating indexes, which can slow down **write-heavy applications**.

Therefore, it's crucial to create indexes **judiciously**, focusing on common query patterns to balance read efficiency and write performance.

---

## 🎯 Conclusion 🏁

Indexes are **invaluable** for **read-heavy operations**, enhancing query performance significantly. However, they should be used **thoughtfully** to avoid unnecessary storage and performance overheads. By understanding and applying these concepts, you can optimize your database interactions effectively.

---

### ↩️ 🔙 [Back](../README.md)