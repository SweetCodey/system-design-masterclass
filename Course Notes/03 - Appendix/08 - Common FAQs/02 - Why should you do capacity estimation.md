# 🧮 **Why Do We Need Capacity Estimation in System Design Interviews?** 🖥️

---

## 1️⃣ **Determining the Number of Servers and Databases** 🖥️🗄️

Capacity estimation helps us figure out **how many servers, databases, or hardware** we need. Here’s how it works:

- We estimate metrics like **daily active users (DAU)**, **monthly active users (MAU)**, **throughput**, **bandwidth**, and **storage**.
- Based on these estimates, we calculate the required infrastructure.

### 🧮 **Example:**
- If your server can handle **1 million requests per hour**, but you expect **10 million requests per hour**, you’ll need **10 servers**.
- Similarly, you can estimate the number of databases required.

This is why capacity estimation is crucial **beforehand**! 📊

---

## 2️⃣ **Cost Management** 💸

Servers and databases aren’t free! Capacity estimation helps us avoid:
- **Overprovisioning**: Having more servers than needed (wasting money).
- **Underprovisioning**: Having fewer servers than needed (risking system failure).

By estimating capacity, we ensure we’re **not overspending** on unnecessary resources. 💡

---

## 3️⃣ **Deciding Hardware Type and Specifications** 🛠️

Capacity estimation helps us choose the **right type and specifications** of hardware (servers, databases, etc.). Let’s see an example:

### 🧮 **Example:**
- Your system needs to handle **10 million queries**.
- You have two database options:
    - **SQL Database**: Handles **50K queries per hour**.
    - **NoSQL Database**: Handles **1 million queries per hour**.

In this case, you’d choose the **NoSQL database** (assuming other factors align). This decision is based on **capacity estimation**! 🗂️

---

## 4️⃣ **Determining if the System is Read-Heavy or Write-Heavy** 📖✍️

Capacity estimation helps us understand whether the system is **read-heavy** or **write-heavy**. Here’s how:

- Through **throughput estimation**, we calculate **read and write throughput**.
- This tells us if the system is **read-heavy** (more reads) or **write-heavy** (more writes).

### 🧮 **Example:**
- If the system is **read-heavy**, we might choose **PostgreSQL** with indexing.
- If the system is **write-heavy**, we might choose **Cassandra** or **HBase**.

This decision impacts the **design and performance** of the system. 🚀

---

## 🎯 **Key Takeaways**
1. **Servers and Databases**: Capacity estimation helps determine the **number of servers and databases** needed.
2. **Cost Management**: It prevents **overspending** on unnecessary resources.
3. **Hardware Selection**: It helps choose the **right type and specifications** of hardware.
4. **Read-Heavy vs. Write-Heavy**: It identifies whether the system is **read-heavy** or **write-heavy**, influencing database choices.

---

## 🏁 **Conclusion**

Capacity estimation is a **critical step** in system design. It ensures:
- The system is **scalable** and **efficient**.
- Costs are **optimized**.
- The right **hardware and databases** are chosen.

I hope this explanation helps you understand why capacity estimation is so important! See you in the next session! 👋

---

### ↩️ 🔙 [Back](../README.md)