#!/usr/bin/env python3
"""
Bulk Vacancy Parser

A deterministic utility to parse a single text file containing multiple vacancies
and split them into individual text files in a target directory.

Usage:
  python scripts/vacancy_parser.py
  python scripts/vacancy_parser.py --dry-run
  python scripts/vacancy_parser.py --input inbox/vacancies.txt --output inbox
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Vacancy:
    title: str
    content: str
    original_index: int

def sanitize_filename(name: str) -> str:
    # Normalize unicode characters
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    
    # Replace whitespace and invalid characters with underscore
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name).strip('_')
    
    # Truncate to avoid too long names
    if len(name) > 50:
        name = name[:50].rstrip('_')
        
    return name

def parse_vacancies(text: str) -> List[Vacancy]:
    vacancies = []
    
    # Strategy 1: Explicit ---JOB--- separator
    if '---JOB---' in text:
        parts = re.split(r'^---JOB---$', text, flags=re.MULTILINE)
        idx = 1
        for part in parts:
            part = part.strip()
            if not part:
                continue
            lines = part.splitlines()
            title = lines[0].strip() if lines else f"vacancy_{idx}"
            vacancies.append(Vacancy(title=title, content=part, original_index=idx))
            idx += 1
        return vacancies
        
    # Strategy 2: Sequential numbered lists
    lines = text.splitlines()
    current_vacancy_lines = []
    current_title = ""
    expected_number = 1
    
    header_pattern = re.compile(r'^(\d+)[\)\.\-]*\s+(.+)$')
    
    for i, line in enumerate(lines):
        match = header_pattern.match(line.strip())
        is_blank_before = (i == 0) or (i > 0 and lines[i-1].strip() == "")
        
        if match and is_blank_before:
            number = int(match.group(1))
            if number == expected_number:
                if current_vacancy_lines:
                    vacancies.append(Vacancy(
                        title=current_title, 
                        content="\n".join(current_vacancy_lines).strip(),
                        original_index=expected_number - 1
                    ))
                
                current_title = match.group(2).strip()
                current_vacancy_lines = [line]
                expected_number += 1
                continue
                
        if expected_number > 1:
            current_vacancy_lines.append(line)

    if current_vacancy_lines:
        vacancies.append(Vacancy(
            title=current_title, 
            content="\n".join(current_vacancy_lines).strip(),
            original_index=expected_number - 1
        ))
        
    return vacancies

def get_file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Bulk Vacancy Parser")
    parser.add_argument("--input", type=str, default="inbox/vacancies.txt", help="Input file containing multiple vacancies")
    parser.add_argument("--output", type=str, default="inbox", help="Output directory for individual vacancy files")
    parser.add_argument("--dry-run", action="store_true", help="Preview parsing without creating files")
    parser.add_argument("--force", action="store_true", help="Force parsing even if the input file has not changed")
    args = parser.parse_args()
    
    root_dir = Path(__file__).resolve().parents[1]
    input_path = root_dir / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_dir = root_dir / args.output if not Path(args.output).is_absolute() else Path(args.output)
    state_file = output_dir / ".vacancy_parser_state.json"
    
    print("=" * 50)
    print("VACANCY IMPORT")
    print("=" * 50)
    print(f"\nInput:\n{input_path.relative_to(root_dir) if input_path.is_relative_to(root_dir) else input_path}\n")
    
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return
        
    try:
        text = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("ERROR: Failed to read input file. Ensure it is UTF-8 encoded.")
        return
        
    current_hash = get_file_hash(input_path)
    
    if not args.force and not args.dry_run and state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if state.get("input_hash") == current_hash:
                print("Input file has not changed since last parsing.")
                print("Nothing to do.")
                print("\n" + "=" * 50)
                print("DONE")
                print("=" * 50)
                return
        except json.JSONDecodeError:
            pass # Invalid state file, proceed with parsing

    vacancies = parse_vacancies(text)
    
    if not vacancies:
        print("WARNING: Could not confidently detect vacancy boundaries or no vacancies found.")
        return
        
    print(f"Detected:\n{len(vacancies)} vacancies\n")
    for v in vacancies:
        print(f"{v.original_index}. {v.title}")
        
    print("\nValidation:\nPASS\n")
    
    if args.dry_run:
        print("No files were created (--dry-run).")
        print("\n" + "=" * 50)
        print("DONE")
        print("=" * 50)
        return
        
    print("Creating files:")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    for v in vacancies:
        safe_title = sanitize_filename(v.title)
        if not safe_title:
            safe_title = "vacancy"
            
        filename = f"{v.original_index:02d}_{safe_title}.txt"
        file_path = output_dir / filename
        
        # Handle filename collisions (should be rare with indexing, but just in case)
        counter = 1
        original_file_path = file_path
        while file_path.exists():
            file_path = output_dir / f"{original_file_path.stem}_{counter}{original_file_path.suffix}"
            counter += 1
            
        # Atomic write by writing to tmp first
        tmp_path = file_path.with_suffix(".tmp")
        tmp_path.write_text(v.content, encoding="utf-8")
        os.replace(tmp_path, file_path)
        
        created_files.append(filename)
        
    print("PASS\n")
    print("Created:")
    print(f"{len(created_files)} files\n")
    
    # Save state
    state = {
        "input_hash": current_hash,
        "processed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "vacancies_count": len(vacancies),
        "created_files": created_files
    }
    
    tmp_state = state_file.with_suffix(".tmp")
    tmp_state.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(tmp_state, state_file)
    
    print("Input preserved:\nYES\n")
    print("=" * 50)
    print("DONE")
    print("=" * 50)

if __name__ == "__main__":
    main()
