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
        self.comedy_themes = [
            {
                "category": "funny_animals",
                "niche": "Animales & Mascotas",
                "hooks": [
                    "POV: Tu gato cuando te atrasas 3 minutos en servirle la comida 💀",
                    "El perro que entendió todo sobre la vida en 5 segundos 😂",
                    "Dramatismo nivel: Este gato después de un susto absurdo 🐱🎭",
                    "Nadie: Absolutamente nadie: Mi perro cuando escucha una bolsa abrirse 🐶⚡",
                    "Prueba irrefutable de que los gatos no son de este planeta 🛸😂"
                ],
                "voiceovers": [
                    "Mira la cara de absoluta indignación. No hay perdón, no hay olvido. Solo juicio silencioso.",
                    "Intentó mantener la dignidad, pero el suelo tenía otros planes. Diez de diez en ejecución.",
                    "Cuando crees que tienes todo bajo control y de pronto... la física decide no colaborar.",
                    "La concentración era máxima. La confianza, indestructible. El resultado... catastróficamente gracioso.",
                    "Ese momento exacto donde se da cuenta de que cometió un grave error de cálculo."
                ],
                "punchlines": [
                    "¿Quién más tiene una mascota así de dramática? 😂",
                    "Etiqueta a tu amigo que reacciona exactamente igual 🐶",
                    "Dime que no soy el único que no puede parar de reír 💀"
                ],
                "tags": ["Shorts", "Humor", "AnimalesGraciosos", "Gatos", "Perros", "Memes", "Risas"]
            },
            {
                "category": "relatable_fails",
                "niche": "Fails Cotidianos",
                "hooks": [
                    "POV: Yo intentando ser productivo un lunes a las 8 AM 💀",
                    "Nivel de confianza: 1000%. Nivel de habilidad: 0% 😂",
                    "Dime que tienes mala suerte sin decirme que tienes mala suerte... 🤡",
                    "Cuando dices 'tranquilo, yo sé exactamente lo que hago' 😭💥",
                    "Mi última neurona intentando sobrevivir el día de hoy 🧠⚡"
                ],
                "voiceovers": [
                    "Todo iba según el plan hasta que el universo decidió darle una lección de humildad.",
                    "No se puede culpar al esfuerzo, pero el resultado merece un premio al intento más torpe del año.",
                    "Segundos antes de la tragedia. La sonrisa todavía en el rostro. Inocencia pura.",
                    "Si alguna vez te sientes torpe, recuerda que este video existe para hacerte sentir mejor.",
                    "La gravedad nunca descansa, y en este momento decidió cobrar venganza personal."
                ],
                "punchlines": [
                    "¿Te ha pasado algo así? Cuéntalo en comentarios 😂👇",
                    "Comparte con esa persona que siempre es un desastre andante 💀",
                    "Dale like si te dolió hasta a ti de solo verlo 😭"
                ],
                "tags": ["Shorts", "Fails", "Comedia", "Risas", "MalaSuerte", "HumorViral", "Relatable"]
            },
            {
                "category": "unexpected_comedy",
                "niche": "Situaciones Absurdas",
                "hooks": [
                    "El plot twist más inesperado que verás en todo tu día 😂",
                    "¿Por qué los hombres vivimos menos? Ejemplo número 47 💀",
                    "Cuando el plan B es 100 veces peor que el plan A 🤡",
                    "La tranquilidad duró exactamente 2 segundos y medio ⏳💥",
                    "No puedo con este nivel de caos en tan poco tiempo 😭"
                ],
                "voiceovers": [
                    "Pensó que nadie lo estaba grabando. El destino tenía otros planes y una cámara en alta definición.",
                    "Hay malas ideas, peores ideas, y luego está esta genialidad absoluta que salió como debía salir.",
                    "Miren ese instante de duda. Supo que no debía hacerlo, y aún así, la curiosidad ganó.",
                    "El verdadero significado de 'espera lo inesperado'. Nadie en la sala estaba preparado para esto.",
                    "Un aplauso para este genio incomprendido que desafió la lógica y perdió con estilo."
                ],
                "punchlines": [
                    "Comenta del 1 al 10 qué tan épico fue el remate 😂",
                    "Sígueme para tu dosis diaria de risas sin sentido 🚀",
                    "¿Esperabas ese final o te tomó por sorpresa? 💀"
                ],
                "tags": ["Shorts", "ComediaViral", "Memes", "PlotTwist", "HumorLatino", "RisasMil"]
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

    def generate_batch_scripts(self, count: int = 3, custom_topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generates a batch of distinct funny scripts (e.g. 3 unique videos per run).
        Ensures diverse comedic categories and unique hooks.
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
                hook = f"POV: {custom_topic} 💀"

            full_speech = f"{hook} {voiceover} {punchline}"

            scripts.append({
                "category": theme["category"],
                "niche": theme["niche"],
                "title": title[:95],
                "hook": hook,
                "voiceover": voiceover,
                "points": [
                    voiceover,
                    f"Situación: {hook}",
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
