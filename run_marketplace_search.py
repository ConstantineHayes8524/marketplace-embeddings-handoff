from marketplace_embeddings import MarketplaceDocument, MarketplaceIndex, handoff_status


def main() -> None:
    index = MarketplaceIndex()
    index.add_documents(
        [
            MarketplaceDocument("asset-1", "seller-7", "order-42", "seller_asset", "linen jacket measurements and care instructions"),
            MarketplaceDocument("update-1", "seller-7", "order-42", "buyer_update", "Buyer confirmed size M and delivery address"),
            MarketplaceDocument("handoff-1", "seller-7", "order-42", "order_handoff", "Pack item after buyer confirmation"),
        ]
    )
    hits = index.search("Is the buyer ready for packing?", order_id="order-42")
    print({"status": handoff_status(hits), "top_document": hits[0].document.document_id if hits else None})


if __name__ == "__main__":
    main()
