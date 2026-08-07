import os
import time
import requests
from app.core.conf import settings

def deepseek_health_check():
    start = time.time()

    try:
        r = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.ai_api}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "ping"}
                ],
                "max_tokens": 1,
                "stream": False
            },
            timeout=15
        )

        latency = round(time.time() - start, 2)

        return {
            "ok": r.status_code == 200,
            "status_code": r.status_code,
            "latency_sec": latency,
            "response": r.text[:300]
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


#print(deepseek_health_check())