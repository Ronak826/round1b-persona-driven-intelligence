# 🧠 Round 1B: Persona-Driven Document Intelligence  
## ✨ Theme: “Connect What Matters — For the User Who Matters”

## ✅ Goal

We built a system that reads multiple PDF documents and picks out the most important parts for a specific user (persona) who needs to do a specific task (job-to-be-done).  
It works for many kinds of users (like students, analysts, researchers) and many types of documents (like reports, textbooks, research papers).

---

## 🏗️ System Overview

Our pipeline has 4 main steps:

### 1. Load and Segment PDFs

- We extract text from each page.
- We split each document into sections using simple rules like:
  - Font size
  - Uppercase or numbered titles (e.g. "2.1 Overview")
- Each section is saved with its title, body, page number, and source document.

### 2. Rank the Most Relevant Sections

- We use a **sentence transformer model** (MiniLM) to understand the meaning of the persona and the task.
- We compare this meaning with each section to calculate how relevant it is.
- We also give extra points to travel-related keywords (like "cities", "cuisine", etc.) to help in travel use cases.
- A hybrid score = 70% semantic similarity + 30% keyword boost.
- We pick the top 5 sections.

### 3. Summarize the Top Sections

- We use **DistilBART** to summarize each selected section.
- A custom prompt is made for each summary:
  > "Summarize for a [persona] who needs to [job]..."
- This makes the summary more helpful and focused.

### 4. Save Output

- We generate a JSON output with:
  - Input metadata (persona, job, file names, timestamp)
  - Top ranked sections (title, page number, rank)
  - Summaries of each section

---

## 🧩 Why It Works for Any Persona

- The system doesn’t depend on fixed rules or topics.
- It uses language models to **understand meaning**, so it works for any domain (science, business, education).
- It reads the persona and job every time and customizes the ranking and summaries.

---

## ⚙️ Models and Performance

| Component       | Model Used                            | Size    |
|----------------|----------------------------------------|---------|
| Embedder       | all-MiniLM-L6-v2 (SentenceTransformer) | ~90 MB  |
| Summarizer     | distilbart-cnn-12-6                    | ~480 MB |
| Total Model Size                                      | **< 600 MB** ✅ |

- Runs fully on CPU
- No internet required during execution
- Processes 3–5 PDFs in **under 60 seconds**

---

## 📦 Final Notes

- All files are containerized with Docker.
- All dependencies are included in the image.
- Output matches the required JSON format.

We’ve kept the system **simple, fast, and general** so that it can adapt to any persona and document type without needing changes.

