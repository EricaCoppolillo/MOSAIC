# MOSAIC

This is the repository of the paper _MOSAIC: Unveiling the Moral, Social and Individual Dimensions of Large Language Models_, currently under submission to the KDD2026 Dataset and Benchmark Track.
In our work, we provide a comprehensive framework for evaluating the Moral, Social, and Individual dimensions of Large Language Models across nine validated questionnaires and four ethical dilemmas.

## Overview

MOSAIC provides a systematic way to evaluate different LLMs on a range of psychological assessments, ethical scenarios, and personality tests. The framework supports multiple models and test types, allowing for comparative analysis of LLM behavior and responses.

## Supported Models

- **Gemini-2-flash** - Google's model
- **LLaMa-3.3-70B** - Meta's model
- **Qwen-3-32B** - Alibaba's model

## Available Tests

### Questionnaires
- **MFQ2** - Moral Foundations Questionnaire 2
- **LSRP** - Levenson Self-Report Psychopathy Scale
- **SVS** - Schwartz Value Survey
- **EC** - Empathic Concern
- **ICS** - Individualism and Collectivism Scale 
- **BJW** - Belief in a Just World
- **PMPS** - Preference for the Merit Principle Scale 
- **SDO** - Social Dominance Orientation
- **MBTI** - Myers-Briggs Type Indicator (Personality test)

### Ethical Dilemmas
- **The Moral Machine** 
- **My Goodness** 
- **Last Haven** 
- **Tinker Tots** 

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Options

```
--llm, -l    Specify which LLM to evaluate (gemini, llama, or qwen)
--test, -t   Specify which test to run (see list above)
```

### Run All Tests on All Models

```bash
python evaluate.py
```

This will evaluate all available LLMs on all available tests.

### Run Specific Model on Specific Test

```bash
python evaluate.py --llm [LLM] --test [TEST]
```

### Run Specific Model on All Tests

```bash
python evaluate.py --llm [LLM]
```

### Run All Models on Specific Test

```bash
python evaluate.py --test [TEST]
```

## Examples

```bash
# Evaluate Gemini on the Moral Foundations Questionnaire
python evaluate.py -l gemini -t mfq2

# Evaluate all models on The Moral Machine dilemma
python evaluate.py -t the_moral_machine

# Evaluate Qwen on all available tests
python evaluate.py -l qwen 
```


