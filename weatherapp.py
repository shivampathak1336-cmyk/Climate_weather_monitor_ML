import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# -----------------------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SkyCast Weather",
    page_icon="Sky",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Custom CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(96,165,250,0.18), transparent 30%),
        radial-gradient(circle at bottom left, rgba(14,165,233,0.12), transparent 25%),
        linear-gradient(135deg, #09111f 0%, #12233a 45%, #0a1425 100%);
    min-height: 100vh;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    text-align: center;
    color: #8fc7ea;
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 2rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.weather-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 1.4rem 1.2rem;
    backdrop-filter: blur(14px);
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    height: 100%;
}

.city-header {
    text-align: center;
    margin-bottom: 2rem;
}

.city-name {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    color: #ffffff;
    font-weight: 700;
}

.city-desc {
    font-size: 1rem;
    color: #8fc7ea;
    text-transform: capitalize;
    margin-top: 0.25rem;
}

.card-icon {
    font-size: 2rem;
    margin-bottom: 0.4rem;
}

.card-label {
    font-size: 0.72rem;
    color: #8fc7ea;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-bottom: 0.35rem;
}

.card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
}

.card-unit {
    font-size: 0.95rem;
    color: #b9d8ea;
    font-weight: 400;
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    color: #ffffff;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.10);
}

.rain-banner {
    border-radius: 18px;
    padding: 1.3rem 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
}

.rain-banner-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.2rem;
}

.rain-banner-sub {
    font-size: 0.92rem;
    color: #cbd5e1;
}

.prob-bar-wrap {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    height: 10px;
    width: 100%;
    margin-top: 0.8rem;
    overflow: hidden;
}

.prob-bar-fill {
    height: 10px;
    border-radius: 999px;
    background: linear-gradient(90deg, #38bdf8, #2563eb);
}

.forecast-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1rem 0.7rem;
    text-align: center;
    height: 100%;
}

.forecast-time {
    font-size: 0.75rem;
    color: #8fc7ea;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.forecast-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
}

.forecast-unit {
    font-size: 0.78rem;
    color: #b6c8d6;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(143,199,234,0.35) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    font-size: 1rem !important;
    padding: 0.78rem 1rem !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.38) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.72rem 2rem !important;
    width: 100% !important;
}

.stDataFrame, div[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

div[data-testid="stMarkdownContainer"] p {
    color: #e5eef6;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
API_KEY = "be45314bce4008639d5a2ae0e56f4ba2"
BASE_URL = "https://api.openweathermap.org/data/2.5"
TIMEZONE = "Asia/Kolkata"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def safe_get(url: str, params: dict):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError:
        try:
            message = response.json().get("message", "Request failed")
        except Exception:
            message = "Request failed"
        return None, message
    except requests.exceptions.RequestException as exc:
        return None, str(exc)


@st.cache_data(show_spinner=False, ttl=600)
def get_current_weather(city: str):
    data, error = safe_get(
        f"{BASE_URL}/weather",
        {"q": city, "appid": API_KEY, "units": "metric"},
    )
    if error:
        return None, error

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "description": data["weather"][0]["description"],
        "current_temp": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),
        "temp_min": round(data["main"]["temp_min"]),
        "temp_max": round(data["main"]["temp_max"]),
        "humidity": round(data["main"]["humidity"]),
        "pressure": round(data["main"]["pressure"]),
        "wind_speed": round(data["wind"].get("speed", 0), 1),
        "clouds": round(data.get("clouds", {}).get("all", 0)),
        "visibility_km": round(data.get("visibility", 0) / 1000, 1),
        "sunrise": data["sys"].get("sunrise"),
        "sunset": data["sys"].get("sunset"),
        "timezone_offset": data.get("timezone", 0),
    }, None


@st.cache_data(show_spinner=False, ttl=600)
def get_forecast(city: str, count: int = 8):
    data, error = safe_get(
        f"{BASE_URL}/forecast",
        {"q": city, "appid": API_KEY, "units": "metric"},
    )
    if error:
        return None, error

    forecast_items = []
    timezone = pytz.timezone(TIMEZONE)
    for item in data.get("list", [])[:count]:
        forecast_items.append(
            {
                "time": datetime.fromtimestamp(item["dt"], timezone).strftime("%H:%M"),
                "temp": round(item["main"]["temp"], 1),
                "humidity": round(item["main"]["humidity"]),
                "pressure": round(item["main"]["pressure"]),
                "clouds": round(item.get("clouds", {}).get("all", 0)),
                "pop": round(item.get("pop", 0) * 100),
                "description": item["weather"][0]["description"],
                "rain_mm": round(item.get("rain", {}).get("3h", 0), 1),
            }
        )

    return forecast_items, None


def format_local_time(unix_ts):
    if not unix_ts:
        return "--"
    timezone = pytz.timezone(TIMEZONE)
    return datetime.fromtimestamp(unix_ts, timezone).strftime("%I:%M %p")


def format_city_time(unix_ts, offset_seconds=0, fmt="%I:%M %p"):
    if not unix_ts:
        return "--"
    city_time = datetime.utcfromtimestamp(unix_ts) + timedelta(seconds=offset_seconds)
    return city_time.strftime(fmt)


def is_night(weather):
    current_time = datetime.now(pytz.utc).timestamp()
    sunrise = weather.get("sunrise")
    sunset = weather.get("sunset")
    if sunrise and sunset:
        return current_time < sunrise or current_time > sunset
    return False


def get_scene_config(weather):
    description = weather["description"].lower()
    night = is_night(weather)

    if "thunder" in description:
        return {
            "theme": "scene-storm",
            "title": "Storm pattern overhead",
            "text": "Dense storm clouds are building above the city, so the atmosphere feels heavier and more dramatic right now.",
            "layers": "clouds rain",
        }
    if "rain" in description or "drizzle" in description:
        return {
            "theme": "scene-rain",
            "title": "Rain-washed skyline",
            "text": "The live scene shifts into a rain mood with moving showers and darker cloud cover to match current conditions.",
            "layers": "clouds rain",
        }
    if "mist" in description or "fog" in description or "haze" in description:
        return {
            "theme": "scene-mist",
            "title": "Soft low-visibility atmosphere",
            "text": "A hazy layer settles across the view, reflecting the softer contrast and lower visibility outside.",
            "layers": "fog clouds",
        }
    if night:
        return {
            "theme": "scene-night",
            "title": "Night sky over the city",
            "text": "The detail panel moves into a calm night palette with stars and a cooler sky tone after sunset.",
            "layers": "stars clouds" if weather["clouds"] > 15 else "stars",
        }
    if weather["clouds"] >= 45:
        return {
            "theme": "scene-day-clouds",
            "title": "Clouds drifting through",
            "text": "The background brightens but keeps a muted overcast feel, with layered clouds moving across the sky.",
            "layers": "clouds",
        }
    return {
        "theme": "scene-day-clear",
        "title": "Bright and open conditions",
        "text": "The live background opens into a clear daytime scene with warmer light and a calmer horizon.",
        "layers": "",
    }


def get_weather_mode(weather):
    description = weather["description"].lower()
    night = is_night(weather)

    if "thunder" in description:
        return "night_storm" if night else "storm"
    if "rain" in description or "drizzle" in description:
        return "night_rain" if night else "rain"
    if "mist" in description or "fog" in description or "haze" in description:
        return "night_mist" if night else "mist"
    if "cloud" in description:
        return "night_clouds" if night else "clouds"
    return "night_clear" if night else "clear"


def render_weather_scene(weather):
    mode = get_weather_mode(weather)
    current_time = format_city_time(datetime.now(pytz.utc).timestamp(), weather.get("timezone_offset", 0))
    scene_label = {
        "clear": "Sunny",
        "clouds": "Cloudy",
        "rain": "Rainy",
        "storm": "Stormy",
        "mist": "Misty",
        "night_clear": "Clear Night",
        "night_clouds": "Cloudy Night",
        "night_rain": "Rainy Night",
        "night_storm": "Stormy Night",
        "night_mist": "Misty Night",
    }.get(mode, "Weather")
    scene_html = f"""
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        background: transparent;
        font-family: 'Segoe UI', sans-serif;
    }}
    .phone-scene {{
        width: 100%;
        height: 430px;
        border-radius: 28px;
        overflow: hidden;
        position: relative;
        color: white;
        background: linear-gradient(180deg, #49c6f3 0%, #7fd8fb 45%, #d8efc5 100%);
        box-shadow: 0 18px 36px rgba(0,0,0,0.20);
    }}
    .phone-scene.rain {{
        background: linear-gradient(180deg, #8ab6df 0%, #b9d5ef 45%, #f0dd99 100%);
    }}
    .phone-scene.storm {{
        background: linear-gradient(180deg, #5d6e88 0%, #7d8ca3 35%, #d8c98e 100%);
    }}
    .phone-scene.mist {{
        background: linear-gradient(180deg, #a6bfd2 0%, #cad8e1 50%, #e8e4cb 100%);
    }}
    .phone-scene.clouds {{
        background: linear-gradient(180deg, #6fc5ed 0%, #a9dbf6 50%, #d7efce 100%);
    }}
    .phone-scene.night_clear {{
        background: linear-gradient(180deg, #071427 0%, #163250 52%, #2b5373 100%);
    }}
    .phone-scene.night_clouds {{
        background: linear-gradient(180deg, #0d1b2f 0%, #233b57 52%, #47627d 100%);
    }}
    .phone-scene.night_rain {{
        background: linear-gradient(180deg, #101726 0%, #253349 48%, #514f66 100%);
    }}
    .phone-scene.night_storm {{
        background: linear-gradient(180deg, #0a101c 0%, #1f2a3a 42%, #474556 100%);
    }}
    .phone-scene.night_mist {{
        background: linear-gradient(180deg, #162234 0%, #32465d 50%, #68707b 100%);
    }}
    .top-bar {{
        position: absolute;
        top: 18px;
        left: 22px;
        right: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        opacity: 0.95;
        z-index: 6;
    }}
    .menu {{
        width: 18px;
        height: 12px;
        position: relative;
    }}
    .menu span {{
        position: absolute;
        left: 0;
        right: 0;
        height: 2px;
        background: rgba(255,255,255,0.95);
        border-radius: 999px;
    }}
    .menu span:nth-child(1) {{ top: 0; }}
    .menu span:nth-child(2) {{ top: 5px; width: 80%; }}
    .menu span:nth-child(3) {{ top: 10px; width: 60%; }}
    .clock {{
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(9, 21, 38, 0.24);
        border: 1px solid rgba(255,255,255,0.22);
        backdrop-filter: blur(8px);
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.05em;
    }}
    .hero-copy {{
        position: absolute;
        top: 56px;
        left: 26px;
        right: 26px;
        z-index: 5;
    }}
    .hero-city {{
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 0.3px;
        margin-bottom: 4px;
    }}
    .hero-desc {{
        font-size: 14px;
        text-transform: capitalize;
        opacity: 0.92;
        margin-bottom: 12px;
    }}
    .temp {{
        position: absolute;
        top: 110px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 62px;
        font-weight: 500;
        letter-spacing: 1px;
        text-shadow: 0 8px 26px rgba(10, 25, 40, 0.22);
    }}
    .label {{
        position: absolute;
        top: 230px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        opacity: 0.98;
        text-shadow: 0 10px 24px rgba(10, 25, 40, 0.25);
    }}
    .sun {{
        position: absolute;
        top: 160px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: radial-gradient(circle, #fff7b0 0%, #ffef8e 55%, #ffd75c 100%);
        box-shadow: 0 0 25px rgba(255,238,150,0.8), 0 0 60px rgba(255,238,150,0.35);
        animation: floatSun 3s ease-in-out infinite;
    }}
    .sun:before, .sun:after {{
        content: "";
        position: absolute;
        background: #34495e;
        border-radius: 50%;
        top: 28px;
        width: 6px;
        height: 6px;
    }}
    .sun:before {{ left: 24px; }}
    .sun:after {{ right: 24px; }}
    .sun-smile {{
        position: absolute;
        left: 50%;
        top: 44px;
        width: 24px;
        height: 12px;
        transform: translateX(-50%);
        border-bottom: 3px solid #34495e;
        border-radius: 0 0 24px 24px;
    }}
    .stars {{
        position: absolute;
        inset: 0;
        opacity: 0.9;
    }}
    .star {{
        position: absolute;
        width: 3px;
        height: 3px;
        background: rgba(255,255,255,0.9);
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(255,255,255,0.6);
        animation: twinkle 2.2s ease-in-out infinite alternate;
    }}
    .moon {{
        position: absolute;
        top: 150px;
        left: 50%;
        transform: translateX(-50%);
        width: 74px;
        height: 74px;
        border-radius: 50%;
        background: radial-gradient(circle, #f8f4d2 0%, #e7e1b2 60%, #d2c88d 100%);
        box-shadow: 0 0 22px rgba(250,244,210,0.55);
    }}
    .moon:after {{
        content: "";
        position: absolute;
        width: 58px;
        height: 58px;
        top: 2px;
        left: 18px;
        border-radius: 50%;
        background: rgba(7, 20, 39, 0.95);
    }}
    .cloud {{
        position: absolute;
        top: 150px;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 42px;
        background: #f7fbff;
        border-radius: 999px;
        box-shadow: 0 12px 28px rgba(255,255,255,0.16);
        animation: floatCloud 3.4s ease-in-out infinite;
    }}
    .cloud:before {{
        content: "";
        position: absolute;
        width: 56px;
        height: 56px;
        left: 12px;
        top: -24px;
        background: #f7fbff;
        border-radius: 50%;
    }}
    .cloud:after {{
        content: "";
        position: absolute;
        width: 68px;
        height: 68px;
        right: 14px;
        top: -30px;
        background: #f7fbff;
        border-radius: 50%;
    }}
    .cloud-core {{
        position: absolute;
        width: 58px;
        height: 58px;
        left: 50%;
        top: -20px;
        transform: translateX(-50%);
        background: #f7fbff;
        border-radius: 50%;
    }}
    .cloud-face:before, .cloud-face:after {{
        content: "";
        position: absolute;
        top: 16px;
        width: 6px;
        height: 6px;
        background: #5a6d85;
        border-radius: 50%;
    }}
    .cloud-face:before {{ left: 42px; }}
    .cloud-face:after {{ right: 42px; }}
    .cloud-smile {{
        position: absolute;
        left: 50%;
        top: 22px;
        width: 24px;
        height: 12px;
        transform: translateX(-50%);
        border-bottom: 3px solid #ef7b90;
        border-radius: 0 0 24px 24px;
    }}
    .rain-line {{
        position: absolute;
        width: 2px;
        height: 34px;
        background: linear-gradient(180deg, rgba(255,255,255,0), rgba(255,255,255,0.85));
        transform: rotate(18deg);
        animation: rainFall 1.25s linear infinite;
        opacity: 0.7;
    }}
    .mountain-back {{
        position: absolute;
        left: -10%;
        right: -10%;
        bottom: 88px;
        height: 120px;
        background: #7da8d1;
        clip-path: polygon(0% 100%, 14% 62%, 28% 78%, 40% 48%, 54% 75%, 68% 42%, 82% 70%, 100% 56%, 100% 100%);
    }}
    .mountain-mid {{
        position: absolute;
        left: -6%;
        right: -6%;
        bottom: 52px;
        height: 132px;
        background: #4e86b8;
        clip-path: polygon(0% 100%, 10% 58%, 24% 80%, 38% 40%, 52% 72%, 64% 50%, 79% 78%, 100% 46%, 100% 100%);
    }}
    .mountain-front {{
        position: absolute;
        left: -5%;
        right: -5%;
        bottom: 0;
        height: 150px;
        background: #285e8f;
        clip-path: polygon(0% 100%, 0% 58%, 12% 50%, 24% 72%, 40% 38%, 55% 64%, 70% 52%, 86% 76%, 100% 62%, 100% 100%);
    }}
    .phone-scene.rain .mountain-front,
    .phone-scene.storm .mountain-front,
    .phone-scene.night_rain .mountain-front,
    .phone-scene.night_storm .mountain-front {{ background: #46507b; }}
    .phone-scene.rain .mountain-mid,
    .phone-scene.storm .mountain-mid,
    .phone-scene.night_rain .mountain-mid,
    .phone-scene.night_storm .mountain-mid {{ background: #7983ad; }}
    .phone-scene.rain .mountain-back,
    .phone-scene.storm .mountain-back,
    .phone-scene.night_rain .mountain-back,
    .phone-scene.night_storm .mountain-back {{ background: #a8b3d0; }}
    .mist-band {{
        position: absolute;
        left: -8%;
        right: -8%;
        height: 42px;
        background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.30), rgba(255,255,255,0.04));
        filter: blur(8px);
        animation: driftMist 5s ease-in-out infinite alternate;
    }}
    .mist-band.one {{ bottom: 88px; }}
    .mist-band.two {{ bottom: 32px; animation-duration: 6.2s; }}
    .stats-grid {{
        position: absolute;
        left: 18px;
        right: 18px;
        bottom: 16px;
        z-index: 6;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
    }}
    .stat-card {{
        background: rgba(9, 21, 38, 0.28);
        border: 1px solid rgba(255,255,255,0.16);
        backdrop-filter: blur(8px);
        border-radius: 18px;
        padding: 12px 10px;
        box-shadow: 0 8px 18px rgba(0,0,0,0.16);
    }}
    .stat-label {{
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        opacity: 0.82;
        margin-bottom: 6px;
    }}
    .stat-value {{
        font-size: 18px;
        font-weight: 700;
        line-height: 1.2;
    }}
    @keyframes rainFall {{
        0% {{ transform: translateY(-20px) rotate(18deg); opacity: 0; }}
        25% {{ opacity: 0.75; }}
        100% {{ transform: translateY(150px) rotate(18deg); opacity: 0; }}
    }}
    @keyframes floatSun {{
        0% {{ transform: translateX(-50%) translateY(0); }}
        50% {{ transform: translateX(-50%) translateY(-6px); }}
        100% {{ transform: translateX(-50%) translateY(0); }}
    }}
    @keyframes floatCloud {{
        0% {{ transform: translateX(-50%) translateY(0); }}
        50% {{ transform: translateX(-50%) translateY(-5px); }}
        100% {{ transform: translateX(-50%) translateY(0); }}
    }}
    @keyframes driftMist {{
        from {{ transform: translateX(-10px); }}
        to {{ transform: translateX(14px); }}
    }}
    @keyframes twinkle {{
        from {{ opacity: 0.35; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1.2); }}
    }}
    </style>
    </head>
    <body>
        <div class="phone-scene {mode}">
            <div class="top-bar">
                <div class="menu"><span></span><span></span><span></span></div>
                <div class="clock">{current_time}</div>
            </div>
            <div class="hero-copy">
                <div class="hero-city">{weather['city']}, {weather['country']}</div>
                <div class="hero-desc">{weather['description']}</div>
            </div>
            <div class="temp">{weather['current_temp']}&deg;</div>
    """

    if mode == "clear":
        scene_html += """
            <div class="sun"><div class="sun-smile"></div></div>
        """
    elif mode == "night_clear":
        scene_html += """
            <div class="stars">
                <div class="star" style="left:18%; top:22%; animation-delay:0.2s;"></div>
                <div class="star" style="left:30%; top:14%; animation-delay:1s;"></div>
                <div class="star" style="left:62%; top:18%; animation-delay:0.7s;"></div>
                <div class="star" style="left:78%; top:24%; animation-delay:1.4s;"></div>
                <div class="star" style="left:84%; top:12%; animation-delay:0.4s;"></div>
            </div>
            <div class="moon"></div>
        """
    else:
        scene_html += """
            <div class="cloud"><div class="cloud-core"></div><div class="cloud-face"></div><div class="cloud-smile"></div></div>
        """
        if mode in ("rain", "storm", "night_rain", "night_storm"):
            scene_html += """
            <div class="rain-line" style="left:18%; top:58px; animation-delay:0s;"></div>
            <div class="rain-line" style="left:30%; top:24px; animation-delay:0.18s;"></div>
            <div class="rain-line" style="left:44%; top:44px; animation-delay:0.35s;"></div>
            <div class="rain-line" style="left:58%; top:18px; animation-delay:0.52s;"></div>
            <div class="rain-line" style="left:74%; top:34px; animation-delay:0.25s;"></div>
            <div class="rain-line" style="left:86%; top:12px; animation-delay:0.46s;"></div>
            """
        elif mode in ("mist", "night_mist"):
            scene_html += """
            <div class="mist-band one"></div>
            <div class="mist-band two"></div>
            """
        if mode in ("night_clouds", "night_rain", "night_storm", "night_mist"):
            scene_html += """
            <div class="stars">
                <div class="star" style="left:20%; top:18%; animation-delay:0.2s;"></div>
                <div class="star" style="left:72%; top:14%; animation-delay:0.9s;"></div>
                <div class="star" style="left:82%; top:20%; animation-delay:1.3s;"></div>
            </div>
            """

    scene_html += f"""
            <div class="label">{scene_label}</div>
            <div class="mountain-back"></div>
            <div class="mountain-mid"></div>
            <div class="mountain-front"></div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-label">Feels Like</div><div class="stat-value">{weather['feels_like']} C</div></div>
                <div class="stat-card"><div class="stat-label">Humidity</div><div class="stat-value">{weather['humidity']}%</div></div>
                <div class="stat-card"><div class="stat-label">Pressure</div><div class="stat-value">{weather['pressure']} hPa</div></div>
                <div class="stat-card"><div class="stat-label">Wind</div><div class="stat-value">{weather['wind_speed']} m/s</div></div>
                <div class="stat-card"><div class="stat-label">Min Temp</div><div class="stat-value">{weather['temp_min']} C</div></div>
                <div class="stat-card"><div class="stat-label">Max Temp</div><div class="stat-value">{weather['temp_max']} C</div></div>
                <div class="stat-card"><div class="stat-label">Cloud Cover</div><div class="stat-value">{weather['clouds']}%</div></div>
                <div class="stat-card"><div class="stat-label">Visibility</div><div class="stat-value">{weather['visibility_km']} km</div></div>
            </div>
        </div>
    </body>
    </html>
    """
    components.html(scene_html, height=440)

def get_forecast_badge(description: str, pop: int):
    desc = description.lower()
    if "thunder" in desc:
        return "STORM"
    if "rain" in desc or pop >= 60:
        return "RAIN"
    if "drizzle" in desc:
        return "DRIZZLE"
    if "cloud" in desc:
        return "CLOUDS"
    if "mist" in desc or "fog" in desc or "haze" in desc:
        return "MIST"
    return "CLEAR"


def get_rain_trend_label(weighted_pop):
    if weighted_pop >= 75:
        return "High", "Rain bands look organized over the next few forecast windows.", "&#127783;"
    if weighted_pop >= 45:
        return "Moderate", "Conditions support scattered showers in the short term.", "&#127782;"
    return "Low", "Rain signals are weak across the next few forecast windows.", "&#9728;"


def analyze_rain_forecast(weather, forecast):
    if not forecast:
        return None

    weights = [0.30, 0.22, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02]
    active_weights = weights[: len(forecast)]
    weight_total = sum(active_weights)

    weighted_pop = sum(slot["pop"] * weight for slot, weight in zip(forecast, active_weights)) / weight_total
    weighted_humidity = sum(slot["humidity"] * weight for slot, weight in zip(forecast, active_weights)) / weight_total
    weighted_clouds = sum(slot["clouds"] * weight for slot, weight in zip(forecast, active_weights)) / weight_total
    total_rainfall = round(sum(slot["rain_mm"] for slot in forecast), 1)
    peak_slot = max(forecast, key=lambda slot: (slot["pop"], slot["rain_mm"], slot["clouds"]))
    rainy_slots = sum(1 for slot in forecast if slot["pop"] >= 40 or slot["rain_mm"] > 0)

    adjusted_score = min(
        100,
        round(
            (weighted_pop * 0.55)
            + (weighted_humidity * 0.20)
            + (weighted_clouds * 0.15)
            + (weather["humidity"] * 0.10)
        ),
    )

    rain_level, rain_note, rain_icon = get_rain_trend_label(adjusted_score)

    first_half = forecast[: max(1, len(forecast) // 2)]
    second_half = forecast[len(forecast) // 2 :]
    first_half_pop = sum(slot["pop"] for slot in first_half) / len(first_half)
    second_half_pop = sum(slot["pop"] for slot in second_half) / len(second_half) if second_half else first_half_pop

    if second_half_pop - first_half_pop >= 10:
        trend = "Rising"
    elif first_half_pop - second_half_pop >= 10:
        trend = "Falling"
    else:
        trend = "Steady"

    return {
        "score": adjusted_score,
        "level": rain_level,
        "note": rain_note,
        "icon": rain_icon,
        "peak_time": peak_slot["time"],
        "peak_pop": peak_slot["pop"],
        "peak_rain_mm": peak_slot["rain_mm"],
        "trend": trend,
        "total_rainfall": total_rainfall,
        "rainy_slots": rainy_slots,
        "window_hours": len(forecast) * 3,
    }


def build_insight_table(weather, forecast, rain_analysis):
    if forecast:
        avg_temp = round(sum(slot["temp"] for slot in forecast) / len(forecast), 1)
        avg_humidity = round(sum(slot["humidity"] for slot in forecast) / len(forecast))
        avg_pressure = round(sum(slot["pressure"] for slot in forecast) / len(forecast))
    else:
        avg_temp = weather["current_temp"]
        avg_humidity = weather["humidity"]
        avg_pressure = weather["pressure"]

    rain_value = "Unavailable"
    rain_detail = "Forecast data is needed for short-term rain analysis."
    peak_window = "--"
    rainfall_window = "--"
    trend_value = "--"

    if rain_analysis:
        rain_value = f"{rain_analysis['score']}% ({rain_analysis['level']})"
        rain_detail = rain_analysis["note"]
        peak_window = f"{rain_analysis['peak_time']} ({rain_analysis['peak_pop']}%)"
        rainfall_window = f"{rain_analysis['total_rainfall']} mm / {rain_analysis['window_hours']}h"
        trend_value = rain_analysis["trend"]

    insights = pd.DataFrame(
        [
            ["Temperature", f"{weather['current_temp']} C", "Current air temperature"],
            ["Feels Like", f"{weather['feels_like']} C", "How it may feel on skin"],
            ["Humidity", f"{weather['humidity']}%", "Higher values can feel sticky"],
            ["Pressure", f"{weather['pressure']} hPa", "Lower pressure can signal unstable weather"],
            ["Wind Speed", f"{weather['wind_speed']} m/s", "Surface wind conditions"],
            ["Cloud Cover", f"{weather['clouds']}%", "How much of the sky is covered"],
            ["Visibility", f"{weather['visibility_km']} km", "Estimated horizontal visibility"],
            ["Rain Outlook", rain_value, rain_detail],
            ["Peak Rain Window", peak_window, "Time slot with the strongest rain signal"],
            ["Rainfall Window", rainfall_window, "Estimated rain accumulation in the short-term window"],
            ["Rain Trend", trend_value, "Whether rain signals are building or easing"],
            ["Forecast Avg Temp", f"{avg_temp} C", "Average across the fetched forecast window"],
            ["Forecast Avg Humidity", f"{avg_humidity}%", "Short-term moisture trend"],
            ["Forecast Avg Pressure", f"{avg_pressure} hPa", "Short-term pressure baseline"],
            ["Sunrise", format_city_time(weather["sunrise"], weather.get("timezone_offset", 0)), "Local sunrise time for the searched city"],
            ["Sunset", format_city_time(weather["sunset"], weather.get("timezone_offset", 0)), "Local sunset time for the searched city"],
        ],
        columns=["Metric", "Value", "Insight"],
    )
    return insights


def render_insight_cards(df: pd.DataFrame):
    left_col, right_col = st.columns(2)
    rows = df.to_dict("records")
    split_index = (len(rows) + 1) // 2

    with left_col:
        for row in rows[:split_index]:
            with st.container(border=True):
                st.caption(row["Metric"].upper())
                st.markdown(f"### {row['Value']}")
                st.write(row["Insight"])

    with right_col:
        for row in rows[split_index:]:
            with st.container(border=True):
                st.caption(row["Metric"].upper())
                st.markdown(f"### {row['Value']}")
                st.write(row["Insight"])


# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------
st.markdown(
    """
<div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
    <div class="hero-title">SkyCast</div>
    <div class="hero-subtitle">AI-Powered Weather Intelligence</div>
</div>
""",
    unsafe_allow_html=True,
)

_, mid, _ = st.columns([1, 3, 1])
with mid:
    city = st.text_input("", placeholder="Enter city name...", label_visibility="collapsed")
    search = st.button("Search", use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if search and not city.strip():
    st.warning("Please enter a city name.")

elif search and city.strip():
    with st.spinner("Fetching weather data..."):
        weather, weather_error = get_current_weather(city.strip())
        forecast, forecast_error = get_forecast(city.strip())

    if weather_error:
        st.error(f"Unable to fetch weather data: {weather_error}")
    else:
        rain_analysis = None if forecast_error else analyze_rain_forecast(weather, forecast)

        st.markdown(
            f"""
            <div class="city-header">
                <div class="city-name">{weather['city']}, {weather['country']}</div>
                <div class="city-desc">{weather['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_weather_scene(weather)

        # ---------------------------------------------------------------------
        # Rain Prediction
        # ---------------------------------------------------------------------
        st.markdown('<div class="section-title">Rain Prediction</div>', unsafe_allow_html=True)

        if forecast_error or not forecast or not rain_analysis:
            st.warning("Rain prediction is unavailable because forecast data could not be loaded.")
        else:
            st.markdown(
                f"""
                <div class="rain-banner">
                    <div class="rain-banner-title">{rain_analysis['icon']} {rain_analysis['level']} Rain Probability</div>
                    <div class="rain-banner-sub">
                        Multi-slot outlook over the next {rain_analysis['window_hours']} hours. {rain_analysis['note']}
                    </div>
                    <div class="prob-bar-wrap">
                        <div class="prob-bar-fill" style="width:{rain_analysis['score']}%"></div>
                    </div>
                    <div style="font-size:0.85rem;color:#cbd5e1;margin-top:0.55rem;">
                        Composite rain score: {rain_analysis['score']}%
                        &nbsp;|&nbsp; Peak window: {rain_analysis['peak_time']}
                        &nbsp;|&nbsp; Estimated rainfall: {rain_analysis['total_rainfall']} mm
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            r1, r2, r3, r4 = st.columns(4)
            rain_cards = [
                (
                    r1,
                    "TIME",
                    "Peak Window",
                    rain_analysis["peak_time"],
                    f"Strongest signal at {rain_analysis['peak_pop']}% precipitation",
                ),
                (
                    r2,
                    "&#128167;",
                    "Rainfall Total",
                    f"{rain_analysis['total_rainfall']} mm",
                    "Expected accumulation across the full forecast window",
                ),
                (
                    r3,
                    "&#128200;",
                    "Trend",
                    rain_analysis["trend"],
                    "Tracks whether rain signals are increasing or easing",
                ),
                (
                    r4,
                    "&#128339;",
                    "Active Slots",
                    f"{rain_analysis['rainy_slots']}",
                    "Forecast windows showing notable rain support",
                ),
            ]
            for col, icon, label, value, note in rain_cards:
                with col:
                    st.markdown(
                        f"""
                        <div class="weather-card">
                            <div class="card-icon">{icon}</div>
                            <div class="card-label">{label}</div>
                            <div class="card-value" style="font-size:1.45rem;">{value}</div>
                            <div style="color:#cbd5e1;font-size:0.86rem;margin-top:0.45rem;">{note}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # ---------------------------------------------------------------------
        # Weather Insight Table
        # ---------------------------------------------------------------------
        st.markdown('<div class="section-title">Weather Insight Table</div>', unsafe_allow_html=True)
        insight_df = build_insight_table(weather, forecast if not forecast_error else [], rain_analysis)
        render_insight_cards(insight_df)

        # ---------------------------------------------------------------------
        # Upcoming Forecast
        # ---------------------------------------------------------------------
        st.markdown('<div class="section-title">Upcoming Forecast</div>', unsafe_allow_html=True)

        if forecast_error:
            st.warning(f"Forecast unavailable: {forecast_error}")
        elif not forecast:
            st.warning("No forecast data available.")
        else:
            cols = st.columns(min(len(forecast), 5))
            for col, item in zip(cols, forecast[:5]):
                with col:
                    st.markdown(
                        f"""
                        <div class="forecast-card">
                            <div class="forecast-time">{item['time']}</div>
                            <div style="font-size:0.82rem; letter-spacing:0.12em; color:#8fc7ea; margin-bottom:0.7rem; font-weight:700;">{get_forecast_badge(item['description'], item['pop'])}</div>
                            <div class="forecast-value">{item['temp']}<span class="forecast-unit"> C</span></div>
                            <div class="forecast-unit" style="margin-top:0.35rem;">Condition: {item['description'].title()}</div>
                            <div class="forecast-unit">Humidity: {item['humidity']}%</div>
                            <div class="forecast-unit">Pressure: {item['pressure']} hPa</div>
                            <div class="forecast-unit">Rain: {item['pop']}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

