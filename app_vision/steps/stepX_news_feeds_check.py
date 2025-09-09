from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
import feedparser, re

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

@register_step("NewsFeedsCheckStep")
class NewsFeedsCheckStep(Step):
    """
    Paso de diagnóstico: revisa cada feed RSS y devuelve conteo y títulos.
    Inputs:
      - feeds: lista de URLs RSS
      - max_per_feed: int (default 5)
    Output:
      - feeds_report: lista de {feed, items, titles[]}
      - total_articles: int
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        feeds: List[str] = data.get("feeds") or []
        max_per_feed = int(data.get("max_per_feed", 5))
        if not feeds:
            raise StepError("InputError", "No se proporcionaron feeds RSS")

        report = []
        total = 0
        for f in feeds:
            try:
                d = feedparser.parse(f)
                entries = d.entries[:max_per_feed]
                titles = []
                for e in entries:
                    titles.append({
                        "title": _clean(getattr(e, "title", "")),
                        "published": _clean(getattr(e, "published", "")),
                        "url": getattr(e, "link", "")
                    })
                report.append({
                    "feed": f,
                    "items": len(entries),
                    "titles": titles
                })
                total += len(entries)
            except Exception as e:
                report.append({
                    "feed": f,
                    "items": 0,
                    "error": str(e)
                })

        return {
            "feeds_report": report,
            "total_articles": total
        }



