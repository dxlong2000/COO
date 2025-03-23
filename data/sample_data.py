import json

PATH_FILE = "COO/data/sampled_user_responses_20_decl_topk.json"
with open(PATH_FILE) as file:
    full_data = json.load(file)

import random

topic_count = {}
sampled_data = []

for idx in range(len(full_data)):
  if full_data[idx]['topic'] not in topic_count: topic_count[full_data[idx]['topic']] = [full_data[idx]]
  else: topic_count[full_data[idx]['topic']].append(full_data[idx])

cnt = 0
for topic in topic_count:
  random.shuffle(topic_count[topic])
  selected_users = topic_count[topic][:25]
  for idx in range(len(selected_users)):
    random.shuffle(selected_users[idx]["implicit_questions"])
    selected_users[idx]["implicit_questions"] = selected_users[idx]["implicit_questions"][:min(15, len(selected_users[idx]["implicit_questions"]))]
    cnt += len(selected_users[idx]["implicit_questions"])
  sampled_data.extend(selected_users)

print("cnt: ", str(cnt))

print(len(sampled_data))
with open("/COO/data/sampled_data_25_users_per_topic_max15q_per_user.json", "w") as outfile:
    json.dump(sampled_data, outfile)