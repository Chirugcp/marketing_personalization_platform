from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np

from src.utils.config import settings

try:
    import faiss  # type: ignore
except Exception:  # noqa: BLE001
    faiss = None


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, ids: list[str], user_ids: list[str], vectors: np.ndarray) -> None:
        raise NotImplementedError

    @abstractmethod
    def similar_users(self, vector: np.ndarray, top_k: int) -> list[str]:
        raise NotImplementedError


class FaissVectorStore(VectorStore):
    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.vector_dim
        self.faiss_index = faiss.IndexFlatIP(self.dim) if faiss is not None else None
        self.numpy_vectors: list[np.ndarray] = []
        self.row_user_ids: list[str] = []
        self.message_ids: list[str] = []

    def upsert(self, ids: list[str], user_ids: list[str], vectors: np.ndarray) -> None:
        if vectors.shape[1] != self.dim:
            raise ValueError(f'Expected vector dim {self.dim}, got {vectors.shape[1]}')
        if self.faiss_index is not None:
            self.faiss_index.add(vectors)
        else:
            self.numpy_vectors.extend(vectors)
        self.row_user_ids.extend(user_ids)
        self.message_ids.extend(ids)

    def similar_users(self, vector: np.ndarray, top_k: int) -> list[str]:
        if not self.row_user_ids:
            return []

        if self.faiss_index is not None:
            query = np.array([vector], dtype='float32')
            _, indices = self.faiss_index.search(query, min(max(top_k * 5, top_k), len(self.row_user_ids)))
            index_iter = indices[0]
        else:
            matrix = np.vstack(self.numpy_vectors).astype('float32')
            scores = matrix @ vector.astype('float32')
            index_iter = np.argsort(scores)[::-1]

        ranked_users: list[str] = []
        seen = set()
        for idx in index_iter:
            idx = int(idx)
            if idx < 0:
                continue
            user_id = self.row_user_ids[idx]
            if user_id not in seen:
                ranked_users.append(user_id)
                seen.add(user_id)
            if len(ranked_users) == top_k:
                break
        return ranked_users


class UserCentroidIndex:
    def __init__(self) -> None:
        self.user_vectors: dict[str, list[np.ndarray]] = defaultdict(list)

    def update(self, user_ids: list[str], vectors: np.ndarray) -> dict[str, np.ndarray]:
        for user_id, vector in zip(user_ids, vectors):
            self.user_vectors[user_id].append(vector)
        return {
            user_id: np.mean(np.stack(vecs), axis=0).astype('float32')
            for user_id, vecs in self.user_vectors.items()
        }
