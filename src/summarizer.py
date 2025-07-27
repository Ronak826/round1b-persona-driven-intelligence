import os
from typing import Dict, List, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROMPT_TMPL = "Summarize for {persona} needing to {job}: {title} - {content}"

class Summarizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("t5-small")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8
        )
        self.model.eval()

    def refine(
        self,
        persona: str,
        job: str,
        ranked_sections: List[Dict],
        raw_sections: List[Tuple[str, str, int, str]],
        max_len: int = 100
    ) -> List[Dict]:
        
       
        id_lookup = {
            (os.path.basename(doc_path), title.strip(), page): body
            for title, body, page, doc_path in raw_sections
        }

        
        cache = {}
        batch_inputs = []
        cache_keys = []
        
        for section in ranked_sections:
            key = (
                section["document"],
                section["section_title"].strip(),
                section["page_number"]
            )
            if key not in id_lookup:
                continue
            if key in cache:
                continue
                
            body = id_lookup[key][:1500]  
            prompt = PROMPT_TMPL.format(
                persona=persona,
                job=job,
                title=section["section_title"],
                content=body
            )
            cache_keys.append(key)
            batch_inputs.append(prompt)
            
           
            if len(batch_inputs) == 4:
                summaries = self._process_batch(batch_inputs, max_len)
                for k, summary in zip(cache_keys, summaries):
                    cache[k] = summary
                batch_inputs = []
                cache_keys = []
                
     
        if batch_inputs:
            summaries = self._process_batch(batch_inputs, max_len)
            for k, summary in zip(cache_keys, summaries):
                cache[k] = summary

       
        analyses = []
        for section in ranked_sections:
            key = (
                section["document"],
                section["section_title"].strip(),
                section["page_number"]
            )
            if key not in cache:
                continue
            analyses.append({
                "document": section["document"],
                "refined_text": cache[key],
                "page_number": section["page_number"]
            })
            
        return analyses

    def _process_batch(self, batch_prompts: List[str], max_len: int) -> List[str]:
        inputs = self.tokenizer(
            batch_prompts,
            padding=True,
            truncation=True,
            max_length=256, 
            return_tensors="pt"
        )
        with torch.no_grad():
            summary_ids = self.model.generate(
                **inputs,
                max_length=max_len,
                num_beams=2,  
                no_repeat_ngram_size=2
            )
        return self.tokenizer.batch_decode(
            summary_ids, 
            skip_special_tokens=True
        )