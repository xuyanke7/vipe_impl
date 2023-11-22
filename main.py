import argparse
import os
import sys
import numpy as np
import openai
import jsonlines
from typing import Union, List, Dict
from utils import read_jsonl, read_jsonl_gz
from tenacity import (
    retry,
    stop_after_attempt,  
    wait_random_exponential,  
)
import const
from executor import function_with_timeout

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = const.API_KEY
# openai.api_key = "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"
openai.api_key = "sess-FxwNtOrpPwUgJW0PzjuFD5U2YTq2wUCpxYlHb75P"


def parserargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_name", type=str, help="The name of the run")
    parser.add_argument("--root_dir", type=str,
                        help="The root logging directory", default="viper_impl/data")
    parser.add_argument("--dataset_path", type=str,
                        help="The path to the benchmark dataset", default="viper_impl/data")
    parser.add_argument("--strategy", type=str, default='general',
                        help="Strategy: `simple`, `reflexion`")
    parser.add_argument("--language", type=str,
                        help="Strategy: `py` or `rs`", default="py")
    parser.add_argument(
        "--model", type=str, default="gpt-3.5-turbo", help="OpenAI models only for now. For best results, use GPT-4")
    parser.add_argument("--pass_at_k", type=int,
                        help="Pass@k metric", default=1)
    parser.add_argument("--max_iters", type=int,
                        help="The maximum number of self-improvement iterations", default=10)
    parser.add_argument("--expansion_factor", type=int,
                        help="The expansion factor for the reflexion UCS and A* strategy", default=3)
    args = parser.parse_args()
    return args


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
def gpt_chat(
    model: str,
    sys_msg: str,
    user_msg: str,
    temperature: float = 0.0,
    num_comps=1,
) -> Union[List[str], str]:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=temperature,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        n=num_comps,
    )
    if num_comps == 1:
        return response.choices[0].message.content

    return [choice.message.content for choice in response.choices]


def code_general(dataset: List[dict],
                 pass_at_k: int,
                 log_path: str,
                 model: str,) -> None:
    # {"imageid": "n290131", "question": [{"query": "Is the busy man waiting for a bus?"}, {"query": "Who is waiting for the food truck that is not large?"}, {"query": "Who is sitting?"}, {"query": "Does the side walk have brown color?"}, {"query": "Do the bags made of plastic look white or black?"}, {"query": "Is there a large window or door?"}, {"query": "How big is the window the man is looking through?"}, {"query": "Is the bag on the bench black and small?"}, {"query": "Is the young man to the left or to the right of the bags near the bench?"}, {"query": "What is the sidewalk made of?"}, {"query": "What is that backpack on?"}, {"query": "What bag is to the right of the man that is looking through the window?"}, {"query": "Is the color of the menu the same as the food truck?"}, {"query": "Is the color of the backpack different than the sidewalk?"}, {"query": "Are there both a window and a door?"}, {"query": "Is the large backpack to the right or to the left of the man on the left side?"}, {"query": "Do you see benches near the bags that look white?"}]}

    with open("prompt\chatapi.prompt","r") as f:
        baseprompt = f.read().strip()
    print('----SYSTEM MESSAGE')
    # print(baseprompt)

    # for each image in the dataset
    for i, item in enumerate(dataset):
        querylist = [q['query'] for q in item['question']]
        for i, item in enumerate(querylist):
            print(' ----USER MESSAGE')
            print(item)
            res_main = gpt_chat(
                model=model,
                sys_msg=baseprompt,
                user_msg=item,
            )
            print('----RESPONSE')
            print(res_main)
            reslist = []
            reslist.append({"question":item,
                            "function":res_main})
            break


        # Code Eval Part (v1)
        # ispass = eval_general(item["entry_point"], res_main, item["test"], timeout = 20)
        # print(f'The {i+1} item,ispass: {ispass}.')

        break


def eval_general(entrypoint: str, response: str, test: str, timeout: int = 5)->bool:
    """
    Evaluates on Human-Eval Py.
    """
    code = f"""{response}{test}check({entrypoint})"""
    try:

        function_with_timeout(exec, (code, globals()), timeout)

        return True
    except Exception:
        return False


def main(args):
    # check root dir
    if not os.path.exists(args.root_dir):
        os.makedirs(args.root_dir)

    # check dataset
    args.dataset_path = "viper_impl/data/sample_question_100.jsonl"  # sample query 100 
    dataset_name = os.path.basename(args.dataset_path).replace(".jsonl", "")
    print(f"loading {dataset_name}")

    # load dataset
    if args.dataset_path.endswith(".jsonl"):
        dataset = read_jsonl(args.dataset_path)
    else:
        raise ValueError(f"File `{args.dataset_path}` is not a jsonl file.")
    print(f"loaded {len(dataset)} items")

    # check logpath
    args.run_name = "test_general"
    log_dir = os.path.join(args.root_dir, args.run_name)
    log_path = os.path.join(
        log_dir, f"{dataset_name}_{args.max_iters}_{args.model}.jsonl")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    print(f"Logging to {log_path}")

    code_general(dataset, args.pass_at_k, log_path, args.model)

def testapi():
    # openai.api_key = ""
    print(openai.api_key)
    with open("prompt\chatapi.prompt","r") as f:
        baseprompt = f.read().strip()
    query = "Is there a helmet to the right of a old and caucasian player?"
    try:
        res_main = gpt_chat(
                model="gpt-3.5-turbo",
                sys_msg=baseprompt,
                user_msg=query,
            )
        print('----RESPONSE')
        print(res_main)


    except openai.error.OpenAIError as e:
        print(f"OpenAIError: {e}.")
    


if __name__ == "__main__":
    testapi()
    args = parserargs()
    main(args)
