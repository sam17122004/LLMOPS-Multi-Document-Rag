import os
import sys
import json
from dotenv import load_dotenv

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)

from langchain_groq import ChatGroq

from multi_doc_chat.utils.config_loader import load_config
from multi_doc_chat.logger import GLOBAL_LOGGER as log
from multi_doc_chat.exception.custom_exception import DocumentPortalException


class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys = {}

        raw = os.getenv("apikeyliveclass")

        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    self.api_keys.update(parsed)
                    log.info("Loaded API keys from secret JSON")
            except Exception as e:
                log.warning("Failed parsing secret JSON", error=str(e))

        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                val = os.getenv(key)
                if val:
                    self.api_keys[key] = val

        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            raise DocumentPortalException(f"Missing API keys: {missing}", sys)

    def get(self, key: str) -> str:
        return self.api_keys[key]


class ModelLoader:
    def __init__(self):
        if os.getenv("ENV", "local") != "production":
            load_dotenv()

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()

    # =========================
    # EMBEDDINGS (FREE TIER SAFE)
    # =========================
    def load_embeddings(self):
        model_name = self.config["embedding_model"]["model_name"]

        # 🔥 FORCE SAFE MODEL IF OLD ONE IS USED
        if model_name not in ["gemini-embedding-001", "text-embedding-004"]:
            model_name = "gemini-embedding-001"

        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
        )

    # =========================
    # LLM LOADER
    # =========================
    def load_llm(self):
        llm_block = self.config["llm"]
        provider = os.getenv("LLM_PROVIDER", "google")

        if provider not in llm_block:
            raise ValueError(f"Invalid provider: {provider}")

        cfg = llm_block[provider]

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=cfg["model_name"],
                google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
                temperature=cfg.get("temperature", 0.2),
                max_output_tokens=cfg.get("max_output_tokens", 1024),
            )

        if provider == "groq":
            return ChatGroq(
                model=cfg["model_name"],
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
                temperature=cfg.get("temperature", 0.2),
            )

        raise ValueError(f"Unsupported provider: {provider}")