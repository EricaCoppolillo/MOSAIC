import json
import re

import google.generativeai as genai
from groq import Groq
import argparse

from openai import AzureOpenAI
from anthropic import AnthropicBedrock
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from utility import *

# TODO: In secret.py, you need to insert your API keys
from secret import *

api_index = 0

def get_client(llm):
    api = secrets_dict[llm][api_index]
    if "gemini" in llm:
        genai.configure(api_key=api)

        client = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    elif "qwen" in llm or "llama" in llm:
        client = Groq(api_key=api)

    # new models
    elif "gpt-4o" in llm:
        endpoint = endpoints_dict[llm]

        client = AzureOpenAI(
            api_key=api,
            api_version="2024-08-01-preview",
            azure_endpoint=endpoint
        )

    elif "o4-mini" in llm:
        endpoint = endpoints_dict[llm]
        client = AzureOpenAI(
            api_key=api,
            api_version="2024-12-01-preview",
            azure_endpoint=endpoint,
        )

    elif "deepseek-r1" in llm:

        endpoint = endpoints_dict[llm]

        client = ChatCompletionsClient(
            credential=AzureKeyCredential(api),
            endpoint=endpoint,
        )

    else:
        raise Exception(f"LLM {llm} not supported")

    return client


def invoke_model(system_prompt, question, llm, client, temperature=0.6):
    text = "Error"

    while "Error" in text:

        try:
            if llm == "gemini":
                response = client.generate_content([system_prompt, question], request_options={"timeout": 10})
                text = response.text.strip().lower()

            elif "gpt-4o" in llm:
                messages = [{"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": question
                            }
                            ]

                text = client.chat.completions.create(messages=messages, model=llm, temperature=temperature).choices[
                    0].message.content

            elif "o4-mini" in llm:
                messages = [{"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": question
                            }
                            ]
                text = client.chat.completions.create(messages=messages, model=llm, stop=None).choices[
                    0].message.content

            elif "deepseek" in llm:
                messages = [{"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": question
                            }
                            ]
                response_with_thinking = client.complete(messages=messages, model=llm, max_tokens=4096, temperature=temperature).choices[
                    0].message.content
                text = re.sub(r"<think>.*?</think>\n?", "", response_with_thinking, flags=re.DOTALL).replace("A:",
                                                                                                                   "").strip()
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
                        temperature=temperature,
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
                        temperature=temperature,
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

            if "llama" in llm or "qwen" in llm:
                print("Changing API Key")
                global api_index
                api_index = (api_index + 1) % len(secrets_dict[llm])

                api = secrets_dict[llm][api_index]
                client = Groq(api_key=api)

            if "The response was filtered due to the prompt triggering Azure OpenAI's content management policy." in str(e):
                text = "1"

    return text


def undergo_questionnaire(test, llm, client, temperature=0.6, prompt_rephrasing=None):

    if prompt_rephrasing is None:
        questionnaire_path = os.path.join(data_folder, f"{test}_data.json")
    else:
        questionnaire_path = os.path.join(data_folder, f"{test}_data_rephrased_{prompt_rephrasing}.json")

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
        answer = invoke_model(system_prompt, question, llm, client, temperature=temperature)
        results_dict[question] = answer

    return results_dict


if __name__ == "__main__":

    llms = ["gpt-4o", "o4-mini", "deepseek-r1", "llama", "qwen", "gemini"]

    tests = ["mfq2", "lsrp", "svs", "ec", "ics", "bjw", "pmps", "sdo",
             "the_moral_machine", "my_goodness", "last_haven", "tinker_tots",
             "personality"]

    TEMPERATURE_SENSITIVITY = False
    PROMPT_REPHRASING = True

    parser = argparse.ArgumentParser(description="Evaluate a given LLM on a specific test. "
                                                 "If no arguments are provided, all available LLMs will be evaluated "
                                                 "on all available tests.")
    parser.add_argument("--llm", "-l", choices=llms, default=None, nargs='+', help="LLM to evaluate")
    parser.add_argument("--test", "-t", choices=tests, default=None, nargs='+', help="Test to run")

    args = parser.parse_args()

    print(f"Evaluating LLM: {args.llm}")
    print(f"Running test: {args.test}")

    if args.llm is not None:
        if not isinstance(args.llm, list):
            llms = [args.llm]
        else:
            llms = args.llm

    if args.test is not None:
        if not isinstance(args.test, list):
            tests = [args.test]
        else:
            tests = args.test

    # undergo the same questionnaire N_PROBING times
    N_PROBING = 10

    if TEMPERATURE_SENSITIVITY:
        tests = ["the_moral_machine"]
        llms = ["gemini"]
        temperatures = [0.1, 0.2, 0.4, 0.8, 1.]
        N_PROBING = 5

    elif PROMPT_REPHRASING:
        tests = ["mfq2"]
        llms = ["gemini", "llama", "qwen"]
        N_PROBING = 10

    print(f"Temperature sensitivity set to {TEMPERATURE_SENSITIVITY}")
    print(f"Prompt rephrasing set to {PROMPT_REPHRASING}")

    print("*****")
    print("CONFIGURATION COMPLETED.")

    for llm in llms:

        print(f"RUNNING LLM {llm}")

        client = get_client(llm=llm)

        for test in tests:

            print(f"RUNNING TEST {test}")

            model_results_folder = os.path.join(results_folder, llm, f"{test}_results")
            if not os.path.exists(model_results_folder):
                os.makedirs(model_results_folder)

            if not TEMPERATURE_SENSITIVITY and not PROMPT_REPHRASING:
                last_probing_fn = os.path.join(model_results_folder, f"invocation_{N_PROBING}.json")

                if os.path.exists(last_probing_fn):
                    print(f"The {test} questionnaire has already been undergone for {N_PROBING} times.")
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

            elif TEMPERATURE_SENSITIVITY:
                sensitivity_results_folder = os.path.join(model_results_folder, "sensitivity_results")
                if not os.path.exists(sensitivity_results_folder):
                    os.makedirs(sensitivity_results_folder)

                for t in temperatures:

                    print("Processing Temperature: ", t)

                    final_sensitivity_results_folder = os.path.join(sensitivity_results_folder, f"temperature_{t}")
                    if not os.path.exists(final_sensitivity_results_folder):
                        os.makedirs(final_sensitivity_results_folder)

                    last_probing_fn = os.path.join(final_sensitivity_results_folder, f"invocation_{N_PROBING}.json")

                    if os.path.exists(last_probing_fn):
                        print(f"The {test} questionnaire has already been undergone for {N_PROBING} times for sensitivity analysis with temperature {t}.")
                        continue

                    probing = 0
                    for probing in range(N_PROBING):
                        print(f"PROBING: {probing + 1}")
                        results_fn = os.path.join(final_sensitivity_results_folder, f"invocation_{probing + 1}.json")

                        if os.path.exists(results_fn):
                            continue

                        test_results = undergo_questionnaire(test, llm, client, temperature=t)

                        with open(results_fn, "w") as f:
                            json.dump(test_results, f)

            elif PROMPT_REPHRASING:
                prompt_results_folder = os.path.join(model_results_folder, "prompt_results")
                if not os.path.exists(prompt_results_folder):
                    os.makedirs(prompt_results_folder)

                for i in [1, 2]:

                    print("Prompt Rephrasing: ", i)

                    final_prompt_results_folder = os.path.join(prompt_results_folder, f"prompt_rephrasing_{i}")
                    if not os.path.exists(final_prompt_results_folder):
                        os.makedirs(final_prompt_results_folder)

                    last_probing_fn = os.path.join(final_prompt_results_folder, f"invocation_{N_PROBING}.json")

                    if os.path.exists(last_probing_fn):
                        print(
                            f"The {test} questionnaire has already been undergone for {N_PROBING} times for prompt analysis with rephrasing {i}.")
                        continue

                    probing = 0
                    for probing in range(N_PROBING):
                        print(f"PROBING: {probing + 1}")
                        results_fn = os.path.join(final_prompt_results_folder, f"invocation_{probing + 1}.json")

                        if os.path.exists(results_fn):
                            continue

                        test_results = undergo_questionnaire(test, llm, client, prompt_rephrasing=i)

                        with open(results_fn, "w") as f:
                            json.dump(test_results, f)
