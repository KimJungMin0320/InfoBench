import json
import ast

input_path = 'evaluation/gpt-4/KoInFoBench.json_DecomposeEval.json'
output_path = 'evaluation/gpt-4/KoInFoBench_DecomposeEval_.json'

fixed_data = []

# 파일 열기
with open(input_path, 'r', encoding='utf-8') as f:
    # {} {} {} 형태면 한 줄씩 파싱
    raw_lines = f.read().strip().split('\n')
    for line in raw_lines:
        if not line.strip():
            continue
        item = json.loads(line)

        ql_raw = item.get('question_label')
        if isinstance(ql_raw, str):
            try:
                # 문자열을 리스트로 안전하게 변환
                ql_parsed = ast.literal_eval(ql_raw)

                # 리스트 안의 요소들을 ""로 감싸기 위해 재구성
                fixed_ql = [[str(elem).replace("'", '"') for elem in sublist] for sublist in ql_parsed]

                # 실제 JSON 리스트로 저장
                item['question_label'] = fixed_ql
            except Exception as e:
                print(f"Error parsing question_label: {ql_raw}\n{e}")
        
        fixed_data.append(item)

# 결과 저장
with open(output_path, 'w', encoding='utf-8') as f:
    for item in fixed_data:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')

print(f"변환된 JSON이 '{output_path}'로 저장되었습니다.")
