RAG_DOCS = {
    "orders": "orders(order_date, amount) used for revenue forecasting"
}


def retrieve_context(_: str) -> str:
    return RAG_DOCS["orders"]