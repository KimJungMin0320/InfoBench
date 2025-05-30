import json
import os
import time
import tiktoken
import argparse

from os.path import join,exists
from openai import OpenAI
from tqdm import tqdm

from transformers import AutoTokenizer

encoder = tiktoken.get_encoding("cl100k_base")

# SYS_MSG ="Based on the provided Input (if any) and Generated Text, answer the ensuing Questions with either a YES or NO choice.\
#     Your selection should be based on your judgment as well as the following rules:\n\n\
#         - YES: Select 'YES' if the generated text entirely fulfills the condition specified in the question.\
#             However, note that even minor inaccuracies exclude the text from receiving a 'YES' rating.\
#             As an illustration. consider a question that asks.\
#                 \"Does each sentence in the generated text use a second person?”\
#             If even one sentence does not use the second person, the answer should NOT be 'YES'.\
#             To qualify for a 'YES' rating, the generated text must be entirely accurate and relevant to the question\n\n\
#         - NO: Opt for 'NO' if the generated text fails to meet the question's requirements or provides no information that could be utilized to answer the question. \
#             For instance, if the question asks. \
#             \"Is the second sentence in the generated text a compound sentence?\" and the generated text only has one sentence. \
#             it offers no relevant information to answer the question. Consequently, the answer should be 'NO'.'''"
            
SYS_MSG = "주어진 입력(있는 경우)과 생성된 텍스트를 바탕으로, 이어지는 질문들에 대해 YES 또는 NO로 답하십시오.\
        선택은 judge의 판단뿐만 아니라 다음 규칙에 따라 이루어져야 합니다.\
        - YES: 생성된 텍스트가 질문에서 명시한 조건을 완전히 충족할 경우 'YES'를 선택합니다.\
            단, 사소한 부정확성이라도 있을 경우, 해당 텍스트는 'YES' 평가 대상에서 제외됩니다.\
            예를 들어, 질문이\
            \"생성된 텍스트의 모든 문장이 2인칭을 사용하고 있습니까?\"\
            라고 묻는다면, 하나의 문장이라도 2인칭을 사용하지 않았다면 'YES'를 선택해서는 안 됩니다.\
            모든 조건이 완전히 정확하고 질문에 부합해야 'YES'로 평가할 수 있습니다.\
        - NO: 생성된 텍스트가 질문의 요구사항을 충족하지 못하거나,\
            질문에 답하는 데 사용할 수 있는 정보가 전혀 없는 경우 'NO'를 선택합니다.\
            예를 들어, 질문이\
            \"생성된 텍스트의 두 번째 문장이 복합문(compound sentence)입니까?\"\
            인데, 생성된 텍스트에 문장이 하나만 있다면, 이는 관련 정보를 제공하지 않는 것이므로 'NO'를 선택해야 합니다."

def load_jsonl(file_path):
    "General function to load jsonl file"
    _data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for data in f:
            jline = json.loads(data)
            _data.append(jline)
    return _data

def bool_ratio(fpath):
    "Calculate true false ratio for eval results"
    _data = load_jsonl(fpath)
    count = {"true":0, "false":0}
    for entry in _data:
        if entry.get("eval", None) is None:
            print("Wrong output")
            print(entry['id'])
        if len(entry['decomposed_questions']) != len(entry['eval']):
            print("Wrong length")
            print(entry['id'])
        if None in entry['eval']:
            print("None in eval")
            print(entry['id'])
        
        for eva_value in entry['eval']:
            if eva_value:
                count["true"] += 1
            else:
                count["false"] += 1
    
    print("-------- True False Table --------")
    print(count)
    print(f"Percentage of True: {count['true']/sum(count.values())}")
    return

def truncate_string_by_token_limit(text: str, max_tokens: int, model_name: str = "gpt2") -> str:
            """
            주어진 문자열을 모델 기준 최대 토큰 수만큼 잘라서 반환.
            
            :param text: 원본 문자열
            :param max_tokens: 최대 토큰 수
            :param model_name: 사용할 모델 이름 (토크나이저 로딩용)
            :return: 잘린 문자열
            """
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            token_ids = tokenizer.encode(text, add_special_tokens=False)
            truncated_ids = token_ids[:max_tokens]
            truncated_text = tokenizer.decode(truncated_ids, skip_special_tokens=True)
            return truncated_text

def run_evaluation(client, in_path, o_dir, eval_model="gpt-4-0314", temperature=0):
    """
    Main function to run decomposed questisons evaluation on models' outputs
        in_path: str, path to the model output file
        o_dir: str, path to the output folder
        eval_model: str, default "gpt-4-0314", model name to be used for evaluation
        temperature: float, default 0, temperature to be used for evaluation
    """
    _data = load_jsonl(in_path)
    _model_name = in_path.split('/')[1].split('_')[0]
    
    # ceate output folder if not exists
    _o_dir = join(o_dir, eval_model)
    if not os.path.exists(_o_dir):
        os.makedirs(_o_dir)
                
    _opath = join(_o_dir, f"{_model_name}_DecomposeEval.json")
    
    # load_results if exists
    if os.path.exists(_opath):
        _exist = load_jsonl(_opath)
        _exist_ids = [i['id'] for i in _exist]
        for pos, instance in enumerate(_data):
            if instance['id'] in _exist_ids:
                _data[pos] = _exist[_exist_ids.index(instance['id'])]
    
    result_writer = open(_opath, 'w', encoding='utf-8')
    
    print(f"--------Evaluating output from {in_path}--------")
    print(f"--------Evaluation Using {eval_model}--------")
    
    print(len(_data))
    
    for entry in tqdm(_data):
        # ski if eval exists
        if entry.get('eval', None) is not None:
            result_writer.write(json.dumps(entry, ensure_ascii=False) + '\n')
            result_writer.flush()
            continue
        
        input_task = entry['input']
        output = entry['output']
        if output is None: # skip if result hasn't been generated
            continue
        max_tokens = 8000
        output = truncate_string_by_token_limit(output, max_tokens=max_tokens, model_name="gpt2")
          
        message = []
        answer = ""
        # print(f"--------Instance {entry['id']}--------")
        if entry['id'] == 'domain_oriented_task_86':
            max_tokens = 8000
            output = truncate_string_by_token_limit(output, max_tokens=max_tokens, model_name="gpt2")
        for question in entry['decomposed_questions']:
            if len(message) == 0:
                if input_task:
                    content =  f"{SYS_MSG}\n\nInput:\n\"{input_task}\"\n\nGenerated Text:\n{output}\n\nQuestion:\n{question}\n"
                else:
                    content =  f"{SYS_MSG}\n\nGenerated Text:\n{output}\n\nQuestion:\n{question}\n"
            else:
                content = f"{question}\n"
            message.append({"role": "user", "content": content})
            # create a chat completion
            success = False
            early_stop = False
            while not success:
                try:
                    completion = client.chat.completions.create(
                        model=eval_model,
                        messages=message,
                        temperature=temperature,
                    )
                    generation = completion.choices[0].message.content
                    message.append(
                        {"role": "assistant", "content": generation})
                    # check if generation is yes or no
                    if generation.lower().startswith("yes") or generation.lower().startswith("no"):
                        if generation.lower().startswith("yes"):
                            answer += "Yes\n"
                        else:
                            answer += "No\n"
                    else:
                        if ("YES" or "예") in generation and ("NO" or "아니오") not in generation:
                            answer += "Yes\n"
                        elif ("YES" or "예") not in generation and ("NO" or "아니오") in generation:
                            answer += "No\n"
                        else:
                            for msg in message:
                                print(msg['content'])
                            print("NO YES or NO answer!" + generation)
                            answer += "None\n"
                            early_stop = True
                            break
                    success = True
                except Exception as e:
                    print("ERROR!")
                    print(e)
                    print("Retry!")
                    time.sleep(20)

            # when no answer occurs, break the loop and continue to next instance
            if early_stop:
                break

        answer = answer[:-1]
        # save eval results as List[bool]
        bool_results = []
        for i in answer.split('\n'):
            if i == "Yes":
                bool_results.append(True)
            elif i == "No":
                bool_results.append(False)
            else:
                bool_results.append(None)
    
        entry['eval'] = bool_results
        result_writer.write(json.dumps(entry, ensure_ascii=False) + '\n')
        result_writer.flush()
        
    result_writer.close()
    
    # run true false ratio calculation
    bool_ratio(_opath)
    
    return _opath

def main_run(args):
    client = OpenAI(api_key=args.api_key)
    results_file = args.input
    output_dir = args.output_dir
    eval_model = args.model
    temperature = args.temperature
    
    if not exists(results_file):
        print(f"results_dir {results_file} not exists")
        return
    
    # run evaluation for each model
    run_evaluation(client, results_file, output_dir, eval_model, temperature) 
    return    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--model", type=str, default="gpt-4-0314", help="model name to be used for evaluation")
    
    parser.add_argument("--input", type=str, required=True, help="path to the results file")
    parser.add_argument("--output_dir", type=str, required=True, help="path to the output folder")
    
    parser.add_argument("--temperature", type=float, default=0, help="temperature to be used for evaluation")
    args = parser.parse_args()
    main_run(args)
