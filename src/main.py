import argparse
import os
from io_utils import load_config, load_pdfs, dump_output, _now_iso
from extractor import segment_document
from ranker import Ranker
from summarizer import Summarizer


def main(config_path: str, output_path: str):
    print("🟡 Loading configuration...")
    config = load_config(config_path)
    persona_role = config["persona"]["role"]
    task_description = config["job_to_be_done"]["task"]

    print("📄 Loading PDF documents...")
    documents_by_name = load_pdfs(config["documents"])

    print("✂️ Segmenting documents into sections...")
    all_sections = []
    for document_name, pages in documents_by_name.items():
        sections = segment_document(pages)
        for title, body, page_num in sections:
            all_sections.append((title, body, page_num, document_name))

    print(f"🔍 Ranking top sections using persona prompt: {persona_role} — {task_description}")
    prompt = f"{persona_role}. {task_description}"
    ranker = Ranker(prompt)
    ranker.build(all_sections)
    top_sections = ranker.topk(5)

    print("🧠 Summarizing top-ranked sections...")
    summarizer = Summarizer()
    final_summary = summarizer.refine(
        persona_role,
        task_description,
        top_sections,
        all_sections
    )

    print("💾 Writing output to JSON...")
    metadata = {
        "input_documents": [os.path.basename(doc["filename"]) for doc in config["documents"]],
        "persona": persona_role,
        "job_to_be_done": task_description,
        "processing_timestamp": _now_iso()
    }

    dump_output(metadata, top_sections, final_summary, output_path)
    print(f"✅ Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.config, args.output)
