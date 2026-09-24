import json, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

uids = [
    "49c1931a-2a7d-42e6-b09b-58ce114226e1",
    "8e6e7ce6-3e89-4b67-9988-95e1ebe77d7b",
    "fcadcec6-704a-4f44-b041-5597d87e981f",
    "aa2d9a74-e12d-4342-a9df-23db2a809b02",
    "4a990cba-dce9-4aa2-adfb-c2f0ad8e34b8",
    "12b15813-6949-4c59-8221-e463ac4357d8",
    "3e4f33ce-d8be-4ac2-91a2-26c47d684a9e",
    "53a0d5d6-a693-432b-bc2d-523aeaca0ba3",
    "985d4b79-fe22-4018-aa23-7bd5f9ecbdc7",
    "3df9d4e0-1a33-4b7a-a4bb-9f546c6796ef",
    "55610fef-ad9e-404f-8182-0f732626f6cd",
    "0be4039a-abad-463d-9d9c-f886925cbd49",
    "b4d5b493-a4d6-4a79-9b48-bff5d603cb8c",
    "9c05c06e-e748-41d3-b5c8-49929e5e7d23",
    "642bde05-0d8a-4b03-9672-4c693c3b4eba",
    "a409ab49-ea3b-45e4-9b38-699c988996f4",
    "35cbcb8f-2217-42ea-930f-9b0e238f1921",
    "709118f8-a97b-4b65-b638-52f8d5e7cb9e",
    "0efd98f5-e0d6-4168-bb98-cc3129db71d8",
    "b9799c58-b746-4072-b70c-046c95d566c2",
    "913bd1f8-cda5-4614-aec8-72320839f114",
    "c0086b5f-e0c9-47c1-9643-5378fd54d0dd",
    "e2708fb5-8e5a-4e10-b830-86931d5e9437",
    "2b352d66-20d1-42a0-b6fd-380b9c8d1422",
    "b5a70556-a473-486f-bf61-90f5875e7b43",
    "7aa3977b-5779-4be9-b8c6-b02fa95d31f9",
    "da721615-fa6e-40af-a5d5-325babc6825d",
    "f22ee1b3-e9dd-4f64-9041-e8ffa95b80b1",
    "af3c6413-4815-4600-9e85-13aca7537c97",
    "410f51f5-21f5-44f1-9ab7-a3da7b81f4c6",
    "9cc88fed-90a0-4412-9d78-52cd23a25fba",
    "feb44623-47e0-4928-a581-a65b07204347",
    "59e61432-8709-43b4-8b65-e548018c8794",
    "a9698af4-a550-4300-97f8-4a1a736ea7fb",
    "b9440dbf-30a4-4f03-86e2-8247a3ad55ca",
    "f6b1a658-721b-4fbc-b281-465611058487",
    "f1ef8c33-e205-4ad4-8b80-31d7f5fb5393",
    "ad507aef-933f-4ad0-a7ad-fe3675b29f98",
    "497c2633-a469-4870-ac9e-f15aff986c17",
    "6de55c75-68d4-465a-af7e-e0fefa89485b",
    "f58de9db-bff3-4b42-bbff-abe5e40498e7",
    "0e2f4016-d321-44d1-b58c-687605d50274",
    "2a662078-93db-4869-970d-b0964127ee16",
    "8541d6a0-a3e1-4cc4-9c6e-72b4a6385ac7",
    "6612bc29-1b61-45f0-b2a9-7ddb378a9115",
]

qbank_dir = r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\qbank'
out = open(r'c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\questions_output.txt', 'w', encoding='utf-8')

for uid in uids:
    fpath = os.path.join(qbank_dir, uid + '.json')
    if os.path.exists(fpath):
        data = json.load(open(fpath, encoding='utf-8'))
        name = data.get('challenge_name', 'Unknown')
        unit = data.get('unit', '?')
        steps = data.get('steps', [])
        out.write(f"\n{'='*80}\n")
        out.write(f"CHALLENGE: {name} (Unit {unit}, UID: {uid})\n")
        out.write(f"{'='*80}\n")
        for s in steps:
            diff = s.get('difficulty', '?')
            sid = s.get('step_id', '?')
            desc = s.get('description', 'No description')
            clean = re.sub(r'<[^>]+>', ' ', desc)
            clean = re.sub(r'\s+', ' ', clean).strip()
            clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            quiz = s.get('quiz', '')
            if quiz:
                quiz_clean = re.sub(r'<[^>]+>', ' ', str(quiz))
                quiz_clean = re.sub(r'\s+', ' ', quiz_clean).strip()
            else:
                quiz_clean = ''
            out.write(f"\n  [{diff.upper()}] Step {sid}:\n")
            out.write(f"  DESC: {clean[:800]}\n")
            if quiz_clean:
                out.write(f"  QUIZ: {quiz_clean[:500]}\n")
    else:
        out.write(f"File not found: {uid}\n")

out.close()
print("Done!")
