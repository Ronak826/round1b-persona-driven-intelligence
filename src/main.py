import argparse
import os

from io_utils import load_config, load_pdfs, dump_output, _now_iso
from extractor import segment_document
from ranker import Ranker
from summarizer import Summarizer


def main(config_path: str, output_path: str):
    config = load_config(config_path)
    persona_role = config["persona"]["role"]
    task_description = config["job_to_be_done"]["task"]

    documents_by_name = load_pdfs(config["documents"])

    all_sections = []
    for document_name, pages in documents_by_name.items():
        sections = segment_document(pages)
        for title, body, page_num in sections:
            all_sections.append((title, body, page_num, document_name))

    prompt = f"{persona_role}. {task_description}"
    ranker = Ranker(prompt)
    ranker.build(all_sections)
    top_sections = ranker.topk(5)

    summarizer = Summarizer()
    final_summary = summarizer.refine(
        persona_role,
        task_description,
        top_sections,
        all_sections
    )

    metadata = {
        "input_documents": [os.path.basename(doc["filename"]) for doc in config["documents"]],
        "persona": persona_role,
        "job_to_be_done": task_description,
        "processing_timestamp": _now_iso()
    }

    dump_output(metadata, top_sections, final_summary, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.config, args.output)
