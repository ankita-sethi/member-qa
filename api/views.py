from django.http import JsonResponse
from rest_framework.decorators import api_view
from src.extract import get_messages, get_prompt, link_llm, filter_relevant_context, get_current_messages, save_update_to_current, detect_update
from pathlib import Path
import json
import re
from django.views.decorators.csrf import csrf_exempt


def extract_name(question):
    """Finds the member name from the question using case-insensitive match against store.json."""
    data_path = Path("data/store.json")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            store = json.load(f)
    except FileNotFoundError:
        return None

    # Normalize dataset names to lowercase for easier matching
    all_names = {name.strip().lower(): name.strip() for name in store.keys()}
    q_lower = re.sub(r"[^a-z\s]", "", question.lower())  # remove punctuation

    # Look for any known name inside the question
    for name_lower, original in all_names.items():
        if name_lower in q_lower:  # direct substring match
            return original

    return None

@csrf_exempt
@api_view(["GET", "POST"])
def ask(request):
    # Step 1: accept GET (for take-home spec) and POST (for your own UI)
    question = (
        request.data.get("question")
        if request.method == "POST"
        else request.GET.get("q", "")
    )
    question = (question or "").strip()

    if not question:
        return JsonResponse({"answer": "Please provide a valid question."})

    name = extract_name(question) or "Member"
    curr_file = Path("data/store.json")
    new_file = Path("data/current.json")

    try:
        context = get_messages(curr_file, name)
        current_context = get_current_messages(new_file, name)
        filtered_context = filter_relevant_context(context, question, current_context)
        print("\n================ DEBUG ================")

        print("QUESTION:", question)
        print("DETECTED NAME:", name)

        # Store.json messages
        store_lines = context.splitlines()
        print("STORE.JSON MESSAGE COUNT:", len(store_lines))
        print("STORE.JSON SAMPLE (first 5):")
        for l in store_lines[:5]:
            print("  ", l)

        # Current.json messages
        curr_lines = current_context.splitlines()
        print("CURRENT.JSON MESSAGE COUNT:", len(curr_lines))
        print("CURRENT.JSON SAMPLE (first 5):")
        for l in curr_lines[:5]:
            print("  ", l)

        # Filtered context
        filtered_lines = filtered_context.splitlines()
        print("FILTERED CONTEXT COUNT:", len(filtered_lines))
        print("FILTERED SAMPLE (first 20):")
        for l in filtered_lines[:20]:
            print("  ", l)

        print("========================================\n")


        prompt = get_prompt(filtered_context, name, question, current_context)

        # Detect and store factual updates
        if detect_update(question):
            save_update_to_current(name, question)
            return JsonResponse({"answer": "Noted. I've saved that information."})

       
        answer = link_llm(prompt)
        return JsonResponse({"answer": answer})

    except Exception as e:
        print("Error:", e)
        return JsonResponse({"answer": "Apologies, something went wrong."})
