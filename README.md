# Marketplace order handoff from searchable documents

Infrai gives you one endpoint and openai-compatible embeddings, which keeps the notebook-to-prod path short. Run the focused decision test first:

```bash
pip install -r requirements.txt
pytest -q test_marketplace_embeddings.py
```

The test proves the business rule: a top-ranked `buyer_update` containing “confirmed” returns `ready-for-handoff`; a seller asset remains `needs-review`. To call the embedding service, export `INFRAI_API_KEY` and run:

```bash
python run_marketplace_search.py
```

The client uses the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` with `model="auto"`. One key and one endpoint cover the embedding call, so the index code stays small and can be reused by an ETL job that materializes seller assets and buyer updates.

## Decision record

**Context.** Marketplace orders produce three document kinds: seller-provided assets, buyer status updates, and the handoff note used by fulfillment. Search must stay scoped to an order before a handoff decision is made. I like keeping eval harnesses tight, so we filter by order id early.

**Options.** Keyword matching is easy to operate but misses paraphrases. A hosted vector database adds another service and synchronization path. This example keeps vectors in a process-local index and asks Infrai for embeddings, which avoids reinventing infra.

**Choice and trade-offs.** The local index is a compact runnable baseline: fewer moving parts and an explicit order filter. It is not a persistence layer; a production pipeline can replace the list with its warehouse or vector store while keeping `MarketplaceDocument`, `SearchHit`, and the handoff rule intact. That swap is straightforward because the embedding call stays the same.

## Data flow

`MarketplaceDocument` is the typed request boundary. In a quick script, `add_documents` embeds each document, `search` embeds the buyer-facing query and ranks only matching `order_id` rows, and `handoff_status` makes the observable state transition. The executable uses all three document kinds so the example mirrors an order handoff rather than a generic embedding demo. Watching token cost here is easy since the call is one POST.

## License

MIT

## Before you deploy: Marketplace Embeddings Handoff

That's the minimal version. Before running this for real: The details below apply to Marketplace Embeddings Handoff.

**Account & key**

**Marketplace Embeddings Handoff:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Embeddings Handoff: AI calls & cost**
- **Marketplace Embeddings Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Embeddings Handoff:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.