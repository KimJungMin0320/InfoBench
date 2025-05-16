import pandas as pd
import json
import ast

# 파일 경로 설정
excel_file = 'KoInFoBench.xlsx'
json_file = 'KoInFoBench.json'
output_file = 'updated.json'

# 엑셀에서 decomposed_questions 컬럼 읽기
df = pd.read_excel(excel_file)

# 문자열 -> 리스트로 안전하게 파싱
decomposed_questions_list = df['decomposed_questions'].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else []
).tolist()

# 기존 JSON 로드
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 길이 일치 확인
if len(data) != len(decomposed_questions_list):
    raise ValueError("엑셀과 JSON의 길이가 다릅니다!")

# 각 항목에 리스트 형태로 필드 추가
for i, item in enumerate(data):
    item['decomposed_questions'] = decomposed_questions_list[i]

# 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"업데이트된 JSON이 저장되었습니다: {output_file}")
