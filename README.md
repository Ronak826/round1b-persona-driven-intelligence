# Round 1B: Persona-Driven Document Intelligence  
##  Theme: “Connect What Matters — For the User Who Matters”

---

We built a system that reads multiple PDF documents and picks out the most important parts for a specific user (persona) who needs to do a specific task (job-to-be-done).  
It works for many kinds of users (like students, analysts, researchers) and many types of documents (like reports, textbooks, research papers).

---

##  System Overview

Our pipeline has 4 main steps:

### 1. Load and Segment PDFs

- We extract text from each page using **PyMuPDF**.
- Documents are split into sections using simple heuristics like:
  - Font size
  - Uppercase or numbered titles (e.g. "2.1 Overview")
- Each section stores title, body, page number, and document path.

---

### 2. Rank the Most Relevant Sections

- We use a lightweight **MiniLM** sentence transformer to encode the user persona and job.
- Each section is embedded and compared with this query.
- We also apply keyword boosting for travel-related terms (like “cities”, “cuisine”, etc.).
- The final **hybrid score** is:

- We select the top-5 most relevant sections.

---

### 3. Summarize the Top Sections

- We use **quantized T5-small** from Hugging Face to summarize each selected section.
- Summarization prompt example:
> "Summarize for a [persona] who needs to [job]: [section title] – [section content]"
- Summaries are computed in small batches for speed.

---

### 4. Save Output

We generate a JSON output containing:
-  Persona and job metadata
-  Ranked section metadata (title, page number, rank)
-  Summary of each selected section

---

## ⚙️  Performance

- Runs fully on **CPU**
- No internet required at runtime
- Processes 3–5 PDFs in **under 60 seconds**

---
### It processes 7 PDFs in under 90 seconds and 5 PDFs in nearly 60 seconds. We can try to optimize this further
<img width="926" height="288" alt="image" src="https://github.com/user-attachments/assets/77d26b60-1f9a-4c40-9a24-93d29629fd8e" />

## 🧩 Why It Works for Any Persona

- The system is model-driven, not rule-based.
- It dynamically adapts to different personas and tasks using embeddings.
- Works across domains (travel, science, business, education) without retraining.

---

```bash
docker build -t round1b-persona-intel .
```
``` bash

docker run --rm -v "$(pwd):/app" round1b-persona-intel

```
### Windows 
```bash
docker run --rm -v "${PWD}:/app" round1b-persona-intel
```

 ## Final Notes
We have reduced processing time and improved accuracy, with potential for further optimization

Everything is containerized with Docker for easy reproducibility.

The system is lightweight, fast, and general-purpose.

JSON output structure matches submission requirements exactly.

