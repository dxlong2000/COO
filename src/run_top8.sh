TYPE="chatgpttopk"
IN_PATH="COO/data/processed_chatgpt_sampled_data_25_users_per_topic_max15q_per_user.json"
OUT_PATH="COO/data/chatgpt-output-${TYPE}-top8-coo"
CACHE_PATH="COO/cache/chatgpt_cache_${TYPE}_top8_coo.jsonl"

CODE_PATH="COO/src"
python $CODE_PATH/coo_main.py --in_path $IN_PATH --out_dir $OUT_PATH --option 0 --implicit_sampling $TYPE --num_implicit 8 --max_users 100 --max_ques 10 --max_topics -1 --option=2 --cache_path $CACHE_PATH
