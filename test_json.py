import json

# 파일 경로 설정
a_path = 'model/KoInFoBench_out.json'  # a.json은 JSON Lines 형식
b_path = 'updated.json'  # b.json은 일반 JSON 리스트 형식
output_path = 'a_updated.json'

# b.json에서 id -> decomq 매핑 만들기
decomq_map_b = {}
with open(b_path, 'r', encoding='utf-8') as f:
    b_data = json.load(f)

    # b_data에서 id와 decomq를 매핑
    for item in b_data:
        decomq_map_b[item['id']] = item['decomposed_questions']

# a.json에서 decomq 값을 b.json의 값으로 덮어쓰기
updated_a_data = []
with open(a_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            a_item = json.loads(line)  # a.json의 각 항목
            item_id = a_item.get('id')
            
            # b.json에서 해당 id에 대응하는 decomq가 있으면 덮어쓰기
            if item_id in decomq_map_b:
                a_item['decomposed_questions'] = decomq_map_b[item_id]  # b의 decomq로 덮어씀

            updated_a_data.append(a_item)

# 수정된 a.json 저장
with open(output_path, 'w', encoding='utf-8') as f:
    for item in updated_a_data:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')  # 각 항목을 새로운 줄로 구분

print(f"a.json이 업데이트되어 {output_path}로 저장되었습니다.")