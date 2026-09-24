import json, sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open(r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\challenges.json', encoding='utf-8'))
ch = data if isinstance(data, list) else data.get('Challenges', data.get('data', []))

filtered = [c for c in ch if c.get('unit') in range(3031, 3040)]
for c in sorted(filtered, key=lambda x: (x['unit'], x['id'])):
    print(f"Unit {c['unit']} | ID {c['id']} | UID {c['uid']} | {c['name']}")
