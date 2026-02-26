from django.utils import timezone

from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k


def build_event_text(e: Event) -> str:
    return " | ".join(
        [
            (e.title or "").strip(),
            (e.description or "").strip(),
            (e.category or "").strip(),
            (e.tags or "").strip(),
        ]
    ).strip()


def retrieve_events(query: str, only_future: bool = True, k: int = 8, min_score: float = 0.25):
    """
    Retorna [(event_obj, score), ...] ordenat per score desc.
    - only_future: si True, només events amb scheduled_date >= ara
    - k: màxim d'events retornats
    - min_score: llindar mínim per evitar recomanar qualsevol cosa
    """
    query = (query or "").strip()
    if not query:
        return []

    q_vec = embed_text(query)

    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())

    items = []

    # Djongo: fem servir only() per carregar menys camps, i validem embedding com list
    for e in qs.only("id", "title", "scheduled_date", "category", "tags", "embedding"):
        emb = getattr(e, "embedding", None)
        if isinstance(emb, list) and len(emb) > 0:
            items.append((e, emb))

    ranked = cosine_top_k(q_vec, items, k=max(k, 20))
    ranked = [(e, s) for (e, s) in ranked if s >= float(min_score)]
    return ranked[:k]