# 🧠 Round 1B: Persona-Driven Document Intelligence  
## ✨ Theme: “Connect What Matters — For the User Who Matters”

---

## ✅ Goal

We built a system that reads multiple PDF documents and picks out the most important parts for a specific user (persona) who needs to do a specific task (job-to-be-done).  
It works for many kinds of users (like students, analysts, researchers) and many types of documents (like reports, textbooks, research papers).

---

## 🏗️ System Overview

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
- ✅ Persona and job metadata
- 📄 Ranked section metadata (title, page number, rank)
- ✍️ Summary of each selected section

---

## ⚙️ Models and Performance

| Component       | Model Used                            | Size     |
|----------------|----------------------------------------|----------|
| Embedder       | all-MiniLM-L6-v2 (SentenceTransformer) | ~90 MB   |
| Summarizer     | t5-small (quantized)                   | ~120 MB  |
| **Total**      |                                        | **< 220 MB** ✅ |

- ✅ Runs fully on **CPU**
- 🚫 No internet required at runtime
- ⚡ Processes 3–5 PDFs in **under 60 seconds**

---
### Processes 6–7 PDFs in under 30 seconds
<img width="1042" height="330" alt="image" src="https://github.com/user-attachments/assets/a7904dd0-812f-4e07-87fe-4e635733ef96" />

## 🧩 Why It Works for Any Persona

- The system is model-driven, not rule-based.
- It dynamically adapts to different personas and tasks using embeddings.
- Works across domains (travel, science, business, education) without retraining.

---

```bash
docker build -t round1b-persona-intel .
```
``` bash
docker build -t round1b-persona-intel .

docker run --rm -v $(pwd):/app round1b-persona-intel python src/main.py --config input.json --output output/challenge1b_output.json

```
### Windows 
```bash
docker run --rm -v ${PWD}:/app round1b-persona-intel \ python src/main.py --config input.json --output output/challenge1b_output.json
```

 ## Final Notes
Everything is containerized with Docker for easy reproducibility.

The system is lightweight, fast, and general-purpose.

JSON output structure matches submission requirements exactly.

