import os
from pathlib import Path
from main import main as process_collection

INPUT_ROOT = Path("input")
OUTPUT_ROOT = Path("output")

def run_all_collections():
    for folder in INPUT_ROOT.iterdir():
        if folder.is_dir() and (folder / "challenge1b_input.json").exists():
            input_path = folder / "challenge1b_input.json"

        
            output_folder = OUTPUT_ROOT / folder.name
            output_folder.mkdir(parents=True, exist_ok=True)
            output_path = output_folder / "challenge1b_output.json"

            print(f"\n Processing {folder.name} ...")
            process_collection(str(input_path), str(output_path))

if __name__ == "__main__":
    run_all_collections()
