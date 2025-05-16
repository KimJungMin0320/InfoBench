import pandas as pd
import json

# 엑셀 파일 불러오기 (예: 'data.xlsx')
# df = pd.read_excel("data.xlsx")

# 혹은 TSV 파일이라면:
# df = pd.read_csv("data.tsv", sep="\t")

# 예를 들어 TSV 파일을 사용하는 경우
df = pd.read_excel("KoInFoBench.xlsx")

# 각 행을 dict로 변환 후 리스트로 만들기
json_list = df.to_dict(orient="records")

# JSON 문자열로 출력 (가독성 위해 indent 추가)
json_str = json.dumps(json_list, indent=2, ensure_ascii=False)

# 필요하면 파일로 저장도 가능
with open("KoInFoBench.json", "w", encoding="utf-8") as f:
    f.write(json_str)
