from marketplace_embeddings import MarketplaceDocument, SearchHit, handoff_status


def test_confirmed_buyer_update_allows_order_handoff() -> None:
    doc = MarketplaceDocument("u1", "seller", "order", "buyer_update", "Buyer confirmed the address")
    assert handoff_status([SearchHit(doc, 0.91)]) == "ready-for-handoff"


def test_seller_asset_does_not_allow_handoff() -> None:
    doc = MarketplaceDocument("a1", "seller", "order", "seller_asset", "packing dimensions")
    assert handoff_status([SearchHit(doc, 0.99)]) == "needs-review"
