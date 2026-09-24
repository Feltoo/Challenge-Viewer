import os
import json
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--markdown", nargs="+", help="Markdown files to process")
args = parser.parse_args()
MD_FILES = args.markdown if args.markdown else []

QBANK_DIR = r"c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\qbank"
CHALLENGES_FILE = r"c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\challenges.json"

def parse_markdowns():
    answers = {} # unit -> challenge_name (lower) -> diff (lower) -> step -> answer_text
    
    for file_path in MD_FILES:
        if not os.path.exists(file_path):
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_unit = None
        current_challenge = None
        current_diff = None
        current_step = None
        
        in_code_block = False
        current_answer_buf = []
        
        for line in lines:
            line_str = line.strip()
            
            # Match Unit
            unit_match = re.match(r'^#\s+UNIT\s+(\d+)', line_str, re.IGNORECASE)
            if unit_match:
                current_unit = int(unit_match.group(1))
                if current_unit not in answers:
                    answers[current_unit] = {}
                continue
                
            # Match Challenge
            ch_match = re.match(r'^##\s+(?:Challenge\s+\d+:\s+)?(.*)', line_str, re.IGNORECASE)
            if ch_match:
                current_challenge = ch_match.group(1).strip().lower()
                if current_unit:
                    if current_challenge not in answers[current_unit]:
                        answers[current_unit][current_challenge] = {'easy': {}, 'moderate': {}, 'hard': {}}
                continue
                
            # Match Difficulty
            diff_match = re.match(r'^###\s+(.*)', line_str, re.IGNORECASE)
            if diff_match:
                group = diff_match.group(1).strip().lower()
                if 'all' in group:
                    current_diff = 'all'
                elif 'and' in group or '/' in group:
                    current_diff = 'mod_hard'
                else:
                    current_diff = group
                continue
                
            # Match Step
            step_match = re.match(r'^(?:\*\*|####\s+)Step\s+(\d+).*?(?:\*\*|$)', line_str, re.IGNORECASE)
            if step_match:
                current_step = int(step_match.group(1))
                current_answer_buf = [] # Reset buffer
                
                # Check for "Same as" on the same line
                same_as_match = re.search(r'Same as (Easy|Moderate) Step (\d+)', line_str, re.IGNORECASE)
                if same_as_match:
                    ref_diff = same_as_match.group(1).lower()
                    ref_step = int(same_as_match.group(2))
                    if current_unit and current_challenge:
                        diffs = []
                        if current_diff == 'all':
                            diffs = ['easy', 'moderate', 'hard']
                        elif current_diff == 'mod_hard':
                            diffs = ['moderate', 'hard']
                        else:
                            diffs = [current_diff]
                        for d in diffs:
                            if ref_diff in answers[current_unit][current_challenge] and ref_step in answers[current_unit][current_challenge][ref_diff]:
                                answers[current_unit][current_challenge][d][current_step] = answers[current_unit][current_challenge][ref_diff][ref_step]
                continue
                
            # Match Step range like **Steps 1-3:** Same as Easy Steps 1-3.
            step_range_match = re.match(r'^\*\*Steps\s+(\d+)-(\d+).*?\*\*', line_str, re.IGNORECASE)
            if step_range_match:
                start = int(step_range_match.group(1))
                end = int(step_range_match.group(2))
                same_as_match = re.search(r'Same as (Easy|Moderate) Steps', line_str, re.IGNORECASE)
                if same_as_match:
                    ref_diff = same_as_match.group(1).lower()
                    if current_unit and current_challenge:
                        diffs = []
                        if current_diff == 'all':
                            diffs = ['easy', 'moderate', 'hard']
                        elif current_diff == 'mod_hard':
                            diffs = ['moderate', 'hard']
                        else:
                            diffs = [current_diff]
                        for s in range(start, end + 1):
                            for d in diffs:
                                if ref_diff in answers[current_unit][current_challenge] and s in answers[current_unit][current_challenge][ref_diff]:
                                    answers[current_unit][current_challenge][d][s] = answers[current_unit][current_challenge][ref_diff][s]
                continue
            
            # Match Code Block
            if line_str.startswith('```'):
                if in_code_block:
                    in_code_block = False
                    if current_unit and current_challenge and current_diff and current_step:
                        diffs = []
                        if current_diff == 'all':
                            diffs = ['easy', 'moderate', 'hard']
                        elif current_diff == 'mod_hard':
                            diffs = ['moderate', 'hard']
                        else:
                            diffs = [current_diff]
                            
                        for d in diffs:
                            answers[current_unit][current_challenge][d][current_step] = "".join(current_answer_buf)
                else:
                    in_code_block = True
                    current_answer_buf = []
                continue
                
            if in_code_block:
                current_answer_buf.append(line)
                
    return answers

def main():
    answers = parse_markdowns()
        
    with open(CHALLENGES_FILE, 'r', encoding='utf-8') as f:
        ch_data = json.load(f)
        
    if isinstance(ch_data, list):
        challenges = ch_data
    else:
        challenges = ch_data.get("challenges", ch_data)
        
    for ch in challenges:
        unit = ch.get("unitId", ch.get("unit", 0))
        name = ch.get("name", ch.get("title", "")).lower()
        uid = ch.get("uid", ch.get("id", ch.get("_id", "")))
        
        if unit in answers:
            matched_ch_key = None
            for k in answers[unit].keys():
                if k in name or name in k:
                    matched_ch_key = k
                    break
                    
            if matched_ch_key:
                ch_answers = answers[unit][matched_ch_key]
                qbank_path = os.path.join(QBANK_DIR, f"{uid}.json")
                if os.path.exists(qbank_path):
                    with open(qbank_path, 'r', encoding='utf-8') as qf:
                        qdata = json.load(qf)
                        
                    steps_updated = 0
                    for step in qdata.get("steps", []):
                        diff = step.get("difficulty", "").lower()
                        step_id = step.get("step_id", 0)
                        
                        if diff in ch_answers and step_id in ch_answers[diff]:
                            step["answer"] = ch_answers[diff][step_id]
                            steps_updated += 1
                            
                    if steps_updated > 0:
                        with open(qbank_path, 'w', encoding='utf-8') as qf:
                            json.dump(qdata, qf)
                        print(f"Updated {steps_updated} steps for {name} ({uid})")

if __name__ == "__main__":
    main()
