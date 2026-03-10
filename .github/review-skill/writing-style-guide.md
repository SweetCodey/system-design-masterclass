# SweetCodey System Design Masterclass - Writing Style Guide

This guide documents the writing patterns, formatting conventions, and style rules extracted from the SweetCodey System Design Masterclass repository. All reviewed documents should follow these conventions.

---

## 1. Document Structure

Every system design document follows this exact order:

### Standard Section Ordering

1. **Title** - ALL CAPS, H1 heading (e.g., `# INSTAGRAM NEWSFEED DESIGN`)
2. **Table of Contents** - Linked, numbered entries for every section
3. **Introduction** (optional) - What is the system? Why do we need it?
4. **Functional Requirements** - What the system does
5. **Non-Functional Requirements** - How the system should behave
6. **Capacity Estimation** (optional) - DAU/MAU, Throughput, Storage, Memory, Network
7. **API Design** - REST API endpoints for each functional requirement
8. **High Level Design** - Architecture diagrams and data flow for each feature
9. **Deep Dive Insights** - Database selection, data modeling, advanced topics

### Section Headers

Each major section is preceded by a colored header:
```html
### <p style="font-size: 24px; font-style: italic; color:red">SECTION NAME</p>
```

Sub-sections use standard Markdown H2 (`##`) headings.

Sections are separated by horizontal rules:
```html
<hr style="border:2px solid gray">
```

---

## 2. Sentence Style

### Keep It Simple

- **Short sentences**: Average 10-20 words per sentence.
- **One idea per sentence**: Don't pack multiple concepts into one sentence.
- **Active voice**: "The server processes the request" NOT "The request is processed by the server."
- **Conversational tone**: Write as if you're explaining to a friend who knows basic programming.

### Good Examples (from the repository)

> "A Tiny URL Service, also known as a URL Shortener Service, helps shorten long URLs."

> "When we ask the server to create a text post, we use an API call. This is how computers talk to each other."

> "Accessing data from the database takes a long time, but if we want to access it faster, we use cache."

> "If the Tiny URL Service is down, people can't open the long URLs."

### Bad Examples (avoid these)

> "The microservices-based architecture leverages asynchronous event-driven communication patterns facilitated by a distributed message broker to ensure eventual consistency across bounded contexts."

This should be rewritten as:

> "Our system uses small, independent services that communicate through a message queue. This means data might take a second or two to update everywhere, but the system stays fast and reliable."

---

## 3. Requirements Formatting

### Functional Requirements

Use HTML tables with two columns: `Requirement` and `Description`.

```html
<table border="1">
    <tr>
        <th>Requirement</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Create Posts</td>
        <td>Users can create text, image, or video posts.</td>
    </tr>
</table>
```

- Each description should be 1-2 sentences max.
- Use simple, direct language.

### Non-Functional Requirements

Same HTML table format. Each NFR should:
- **Name the requirement** (Availability, Consistency, Latency, Scalability, etc.)
- **State a specific target** (99.999% uptime, under 1 second, etc.)
- **Explain WHY it matters** for this specific system in plain language

Example:
> **Availability**: If the Tiny URL Service is down, people can't open the long URLs. The system must be highly available with 99.99999% uptime.

---

## 4. Capacity Estimation Style

### Structure

Each estimation section follows this pattern:
1. **State what you're estimating**
2. **List assumptions clearly** (with bold formatting)
3. **Show the calculation** step by step
4. **State the result clearly**

### Example Pattern

```markdown
## Throughput Estimation

### Writes

There are only three possible ways to write data into the system:
- **Creating Posts**
- **Following**
- **Commenting/Liking**

#### Post Creation Calculation

Assume 10% of all Daily Active Users (DAU) create posts in a day.

- Total DAU = **500 million**
- 10% of DAU create posts = **50 million users** create posts daily
- This results in **50 million 'create post' requests per day**
```

### Key Rules
- Always state assumptions before calculations
- Use bold for key numbers
- Show math in code blocks for complex calculations
- Round numbers for readability
- Use consistent units throughout

---

## 5. API Design Formatting

### Structure for Each API

1. **Title**: "API Design: [Action Name]"
2. **Context**: One sentence explaining what this API does
3. **Diagram/Image**: Visual showing the API call
4. **HTTP Method**: Explain why this method is used
5. **Endpoint**: Show the full endpoint path
6. **Request Body** (for POST/PUT): Show JSON with all fields
7. **Response Body**: Show expected response JSON

### HTTP Method Explanations

Always explain the method choice:
> "Since we want to create something new on the server, we use the `POST` action."

> "Since we want to read data from the server, we use the `GET` action."

### Endpoint Conventions

- Version prefix: `/v1/`
- Plural nouns: `/v1/posts`, `/v1/users`, `/v1/bookings`
- Path parameters: `/v1/posts/{postId}`
- Explain versioning on first use:
> **Note:** 'v1' means version 1. It is a good practice to version your APIs.

### Request/Response Body

Show as JSON code blocks:
```json
{
  "userId": "12345",
  "content": "Hello World",
  "hashtags": ["tech", "coding"]
}
```

---

## 6. High-Level Design Style

### Data Flow Explanation

Use numbered steps to explain how data flows through the system:

> **Step 1**: The user sends a request to the API Gateway.
> **Step 2**: The API Gateway forwards the request to the Post Writer Service.
> **Step 3**: The Post Writer Service saves the post to the Posts Database.
> **Step 4**: The Post Writer Service publishes an event to the Message Queue.

### Component Introduction

When introducing a new component, always:
1. **Name it** (bold)
2. **Explain what it does** in 2-3 simple sentences
3. **Explain why we need it** for this specific system

Example:
> We use a **Message Queue** here. A message queue is like a to-do list for our system. When the Post Writer Service creates a post, it adds a "new post created" message to this queue. Other services can then pick up these messages and do their work (like updating feeds) without slowing down the post creation.

### Diagram Requirements

- Every major flow should have a diagram
- Diagrams should show: User -> API Gateway -> Service -> Database
- Include arrows showing data direction
- Label each arrow with what data is being sent

---

## 7. Deep Dive Style

### Database Selection

Compare options using a structured approach:
1. List the requirements (read-heavy? write-heavy? structured data?)
2. Compare 2-3 database options
3. Pick one and explain why
4. Use tables for comparisons

### Data Modeling

Show schemas with:
- Table/Collection name
- Field names and types
- Primary keys and indexes
- Brief explanation of why certain fields exist

### Problem-Solution Pattern

For deep dive topics, follow this pattern:
1. **State the problem** clearly
2. **Show why the naive approach fails**
3. **Present the solution**
4. **Explain how the solution works**
5. **Discuss trade-offs**

Example from TinyURL (collision handling):
- Approach 1: Random strings -> Problem: not unique across servers
- Approach 2: MD5 hash -> Problem: too long when truncated
- Approach 3: Check DB -> Problem: slow lookups
- Approach 4: Counters + ZooKeeper -> Solution!

---

## 8. Formatting Quick Reference

| Element | How to Format |
|---------|---------------|
| Major section dividers | `<hr style="border:2px solid gray">` |
| Section headers | `### <p style="font-size: 24px; font-style: italic; color:red">SECTION NAME</p>` |
| Requirements tables | HTML `<table>` with `border="1"` |
| Key numbers | **Bold** (e.g., **500 million**) |
| Technical terms | `code formatting` on first use |
| Calculations | Code blocks |
| API endpoints | `code formatting` |
| JSON bodies | ```json code blocks |
| Assumptions | Bullet points with bold labels |
| Step-by-step flows | Numbered bold steps |
| Comparisons | HTML tables |
| Notes/Tips | Blockquotes (`>`) |

---

## 9. Language Guidelines

### Words to Use
- "Let's" (collaborative tone)
- "We" (inclusive)
- "Simply" / "Just" (to show simplicity)
- "Think of it like..." (analogies)
- "In other words" (clarifications)
- "For example" (concrete examples)

### Words to Avoid
- "Obviously" / "Clearly" (might not be obvious to beginners)
- "Trivially" / "Simply put" without actually simplifying
- Excessive acronyms without expansion
- Academic/textbook language
- Passive voice constructions

### Explaining New Concepts

Every new concept needs:
1. **Name** (bolded)
2. **What it is** (1 sentence)
3. **Why we use it** (1 sentence)
4. **Simple analogy** (optional but recommended)

Example:
> We will use **ZooKeeper** for this. ZooKeeper is a coordination service that helps multiple servers work together without stepping on each other's toes. Think of it like a traffic controller at a busy intersection - it tells each server which range of numbers to use, so no two servers create the same short URL.

---

## 10. Common Patterns

### The "Zoom In" Pattern
Used for API sections:
> "Let's zoom into the 'communication' for creating a text post and understand exactly what's happening."

### The "Assumption" Pattern
Used before calculations:
> "Assume 10% of all Daily Active Users (DAU) create posts in a day."

### The "Problem -> Solution" Pattern
Used in deep dives:
> "But wait, there's a problem. Two different long URLs could produce the same short URL. This is called a collision."

### The "Real-World Analogy" Pattern
Used to explain complex concepts:
> "Think of cache as a small notebook you keep on your desk. Instead of going to the library every time you need information, you write down the most used facts in your notebook for quick access."
