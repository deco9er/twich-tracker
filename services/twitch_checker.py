import re
from typing import Tuple
import requests
import config


def extract_channel_name(url: str) -> str:
    patterns = [
        r'twitch\.tv/([^/?]+)',
        r'twitch\.tv/([^/?]+)/?$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1).lower()
    
    return ""


def check_channel_online_api(channel_name: str) -> Tuple[bool, int]:
    try:
        url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"
        headers = {
            "Client-ID": config.TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {config.TWITCH_ACCESS_TOKEN}"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        streams = data.get("data", [])
        if len(streams) > 0:
            viewer_count = streams[0].get("viewer_count", 0)
            return True, viewer_count
        return False, 0
    except Exception as e:
        print(f"⚠️ Ошибка при проверке через API для {channel_name}: {e}")
        return False, 0


def check_channel_status(channel_url: str) -> Tuple[bool, str, str, int]:
    channel_name = extract_channel_name(channel_url)
    if not channel_name:
        return False, "", "unknown", 0
    
    is_online, viewer_count = check_channel_online_api(channel_name)
    status = "online" if is_online else "offline"
    
    if is_online:
        print(f"🟢 Статус канала {channel_name}: ONLINE (через API) | 👥 Зрителей: {viewer_count}")
    else:
        print(f"📴 Статус канала {channel_name}: OFFLINE (через API)")
    
    return True, channel_name, status, viewer_count
