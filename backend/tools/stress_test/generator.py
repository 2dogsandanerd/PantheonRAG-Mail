import os
import random
import time
from pathlib import Path
from fpdf import FPDF

class DataGenerator:
    """Generates synthetic test data for stress testing."""
    
    def __init__(self, output_dir: str = "./test_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def generate_dummy_pdf(self, filename: str, pages: int = 1) -> str:
        """Create a simple PDF with random text."""
        pdf = FPDF()
        for _ in range(pages):
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Add some "business" content
            lines = [
                f"Confidential Report - {random.randint(1000, 9999)}",
                f"Date: {time.strftime('%Y-%m-%d')}",
                "Subject: Stress Test Analysis",
                "",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                f"Random Value: {random.random() * 1000:.2f} EUR",
                "End of page."
            ]
            
            for line in lines:
                pdf.cell(200, 10, txt=line, ln=1, align='L')
                
        output_path = self.output_dir / filename
        pdf.output(str(output_path))
        return str(output_path)

    def create_batch(self, count: int = 10) -> list[str]:
        """Generate a batch of PDF files."""
        print(f"🏭 Generating {count} dummy PDFs in {self.output_dir}...")
        files = []
        for i in range(count):
            name = f"stress_test_{int(time.time())}_{i}.pdf"
            path = self.generate_dummy_pdf(name, pages=random.randint(1, 3))
            files.append(path)
        return files

    def cleanup(self):
        """Remove generated files."""
        print("🧹 Cleaning up test data...")
        for f in self.output_dir.glob("stress_test_*.pdf"):
            f.unlink()
        self.output_dir.rmdir()

if __name__ == "__main__":
    # Test run
    gen = DataGenerator()
    files = gen.create_batch(5)
    print(f"Created: {files}")
    gen.cleanup()
