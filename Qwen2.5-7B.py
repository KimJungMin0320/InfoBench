from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)


SYS_MSG ="Based on the provided Input (if any) and Generated Text, answer the ensuing Questions with either a YES or NO choice.\
    Your selection should be based on your judgment as well as the following rules:\n\n\
        - YES: Select 'YES' if the generated text entirely fulfills the condition specified in the question.\
            However, note that even minor inaccuracies exclude the text from receiving a 'YES' rating.\
            As an illustration. consider a question that asks.\
                \"Does each sentence in the generated text use a second person?”\
            If even one sentence does not use the second person, the answer should NOT be 'YES'.\
            To qualify for a 'YES' rating, the generated text must be entirely accurate and relevant to the question\n\n\
        - NO: Opt for 'NO' if the generated text fails to meet the question's requirements or provides no information that could be utilized to answer the question. \
            For instance, if the question asks. \
            \"Is the second sentence in the generated text a compound sentence?\" and the generated text only has one sentence. \
            it offers no relevant information to answer the question. Consequently, the answer should be 'NO'."
input_task = "The typical avocado is over 300 calories from the oil in it. That’s the amount of calories in a large candy bar. If you get enough exercise to eat a large candy bar every day without gaining weight, it wouldn’t be a problem to eat an avocado every day. Other wise you should probably eat them sparingly."
output = "Balancing Your Calorie Intake: Avocados vs. Candy Bars"
question = "Is the generated text a post title?"
content =  f"{SYS_MSG}\n\nInput:\n\"{input_task}\"\n\nGenerated Text:\n{output}\n\nQuestion:\n{question}\n"
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": content}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(response)