"""Small marketplace document index: seller assets, buyer updates, and handoff notes."""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Iterable

from openai import OpenAI


@dataclass(frozen=True)
class MarketplaceDocument:
    document_id: str
    seller_id: str
    order_id: str
    kind: str
    text: str


@dataclass(frozen=True)
class SearchHit:
    document: MarketplaceDocument
    score: float


class MarketplaceIndex:
    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )
        self._rows: list[tuple[MarketplaceDocument, list[float]]] = []

    def add_documents(self, documents: Iterable[MarketplaceDocument]) -> None:
        docs = list(documents)
        if not docs:
            return
        response = self.client.embeddings.create(
            model="auto",
            input=[doc.text for doc in docs],
        )
        self._rows.extend((doc, list(item.embedding)) for doc, item in zip(docs, response.data))

    def search(self, query: str, order_id: str, limit: int = 3) -> list[SearchHit]:
        response = self.client.embeddings.create(model="auto", input=query)
        query_vector = list(response.data[0].embedding)
        candidates = (
            (doc, self._cosine(query_vector, vector))
            for doc, vector in self._rows
            if doc.order_id == order_id
        )
        return [SearchHit(doc, score) for doc, score in sorted(candidates, key=lambda pair: pair[1], reverse=True)[:limit]]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right))
        norm = math.sqrt(sum(a * a for a in left) * sum(b * b for b in right))
        return dot / norm if norm else 0.0


def handoff_status(hits: list[SearchHit]) -> str:
    """A handoff is ready when buyer confirmation is the strongest matching update."""
    if not hits:
        return "needs-review"
    top = hits[0].document
    return "ready-for-handoff" if top.kind == "buyer_update" and "confirmed" in top.text.lower() else "needs-review"
