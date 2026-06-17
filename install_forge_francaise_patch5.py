from pathlib import Path
import subprocess
import textwrap
import json

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

BACKEND_PORT = 8797
FRONTEND_PORT = 5197

GIT_NAME = "web-lizard"
GIT_EMAIL = "web-lizard@users.noreply.github.com"


def clean(content: str) -> str:
    return textwrap.dedent(content).lstrip("\n").rstrip() + "\n"


def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    print(f"written: {rel_path}")


def mkdir(rel_path: str) -> None:
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    print(f"dir: {rel_path}")


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 5")
    print("Step 5/6: audio provider upgrade, cache controls, audio drill, UI polish")
    print(f"root: {ROOT}")
    print("")

    for rel in [
        "backend/app/api",
        "backend/app/models",
        "backend/app/services",
        "backend/app/tts",
        "backend/data/audio_cache",
        "frontend/src/components/audio",
        "frontend/src/pages",
        "frontend/src/stores",
        "scripts",
    ]:
        mkdir(rel)

    w("backend/requirements.txt", """
    fastapi>=0.111.0
    uvicorn[standard]>=0.30.0
    pydantic>=2.7.0
    python-multipart>=0.0.9
    edge-tts>=7.0.0
    """)

    w("backend/app/models/audio.py", """
    from pydantic import BaseModel, Field


    class Voice(BaseModel):
        id: str
        label: str
        lang: str = "fr"
        engine: str
        quality: str = "mock"
        gender: str | None = None
        description: str | None = None


    class AudioRequest(BaseModel):
        text: str = Field(min_length=1)
        lang: str = "fr"
        voice_id: str = "mock_fr_female"
        speed: float = 1.0
        mode: str = "normal"


    class AudioResponse(BaseModel):
        audio_id: str
        url: str
        cached: bool
        duration_ms: int
        provider: str = "mock"
        format: str = "wav"
        fallback: bool = False


    class AudioCacheEntry(BaseModel):
        audio_id: str
        text: str
        voice_id: str
        mode: str
        provider: str
        format: str
        path: str
        created_at: str
    """)

    w("backend/app/tts/base.py", """
    from abc import ABC, abstractmethod
    from pathlib import Path

    from app.models.audio import AudioRequest, Voice


    class TTSProvider(ABC):
        engine: str = "base"
        extension: str = "wav"

        @abstractmethod
        def voices(self) -> list[Voice]:
            raise NotImplementedError

        @abstractmethod
        def synthesize(self, request: AudioRequest, output_path: Path) -> int:
            raise NotImplementedError
    """)

    w("backend/app/tts/mock_provider.py", """
    from pathlib import Path
    import wave

    from app.models.audio import AudioRequest, Voice
    from app.tts.base import TTSProvider


    class MockProvider(TTSProvider):
        engine = "mock"
        extension = "wav"

        def voices(self) -> list[Voice]:
            return [
                Voice(
                    id="mock_fr_female",
                    label="Voix impériale féminine, mock",
                    engine="mock",
                    quality="dev",
                    gender="female",
                    description="Fallback silence generator for offline development.",
                ),
                Voice(
                    id="mock_fr_male",
                    label="Voix impériale masculine, mock",
                    engine="mock",
                    quality="dev",
                    gender="male",
                    description="Fallback silence generator for offline development.",
                ),
            ]

        def synthesize(self, request: AudioRequest, output_path: Path) -> int:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            sample_rate = 16000
            duration_seconds = 0.45 if request.mode == "normal" else 0.75
            frame_count = int(sample_rate * duration_seconds)
            silence = b"\\x00\\x00" * frame_count

            with wave.open(str(output_path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(silence)

            return int(duration_seconds * 1000)
    """)

    w("backend/app/tts/edge_provider.py", """
    import asyncio
    from pathlib import Path

    from app.models.audio import AudioRequest, Voice
    from app.tts.base import TTSProvider


    EDGE_VOICES = [
        {
            "id": "edge_fr_denise",
            "name": "fr-FR-DeniseNeural",
            "label": "Denise Neural, France",
            "gender": "female",
        },
        {
            "id": "edge_fr_henri",
            "name": "fr-FR-HenriNeural",
            "label": "Henri Neural, France",
            "gender": "male",
        },
        {
            "id": "edge_fr_vivienne",
            "name": "fr-FR-VivienneMultilingualNeural",
            "label": "Vivienne Multilingual, France",
            "gender": "female",
        },
        {
            "id": "edge_fr_remy",
            "name": "fr-FR-RemyMultilingualNeural",
            "label": "Rémy Multilingual, France",
            "gender": "male",
        },
        {
            "id": "edge_fr_sylvie",
            "name": "fr-CA-SylvieNeural",
            "label": "Sylvie Neural, Canada",
            "gender": "female",
        },
        {
            "id": "edge_fr_antoine",
            "name": "fr-CA-AntoineNeural",
            "label": "Antoine Neural, Canada",
            "gender": "male",
        },
    ]


    class EdgeTTSProvider(TTSProvider):
        engine = "edge"
        extension = "mp3"

        def voices(self) -> list[Voice]:
            return [
                Voice(
                    id=item["id"],
                    label=item["label"],
                    lang="fr",
                    engine="edge",
                    quality="neural-online",
                    gender=item["gender"],
                    description=item["name"],
                )
                for item in EDGE_VOICES
            ]

        def voice_name(self, voice_id: str) -> str:
            for item in EDGE_VOICES:
                if item["id"] == voice_id:
                    return item["name"]
            return "fr-FR-DeniseNeural"

        def rate_for(self, request: AudioRequest) -> str:
            if request.mode == "slow" or request.speed < 0.9:
                return "-25%"
            if request.speed > 1.1:
                return "+15%"
            return "+0%"

        def synthesize(self, request: AudioRequest, output_path: Path) -> int:
            try:
                import edge_tts
            except Exception as exc:
                raise RuntimeError("edge-tts is not installed") from exc

            output_path.parent.mkdir(parents=True, exist_ok=True)
            voice_name = self.voice_name(request.voice_id)
            rate = self.rate_for(request)

            async def run_save() -> None:
                communicate = edge_tts.Communicate(
                    text=request.text,
                    voice=voice_name,
                    rate=rate,
                )
                await communicate.save(str(output_path))

            asyncio.run(run_save())

            # MP3 duration is not parsed in MVP. Good enough for UI metadata.
            return max(600, min(6000, len(request.text) * 70))
    """)

    w("backend/app/services/audio_service.py", """
    from datetime import datetime, timezone
    import hashlib
    import json
    from pathlib import Path
    from typing import Any

    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    from app.core.json_utils import read_json, write_json_atomic
    from app.core.paths import AUDIO_CACHE_ROOT
    from app.models.audio import AudioRequest, AudioResponse, Voice
    from app.tts.edge_provider import EdgeTTSProvider
    from app.tts.mock_provider import MockProvider


    CACHE_INDEX_PATH = AUDIO_CACHE_ROOT / "index.json"


    class AudioService:
        def __init__(self) -> None:
            self.mock_provider = MockProvider()
            self.edge_provider = EdgeTTSProvider()

        def providers(self):
            return {
                "mock": self.mock_provider,
                "edge": self.edge_provider,
            }

        def voices(self) -> list[Voice]:
            voices: list[Voice] = []
            voices.extend(self.edge_provider.voices())
            voices.extend(self.mock_provider.voices())
            return voices

        def provider_for_voice(self, voice_id: str):
            if voice_id.startswith("edge_"):
                return self.edge_provider
            return self.mock_provider

        def audio_id(self, request: AudioRequest, provider_engine: str) -> str:
            payload = request.model_dump()
            payload["provider_engine"] = provider_engine
            raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
            return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

        def cache_index(self) -> dict[str, Any]:
            if not CACHE_INDEX_PATH.exists():
                return {"items": []}

            try:
                return read_json(CACHE_INDEX_PATH)
            except Exception:
                return {"items": []}

        def save_cache_entry(self, entry: dict[str, Any]) -> None:
            payload = self.cache_index()
            items = payload.setdefault("items", [])
            items = [item for item in items if item.get("audio_id") != entry["audio_id"]]
            items.append(entry)
            payload["items"] = items[-1000:]
            write_json_atomic(CACHE_INDEX_PATH, payload)

        def cache_summary(self) -> dict[str, Any]:
            payload = self.cache_index()
            items = payload.get("items", [])
            files = list(AUDIO_CACHE_ROOT.glob("*.mp3")) + list(AUDIO_CACHE_ROOT.glob("*.wav"))
            total_bytes = sum(path.stat().st_size for path in files if path.exists())

            return {
                "count": len(files),
                "indexed_count": len(items),
                "total_bytes": total_bytes,
                "total_mb": round(total_bytes / 1024 / 1024, 3),
                "items": items[-50:],
            }

        def clear_cache(self) -> dict[str, Any]:
            removed = 0

            for path in list(AUDIO_CACHE_ROOT.glob("*.mp3")) + list(AUDIO_CACHE_ROOT.glob("*.wav")):
                try:
                    path.unlink()
                    removed += 1
                except FileNotFoundError:
                    pass

            write_json_atomic(CACHE_INDEX_PATH, {"items": []})

            return {
                "removed": removed,
                "ok": True,
            }

        def speak(self, request: AudioRequest) -> AudioResponse:
            primary_provider = self.provider_for_voice(request.voice_id)
            provider = primary_provider
            fallback = False

            audio_id = self.audio_id(request, provider.engine)
            extension = provider.extension
            output_path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"

            cached = output_path.exists()
            duration_ms = 0

            if not cached:
                try:
                    duration_ms = provider.synthesize(request, output_path)
                except Exception:
                    fallback = True
                    provider = self.mock_provider
                    audio_id = self.audio_id(request, "mock-fallback")
                    extension = provider.extension
                    output_path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"
                    cached = output_path.exists()

                    if not cached:
                        duration_ms = provider.synthesize(request, output_path)
                    else:
                        duration_ms = 450
            else:
                duration_ms = max(450, min(6000, len(request.text) * 70))

            self.save_cache_entry(
                {
                    "audio_id": audio_id,
                    "text": request.text,
                    "voice_id": request.voice_id,
                    "mode": request.mode,
                    "provider": provider.engine,
                    "format": extension,
                    "path": str(output_path),
                    "fallback": fallback,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            return AudioResponse(
                audio_id=audio_id,
                url=f"/api/audio/file/{audio_id}",
                cached=cached,
                duration_ms=duration_ms,
                provider=provider.engine,
                format=extension,
                fallback=fallback,
            )

        def file_path(self, audio_id: str) -> Path:
            for extension in ["mp3", "wav"]:
                path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"
                if path.exists():
                    return path
            raise HTTPException(status_code=404, detail="Audio file not found")

        def file_response(self, audio_id: str) -> FileResponse:
            path = self.file_path(audio_id)
            media_type = "audio/mpeg" if path.suffix == ".mp3" else "audio/wav"
            return FileResponse(path, media_type=media_type, filename=path.name)


    def get_audio_service() -> AudioService:
        return AudioService()
    """)

    w("backend/app/api/audio.py", """
    from fastapi import APIRouter

    from app.models.audio import AudioRequest
    from app.services.audio_service import get_audio_service

    router = APIRouter(tags=["audio"])


    @router.get("/audio/voices")
    def voices():
        return [voice.model_dump() for voice in get_audio_service().voices()]


    @router.get("/audio/cache")
    def cache_summary():
        return get_audio_service().cache_summary()


    @router.delete("/audio/cache")
    def clear_cache():
        return get_audio_service().clear_cache()


    @router.post("/audio/speak")
    def speak(request: AudioRequest):
        return get_audio_service().speak(request)


    @router.get("/audio/file/{audio_id}")
    def audio_file(audio_id: str):
        return get_audio_service().file_response(audio_id)
    """)

    w("frontend/src/stores/audioStore.ts", """
    import { defineStore } from 'pinia'
    import { apiDelete, apiGet, apiPost, publicApiUrl } from '../lib/api'
    import { useSettingsStore } from './settingsStore'

    export const useAudioStore = defineStore('audio', {
      state: () => ({
        cache: null as any | null,
        loading: false,
        error: null as string | null,
        lastResult: null as any | null,
      }),
      actions: {
        async loadCache() {
          this.loading = true
          this.error = null

          try {
            this.cache = await apiGet('/audio/cache')
          } catch (error) {
            this.error = error instanceof Error ? error.message : String(error)
          } finally {
            this.loading = false
          }
        },
        async clearCache() {
          this.loading = true
          this.error = null

          try {
            await apiDelete('/audio/cache')
            await this.loadCache()
          } catch (error) {
            this.error = error instanceof Error ? error.message : String(error)
          } finally {
            this.loading = false
          }
        },
        async speak(text: string, mode = 'normal') {
          const settings = useSettingsStore()
          this.loading = true
          this.error = null

          try {
            const result = await apiPost<any>('/audio/speak', {
              text,
              lang: 'fr',
              voice_id: settings.voiceId,
              speed: mode === 'slow' ? 0.75 : 1,
              mode,
            })

            this.lastResult = result
            const audio = new Audio(publicApiUrl(result.url))
            await audio.play()
            return result
          } catch (error) {
            this.error = error instanceof Error ? error.message : String(error)
            throw error
          } finally {
            this.loading = false
          }
        },
      },
    })
    """)

    w("frontend/src/lib/api.ts", """
    export const apiBase = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8797/api'

    export async function apiGet<T>(path: string): Promise<T> {
      const response = await fetch(apiBase + path)

      if (!response.ok) {
        throw new Error('GET ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
      const response = await fetch(apiBase + path, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('POST ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
      const response = await fetch(apiBase + path, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('PATCH ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export async function apiDelete<T>(path: string): Promise<T> {
      const response = await fetch(apiBase + path, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('DELETE ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export function publicApiUrl(path: string): string {
      return apiBase.replace('/api', '') + path
    }
    """)

    w("frontend/src/components/learning/AudioButton.vue", """
    <script setup lang="ts">
    import { ref } from 'vue'
    import { apiPost, publicApiUrl } from '../../lib/api'
    import { useSettingsStore } from '../../stores/settingsStore'

    const props = defineProps<{
      text: string
      label?: string
      mode?: string
      compact?: boolean
    }>()

    const settings = useSettingsStore()
    const loading = ref(false)
    const fallback = ref(false)

    async function play() {
      loading.value = true
      fallback.value = false

      try {
        const result = await apiPost<{ url: string; fallback?: boolean }>('/audio/speak', {
          text: props.text,
          lang: 'fr',
          voice_id: settings.voiceId,
          speed: props.mode === 'slow' ? 0.75 : 1,
          mode: props.mode ?? 'normal',
        })

        fallback.value = Boolean(result.fallback)
        const audio = new Audio(publicApiUrl(result.url))
        await audio.play()
      } finally {
        loading.value = false
      }
    }
    </script>

    <template>
      <button
        class="audio-button"
        :class="{ compact }"
        type="button"
        :disabled="loading"
        @click="play"
      >
        <span v-if="loading">...</span>
        <span v-else>▶</span>
        {{ label ?? 'Слушать' }}
        <small v-if="fallback">mock</small>
      </button>
    </template>
    """)

    w("frontend/src/components/audio/VoiceSelector.vue", """
    <script setup lang="ts">
    import { computed } from 'vue'
    import { useBootstrapStore } from '../../stores/bootstrapStore'
    import { useSettingsStore } from '../../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    const voices = computed(() => bootstrap.payload?.voices ?? [])
    const edgeVoices = computed(() => voices.value.filter((voice) => voice.engine === 'edge'))
    const mockVoices = computed(() => voices.value.filter((voice) => voice.engine === 'mock'))
    </script>

    <template>
      <div class="voice-selector">
        <label for="voice">Голос</label>
        <select id="voice" :value="settings.voiceId" @change="settings.setVoice(($event.target as HTMLSelectElement).value)">
          <optgroup label="Edge neural online">
            <option v-for="voice in edgeVoices" :key="voice.id" :value="voice.id">
              {{ voice.label }}
            </option>
          </optgroup>
          <optgroup label="Mock fallback">
            <option v-for="voice in mockVoices" :key="voice.id" :value="voice.id">
              {{ voice.label }}
            </option>
          </optgroup>
        </select>

        <p class="voice-note">
          Edge-голоса звучат лучше, но требуют интернет. Mock нужен как аварийный fallback.
        </p>
      </div>
    </template>
    """)

    w("frontend/src/pages/AudioDrillPage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import VoiceSelector from '../components/audio/VoiceSelector.vue'
    import AudioButton from '../components/learning/AudioButton.vue'
    import { apiGet } from '../lib/api'
    import { useAudioStore } from '../stores/audioStore'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const audio = useAudioStore()

    const session = ref<any | null>(null)
    const index = ref(0)
    const showTranslation = ref(false)

    const current = computed(() => session.value?.exercises?.[index.value] ?? null)
    const total = computed(() => session.value?.exercises?.length ?? 0)

    async function load() {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      session.value = await apiGet('/review/local_lizard/session?mode=audio&limit=10')
      index.value = 0
      showTranslation.value = false
      await audio.loadCache()
    }

    function next() {
      if (index.value < total.value - 1) {
        index.value += 1
        showTranslation.value = false
      }
    }

    onMounted(load)
    </script>

    <template>
      <section class="page">
        <div class="section-title compact-title">
          <div class="eyebrow">Audio Drill</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Аудио-дрель' : 'Drill audio' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Слушаем французский, повторяем, потом раскрываем перевод.'
                : 'Écoute, répète, puis ouvre la traduction.'
            }}
          </p>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
          <VoiceSelector />
        </div>

        <template v-if="current">
          <div class="practice-head">
            <span>{{ index + 1 }} / {{ total }}</span>
            <span>{{ current.section_id }}</span>
          </div>

          <div class="lesson-progress">
            <div :style="{ width: ((index + 1) / total * 100) + '%' }"></div>
          </div>

          <article class="study-card audio-drill-card">
            <div class="crest-orb">♪</div>
            <div class="eyebrow">Écoute</div>

            <h2>{{ current.audio_text }}</h2>

            <div class="audio-grid">
              <AudioButton :text="current.audio_text" label="Normal" />
              <AudioButton :text="current.audio_text" label="Lentement" mode="slow" />
            </div>

            <button class="ghost-button wide" type="button" @click="showTranslation = !showTranslation">
              {{ showTranslation ? 'Скрыть перевод' : 'Показать перевод' }}
            </button>

            <div v-if="showTranslation" class="result-box good">
              <strong>{{ current.prompt?.ru }}</strong>
              <p>{{ current.explanation?.ru }}</p>
            </div>

            <button class="primary-button" type="button" @click="next">
              {{ settings.uiLanguage === 'ru' ? 'Следующее' : 'Suivant' }}
            </button>
          </article>
        </template>

        <div v-if="audio.cache" class="study-card">
          <h2>Audio cache</h2>
          <div class="stat-grid">
            <div>
              <strong>{{ audio.cache.count }}</strong>
              <span>files</span>
            </div>
            <div>
              <strong>{{ audio.cache.total_mb }}</strong>
              <span>mb</span>
            </div>
            <div>
              <strong>{{ audio.cache.indexed_count }}</strong>
              <span>indexed</span>
            </div>
          </div>
          <button class="ghost-button wide" type="button" @click="audio.clearCache">
            Очистить кэш
          </button>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/router/index.ts", """
    import { createRouter, createWebHistory } from 'vue-router'

    import ThronePage from '../pages/ThronePage.vue'
    import CampaignPage from '../pages/CampaignPage.vue'
    import SectionPage from '../pages/SectionPage.vue'
    import LessonPage from '../pages/LessonPage.vue'
    import PracticePage from '../pages/PracticePage.vue'
    import AudioDrillPage from '../pages/AudioDrillPage.vue'
    import CodexPage from '../pages/CodexPage.vue'
    import VulgarLibraryPage from '../pages/VulgarLibraryPage.vue'
    import ProfilePage from '../pages/ProfilePage.vue'

    export const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'throne', component: ThronePage },
        { path: '/campaign', name: 'campaign', component: CampaignPage },
        { path: '/section/:sectionId', name: 'section', component: SectionPage },
        { path: '/lesson/:lessonId', name: 'lesson', component: LessonPage },
        { path: '/practice', name: 'practice', component: PracticePage },
        { path: '/audio', name: 'audio', component: AudioDrillPage },
        { path: '/codex', name: 'codex', component: CodexPage },
        { path: '/vulgar', name: 'vulgar', component: VulgarLibraryPage },
        { path: '/profile', name: 'profile', component: ProfilePage },
      ],
    })
    """)

    w("frontend/src/components/layout/BottomNav.vue", """
    <script setup lang="ts">
    import { useSettingsStore } from '../../stores/settingsStore'

    const settings = useSettingsStore()
    </script>

    <template>
      <nav class="bottom-nav">
        <RouterLink to="/">{{ settings.uiLanguage === 'ru' ? 'Трон' : 'Trône' }}</RouterLink>
        <RouterLink to="/campaign">{{ settings.uiLanguage === 'ru' ? 'Уроки' : 'Leçons' }}</RouterLink>
        <RouterLink to="/practice">{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</RouterLink>
        <RouterLink to="/audio">{{ settings.uiLanguage === 'ru' ? 'Аудио' : 'Audio' }}</RouterLink>
        <RouterLink to="/profile">{{ settings.uiLanguage === 'ru' ? 'Профиль' : 'Profil' }}</RouterLink>
      </nav>
    </template>
    """)

    w("frontend/src/pages/ThronePage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import { RouterLink } from 'vue-router'
    import AudioButton from '../components/learning/AudioButton.vue'
    import { apiGet } from '../lib/api'
    import { ui } from '../lib/i18n'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
    })

    const profile = computed(() => bootstrap.payload?.profile)
    const firstLesson = computed(() => bootstrap.payload?.sections?.[0]?.lessons?.[0] ?? 'greetings_001')
    </script>

    <template>
      <section class="page throne-page">
        <div class="hero-card">
          <div class="crest-orb">♛</div>
          <div class="eyebrow">Forge Française</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Тронный зал' : 'Salle du trône' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Мобильная имперская кузница французского. Без перегруза, но с короной.'
                : 'Une forge mobile et impériale pour apprendre le français.'
            }}
          </p>

          <div class="profile-strip" v-if="profile">
            <span>{{ profile.display_name }}</span>
            <strong>{{ profile.rank_id }}</strong>
          </div>

          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>

          <div class="hero-actions">
            <RouterLink class="primary-button" :to="'/lesson/' + firstLesson">
              {{ ui('continue', settings.uiLanguage) }}
            </RouterLink>
            <AudioButton text="Bonjour, monsieur." :label="ui('listen', settings.uiLanguage)" />
          </div>
        </div>

        <div class="quick-grid">
          <RouterLink class="quick-card" to="/practice">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? '5 быстрых ударов по хаосу' : 'Cinq coups rapides contre le chaos' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/audio">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Аудио' : 'Audio' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Слушать, повторять, запоминать' : 'Écouter, répéter, retenir' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/vulgar">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/codex">
            <strong>{{ ui('codex', settings.uiLanguage) }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Артикли, de и прочая магия' : 'Articles, de et autres mystères' }}</span>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/ProfilePage.vue", """
    <script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import VoiceSelector from '../components/audio/VoiceSelector.vue'
    import { apiGet } from '../lib/api'
    import { useAudioStore } from '../stores/audioStore'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const audio = useAudioStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
      await audio.loadCache()
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Profil</div>
          <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Интерфейс' : 'Interface' }}</h2>
          <button class="primary-button" type="button" @click="settings.toggleLanguage">
            {{ settings.uiLanguage === 'ru' ? 'Переключить на французский' : 'Passer en russe' }}
          </button>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Прогресс' : 'Progression' }}</h2>
          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
          <VoiceSelector />
        </div>

        <div class="study-card">
          <h2>Audio cache</h2>
          <div class="stat-grid" v-if="audio.cache">
            <div>
              <strong>{{ audio.cache.count }}</strong>
              <span>files</span>
            </div>
            <div>
              <strong>{{ audio.cache.total_mb }}</strong>
              <span>mb</span>
            </div>
            <div>
              <strong>{{ audio.cache.indexed_count }}</strong>
              <span>indexed</span>
            </div>
          </div>
          <button class="ghost-button wide" type="button" @click="audio.clearCache">
            Очистить аудио-кэш
          </button>
        </div>

        <div class="study-card" v-if="summary?.weak_topics?.length">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Слабые темы' : 'Points faibles' }}</h2>
          <div class="chip-row">
            <span v-for="tag in summary.weak_topics" :key="tag" class="stat-chip">{{ tag }}</span>
          </div>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/styles/tokens.css", """
    :root {
      --imperial-black: #171717;
      --deep-black: #0b0d0c;
      --panel-black: rgba(14, 17, 15, 0.92);
      --sovereign-green: #255b32;
      --emerald-green: #2f7a45;
      --bone-white: #e8e2d8;
      --cloth-white: #c9c3ba;
      --antique-gold: #b08a45;
      --muted-gold: #7f6a3c;
      --danger-red: #8a2d2d;
      --text-main: #f5f0e8;
      --text-muted: #b9b2a7;
      --radius-lg: 24px;
      --radius-md: 18px;
      --shadow-soft: 0 18px 50px rgba(0, 0, 0, 0.35);
      --bottom-nav-height: 72px;
    }
    """)

    w("frontend/src/styles/base.css", """
    * {
      box-sizing: border-box;
    }

    html,
    body,
    #app {
      min-height: 100%;
      margin: 0;
    }

    body {
      background:
        radial-gradient(circle at top, rgba(47, 122, 69, 0.22), transparent 34rem),
        linear-gradient(180deg, #0b0d0c 0%, #171717 48%, #0b0d0c 100%);
      color: var(--text-main);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    button,
    input,
    select {
      font: inherit;
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    """)

    w("frontend/src/styles/imperial.css", """
    .imperial-shell {
      position: relative;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: calc(var(--bottom-nav-height) + 18px);
    }

    .shell-main {
      width: min(100%, 980px);
      margin: 0 auto;
      padding: 14px;
    }

    .top-bar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px;
      background: rgba(11, 13, 12, 0.82);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(176, 138, 69, 0.25);
    }

    .top-title,
    h1,
    h2 {
      letter-spacing: 0.02em;
    }

    .top-title {
      font-weight: 800;
    }

    .eyebrow {
      color: var(--antique-gold);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .page {
      display: grid;
      gap: 14px;
    }

    .hero-card,
    .study-card,
    .soft-card,
    .quick-card,
    .lesson-tile {
      border: 1px solid rgba(232, 226, 216, 0.12);
      background:
        linear-gradient(135deg, rgba(37, 91, 50, 0.28), transparent 38%),
        var(--panel-black);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
    }

    .hero-card {
      min-height: calc(100vh - 190px);
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 16px;
      padding: 26px;
    }

    .hero-card h1,
    .section-title h1 {
      margin: 0;
      font-size: clamp(2rem, 12vw, 4.6rem);
      line-height: 0.95;
    }

    .compact-title h1 {
      font-size: clamp(1.5rem, 8vw, 2.6rem);
    }

    .hero-card p,
    .section-title p,
    .study-card p,
    .voice-note {
      color: var(--text-muted);
      line-height: 1.55;
    }

    .voice-note {
      margin: 0;
      font-size: 0.86rem;
    }

    .crest-orb {
      width: 72px;
      height: 72px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(176, 138, 69, 0.55);
      border-radius: 50%;
      background: radial-gradient(circle, rgba(176, 138, 69, 0.35), rgba(37, 91, 50, 0.25));
      font-size: 2rem;
    }

    .profile-strip,
    .practice-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
    }

    .practice-head {
      color: var(--antique-gold);
      font-size: 0.82rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    .hero-actions,
    .quick-grid,
    .option-grid,
    .button-row,
    .audio-grid {
      display: grid;
      gap: 10px;
    }

    .button-row {
      grid-template-columns: 1fr auto;
    }

    .audio-grid {
      grid-template-columns: 1fr 1fr;
    }

    .primary-button,
    .audio-button,
    .ghost-button,
    .option-button {
      border: 0;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 800;
    }

    .primary-button,
    .audio-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 48px;
      padding: 0 18px;
    }

    .audio-button.compact {
      min-height: 38px;
      padding: 0 12px;
      font-size: 0.86rem;
    }

    .audio-button small {
      opacity: 0.7;
      font-size: 0.7rem;
    }

    .primary-button {
      color: #071009;
      background: linear-gradient(135deg, var(--bone-white), var(--antique-gold));
    }

    .audio-button {
      color: var(--bone-white);
      background: rgba(47, 122, 69, 0.45);
      border: 1px solid rgba(232, 226, 216, 0.14);
    }

    .ghost-button {
      min-height: 40px;
      padding: 0 14px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
    }

    .ghost-button.active,
    .ghost-button.wide {
      border: 1px solid rgba(176, 138, 69, 0.45);
    }

    .quick-grid {
      grid-template-columns: 1fr;
    }

    .quick-card,
    .lesson-tile,
    .study-card,
    .soft-card {
      padding: 18px;
    }

    .quick-card,
    .lesson-tile {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .lesson-tile-vertical {
      align-items: flex-start;
      flex-direction: column;
    }

    .lesson-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--antique-gold);
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    .quick-card span,
    .lesson-tile span,
    .lesson-tile small {
      display: block;
      margin-top: 4px;
      color: var(--text-muted);
      font-size: 0.92rem;
    }

    .tile-icon {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 16px;
      background: rgba(176, 138, 69, 0.16);
    }

    .card-list {
      display: grid;
      gap: 12px;
    }

    .study-card {
      display: grid;
      gap: 10px;
      min-height: min(420px, calc(100vh - 260px));
      align-content: center;
    }

    .audio-drill-card {
      justify-items: stretch;
    }

    .study-card h2 {
      margin: 0;
      font-size: clamp(1.4rem, 9vw, 2.8rem);
    }

    .transcription {
      color: var(--antique-gold) !important;
      font-weight: 700;
    }

    .muted {
      color: var(--text-muted);
    }

    .mini-details {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.05);
    }

    .option-grid {
      grid-template-columns: 1fr;
    }

    .option-button {
      min-height: 52px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(232, 226, 216, 0.12);
    }

    .option-button.selected {
      outline: 2px solid var(--antique-gold);
    }

    .answer-input,
    .built-phrase {
      width: 100%;
      min-height: 54px;
      padding: 0 16px;
      border-radius: 18px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .answer-input {
      outline: none;
    }

    .built-phrase {
      display: flex;
      align-items: center;
      line-height: 1.4;
    }

    .result-box {
      padding: 14px;
      border-radius: 16px;
    }

    .result-box.good {
      background: rgba(47, 122, 69, 0.24);
    }

    .result-box.bad {
      background: rgba(138, 45, 45, 0.24);
    }

    .codex-row {
      display: grid;
      gap: 4px;
      padding: 10px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .danger-card {
      border-color: rgba(138, 45, 45, 0.45);
    }

    .rudeness {
      width: fit-content;
      padding: 6px 10px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(138, 45, 45, 0.45);
      font-size: 0.8rem;
      font-weight: 900;
    }

    .voice-selector {
      display: grid;
      gap: 8px;
    }

    .voice-selector select {
      width: 100%;
      min-height: 48px;
      padding: 0 14px;
      border-radius: 16px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .sheet-backdrop {
      position: fixed;
      inset: 0;
      z-index: 80;
      display: flex;
      align-items: flex-end;
      background: rgba(0, 0, 0, 0.58);
    }

    .bottom-sheet {
      width: 100%;
      max-height: 76vh;
      overflow: auto;
      padding: 14px 18px 24px;
      border-radius: 28px 28px 0 0;
      border: 1px solid rgba(232, 226, 216, 0.12);
      background: rgba(11, 13, 12, 0.98);
      box-shadow: var(--shadow-soft);
    }

    .sheet-handle {
      width: 54px;
      height: 5px;
      margin: 0 auto 14px;
      border-radius: 999px;
      background: rgba(232, 226, 216, 0.26);
    }

    .sheet-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .sheet-head h2 {
      margin: 0;
    }

    .lesson-progress {
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
    }

    .lesson-progress div {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--sovereign-green), var(--antique-gold));
      transition: width 0.2s ease;
    }

    .lesson-nav-row {
      display: grid;
      grid-template-columns: auto 1fr 1fr;
      gap: 10px;
    }

    .lesson-nav-row .ghost-button,
    .lesson-nav-row .primary-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
    }

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .stat-grid div {
      display: grid;
      gap: 2px;
      padding: 12px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.06);
      text-align: center;
    }

    .stat-grid strong {
      font-size: 1.25rem;
      color: var(--antique-gold);
    }

    .stat-grid span {
      color: var(--text-muted);
      font-size: 0.74rem;
      text-transform: uppercase;
    }

    .stat-chip {
      flex: 0 0 auto;
      padding: 8px 12px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(176, 138, 69, 0.16);
      font-size: 0.82rem;
      font-weight: 800;
    }
    """)

    w("project.config.json", json.dumps({
        "name": "Forge Francaise",
        "public_title_ru": "Имперский мозговыбиватель французского языка",
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "api_base": f"http://127.0.0.1:{BACKEND_PORT}/api",
        "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}",
        "version": "0.5.0",
        "patch": "patch 5: edge tts, audio drill, cache controls"
    }, ensure_ascii=False, indent=2))

    w("README.md", """
    # Forge Française

    Имперский мозговыбиватель французского языка.

    Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

    ## Ports

    Backend:
    http://127.0.0.1:8797/api/health

    Frontend:
    http://127.0.0.1:5197

    ## Быстрый запуск

    scripts\\Forge Francaise Launcher.cmd

    ## Что уже заложено

    - Vue 3 + TypeScript + Vite
    - FastAPI backend
    - JSON content engine
    - profiles / progress / ranks
    - TTS provider architecture
    - edge-tts provider
    - mock fallback provider
    - audio cache API
    - audio drill page
    - vulgar French library
    - mobile-first UI
    - bottom navigation
    - bottom sheet
    - RU / FR UI switch
    - voice selector
    - storage adapter
    - scalable ExerciseRenderer
    - course API
    - section pages
    - lesson card mode
    - expanded A0 content
    - real practice sessions
    - weak topic review
    - progress scoring
    - answer event log

    ## Patch 5

    Patch 5 adds:

    - edge-tts dependency
    - EdgeTTSProvider
    - MP3 audio generation
    - mock fallback if Edge TTS fails
    - audio cache index
    - GET /api/audio/cache
    - DELETE /api/audio/cache
    - AudioDrillPage
    - /audio route
    - stronger VoiceSelector
    - audio cache controls in profile
    - bottom nav audio entry

    Edge voices require internet. If they fail, app falls back to mock.
    """)

    w("scripts/git_push_patch5.cmd", f"""
    @echo off
    cd /d "%~dp0.."
    git config user.name "{GIT_NAME}"
    git config user.email "{GIT_EMAIL}"
    git status --short
    git add .
    git commit -m "patch 5: edge tts audio drill and cache controls"
    git push -u origin main
    """)

    print("")
    print("Running content validation...")
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Git identity...")
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 5: edge tts audio drill and cache controls"])

    if commit_code != 0:
        print("commit failed or nothing to commit")

    print("")
    print("Git push...")
    push_code = run(["git", "push", "-u", "origin", "main"])

    if push_code != 0:
        print("")
        print("GIT PUSH FAILED OR NEEDS AUTH")
        print("Manual command:")
        print(r'cd /d "D:\PYTHON\Forge Francaise"')
        print(r"scripts\git_push_patch5.cmd")

    print("")
    print("PATCH 5 DONE")
    print("Готовность проекта: примерно 80%")
    print("")
    print("Что добавлено:")
    print("- edge-tts provider")
    print("- mp3 audio generation")
    print("- mock fallback")
    print("- audio cache index")
    print("- audio cache API")
    print("- AudioDrillPage")
    print("- /audio route")
    print("- voice selector upgrade")
    print("- profile audio cache controls")
    print("- UI polish")
    print("")
    print("Next patch will be step 6/6: final test/build scripts, diagnostics, MVP polish.")

if __name__ == "__main__":
    main()