"""
growth_optimizer.py
-------------------
Comedic Growth Optimizer and viral humor script generator for YouTube Shorts & Reels.
Generates unique, high-retention comedy formats:
- POV Relatable memes
- Hilarious pet & animal fails
- Clumsy & unexpected comedic plot twists
Supports generating batches of 3 completely distinct videos per day without repetition.
"""

import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("GrowthOptimizer")


class GrowthOptimizer:
    def __init__(self, history_file: str = "data/history.json", metrics_file: str = "data/metrics.json"):
        self.history_file = history_file
        self.metrics_file = metrics_file
        self.history: List[Dict[str, Any]] = self._load_json(history_file, default=[])
        self.metrics: Dict[str, Any] = self._load_json(metrics_file, default={})

        # Comedic categories and angle templates
        # Comedic categories and angle templates (focused on real action, fails, and viral humor)
        self.comedy_themes = [
            {
                "category": "viral_fails",
                "niche": "Fails Épicos & Instant Regret",
                "hooks": [
                    "Segundos antes de una tragedia cómica 😂",
                    "Cuando la gravedad decide arruinarte el día 💀",
                    "Nivel de confianza: 1000%. Nivel de habilidad: 0% 😂",
                    "Dime que te salió mal sin decirme que te salió mal 😭",
                    "Cuando dices: tranquilo, yo sé exactamente lo que hago 💥"
                ],
                "voiceovers": [
                    "Todo iba de maravilla hasta que la física y las malas decisiones decidieron aliarse.",
                    "Miren la seguridad con la que empezó. Esa confianza duró exactamente tres segundos.",
                    "No se puede culpar la intención, pero la ejecución merece un trofeo al fail del año.",
                    "El momento exacto donde el cerebro procesa que el plan falló miserablemente.",
                    "Si pensabas que tu día iba mal, agradece no haber estado en sus zapatos."
                ],
                "punchlines": [
                    "Dime en comentarios si te dolió hasta a ti de solo verlo 😂",
                    "Comparte con tu amigo que siempre tiene esta misma suerte 💀",
                    "Califica del uno al diez este aterrizaje forzoso 👇"
                ],
                "tags": ["Shorts", "Fails", "HumorViral", "InstantRegret", "Comedia", "Risas", "Meme"]
            },
            {
                "category": "chaotic_pets",
                "niche": "Mascotas Caóticas & Bloopers",
                "hooks": [
                    "Cuando tu perro activa el modo turbo y fallan los frenos 🐶⚡",
                    "El gato que calculó mal la trayectoria por tres metros 🐱✈️",
                    "Prueba de que a los animales también se les apaga el cerebro 😂",
                    "Mi mascota viviendo en su propia dimensión paralela 🛸😂",
                    "Ese momento de pánico cuando el salto sale terriblemente mal 💀"
                ],
                "voiceovers": [
                    "La aceleración fue digna de Fórmula 1, pero olvidó instalar los frenos de emergencia.",
                    "Ese salto tenía un noventa por ciento de fe y un cero por ciento de cálculo.",
                    "Miren la cara de sorpresa cuando la física se niega a colaborar con sus acrobacias.",
                    "Intentó fingir que nada pasó, pero la dignidad ya se había quedado en el suelo.",
                    "El verdadero significado de actuar primero y pensar después."
                ],
                "punchlines": [
                    "¿Quién más tiene una mascota así de loquita? 😂",
                    "Etiqueta al dueño de una mascota que hace exactamente esto 🐶",
                    "No puedo parar de reír con ese final épico 💀"
                ],
                "tags": ["Shorts", "MascotasGraciosas", "Animales", "PerrosChistosos", "GatosLocos", "Humor"]
            },
            {
                "category": "instant_karma",
                "niche": "Karma Instantáneo & Risas",
                "hooks": [
                    "El karma instantáneo más rápido de la historia ⚡😂",
                    "Cuando el karma te cobra la factura en dos segundos 💀",
                    "El plot twist que absolutamente nadie vio venir 🍿💥",
                    "Por qué los hombres vivimos menos, prueba irrefutable 🤡",
                    "Cuando intentas hacerte el valiente frente a todos y pasa esto 😭"
                ],
                "voiceovers": [
                    "El universo no suele apresurarse, pero hoy decidió dar una lección express en tiempo récord.",
                    "Se sentía el rey del mundo hasta que el destino le recordó quién manda aquí.",
                    "Un aplauso de pie para esta genialidad que no tenía ninguna posibilidad de salir bien.",
                    "Ese instante de duda antes del desastre. Sabía que no debía hacerlo, y aún así lo intentó.",
                    "El remate perfecto que ni el mejor guionista de comedia pudo haber planeado."
                ],
                "punchlines": [
                    "Comenta del uno al diez qué tan merecido fue ese karma 😂",
                    "Comparte si no pudiste contener la risa 🚀",
                    "¿Esperabas ese final o te tomó por sorpresa? 💀"
                ],
                "tags": ["Shorts", "KarmaInstantaneo", "ComediaViral", "PlotTwist", "HumorLatino", "RisasMil"]
            }
        ]

    def _load_json(self, filepath: str, default: Any) -> Any:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _clean_for_speech(self, text: str) -> str:
        """Strips emojis, hashtags, and formatting so spoken audio is clean natural narration."""
        import re
        import unicodedata
        if not text:
            return ""
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\bPOV:\s*', 'Punto de vista: ', text, flags=re.IGNORECASE)
        # Unicode emoji strip
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\ufe0f\u200d]+')
        text = emoji_pattern.sub('', text)
        cleaned_chars = [ch for ch in text if unicodedata.category(ch) not in ('So', 'Sk')]
        text = "".join(cleaned_chars)
        text = re.sub(r'[\~\|\_\=\+\{\}\[\]\<\>\*\^]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_batch_scripts(self, count: int = 3, custom_topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generates a batch of distinct funny scripts (e.g. 3 unique videos per run).
        Ensures diverse comedic categories and unique hooks.
        Spoken audio is 100% clean Spanish narration without reciting emojis or tags aloud.
        """
        scripts = []
        recent_titles = [v.get("title", "") for v in self.history[:10]]

        # Cycle through themes to guarantee variety
        selected_themes = list(self.comedy_themes)
        random.shuffle(selected_themes)

        for i in range(count):
            theme = selected_themes[i % len(selected_themes)]

            # Filter unused hooks
            available_hooks = [h for h in theme["hooks"] if h not in recent_titles]
            hook = random.choice(available_hooks) if available_hooks else random.choice(theme["hooks"])

            voiceover = random.choice(theme["voiceovers"])
            punchline = random.choice(theme["punchlines"])

            title = hook
            if custom_topic and i == 0:
                title = f"{custom_topic} 😂 #Shorts"
                hook = f"Cuando {custom_topic} sale terriblemente gracioso 😂"

            # Clean audio speech narration: natural spoken commentary
            clean_hook = self._clean_for_speech(hook)
            clean_punchline = self._clean_for_speech(punchline)
            full_speech = f"{clean_hook}. {voiceover} {clean_punchline}"

            scripts.append({
                "category": theme["category"],
                "niche": theme["niche"],
                "title": title[:95],
                "hook": hook,
                "voiceover": voiceover,
                "points": [
                    voiceover,
                    f"Situación: {clean_hook}",
                    punchline
                ],
                "cta": punchline,
                "full_speech": full_speech,
                "tags": theme["tags"]
            })

        return scripts

    def generate_optimized_script(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        """Single script generator."""
        batch = self.generate_batch_scripts(count=1, custom_topic=custom_topic)
        return batch[0]

    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyzes historical video performance and returns data-backed growth recommendations.
        """
        if not self.history:
            return {
                "top_niche": "Fails Épicos & Instant Regret",
                "recommendations": [
                    {
                        "type": "content_strategy",
                        "priority": "HIGH",
                        "title": "Publicar en horarios pico de comedia",
                        "description": "Los shorts cómicos y fails tienen mayor retención entre 12:00 y 15:00 y de 19:00 a 22:00."
                    }
                ]
            }

        # Analyze top niches by views and engagement
        niche_stats = {}
        for item in self.history:
            niche = item.get("niche", "Humor")
            views = item.get("metrics_summary", {}).get("total_views", 0)
            eng = item.get("metrics_summary", {}).get("engagement_rate", 0.0)
            if niche not in niche_stats:
                niche_stats[niche] = {"views": 0, "eng_sum": 0.0, "count": 0}
            niche_stats[niche]["views"] += views
            niche_stats[niche]["eng_sum"] += eng
            niche_stats[niche]["count"] += 1

        top_niche = max(niche_stats.items(), key=lambda x: (x[1]["views"], x[1]["eng_sum"] / max(x[1]["count"], 1)))[0]

        recommendations = [
            {
                "type": "retention_hook",
                "priority": "HIGH",
                "title": f"Potenciar categoría '{top_niche}'",
                "description": f"Los videos de '{top_niche}' lideran en retención. Continúa usando ganchos visuales con texto contrastado en los primeros 2 segundos."
            },
            {
                "type": "audio_optimization",
                "priority": "MEDIUM",
                "title": "Sonido original de comedia + Locución limpia",
                "description": "La mezcla de audio del video original (35%) con la locución neural en español multiplica la tasa de finalización."
            },
            {
                "type": "call_to_action",
                "priority": "MEDIUM",
                "title": "Disparadores de interacción y comentarios",
                "description": "Remates que preguntan '¿Te ha pasado esto?' o 'Comenta del 1 al 10' disparan el engagement."
            }
        ]

        return {
            "top_niche": top_niche,
            "recommendations": recommendations
        }

