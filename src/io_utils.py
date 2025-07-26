import json, os, datetime as dt
from typing import Dict, List, Any
import fitz                       # PyMuPDF


# ---------- helpers ----------
def _now_iso() -> str:
    return dt.datetime.utcnow().isoformat(timespec="microseconds")


# ---------- load / save ----------
def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def load_pdfs(doc_list: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """
    Return {filename: [page_text, …]} using the exact name in the JSON.
    """
    pages = {}
    for doc in doc_list:
        fn = doc["filename"]
        if not os.path.exists(fn):
            raise FileNotFoundError(fn)
        pdf = fitz.open(fn)
        pages[fn] = [p.get_text("text") for p in pdf]
        pdf.close()
    return pages


def dump_output(meta: Dict[str, Any],
                extracted: List[Dict[str, Any]],
                analyses: List[Dict[str, Any]],
                out_path: str) -> None:
    payload = {
        "metadata": meta,
        "extracted_sections": extracted,
        "subsection_analysis": analyses
    }
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)
