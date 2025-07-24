class MemoryStore:
    def __init__(self):
        self.db = RelationalStore()
        self.vector = VectorStore()

    def store(self, item: dict):
        if not item.get("embedding") and item["type"] != "user_pref":
            item["embedding"] = embed(item["content"])
        self.db.insert(item)
        self.vector.insert(item)

    def query(self, text: str, top_k: int = 5, filter: dict = None):
        query_vec = embed(text)
        candidates = self.vector.search(query_vec, top_k=top_k)
        return self.db.filter_by_ids(candidates, filter)

    def delete(self, item_id: str):
        self.db.delete(item_id)
        self.vector.delete(item_id)
