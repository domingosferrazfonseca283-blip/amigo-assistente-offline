from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request


class ModelUnavailableError(RuntimeError):
    """Nenhum motor de linguagem configurado ou disponível."""


class TextModel:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class VisionModel:
    def describe_image(self, image_path: str, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class OllamaModel(TextModel):
    """Cliente mínimo para um modelo local servido pelo Ollama."""

    model: str = "llama3.2"
    base_url: str = "http://127.0.0.1:11434"
    timeout: float = 120.0

    def generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        req = request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.URLError, TimeoutError) as exc:
            raise ModelUnavailableError(f"Modelo local indisponível: {exc}") from exc
        return str(data.get("response", "")).strip()


@dataclass
class OllamaVisionModel(VisionModel):
    """Visão local via endpoint multimodal do Ollama."""

    model: str = "llava"
    base_url: str = "http://127.0.0.1:11434"
    timeout: float = 120.0

    def describe_image(self, image_path: str, prompt: str) -> str:
        path = Path(image_path)
        if not path.is_file():
            raise ModelUnavailableError(f"Imagem não encontrada: {image_path}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "images": [encoded],
            "stream": False,
        }).encode()
        req = request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.URLError, TimeoutError) as exc:
            raise ModelUnavailableError(f"Modelo visual local indisponível: {exc}") from exc
        return str(data.get("response", "")).strip()


@dataclass
class OpenAICompatibleModel(TextModel):
    """Cliente HTTP genérico para endpoints compatíveis com /v1/chat/completions."""

    endpoint: str
    model: str
    api_key: str | None = None
    timeout: float = 60.0

    def generate(self, prompt: str) -> str:
        body = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(self.endpoint, data=json.dumps(body).encode(), headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.URLError, TimeoutError) as exc:
            raise ModelUnavailableError(f"Modelo online indisponível: {exc}") from exc
        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelUnavailableError("Resposta inválida do modelo online.") from exc


class ModelRouter(TextModel):
    """Escolhe inteligência local primeiro e online apenas quando explicitamente configurado."""

    def __init__(self, local: TextModel | None = None, online: TextModel | None = None,
                 vision_local: VisionModel | None = None) -> None:
        self.local = local
        self.online = online
        self.vision_local = vision_local

    @classmethod
    def from_environment(cls) -> "ModelRouter":
        local_model = os.getenv("NOEMIA_LOCAL_MODEL", "llama3.2")
        local_url = os.getenv("NOEMIA_LOCAL_URL", "http://127.0.0.1:11434")
        local = OllamaModel(local_model, local_url)
        vision_model = os.getenv("NOEMIA_VISION_MODEL", "llava")
        vision_local = OllamaVisionModel(vision_model, local_url)
        online_endpoint = os.getenv("NOEMIA_ONLINE_ENDPOINT")
        online_model = os.getenv("NOEMIA_ONLINE_MODEL")
        online_key = os.getenv("NOEMIA_ONLINE_API_KEY")
        online = OpenAICompatibleModel(online_endpoint, online_model, online_key) if online_endpoint and online_model else None
        return cls(local=local, online=online, vision_local=vision_local)

    def generate(self, prompt: str) -> str:
        failures: list[str] = []
        for backend in (self.local, self.online):
            if backend is None:
                continue
            try:
                response = backend.generate(prompt)
                if response:
                    return response
            except ModelUnavailableError as exc:
                failures.append(str(exc))
        detail = "; ".join(failures) if failures else "nenhum backend configurado"
        raise ModelUnavailableError(f"Noémia não encontrou um modelo disponível: {detail}")

    def describe_image(self, image_path: str, prompt: str = "Descreva objetivamente o que vê nesta imagem.") -> str:
        if self.vision_local is None:
            raise ModelUnavailableError("Nenhum modelo visual local configurado.")
        return self.vision_local.describe_image(image_path, prompt)
