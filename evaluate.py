import json
import google.generativeai as genai
from groq import Groq
import argparse

from utility import *


def get_client(llm):
    if "gemini" in llm:
        api = "[API-KEY]"
        genai.configure(api_key=api)

        client = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    elif "qwen" in llm or "llama" in llm:
        api = "[API-KEY]"
        client = Groq(api_key=api)

    else:
        raise Exception(f"LLM {llm} not supported")

    return client


def invoke_model(system_prompt, question, llm, client):
    text = "Error"
    while "Error" in text:

        try:
            if llm == "gemini":
                response = client.generate_content([system_prompt, question], request_options={"timeout": 10})
                text = response.text.strip().lower()

            else:
                if "qwen" in llm:
                    model_name = "qwen/qwen3-32b"
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": "/no_think" + " " + question
                            }
                        ],
                        temperature=0.6,
                        max_completion_tokens=4096,
                        top_p=0.95,
                        reasoning_effort="default",
                        stream=True,
                        stop=None
                    )
                elif "llama" in llm:
                    model_name = "llama-3.3-70b-versatile"
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": question
                            }
                        ],
                        temperature=0.6,
                        max_completion_tokens=1024,
                        top_p=1,
                        stream=True,
                        stop=None
                    )

                text = ""
                for chunk in completion:
                    text += chunk.choices[0].delta.content or ""

                text = text.replace("<think>", "").replace("</think>", "").strip()


        except Exception as e:
            print(e)
            time.sleep(5)
            text = f"Error: {e}"

    return text


def undergo_questionnaire(test, llm, client):
    questionnaire_path = os.path.join(data_folder, f"{test}_data.json")
    with open(questionnaire_path, 'r') as f:
        questionnaire = json.load(f)

    system_prompt = questionnaire['system_prompt']

    question_name = "questions"
    if test in PLATFORM_BASED_TESTS:
        question_name = "scenarios"

    questions = questionnaire[question_name]

    results_dict = {}

    for i, question in enumerate(questions):
        print(f"Question: {i + 1} out of {len(questions)}")
        answer = invoke_model(system_prompt, question, llm, client)
        results_dict[question] = answer

    return results_dict


if __name__ == "__main__":

    llms = ["gemini", "llama", "qwen"]

    tests = ["mfq2", "lsrp", "svs", "ec", "ics", "bjw", "pmps", "sdo",
             "the_moral_machine", "my_goodness", "last_haven", "tinker_tots",
             "personality"]

    parser = argparse.ArgumentParser(description="Evaluate a given LLM on a specific test. "
                                                 "If no arguments are provided, all available LLMs will be evaluated "
                                                 "on all available tests.")
    parser.add_argument("--llm", "-l", choices=llms, default=None, help="LLM to evaluate")
    parser.add_argument("--test", "-t", choices=tests, default=None, help="Test to run")

    args = parser.parse_args()

    print(f"Evaluating LLM: {args.llm}")
    print(f"Running test: {args.test}")

    if args.llm is not None:
        llms = [args.llm]

    if args.test is not None:
        tests = [args.test]

    for llm in llms:

        client = get_client(llm=llm)

        print("CONFIGURATION COMPLETED.")

        for test in tests:

            print(f"RUNNING TEST {test}")
            model_results_folder = os.path.join(results_folder, llm, f"{test}_results")
            if not os.path.exists(model_results_folder):
                os.makedirs(model_results_folder)

            # undergo the same questionnaire 5 times
            N_PROBING = 5

            last_probing_fn = os.path.join(model_results_folder, f"invocation_5.json")

            if os.path.exists(last_probing_fn):
                print(f"The {test} questionnaire has already been undergone for 5 times.")
                continue

            probing = 0
            for probing in range(N_PROBING):
                print(f"PROBING: {probing + 1}")
                results_fn = os.path.join(model_results_folder, f"invocation_{probing + 1}.json")

                if os.path.exists(results_fn):
                    continue

                test_results = undergo_questionnaire(test, llm, client)

                with open(results_fn, "w") as f:
                    json.dump(test_results, f)
