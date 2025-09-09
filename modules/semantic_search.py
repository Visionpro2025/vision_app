from __future__ import annotations
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss, numpy as np
from config.settings import SEM

_model = None
_index = None
_docs: List[str] = []


def init_index():
    global _model, _index
    if _model is None:
        _model = SentenceTransformer(SEM.embedding_model)


def build_corpus(docs: List[str]):
    global _docs, _index
    init_index()
    _docs = docs
    emb = _model.encode(docs, normalize_embeddings=True)
    _index = faiss.IndexFlatIP(emb.shape[1])
    _index.add(np.array(emb, dtype='float32'))


def query(text: str, k: int = None) -> List[Tuple[str,float]]:
    global _index, _docs
    if k is None: k = SEM.top_k
    if _index is None or not _docs:
        return []
    vec = _model.encode([text], normalize_embeddings=True)
    D,I = _index.search(np.array(vec, dtype='float32'), k)
    return [( _docs[i], float(D[0][j]) ) for j,i in enumerate(I[0])]
