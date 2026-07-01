from __future__ import annotations

import json
import sys
import uuid
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Iterable, List, Optional, Dict, Any

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from multi_doc_chat.utils.model_loader import ModelLoader
from multi_doc_chat.logger.custom_logger import GLOBAL_LOGGER as log
from multi_doc_chat.exception.custom_exception import DocumentPortalException
from multi_doc_chat.utils.file_io import save_uploaded_files
from multi_doc_chat.utils.document_ops import load_documents


# =========================
# SESSION ID
# =========================
def generate_session_id() -> str:
    return f"session_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"


# =========================
# SAFE EMBED RETRY WRAPPER
# =========================
def retry_embed(func, *args, retries=5):
    for i in range(retries):
        try:
            return func(*args)
        except Exception as e:
            if "429" in str(e):
                wait = 20 + (i * 10)
                log.warning("Rate limit hit, sleeping", wait=wait)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Embedding failed after retries")


# =========================
# INGESTOR
# =========================
class ChatIngestor:
    def __init__(
        self,
        temp_base: str = "data",
        faiss_base: str = "faiss_index",
        use_session_dirs: bool = True,
        session_id: Optional[str] = None,
    ):
        self.model_loader = ModelLoader()

        self.use_session = use_session_dirs
        self.session_id = session_id or generate_session_id()

        self.temp_base = Path(temp_base)
        self.faiss_base = Path(faiss_base)

        self.temp_base.mkdir(parents=True, exist_ok=True)
        self.faiss_base.mkdir(parents=True, exist_ok=True)

        self.temp_dir = self._resolve_dir(self.temp_base)
        self.faiss_dir = self._resolve_dir(self.faiss_base)

        log.info("ChatIngestor ready", session=self.session_id)

    def _resolve_dir(self, base: Path):
        if self.use_session:
            d = base / self.session_id
            d.mkdir(parents=True, exist_ok=True)
            return d
        return base

    # =========================
    # CHUNKING (FREE TIER SAFE)
    # =========================
    def _split(
     self,
     docs: List[Document],
     chunk_size: int = 1400,
     chunk_overlap: int = 100,
)    -> List[Document]:

     splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

     return splitter.split_documents(docs)

    # =========================
    # MAIN PIPELINE
    # =========================
    def built_retriver(
    self,
    uploaded_files: Iterable,
    chunk_size: int = 1400,
    chunk_overlap: int = 100,
    k: int = 5,
    search_type: str = "mmr",
    fetch_k: int = 20,
    lambda_mult: float = 0.5
):
        try:
            paths = save_uploaded_files(uploaded_files, self.temp_dir)
            docs = load_documents(paths)

            if not docs:
                raise ValueError("No documents found")

            chunks = self._split(docs)

            fm = FaissManager(self.faiss_dir, self.model_loader)

            # 🔥 ONLY LOAD OR INIT (NO TEXTS HERE)
            vs = fm.load_or_create()

            # 🔥 ADD IN SMALL BATCHES (CRITICAL FOR FREE TIER)
            batch_size = 3
            total_added = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]

                added = fm.add_documents(batch)
                total_added += added

                time.sleep(2.5)  # 🔥 throttle requests

            log.info("Ingestion complete", added=total_added)

            search_kwargs = {"k": k}

            if search_type == "mmr":
                search_kwargs.update({
                    "fetch_k": fetch_k,
                    "lambda_mult": lambda_mult
                })

            return vs.as_retriever(
                search_type=search_type,
                search_kwargs=search_kwargs
            )

        except Exception as e:
            log.error("Ingestion failed", error=str(e))
            raise DocumentPortalException("Retriever build failed", e)


# =========================
# FAISS MANAGER
# =========================
class FaissManager:
    def __init__(self, index_dir: Path, model_loader: ModelLoader):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.index_dir / "meta.json"
        self.meta = {"rows": {}}

        if self.meta_path.exists():
            try:
                self.meta = json.loads(self.meta_path.read_text())
            except:
                self.meta = {"rows": {}}

        self.emb = model_loader.load_embeddings()
        self.vs: Optional[FAISS] = None

    def _exists(self):
        return (self.index_dir / "index.faiss").exists()

    def _fingerprint(self, text: str, md: Dict[str, Any]) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self.meta, indent=2))

    # =========================
    # LOAD OR INIT
    # =========================
    def load_or_create(self):
        if self._exists():
            self.vs = FAISS.load_local(
            str(self.index_dir),
            self.emb,
            allow_dangerous_deserialization=True,
        )
        else:
            self.vs = FAISS.from_texts(
    texts=["init"],
    embedding=self.emb,
    metadatas=[{"init": True}],
)

        return self.vs
    # =========================
    # ADD DOCUMENTS (SAFE)
    # =========================
    def add_documents(self, docs: List[Document]) -> int:
     new_docs = []

     for d in docs:
        key = self._fingerprint(d.page_content, d.metadata or {})
        if key in self.meta["rows"]:
            continue
        self.meta["rows"][key] = True
        new_docs.append(d)

     if not new_docs:
        return 0

     texts = [d.page_content for d in new_docs]
     metadatas = [d.metadata for d in new_docs]

     embeddings = self.emb.embed_documents(texts)

     self.vs.add_embeddings(
        list(zip(texts, embeddings)),
        metadatas=metadatas
    )

     self.vs.save_local(str(self.index_dir))
     self._save_meta()

     return len(new_docs)