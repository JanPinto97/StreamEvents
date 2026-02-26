import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .services.retriever import retrieve_events
from .services.llm_ollama import generate
from .services.prompts import build_prompt


def chat_page(request):
    return render(request, "assistant_chat/chat.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    ranked = retrieve_events(message, only_future=only_future, k=5)
    candidates = []
    for e, score in ranked:
        candidates.append({
            "id": int(e.pk),
            "title": e.title,
            "scheduled_date": e.scheduled_date.isoformat() if e.scheduled_date else None,
            "category": e.category,
            "url": e.get_absolute_url(),
            "score": round(float(score), 3),
        })

    # PROMPT SIMPLE TEMPORAL
    context_text = "\n".join([
        f"- {c['title']} ({c['category']}) el {c['scheduled_date']}"
        for c in candidates
    ])

    prompt = f"""
    Ets un assistent que recomana esdeveniments.

    Usuari: {message}

    Esdeveniments disponibles:
    {context_text}

    Recomana només entre aquests esdeveniments.
    Respon en català.
    """

    ranked = retrieve_events(message, only_future=only_future, k=8)

    candidates = []
    for e, score in ranked:
        candidates.append({
            "id": int(e.pk),
            "title": e.title,
            "scheduled_date": e.scheduled_date.isoformat() if e.scheduled_date else None,
            "category": e.category,
            "tags": e.tags or "",
            "url": e.get_absolute_url(),
            "score": round(float(score), 3),
        })

    prompt = build_prompt(message, candidates)
    llm_text = generate(prompt)

    # Parse JSON del model
    try:
        llm_json = json.loads(llm_text)
    except Exception:
        # fallback segur
        llm_json = {
            "answer": "No he pogut generar una resposta estructurada. Prova amb una consulta més concreta.",
            "recommended_ids": [c["id"] for c in candidates[:3]],
            "follow_up": ""
        }

    # Filtrar IDs inventats
    allowed_ids = {c["id"] for c in candidates}
    recommended_ids = [
        i for i in llm_json.get("recommended_ids", [])
        if i in allowed_ids
    ]

    # Construir cards finals
    final_cards = [c for c in candidates if c["id"] in recommended_ids]

    if not final_cards:
        final_cards = candidates[:3]

    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": final_cards,
    })