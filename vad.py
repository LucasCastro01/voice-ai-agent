import numpy as np
import torch
from silero_vad import load_silero_vad

model = load_silero_vad()

SILENCE_THRESHOLD = 0.5   # probabilidade mínima para considerar voz
SILENCE_DURATION_MS = 800 # ms de silêncio para considerar fim de fala
CHUNK_MS = 32          # duração de cada chunk do microfone


def _tem_voz(chunk_pcm: bytes, sample_rate: int) -> bool:
    audio = np.frombuffer(chunk_pcm, dtype=np.int16).astype(np.float32) / 32768.0
    prob = model(torch.tensor(audio), sample_rate).item()
    return prob >= SILENCE_THRESHOLD


class VADBuffer:
    """
    Acumula chunks de áudio e detecta quando o cliente parou de falar.
    Retorna o áudio completo da fala quando detecta fim de fala.
    """

    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self._buffer: list[bytes] = []
        self._silence_ms = 0
        self._falando = False

    def adicionar_chunk(self, chunk_pcm: bytes) -> bytes | None:
        """
        Retorna o áudio completo da fala quando o cliente para de falar.
        Retorna None enquanto o cliente ainda está falando (ou em silêncio inicial).
        """
        if _tem_voz(chunk_pcm, self.sample_rate):
            self._falando = True
            self._silence_ms = 0
            self._buffer.append(chunk_pcm)

        elif self._falando:
            self._buffer.append(chunk_pcm)
            self._silence_ms += CHUNK_MS

            if self._silence_ms >= SILENCE_DURATION_MS:
                audio = b"".join(self._buffer)
                self._resetar()
                return audio

        return None

    def _resetar(self):
        self._buffer = []
        self._silence_ms = 0
        self._falando = False