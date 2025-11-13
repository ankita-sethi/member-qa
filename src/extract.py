#function with name of the file and name of the person returnig all messages in timestamp order = latest first
import json
import os
from pathlib import Path
from string import Template
import re
from datetime import datetime,timezone

curr_file= Path("data/store.json")
new_file = Path("data/current.json")

def get_messages(file_path, name):
    with open(file_path,'r',encoding='utf-8') as file:
        raw=json.load(file)
    messages = raw.get(name, [])
    sorted_message=sorted(messages, key=lambda x:x["timestamp"], reverse = True)
    result = [f'{m["timestamp"]}:{m["message"]}' for m in sorted_message]
    context= "\n".join(result)
    return context

def get_current_messages(file_path, name):
    if not file_path.exists():
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw = json.load(file)
    except json.JSONDecodeError:
        return ""
    messages = raw.get(name,[])
    if not messages:
        return ""
    sorted_messages = sorted(messages, key=lambda x: x["timestamp"], reverse=True)
    result = [f'{m["timestamp"]}: {m["message"]}' for m in sorted_messages]
    current_context = "\n".join(result)
    return current_context

def filter_relevant_context(context: str, question: str, current_context: str = "") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found — using raw merged context.")
        return f"{current_context}\n{context}" if current_context else context

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "models/gemini-2.5-flash-lite",
        generation_config={"temperature": 0}
    )

    # Merge both sources
    combined = f"{current_context}\n{context}" if current_context else context

    # 🔥 NEW: More precise and compact filtering prompt
    prompt = f"""
Your job is to extract ONLY the message lines that are useful for answering the question.

Rules:
1. Include ANY line containing or related to:
   - Dates, months, weeks, “next”, “tomorrow”, “tonight”, “this weekend”
   - Travel words: trip, visit, fly, flight, stay, vacation, London, hotel, itinerary
   - Bookings, reservations, chauffeurs, car service, villa stays
   - Food/dining: restaurant, cuisine, dinner, meal, chef
   - Preferences: “favorite”, “usual”, “preferred”

2. If unsure, INCLUDE the line. Do NOT exclude potential clues.

3. DO NOT rewrite. DO NOT summarize. Return only original lines.

Messages:
{combined}

Question:
{question}

Return ONLY the relevant message lines exactly as they appear:
"""

    try:
        resp = model.generate_content(prompt)
        filtered = (resp.text or "").strip()

        # Count lines
        total = len(combined.splitlines())
        count = len(filtered.splitlines()) if filtered else 0

        # 🔥 NEW: Smart fallback when filtering is too strict
        if (not filtered) or count < 20:
            print(f"Gemini filtered too narrowly ({count}/{total}) — trimming to most recent 150 lines.")

            lines = combined.splitlines()

            # 👉 Keep ONLY the last 150 lines — fast and safe
            filtered = "\n".join(lines[:150])

        # 🔥 Clean out any commentary
        filtered = "\n".join(
            line for line in filtered.split("\n")
            if line.strip() and not any(t in line.lower() for t in ["relevant", "lines", "---"])
        )

        return filtered.strip()

    except Exception as e:
        print(f"Gemini error, using fallback: {e}")
        return combined

def get_prompt(context,name,ques,current_context=""):
    if current_context:
        combined_context = (
        f"Recent Updates (newest first):\n{current_context}\n\n"
        f"Older Messages (reference data):\n{context}"
    )
    else:
        combined_context = context

    t = Template(""" You are a factual and reasoning-based question answering assistant.

Your task is to answer the user's question using only the messages below from a member.

Member name: $name  
Messages: $context  
User question: $question

---

**Step 1: Identify Relevant Clues**  
Before reasoning, search the messages for **keywords or synonyms** from the question.  
Look for related or semantically similar terms, such as:  
- Travel-related: trip, vacation, flight, stay, journey, booking, itinerary, plan  
- Dining-related: restaurant, meal, dining, cuisine, chef, dinner, reservation  
- Event-related: birthday, celebration, anniversary, party, concert, event  
- Location/time-related: city, hotel, next week, on Friday, date, month  

If uncertain, include any messages that might logically relate — err on the side of inclusion.

---

**Step 2: Direct or Implicit Evidence**  
If the answer or a clear clue exists anywhere in the messages, use it.  
You do **not** need an exact phrase match — use logical inference.  

For example:  
- “Stay in London next month” → means “trip to London next month.”  
- “Hotel in Paris on May 5th” → means “trip to Paris on May 5th.”  
- “Flight booked for Friday” → means “trip planned for Friday.”  

When time or location clues exist, combine them to form a natural answer like  
“Layla is planning her trip to London next month.”  

---

**Step 3: Logical Inference**  
If no direct date is given, infer from context:  
- “next week / next month / in December” → timing clues.  
- Mentions of chauffeur, hotel, reservation, booking, villa, or stay in a city → travel clues.  
- Mentions of restaurant, dinner, cuisine → dining preference clues.  

Always prefer giving a reasoned best answer rather than the fallback apology,  
as long as there is any plausible supporting evidence in the messages.


**Step 4: Fallback**  
If no relevant evidence exists at all, respond exactly with:  
> “Apologies, I don't have the complete data for this question.”

---

**Answer-Type Awareness**  
Determine the expected type of answer based on the question:  
- “When” → use time or date clues.  
- “Where” → use place or location mentions.  
- “How many” → use quantity or count.  
- “What” (preferences) → use likes, favorites, bookings, or repeated mentions.  
Avoid substituting unrelated details (e.g., don’t return an address for a “when” question).

---

**Behavior Rules**  
- Use frequency and exclusivity patterns confidently.  
- Never invent facts or hallucinate.  
- Keep answers short and natural (1–2 sentences).  

---

**Example Responses:**  
Q: When is Layla planning her trip to London?  
A: Layla is planning her trip to London next month.  

Q: How many cars does Vikram Desai have?  
A: Vikram seems to have 0 cars as he usually books rentals.  

Q: What are Amina’s favorite restaurants?  
A: Amina enjoys sushi and Italian food and often books restaurants in Malibu.  

Q: Do they own a car?  
A: The member likely does not own a car; they frequently request chauffeur or car service.  

---

**Formatting Rule for Factual Answers:**  
When a message explicitly contains factual data (e.g., numbers, addresses, phone), respond with a complete declarative statement using the member’s name.  
Example:  
- “Hans’s passport number is BA8493921.”  
- “Layla’s phone number is 9876543210.”  
- “Amina’s address is 123 Park Avenue, New York.”  



              """)

    prompt = t.safe_substitute(name=name, context=combined_context, question=ques)

    return prompt
    
def link_llm(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found — returning fallback response.")
        return "Apologies, I don't have the complete data for this question."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite", generation_config={"temperature": 0})

        response = model.generate_content(prompt)
        return (response.text or "").strip()
    except Exception as e:
        print(f"Gemini call failed: {e}")
        return "Apologies, the AI service is temporarily unavailable."
    
def save_update_to_current(name, message):
    data_path = new_file
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data.setdefault(name, []).insert(0,{
        "full_name": name,
        "message": message.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_update(user_text: str) -> bool:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.5-flash-lite")


    classify_prompt = f"""
You are a strict classifier. Decide if the user text is PROVIDING a new factual update
that should be stored (like "My new number is 555-1234", "Sophia’s address is now ...",
"Use +44 for me going forward") versus NOT an update (a question/command like
"Book a table", "What is my number?", "Can you arrange ...", etc).

Rules:
- If the text asserts a new fact about a member or their preferences, return exactly: UPDATE
- Otherwise return exactly: NOT_UPDATE
- No extra words.

User text: "{user_text}"
"""

    try:
        out = model.generate_content(classify_prompt).text.strip().upper()
        return out == "UPDATE"
    except Exception:
        return False
