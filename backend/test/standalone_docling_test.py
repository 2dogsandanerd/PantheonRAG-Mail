import os
from pathlib import Path
import docling
import time

# Define directories
INPUT_DIR = Path(__file__).parent / "test_data" / "docling_samples"
OUTPUT_DIR = Path(__file__).parent / "test_data" / "docling_output"

# Define supported file extensions based on our test data
SUPPORTED_EXTENSIONS = [".txt", ".md", ".csv"]

# --- Performance Benchmark ---
# Add larger files here for a real benchmark. For now, we test with what we have.
# e.g., BENCHMARK_FILES = ["large_document.pdf", "complex_report.docx"]
BENCHMARK_FILES = []


def main():
    """
    Processes documents in the input directory using Docling, saves
    the structured output, and performs a simple performance benchmark.
    """
    print(f"Starting document processing test...")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("Output directory created or already exists.")

    # Initialize Docling
    try:
        from docling.document_converter import DocumentConverter

        engine = DocumentConverter()
        print("Docling DocumentConverter initialized successfully.")
    except Exception as e:
        print(f"FATAL: Error initializing Docling engine: {e}")
        return

    processed_files = 0
    skipped_files = 0
    total_time = 0

    # Iterate over files in the input directory
    all_files = list(INPUT_DIR.iterdir())
    print(f"\nFound {len(all_files)} files to check.")

    for file_path in all_files:
        if file_path.is_file():
            print(f"\n--- Analyzing file: {file_path.name} ---")

            # --- File Type Validation (Task 1.3) ---
            if file_path.suffix not in SUPPORTED_EXTENSIONS:
                print(f"Skipping file: Unsupported extension '{file_path.suffix}'.")
                skipped_files += 1
                continue

            try:
                print(f"Processing '{file_path.name}'...")

                # --- Performance Measurement (Task 1.5) ---
                start_time = time.time()

                # Process the document with Docling
                result = engine.convert(str(file_path))

                # Get the structured output as Markdown
                markdown_output = result.document.export_to_markdown()

                end_time = time.time()
                duration = end_time - start_time
                total_time += duration

                print(f"Processing took {duration:.4f} seconds.")

                # Define the output path
                output_filename = f"{file_path.name}.md"
                output_path = OUTPUT_DIR / output_filename

                # Save the Markdown output
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown_output)

                print(f"Successfully processed and saved to '{output_path}'")
                processed_files += 1

            except Exception as e:
                print(f"ERROR processing file {file_path.name}: {e}")
                skipped_files += 1

    print("\n========================================")
    print("           PROCESSING SUMMARY")
    print("========================================")
    print(f"Successfully processed files: {processed_files}")
    print(f"Skipped / Errored files:    {skipped_files}")
    print(f"Total processing time:      {total_time:.4f} seconds")
    if processed_files > 0:
        print(f"Average time per file:      {total_time / processed_files:.4f} seconds")
    print("========================================")
    print("\nPlease check the output files in the 'docling_output' directory.")


if __name__ == "__main__":
    main()
