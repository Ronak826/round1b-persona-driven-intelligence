import os
from typing import Dict, List, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROMPT_TMPL = (
    "Summarize for a {persona} who needs to {job}.\n\n"
    "### Section title\n{title}\n\n"
    "### Content\n{content}"
)

class Summarizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
        self.model.eval()

    def refine(
        self,
        persona: str,
        job: str,
        ranked_sections: List[Dict],
        raw_sections: List[Tuple[str, str, int, str]],
        max_len: int = 140
    ) -> List[Dict]:

        id_lookup = {
            (os.path.basename(doc_path), title.strip(), page): body
            for title, body, page, doc_path in raw_sections
        }

        analyses = []

        for section in ranked_sections:
            key = (
                section["document"],
                section["section_title"].strip(),
                section["page_number"]
            )

            if key not in id_lookup:
                print(f"⚠️ Warning: Section not found for key: {key}")
                continue

            body = id_lookup[key]

            prompt = PROMPT_TMPL.format(
                persona=persona,
                job=job,
                title=section["section_title"],
                content=body[:3000]
            )

            inputs = self.tokenizer(
                prompt,
                truncation=True,
                max_length=768,
                return_tensors="pt"
            )

            with torch.no_grad():
                summary_ids = self.model.generate(
                    **inputs,
                    max_length=max_len,
                    num_beams=4,
                    no_repeat_ngram_size=3
                )

            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            analyses.append({
                "document": section["document"],
                "refined_text": summary,
                "page_number": section["page_number"]
            })

        return analyses
