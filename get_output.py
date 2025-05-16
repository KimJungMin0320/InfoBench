from datasets import load_dataset, Dataset

import os
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

import json

# dataset = load_dataset("kqsong/InFoBench")
# train = dataset['train']

with open('KoInFoBench.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
train = Dataset.from_list(data)

# json field
id = train['id']
input = train['input']
category = train['category']
instruction = train['instruction']
decomposed_questions = train['decomposed_questions']
subset = train['subset']
question_label = train['question_label']

output = []
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4"
for i in tqdm(range(len(instruction))):
    USER_INPUT_MSG = f"input:\n\"{input[i]}\"\n\ninstruction:\n\"{instruction[i]}\""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_INPUT_MSG}, 
            # {"role": "assistant", "content": "Who's there?"},
        ],
        temperature=0,
    )
    output.append(response.choices[0].message.content)
    
print(len(instruction))
print(len(output))

with open("KoInFoBench_out.json", "w", encoding="utf-8") as f:
    for i in range(len(instruction)):
        json.dump({
                    "id": id[i],
                    "input": input[i],
                    "category": category[i],
                    "instruction": instruction[i],
                    "decomposed_questions": decomposed_questions[i],
                    "subset": subset[i],
                    "question_label": question_label[i],
                    "output": output[i],
                }, f, ensure_ascii=False)
        f.write("\n")