import sounddevice as sd
from abc import ABC, abstractmethod

SAMPLE_RATE = 16000
CHUNK_MS = 32
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_MS / 1000)  # 320 amostras por chunk


class AudioSource(ABC):
    @abstractmethod
    def iniciar(self): pass

    @abstractmethod
    def parar(self): pass

    @abstractmethod
    def ler_chunk(self) -> bytes | None:
        """Retorna um chunk PCM 16-bit de ~20ms, ou None se não houver dados."""
        pass


class MicrofoneSource(AudioSource):
    def __init__(self):
        self._stream = None
        self._fila: list[bytes] = []

    def iniciar(self):
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SAMPLES,
            callback=lambda indata, *_: self._fila.append(indata.tobytes()),
        )
        self._stream.start()

    def parar(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()

    def ler_chunk(self) -> bytes | None:
        return self._fila.pop(0) if self._fila else None