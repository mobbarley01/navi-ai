import os
import time
import requests
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_KEY    = os.getenv("NEWS_API_KEY")
TAVILY_KEY  = os.getenv("TAVILY_API_KEY")
HEADERS     = {"User-Agent": "NaviAI/1.0 (personal AI assistant; raspberry pi project)"}

tavily_client = TavilyClient(api_key=TAVILY_KEY)

# ============================================================
# CACHE
# ============================================================
_cache = {}

def _get_cache(key, ttl=600):
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < ttl:
            return data
    return None

def _set_cache(key, data):
    _cache[key] = (data, time.time())

# ============================================================
# WEATHER
# ============================================================
def get_weather(city="Malta"):
    cache_key = f"weather_{city}"
    cached = _get_cache(cache_key, ttl=600)
    if cached:
        return cached
    try:
        response = requests.get(
            f"http://wttr.in/{city}",
            params={"format": "j1"},
            headers=HEADERS,
            timeout=10
        )
        data    = response.json()
        current = data["current_condition"][0]
        area    = data["nearest_area"][0]
        weather = {
            "city":       f"{area['areaName'][0]['value']}, {area['country'][0]['value']}",
            "temp":       current["temp_C"],
            "feels_like": current["FeelsLikeC"],
            "condition":  current["weatherDesc"][0]["value"],
            "humidity":   current["humidity"],
            "wind_speed": current["windspeedKmph"],
            "uv_index":   current["uvIndex"],
            "visibility": current["visibility"]
        }
        forecast = []
        for day in data["weather"][:3]:
            forecast.append({
                "date":      day["date"],
                "min":       day["mintempC"],
                "max":       day["maxtempC"],
                "condition": day["hourly"][4]["weatherDesc"][0]["value"]
            })
        result = {"weather": weather, "forecast": forecast}
        _set_cache(cache_key, result)
        return result
    except Exception:
        return None

def format_weather_for_navi(city="Malta"):
    data = get_weather(city)
    if not data:
        return f"Weather for {city} unavailable."
    w = data["weather"]
    f = data["forecast"]
    result = f"""
CURRENT WEATHER in {w['city']}:
Temperature: {w['temp']}C (feels like {w['feels_like']}C)
Condition: {w['condition']}
Humidity: {w['humidity']}%
Wind: {w['wind_speed']} km/h
UV Index: {w['uv_index']}
Visibility: {w['visibility']} km
"""
    if f:
        result += "\n3-DAY FORECAST:\n"
        for day in f:
            result += f"{day['date']}: {day['min']}C to {day['max']}C, {day['condition']}\n"
    return result

def is_weather_severe(city="Malta"):
    data = get_weather(city)
    if not data:
        return False
    condition  = data["weather"]["condition"].lower()
    wind_speed = int(data["weather"]["wind_speed"])
    severe     = ["storm", "thunder", "heavy rain", "gale",
                  "hurricane", "extreme", "dust", "sand", "hail", "snow"]
    return any(w in condition for w in severe) or wind_speed > 60

# ============================================================
# NEWS
# ============================================================
BLOCKED_SOURCES = [
    "tmz", "buzzfeed", "daily mail", "the sun", "mirror",
    "people magazine", "us weekly", "e! news", "ladbible",
    "nintendoeverything", "polygon", "kotaku", "ign",
    "deadline", "variety", "the hollywood reporter"
]

BLOCKED_KEYWORDS = [
    "kardashian", "taylor swift", "reality tv", "housewives",
    "bachelor", "bachelorette", "animal crossing", "pokemon",
    "game update", "patch notes", "box office", "oscars",
    "grammy", "award show", "celebrity", "cinemacon",
    "jumanji", "spider-man", "wnba draft", "nfl draft",
    "music video", "pop star", "dating show"
]

def is_quality_article(article):
    title       = (article.get("title") or "").lower()
    source_name = (article.get("source") or {}).get("name", "").lower()
    description = (article.get("description") or "").lower()
    for blocked in BLOCKED_SOURCES:
        if blocked in source_name:
            return False
    for kw in BLOCKED_KEYWORDS:
        if kw in title or kw in description:
            return False
    return True

def get_news(query=None, max_articles=8):
    cache_key = f"news_{query or 'top'}"
    cached = _get_cache(cache_key, ttl=600)
    if cached:
        return cached
    articles = []
    try:
        if query:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "apiKey":   NEWS_KEY,
                    "q":        query,
                    "language": "en",
                    "sortBy":   "publishedAt",
                    "pageSize": 20
                },
                timeout=10
            )
            data = response.json()
            if response.status_code == 200:
                for a in data.get("articles", []):
                    if (a.get("title") and
                        a["title"] != "[Removed]" and
                        is_quality_article(a)):
                        articles.append({
                            "title":       a["title"],
                            "source":      a["source"]["name"],
                            "description": (a.get("description") or "")[:120],
                            "published":   (a.get("publishedAt") or "")[:10]
                        })
                        if len(articles) >= max_articles:
                            break
        else:
            for category in ["general", "technology", "business", "science"]:
                response = requests.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        "apiKey":   NEWS_KEY,
                        "category": category,
                        "language": "en",
                        "pageSize": 15
                    },
                    timeout=10
                )
                data = response.json()
                if response.status_code == 200:
                    for a in data.get("articles", []):
                        if (a.get("title") and
                            a["title"] != "[Removed]" and
                            is_quality_article(a)):
                            articles.append({
                                "title":       a["title"],
                                "source":      a["source"]["name"],
                                "description": (a.get("description") or "")[:120],
                                "category":    category,
                                "published":   (a.get("publishedAt") or "")[:10]
                            })
        _set_cache(cache_key, articles)
        return articles[:max_articles]
    except Exception:
        return []

def format_news_for_navi(query=None, max_articles=8):
    articles = get_news(query, max_articles)
    if not articles:
        return "News unavailable right now."
    header = f"LATEST NEWS - {query.upper()}:" if query else "TOP WORLD NEWS:"
    result = f"\n{header}\n"
    for i, a in enumerate(articles, 1):
        result += f"\n{i}. [{a['source']}] {a['title']}"
        if a.get("description"):
            result += f"\n   {a['description']}"
        result += f"\n   {a['published']}\n"
    return result

# ============================================================
# WIKIPEDIA
# ============================================================
def format_wikipedia_for_navi(query):
    cache_key = f"wiki_{query.lower()}"
    cached = _get_cache(cache_key, ttl=3600)
    if cached:
        return cached
    try:
        url = "https://en.wikipedia.org/w/api.php"
        search_response = requests.get(
            url,
            params={
                "action":   "query",
                "list":     "search",
                "srsearch": query,
                "format":   "json",
                "srlimit":  1
            },
            headers=HEADERS,
            timeout=10
        )
        results = search_response.json().get("query", {}).get("search", [])
        if not results:
            return f"No Wikipedia article found for: {query}"
        page_title = results[0]["title"]
        extract_response = requests.get(
            url,
            params={
                "action":      "query",
                "titles":      page_title,
                "prop":        "extracts",
                "exintro":     True,
                "explaintext": True,
                "exsentences": 8,
                "format":      "json"
            },
            headers=HEADERS,
            timeout=10
        )
        pages = extract_response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            extract = page.get("extract", "")
            if extract:
                result = f"WIKIPEDIA - {page_title}:\n{extract}"
                _set_cache(cache_key, result)
                return result
        return f"No content found for: {query}"
    except Exception as e:
        return f"Wikipedia lookup failed: {str(e)[:50]}"

# ============================================================
# TAVILY WEB SEARCH
# ============================================================
def tavily_search(query, depth="basic", max_results=3):
    """
    Search the live web via Tavily.
    depth: basic (fast) or advanced (deeper research)
    Returns list of results with title, content, url, date
    """
    cache_key = f"tavily_{depth}_{query.lower()[:50]}"
    cached = _get_cache(cache_key, ttl=300)  # 5 min cache for live search
    if cached:
        return cached

    try:
        if depth == "advanced":
            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
        else:
            response = tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )

        results = []

        # Include Tavily's own synthesised answer if available
        if response.get("answer"):
            results.append({
                "type":    "summary",
                "content": response["answer"],
                "source":  "Tavily synthesis",
                "url":     "",
                "date":    ""
            })

        # Include individual results
        for r in response.get("results", [])[:max_results]:
            results.append({
                "type":    "result",
                "title":   r.get("title", ""),
                "content": r.get("content", "")[:300],
                "source":  r.get("url", "").split("/")[2] if r.get("url") else "",
                "url":     r.get("url", ""),
                "date":    r.get("published_date", "")[:10] if r.get("published_date") else ""
            })

        _set_cache(cache_key, results)
        return results

    except Exception as e:
        return []

def format_search_for_navi(query, depth="basic"):
    """Format Tavily search results for Navi's context"""
    results = tavily_search(query, depth=depth)

    if not results:
        return f"Web search for '{query}' returned no results."

    formatted = f"\nLIVE WEB SEARCH - {query}:\n"

    for r in results:
        if r["type"] == "summary":
            formatted += f"\nSYNTHESIS: {r['content']}\n"
        else:
            formatted += f"\n[{r['source']}]"
            if r.get("title"):
                formatted += f" {r['title']}"
            if r.get("date"):
                formatted += f" ({r['date']})"
            formatted += f"\n{r['content']}\n"

    return formatted

def format_advanced_search_for_navi(query):
    """Deep research search — used for explicit search commands"""
    return format_search_for_navi(query, depth="advanced")
