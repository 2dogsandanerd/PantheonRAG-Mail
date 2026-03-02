"""
Tests for DataTypeDetector (Phase 7).

Tests automatic file type detection and ingestion strategy recommendation.
"""

import pytest
import tempfile
from pathlib import Path
import pandas as pd

from src.services.data_type_detector import DataTypeDetector, DataType, detect_file_type


class TestDataTypeEnum:
    """Test DataType enumeration."""

    def test_data_type_values(self):
        """Test that all expected data types exist."""
        assert DataType.UNSTRUCTURED_TEXT.value == "unstructured_text"
        assert DataType.STRUCTURED_TABLE.value == "structured_table"
        assert DataType.CODE.value == "code"
        assert DataType.EMAIL.value == "email"
        assert DataType.UNKNOWN.value == "unknown"


class TestDataTypeDetector:
    """Test DataTypeDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a DataTypeDetector instance."""
        return DataTypeDetector()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    # === Email Detection Tests ===

    def test_detect_eml_file(self, detector, temp_dir):
        """Test detection of .eml files."""
        eml_file = temp_dir / "test.eml"
        eml_file.write_text("From: test@example.com\nSubject: Test\n\nBody")

        result = detector.detect(str(eml_file))
        assert result == DataType.EMAIL

    def test_detect_mbox_file(self, detector, temp_dir):
        """Test detection of .mbox files."""
        mbox_file = temp_dir / "archive.mbox"
        mbox_file.write_text("From test@example.com")

        result = detector.detect(str(mbox_file))
        assert result == DataType.EMAIL

    # === Code Detection Tests ===

    def test_detect_python_file(self, detector, temp_dir):
        """Test detection of .py files."""
        py_file = temp_dir / "script.py"
        py_file.write_text("def hello():\n    print('Hello')")

        result = detector.detect(str(py_file))
        assert result == DataType.CODE

    def test_detect_javascript_file(self, detector, temp_dir):
        """Test detection of .js files."""
        js_file = temp_dir / "app.js"
        js_file.write_text("function hello() { console.log('Hello'); }")

        result = detector.detect(str(js_file))
        assert result == DataType.CODE

    def test_detect_typescript_file(self, detector, temp_dir):
        """Test detection of .ts files."""
        ts_file = temp_dir / "app.ts"
        ts_file.write_text("const greeting: string = 'Hello';")

        result = detector.detect(str(ts_file))
        assert result == DataType.CODE

    # === Table Detection Tests ===

    def test_detect_excel_with_table(self, detector, temp_dir):
        """Test detection of Excel file with real table data."""
        excel_file = temp_dir / "data.xlsx"

        # Create a real table (3 columns, 5 rows)
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Age': [25, 30, 35, 40, 45],
            'City': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt']
        })
        df.to_excel(excel_file, index=False)

        result = detector.detect(str(excel_file))
        assert result == DataType.STRUCTURED_TABLE

    def test_detect_csv_with_table(self, detector, temp_dir):
        """Test detection of CSV file with real table data."""
        csv_file = temp_dir / "data.csv"

        # Create a real table
        df = pd.DataFrame({
            'Product': ['A', 'B', 'C'],
            'Price': [10, 20, 30],
            'Stock': [100, 200, 300]
        })
        df.to_csv(csv_file, index=False)

        result = detector.detect(str(csv_file))
        assert result == DataType.STRUCTURED_TABLE

    def test_detect_excel_with_insufficient_structure(self, detector, temp_dir):
        """Test Excel file with only 1 column (not a real table)."""
        excel_file = temp_dir / "single_column.xlsx"

        # Only 1 column → Not a table
        df = pd.DataFrame({'Notes': ['Line 1', 'Line 2', 'Line 3']})
        df.to_excel(excel_file, index=False)

        result = detector.detect(str(excel_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    def test_detect_csv_with_single_row(self, detector, temp_dir):
        """Test CSV with only 1 data row (header + 1 row = not enough)."""
        csv_file = temp_dir / "single_row.csv"

        # Only 1 data row → Not a table
        df = pd.DataFrame({'Col1': [1], 'Col2': [2]})
        df.to_csv(csv_file, index=False)

        result = detector.detect(str(csv_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    # === Unstructured Text Detection Tests ===

    def test_detect_pdf_file(self, detector, temp_dir):
        """Test detection of PDF files (Docling-supported)."""
        pdf_file = temp_dir / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")  # Minimal PDF header

        result = detector.detect(str(pdf_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    def test_detect_docx_file(self, detector, temp_dir):
        """Test detection of .docx files."""
        docx_file = temp_dir / "document.docx"
        docx_file.write_text("Sample content")

        result = detector.detect(str(docx_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    def test_detect_markdown_file(self, detector, temp_dir):
        """Test detection of .md files."""
        md_file = temp_dir / "README.md"
        md_file.write_text("# Heading\n\nContent")

        result = detector.detect(str(md_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    def test_detect_txt_file(self, detector, temp_dir):
        """Test detection of .txt files."""
        txt_file = temp_dir / "notes.txt"
        txt_file.write_text("Plain text content")

        result = detector.detect(str(txt_file))
        assert result == DataType.UNSTRUCTURED_TEXT

    # === Unknown File Type Tests ===

    def test_detect_unknown_extension(self, detector, temp_dir):
        """Test detection of unsupported file type."""
        unknown_file = temp_dir / "data.xyz"
        unknown_file.write_text("Unknown format")

        result = detector.detect(str(unknown_file))
        assert result == DataType.UNKNOWN

    def test_detect_nonexistent_file(self, detector):
        """Test detection of non-existent file."""
        result = detector.detect("/nonexistent/file.pdf")
        assert result == DataType.UNKNOWN

    # === Strategy Recommendation Tests ===

    def test_get_recommended_strategy_for_text(self, detector):
        """Test strategy recommendation for unstructured text."""
        strategy = detector.get_recommended_strategy(DataType.UNSTRUCTURED_TEXT)
        assert strategy == "vector"

    def test_get_recommended_strategy_for_table(self, detector):
        """Test strategy recommendation for structured table."""
        strategy = detector.get_recommended_strategy(DataType.STRUCTURED_TABLE)
        assert strategy == "pandas_agent"

    def test_get_recommended_strategy_for_code(self, detector):
        """Test strategy recommendation for code."""
        strategy = detector.get_recommended_strategy(DataType.CODE)
        assert strategy == "hybrid"

    def test_get_recommended_strategy_for_email(self, detector):
        """Test strategy recommendation for email."""
        strategy = detector.get_recommended_strategy(DataType.EMAIL)
        assert strategy == "vector"

    # === Full Analysis Tests ===

    def test_analyze_returns_complete_info(self, detector, temp_dir):
        """Test that analyze() returns all expected fields."""
        py_file = temp_dir / "test.py"
        py_file.write_text("print('test')")

        analysis = detector.analyze(str(py_file))

        assert "file_path" in analysis
        assert "file_name" in analysis
        assert analysis["file_name"] == "test.py"
        assert "extension" in analysis
        assert analysis["extension"] == ".py"
        assert "data_type" in analysis
        assert analysis["data_type"] == "code"
        assert "index_strategy" in analysis
        assert analysis["index_strategy"] == "hybrid"
        assert "mime_type" in analysis

    def test_analyze_excel_table(self, detector, temp_dir):
        """Test full analysis of Excel table."""
        excel_file = temp_dir / "customers.xlsx"

        df = pd.DataFrame({
            'Customer': ['A', 'B', 'C'],
            'Revenue': [1000, 2000, 3000]
        })
        df.to_excel(excel_file, index=False)

        analysis = detector.analyze(str(excel_file))

        assert analysis["data_type"] == "structured_table"
        assert analysis["index_strategy"] == "pandas_agent"
        assert analysis["file_name"] == "customers.xlsx"

    # === Convenience Function Tests ===

    def test_convenience_function(self, temp_dir):
        """Test the convenience detect_file_type() function."""
        py_file = temp_dir / "test.py"
        py_file.write_text("def test(): pass")

        result = detect_file_type(str(py_file))
        assert result == DataType.CODE


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def detector(self):
        return DataTypeDetector()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_empty_csv_file(self, detector, temp_dir):
        """Test detection of empty CSV file."""
        csv_file = temp_dir / "empty.csv"
        csv_file.write_text("")

        result = detector.detect(str(csv_file))
        # Should handle gracefully and return UNSTRUCTURED_TEXT or UNKNOWN
        assert result in [DataType.UNSTRUCTURED_TEXT, DataType.UNKNOWN]

    def test_corrupted_excel(self, detector, temp_dir):
        """Test detection of corrupted Excel file."""
        excel_file = temp_dir / "corrupted.xlsx"
        excel_file.write_text("Not a real Excel file")

        result = detector.detect(str(excel_file))
        # Should handle gracefully
        assert result == DataType.UNSTRUCTURED_TEXT

    def test_excel_with_multiple_sheets(self, detector, temp_dir):
        """Test Excel with multiple sheets (should still work)."""
        excel_file = temp_dir / "multi_sheet.xlsx"

        # pandas.to_excel creates single sheet by default
        # For multi-sheet, use ExcelWriter
        with pd.ExcelWriter(excel_file) as writer:
            pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_excel(writer, sheet_name='Sheet1', index=False)
            pd.DataFrame({'C': [5, 6], 'D': [7, 8]}).to_excel(writer, sheet_name='Sheet2', index=False)

        result = detector.detect(str(excel_file))
        # Should read first sheet and detect as table
        assert result == DataType.STRUCTURED_TABLE
