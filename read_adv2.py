import json, os, re

CHALLENGES_FILE = r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\challenges.json'
QBANK_DIR = r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\qbank'
OUT_FILE = r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\advanced2_questions.txt'

def main():
    # Load all challenges
    with open(CHALLENGES_FILE, 'r', encoding='utf-8') as f:
        ch_data = json.load(f)
        
    challenges = ch_data.get("challenges", ch_data) if isinstance(ch_data, dict) else ch_data
    
    # Filter 3040 to 3047
    adv2_challenges = [ch for ch in challenges if 3040 <= int(ch.get("unitId", ch.get("unit", 0))) <= 3047]
    
    # Sort by unit, then step/order (not strictly necessary but good for readability)
    adv2_challenges.sort(key=lambda x: (int(x.get("unitId", x.get("unit", 0))), int(x.get("step", x.get("order", 0)))))
    
    with open(OUT_FILE, 'w', encoding='utf-8') as out:
        for ch in adv2_challenges:
            uid = ch.get("uid", ch.get("id", ch.get("_id", "")))
            name = ch.get("name", ch.get("title", "Unknown"))
            unit = ch.get("unitId", ch.get("unit", 0))
            
            fpath = os.path.join(QBANK_DIR, f"{uid}.json")
            if os.path.exists(fpath):
                data = json.load(open(fpath, encoding='utf-8'))
                steps = data.get('steps', [])
                out.write(f"\n{'='*80}\n")
                out.write(f"CHALLENGE: {name} (Unit {unit}, UID: {uid})\n")
                out.write(f"{'='*80}\n")
                
                for s in steps:
                    diff = s.get('difficulty', '?')
                    sid = s.get('step_id', '?')
                    desc = s.get('description', 'No description')
                    
                    # Clean up HTML tags
                    clean = re.sub(r'<[^>]+>', ' ', desc)
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    
                    quiz = s.get('quiz', '')
                    quiz_clean = ''
                    if quiz:
                        quiz_clean = re.sub(r'<[^>]+>', ' ', str(quiz))
                        quiz_clean = re.sub(r'\s+', ' ', quiz_clean).strip()
                        
                    out.write(f"\n  [{diff.upper()}] Step {sid}:\n")
                    out.write(f"  DESC: {clean}\n")
                    if quiz_clean:
                        out.write(f"  QUIZ: {quiz_clean}\n")
            else:
                out.write(f"File not found: {uid}\n")
                
    print(f"Done! Wrote {len(adv2_challenges)} challenges to {OUT_FILE}")

if __name__ == '__main__':
    main()
