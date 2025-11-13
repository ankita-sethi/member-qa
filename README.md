# Member Question Answering System

## Overview

This project is a **member-aware question answering system** that responds to natural-language questions using only the member’s historical messages. It retrieves the message history, filters relevant lines, builds a reasoning prompt and uses **Google Gemini 2.5 Flash-Lite / Pro** to generate factual answers.

If stored messages contain:

2025-10-12: Layla is planning her trip to London next month.

Then the system can answer:

**Q:** When is Layla planning her trip to London?  
**A:** Layla is planning her trip to London next month.

The model never hallucinates and only uses verified message history.

---

## Live Deployment (Public API)

Your question answering system is deployed here:

https://member-qa-9vly.onrender.com

This URL opens a small demo chatbot UI.

## API Endpoint

The main endpoint is:

POST https://member-qa-9vly.onrender.com/api/ask/

### Example cURL

curl -X POST "https://member-qa-9vly.onrender.com/api/ask/" \
 -H "Content-Type: application/json" \
 -d '{"question": "When is Layla planning her trip to London?"}'

### Example Response

{ "answer": "Layla is planning her trip to London next month." }

## Quick Test Prompts

Try any of these:

- "What are Amina’s favorite restaurants?"

- "When is Layla planning her trip?"

- "What is Sophia’s number?"

- "Update Armand’s phone number to 555-9999."

- "Where is Lily currently staying?"

## Features

- Loads and organizes each member's message history from JSON files
- Merges older and recent messages for stronger context
- Smart filtering using Gemini (keeps dates, travel, dining, bookings, preferences)
- Structured reasoning prompt ensures evidence-based answers
- Safe fallback:
  > Apologies, I don't have the complete data for this question.
- Automatic update detection (saved into `current.json`)
- Fast Django API endpoint: **POST /api/ask**
- Simple chatbot UI with light/dark theme and reset button

---

## What’s Included

### 1. Data ingestion

- Fetch raw dataset using `curl`
- Save as `response.json`

### 2. Data cleaning

- `clean_data.py` → Converts raw → structured dataset
- Groups messages by first name, sorted by timestamp

### 3. Message extraction

- `get_messages()` and `get_current_messages()` combine long-term + recent data

### 4. Context filtering

- Keeps only relevant message lines (time, travel, bookings, preferences)
- Falls back to recent 150 lines when the filtering is too strict

### 5. Prompt generation

- Builds a structured reasoning prompt
- Ensures no hallucination, short answers, and factual correctness

### 6. LLM inference

- Uses Gemini 2.5 Flash-Lite (fast) or Pro (more accurate)

### 7. Update detection

- Detects lines like “My phone number is now…”
- Saves them to `data/current.json`

---

## API Example

## Request

```http
POST /api/ask
```

```json
{
  "question": "When is Amina’s husband’s birthday?"
}
```

## Response

```json
{
  "answer": "Amina’s husband’s birthday is on July 6th."
}
```

## Project Structure

```
member_qa/
│
├── data/
│   ├── response.json      # Raw dataset
│   ├── store.json         # Cleaned messages by member
│   └── current.json       # Runtime updates saved by the bot
│
├── src/
│   ├── clean_data.py      # Converts raw → structured JSON
│   ├── extract.py         # Filtering, LLM prompts, Gemini logic
│   └── test/
│       ├── list_models.py # Lists available Gemini models
│       └── test_gemini.py # Verifies API key access
│
├── templates/
│   └── index.html         # Minimal chatbot UI
│
├── qa_service/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md
```
