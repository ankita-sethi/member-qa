# Member Question Answering System

## Overview

This project is part of a **question-answering system** designed to understand and respond to member's natural-language questions based on their historical messages.

The system retrieves real message data from a public API, cleans and organizes it and then uses an **LLM** (Gemini 2.0 Flash) to infer answers.

For example, if the dataset has a message like _“Layla is planning her trip to London next month”_, the model can answer:

> **Q:** When is Layla planning her trip to London?  
> **A:** Layla is planning her trip to London next month.

---

## What’s Been Done So Far

So far, the project has:

1. **Fetched data** from a public API using a `curl` command and stored it as `response.json`.
2. **Cleaned and transformed** the JSON using Python (`clean_data.py`) to group messages by first name and timestamp.
3. **Created a message extractor** (`extract.py`) that:
   - Reads messages for a given member.
   - Sorts them by latest timestamp.
   - Builds a conversational context string.
4. **Built a prompt generator** that feeds this context, member name and question into the LLM (Gemini).
5. **Integrated Gemini 2.0 Flash** model for generating concise, factual answers based only on user context.

---

## Example Flow

1. **Input question:**  
   `"When is Sophia planning her trip to Paris?"`

2. **Data source:**  
   A message like  
   `"Please book a private jet to Paris for this Friday."`

3. **Model output:**  
   `"Sophia is planning her trip to Paris this Friday."`

---

## Project Structure

```plaintext
member_qa/
│
├── data/
│   ├── response_minified.json      # Optional smaller version of the dataset
│   ├── response.json               # Raw API dump (fetched using curl)
│   └── store.json                  # Cleaned data grouped by member first name
│
├── src/
│   ├── clean_data.py               # Converts response.json → store.json
│   ├── extract.py                  # get_messages, get_prompt, link_llm
│   │
│   └── test/                       # Test utilities
│       ├── list_models.py          # Lists all available Gemini models
│       └── test_gemini.py          # Quick test script for API and key verification
│
├── venv/                           # Python virtual environment (ignored by Git)
└── README.md                       # Project documentation
```
