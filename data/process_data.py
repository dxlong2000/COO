import os
import openai
import torch
import json
from tqdm import tqdm
import time

openai.api_key = ""

def get_chatgpt_answer(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": input_text}],
        max_tokens=1024,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response['choices'][0]['message']['content']

print("Loading data...")
PATH_FILE = "COO/data/sampled_data_25_users_per_topic_max15q_per_user.json"

with open(PATH_FILE) as file: full_data = json.load(file)

print(f"Done loading data! Len of data: {len(full_data)}")

cosi = torch.nn.CosineSimilarity(dim=0)
tens_1 = torch.tensor(full_data[0]["implicit_persona"][0]['emb'])
tens_2 = torch.tensor(full_data[0]["implicit_persona"][1]['emb'])
output = cosi(tens_1, tens_2)

print("Check torch: ", str(output))

data = full_data
fail_cases = 0
total_cases = 0 

for data_idx in tqdm(range(len(data))):
    persona_question_lists = []
    persona_question_embs = []
    for idx in range(len(data[data_idx]["implicit_persona"])):
        persona_question_lists.append(data[data_idx]["implicit_persona"][idx]['question'] + f" (answer: {data[data_idx]['implicit_persona'][idx]['answer']})")
        persona_question_embs.append(torch.tensor(data[data_idx]["implicit_persona"][idx]['emb']))

    original_attribute_list = str(data[data_idx]["explicit_persona"])

    original_persona_question_order = ""
    for idx_question in range(len(persona_question_lists)):
        original_persona_question_order += f"{idx_question}. " + persona_question_lists[idx_question] + "\n"
    for question_experiment_idx in tqdm(range(len(data[data_idx]["implicit_questions"]))):
        total_cases += 1
        try:
            test_question = data[data_idx]["implicit_questions"][question_experiment_idx]['question']
            test_choices = data[data_idx]["implicit_questions"][question_experiment_idx]['choices']
            test_emb = torch.tensor(data[data_idx]["implicit_questions"][question_experiment_idx]['emb'])
            subtopic = data[data_idx]["implicit_questions"][question_experiment_idx]["subtopic_cg"][0]
        except Exception as exc:
            print(f"Exception: {exc}")
            fail_cases += 1
            print(f"Fail total: {fail_cases} over {total_cases}")
            with open("COO/data/processed_chatgpt_sampled_data_25_users_per_topic_max15q_per_user.json", "w") as file: 
                json.dump(data, file)
            continue

        scores = []
        score_indexes = {}
        for iidx_ in range(20):
            score = cosi(persona_question_embs[iidx_], test_emb)
            scores.append(float(score))
            score_indexes[float(score)] = iidx_

        scores.sort(reverse=True)
        orders = [score_indexes[scores[iiidx]] for iiidx in range(20)]

        chatgpt_order_prompt = f"""Given 20 social behavior question-answer pairs answered by a user about his opinions about {subtopic}:
{original_persona_question_order}
You are an expert in analyzing social behaviors of an user. Given a new question asking him: '{test_question}', your task is to sort the list of given 20 question-answer pairs in the descending order such that the first question-answer pair brings the most useful information to answer the new question, whilst the last  question-answer pair brings the least useful information.
Give me the answer in the form of Python list of indexes:

Give me the answer in the format below without any explanation:
Answer: [...]"""

        chatgpt_attributes_selection_prompt = f"""A person can be described by the following attributes:
{original_attribute_list}
The person has the following opinions on {subtopic}.
Opinions:
{original_persona_question_order}
Based on the above list of opinions and the demographic information, now I give you a new question with possible answer choices:

Question: '{test_question}'
Answer choices: '{test_choices}'

Please analyze which attributes in the demographic information are useful for you to answer the above question step by step. Give me the output in the Python list format: [...]

Give me the answer in the format below:
Explainations: ...
Answer: [...]"""

        try:
            chatgpt_order_answer = get_chatgpt_answer(chatgpt_order_prompt).strip().split("Answer: ")[1].strip()
            chatgpt_removed_features = get_chatgpt_answer(chatgpt_attributes_selection_prompt).strip().split("Answer: ")[1].strip()
            
            data[data_idx]["implicit_questions"][question_experiment_idx]["rewritten_persona_questions"] = persona_question_lists
            data[data_idx]["implicit_questions"][question_experiment_idx]["similarity_orders"] = orders
            data[data_idx]["implicit_questions"][question_experiment_idx]["similarity_scores"] = scores

            data[data_idx]["implicit_questions"][question_experiment_idx]['chatgpt_orders'] = eval(chatgpt_order_answer)
            data[data_idx]["implicit_questions"][question_experiment_idx]['chatgpt_attributes'] = eval(chatgpt_removed_features)

        except Exception as exc:
            print(f"Exception: {exc}")
            print(f"Fail total: {fail_cases} over {total_cases}")
            with open("COO/data/processed_chatgpt_sampled_data_25_users_per_topic_max15q_per_user.json", "w") as file:
                json.dump(data, file)
            fail_cases += 1
            continue

with open("COO/data/processed_chatgpt_sampled_data_25_users_per_topic_max15q_per_user.json", "w") as file:
    json.dump(data, file)
