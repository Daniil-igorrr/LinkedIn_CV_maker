import os
import sys
import tempfile
import unittest
import json
import subprocess
from pathlib import Path

# Add project root to path so we can import the script
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from scripts.vacancy_parser import parse_vacancies, sanitize_filename

class TestVacancyParser(unittest.TestCase):
    
    def test_single_job(self):
        content = "1) Sales Manager\nDescription..."
        vacancies = parse_vacancies(content)
        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0].title, "Sales Manager")
        self.assertEqual(vacancies[0].content, "1) Sales Manager\nDescription...")
        
    def test_three_numbered_jobs(self):
        content = "1) First Job\nDesc 1\n\n2) Second Job\nDesc 2\n\n3) Third Job\nDesc 3"
        vacancies = parse_vacancies(content)
        self.assertEqual(len(vacancies), 3)
        self.assertEqual(vacancies[0].title, "First Job")
        self.assertEqual(vacancies[1].title, "Second Job")
        self.assertEqual(vacancies[2].title, "Third Job")
        
    def test_explicit_separator(self):
        content = "First Job\nDesc 1\n---JOB---\nSecond Job\nDesc 2"
        vacancies = parse_vacancies(content)
        self.assertEqual(len(vacancies), 2)
        self.assertEqual(vacancies[0].title, "First Job")
        self.assertEqual(vacancies[1].title, "Second Job")
        
    def test_internal_numbered_list(self):
        content = "1) First Job\nRequirements:\n1) Salesforce\n2) HubSpot\n3) English\n\n2) Second Job\nDesc 2"
        vacancies = parse_vacancies(content)
        self.assertEqual(len(vacancies), 2)
        self.assertEqual(vacancies[0].title, "First Job")
        self.assertIn("2) HubSpot", vacancies[0].content)
        self.assertEqual(vacancies[1].title, "Second Job")

    def test_filename_sanitization(self):
        self.assertEqual(sanitize_filename("Senior Sales / Business Development: EMEA?"), "Senior_Sales_Business_Development_EMEA")
        self.assertEqual(sanitize_filename("Responsable Commercial – España"), "Responsable_Commercial_Espana")
        
class TestVacancyParserIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.inbox = self.root / "inbox"
        self.inbox.mkdir()
        self.input_file = self.inbox / "vacancies.txt"
        
        self.script_path = project_root / "scripts" / "vacancy_parser.py"

    def tearDown(self):
        self.temp_dir.cleanup()
        
    def run_parser(self, *args):
        # We need to run it in a way that respects root_dir. 
        # By default vacancy_parser uses project_root.
        # So we can't just pass absolute paths easily unless we test it as a module
        # Wait, vacancy_parser.py uses: root_dir = Path(__file__).resolve().parents[1]
        # And input_path = root_dir / args.input if not Path(args.input).is_absolute() else Path(args.input)
        # So absolute paths work!
        cmd = [sys.executable, str(self.script_path)] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_integration_flow(self):
        # 1. Setup input
        self.input_file.write_text("1) Job A\nDesc A\n\n2) Job B\nDesc B", encoding="utf-8")
        
        # 2. Run parser
        res = self.run_parser("--input", str(self.input_file), "--output", str(self.inbox))
        self.assertEqual(res.returncode, 0)
        
        # 3. Check files
        files = list(self.inbox.glob("*.txt"))
        self.assertEqual(len(files), 3) # input + 2 jobs
        
        job1 = self.inbox / "01_Job_A.txt"
        job2 = self.inbox / "02_Job_B.txt"
        self.assertTrue(job1.exists())
        self.assertTrue(job2.exists())
        
        # 4. Check state
        state_file = self.inbox / ".vacancy_parser_state.json"
        self.assertTrue(state_file.exists())
        
        # 5. Run again (should skip)
        res2 = self.run_parser("--input", str(self.input_file), "--output", str(self.inbox))
        self.assertIn("Nothing to do", res2.stdout)
        
        # 6. Change input and run again
        self.input_file.write_text("1) Job C\nDesc C", encoding="utf-8")
        res3 = self.run_parser("--input", str(self.input_file), "--output", str(self.inbox))
        self.assertIn("Detected:\n1 vacancies", res3.stdout)
        self.assertTrue((self.inbox / "01_Job_C.txt").exists())

    def test_dry_run(self):
        self.input_file.write_text("1) Job A\nDesc A", encoding="utf-8")
        res = self.run_parser("--input", str(self.input_file), "--output", str(self.inbox), "--dry-run")
        self.assertIn("No files were created (--dry-run)", res.stdout)
        self.assertFalse((self.inbox / "01_Job_A.txt").exists())

    def test_duplicate_titles(self):
        self.input_file.write_text("1) Sales\nDesc A\n\n2) Sales\nDesc B", encoding="utf-8")
        res = self.run_parser("--input", str(self.input_file), "--output", str(self.inbox))
        self.assertTrue((self.inbox / "01_Sales.txt").exists())
        self.assertTrue((self.inbox / "02_Sales.txt").exists())

if __name__ == '__main__':
    unittest.main()
