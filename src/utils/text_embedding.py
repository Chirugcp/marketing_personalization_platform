from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np

from src.utils.config import settings


class Embedder:
    def __init__(self) -> None:
        self.model = None
        self.dim = settings.vector_dim
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(settings.embedding_model)
            probe = self.model.encode(['probe'], normalize_embeddings=True)
            self.dim = int(np.array(probe).shape[1])
        except Exception:
            self.model = None

    def _fallback_encode_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype='float32')
        tokens = text.lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode('utf-8')).digest()
            for i in range(self.dim):
                vec[i] += digest[i % len(digest)] / 255.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        texts_list = list(texts)
        if self.model is not None:
            vectors = self.model.encode(texts_list, normalize_embeddings=True)
            return np.array(vectors, dtype='float32')
        return np.vstack([self._fallback_encode_one(text) for text in texts_list]).astype('float32')
