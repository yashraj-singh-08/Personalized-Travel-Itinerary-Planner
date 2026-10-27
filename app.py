from __future__ import annotations

import json
import math
import os
import random
import re
from datetime import date, timedelta
from io import BytesIO
from typing import Any

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether
)

APP_NAME = "Personalized Travel Itinerary Planner"
CURRENCY = {"India": ("INR", 83.0), "United States": ("USD", 1.0),
            "United Kingdom": ("GBP", 0.79), "Japan": ("JPY", 150.0),
            "Thailand": ("THB", 36.0), "France": ("EUR", 0.92),
            "Italy": ("EUR", 0.92), "Indonesia": ("IDR", 15700.0),
            "Australia": ("AUD", 1.52), "United Arab Emirates": ("AED", 3.67)}
# Curated starter data. Coordinates are approximate city/attraction coordinates;
# extend this catalogue or replace with a verified places provider for live use.
DESTINATIONS = [
    {"city":"Jaipur","country":"India","region":"India","vibes":["Cultural","Urban"],
     "budget":"Budget","season":["Winter","Spring"],"tags":["Heritage","Markets","Food"],
     "summary":"Pink-hued forts, lively bazaars and Rajasthani cuisine.","lat":26.9124,"lon":75.7873,
     "attractions":[("Amber Fort","History",26.9855,75.8513,500),("Hawa Mahal","History",26.9239,75.8267,200),("City Palace","History",26.9258,75.8237,400),("Johari Bazaar","Food",26.9195,75.8260,300),("Jal Mahal promenade","Leisure",26.9535,75.8460,0),("Masala Chowk","Food",26.9120,75.8150,350),("Albert Hall Museum","History",26.9117,75.8190,300),("Nahargarh sunset point","Adventure",26.9370,75.8150,150)]},
    {"city":"Goa","country":"India","region":"India","vibes":["Beach","Urban"],
     "budget":"Moderate","season":["Winter"],"tags":["Beaches","Seafood","Sunsets"],
     "summary":"Beach days, Portuguese-era lanes and easy-going evenings.","lat":15.2993,"lon":74.1240,
     "attractions":[("Fontainhas heritage quarter","History",15.4989,73.8278,0),("Miramar Beach","Leisure",15.4779,73.8077,0),("Dona Paula viewpoint","Adventure",15.4589,73.8030,50),("Anjuna Flea Market area","Shopping",15.5730,73.7400,100),("Baga Beach","Leisure",15.5557,73.7516,0),("Chapora Fort","History",15.6000,73.7390,50),("Local seafood shack","Food",15.5600,73.7600,900),("Sunset beach café","Food",15.5450,73.7650,700)]},
    {"city":"Rishikesh","country":"India","region":"India","vibes":["Mountains","Adventure","Cultural"],
     "budget":"Budget","season":["Spring","Autumn"],"tags":["River","Yoga","Outdoors"],
     "summary":"Ganges-side walks, yoga, mountain air and outdoor adventures.","lat":30.0869,"lon":78.2676,
     "attractions":[("Ram Jhula riverside","Leisure",30.1268,78.3220,0),("Beatles Ashram","History",30.1110,78.3130,150),("Triveni Ghat","Cultural",30.1030,78.2930,0),("Neer Garh waterfall trail","Adventure",30.1150,78.3500,100),("Local thali café","Food",30.1250,78.3210,350),("Yoga session","Leisure",30.1240,78.3200,500),("Ganga Aarti","Cultural",30.1030,78.2930,0),("Riverside vegetarian dinner","Food",30.1270,78.3230,450)]},
    {"city":"Udaipur","country":"India","region":"India","vibes":["Cultural","Relaxed"],
     "budget":"Moderate","season":["Winter","Autumn"],"tags":["Lakes","Palaces","Romance"],
     "summary":"Lake views, intricate palaces and unhurried old-city strolls.","lat":24.5854,"lon":73.7125,
     "attractions":[("City Palace","History",24.5764,73.6835,400),("Jagdish Temple","Cultural",24.5797,73.6831,0),("Lake Pichola boat ride","Leisure",24.5760,73.6770,600),("Bagore Ki Haveli","History",24.5780,73.6830,150),("Gangaur Ghat","Leisure",24.5785,73.6820,0),("Old-city thali restaurant","Food",24.5790,73.6840,450),("Saheliyon-ki-Bari","Leisure",24.6010,73.6850,100),("Rooftop dinner","Food",24.5790,73.6820,800)]},
    {"city":"Bangkok","country":"Thailand","region":"Southeast Asia","vibes":["Urban","Cultural","Food"],
     "budget":"Budget","season":["Winter"],"tags":["Street Food","Temples","Nightlife"],
     "summary":"Street-food lanes, ornate temples and energetic night markets.","lat":13.7563,"lon":100.5018,
     "attractions":[("Wat Pho","History",13.7465,100.4927,300),("Grand Palace area","History",13.7500,100.4913,500),("Tha Tian food market","Food",13.7440,100.4890,250),("Chinatown walk","Food",13.7390,100.5100,250),("Lumphini Park","Leisure",13.7308,100.5417,0),("Jim Thompson House","History",13.7466,100.5347,200),("Riverside dinner cruise","Food",13.7230,100.5140,1800),("Night market stroll","Nightlife",13.7460,100.5340,400)]},
    {"city":"Kyoto","country":"Japan","region":"East Asia","vibes":["Cultural","Mountains","Relaxed"],
     "budget":"Moderate","season":["Spring","Autumn"],"tags":["Temples","Gardens","Tea"],
     "summary":"Quiet gardens, historic streets and seasonal landscapes.","lat":35.0116,"lon":135.7681,
     "attractions":[("Kiyomizu-dera","History",34.9949,135.7850,500),("Sannenzaka lanes","Cultural",34.9975,135.7800,0),("Nishiki Market","Food",35.0050,135.7648,600),("Gion evening walk","Cultural",35.0037,135.7788,0),("Arashiyama bamboo grove","Leisure",35.0170,135.6713,0),("Tenryu-ji garden","Leisure",35.0157,135.6770,500),("Fushimi Inari shrine","History",34.9671,135.7727,0),("Tea-house experience","Food",35.0030,135.7750,1200)]},
    {"city":"Lisbon","country":"Portugal","region":"Europe","vibes":["Cultural","Urban","Food"],
     "budget":"Moderate","season":["Spring","Autumn"],"tags":["Trams","Seafood","Architecture"],
     "summary":"Hillside viewpoints, tiled streets, pastries and Atlantic breezes.","lat":38.7223,"lon":-9.1393,
     "attractions":[("Alfama walking route","Cultural",38.7110,-9.1290,0),("São Jorge Castle","History",38.7139,-9.1335,1500),("Time Out Market","Food",38.7075,-9.1450,1200),("Belém waterfront","Leisure",38.6979,-9.2066,0),("Jerónimos Monastery","History",38.6979,-9.2066,1200),("LX Factory","Shopping",38.7037,-9.1780,300),("Miradouro sunset viewpoint","Leisure",38.7150,-9.1330,0),("Fado dinner venue","Food",38.7110,-9.1320,2500)]},
    {"city":"Bali (Ubud)","country":"Indonesia","region":"Southeast Asia","vibes":["Beach","Mountains","Cultural","Relaxed"],
     "budget":"Moderate","season":["Summer","Spring"],"tags":["Nature","Wellness","Temples"],
     "summary":"Lush rice terraces, wellness retreats and temple visits.","lat":-8.5069,"lon":115.2625,
     "attractions":[("Tegallalang rice terraces","Leisure",-8.4312,115.2792,150000),("Ubud Art Market","Shopping",-8.5069,115.2625,0),("Sacred Monkey Forest","Adventure",-8.5186,115.2588,80000),("Tirta Empul temple","Cultural",-8.4150,115.3150,75000),("Campuhan Ridge Walk","Adventure",-8.4990,115.2530,0),("Balinese cooking class","Food",-8.5060,115.2630,450000),("Ubud vegetarian café","Food",-8.5070,115.2650,120000),("Traditional dance performance","Cultural",-8.5060,115.2620,100000)]},
    {"city":"Dubai","country":"United Arab Emirates","region":"Middle East","vibes":["Urban","Luxury","Food"],
     "budget":"Luxury","season":["Winter"],"tags":["Skyline","Shopping","Dining"],
     "summary":"Modern architecture, souks and memorable dining experiences.","lat":25.2048,"lon":55.2708,
     "attractions":[("Al Fahidi historic district","History",25.2630,55.3000,0),("Dubai Creek abra crossing","Cultural",25.2570,55.2900,5),("Dubai Mall & fountains","Shopping",25.1985,55.2796,0),("Museum of the Future","History",25.2190,55.2819,150),("Jumeirah Beach","Leisure",25.2048,55.2390,0),("Old souk food walk","Food",25.2630,55.2900,150),("Marina evening promenade","Leisure",25.0800,55.1400,0),("Skyline dinner","Food",25.1970,55.2740,300)]},
]

SLOT_DEFS = [
    ("09:00–12:00", "Morning Sightseeing", "History"),
    ("12:30–14:00", "Lunch Recommendation", "Food"),
    ("15:00–17:00", "Afternoon Leisure", "Leisure"),
    ("18:30–21:00", "Evening Dining & Entertainment", "Food"),
]
INTERESTS = ["Food", "Adventure", "History", "Nightlife"]
VIBES = ["Beach", "Mountains", "Cultural", "Urban", "Relaxed", "Adventure", "Food"]
SEASONS = ["Winter", "Spring", "Summer", "Monsoon", "Autumn"]

st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#1d3431; --muted:#647873; --green:#1f6657; --mint:#dff1e8; --sand:#fbf5e9; --coral:#e98d6e; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(180deg,#f7fbf7 0%,#fbf7ef 100%); color:var(--ink); }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:#183d35; }
.hero { padding:1.7rem 2rem; border-radius:24px; background:linear-gradient(120deg,#173f37,#397967); color:white; margin-bottom:1rem; box-shadow:0 12px 36px #234d3b20; }
.hero h1 { color:white !important; margin:0; font-size:2.3rem; }
.hero p { color:#e5f3eb; margin:.5rem 0 0; }
.pill { display:inline-block; border-radius:100px; background:#e0f0e7; color:#245d4f; padding:4px 10px; margin:2px 4px 2px 0; font-size:.78rem; font-weight:600; }
.plan-card { background:#fff; border:1px solid #e5ebe5; padding:1rem 1.1rem; border-radius:16px; margin:.45rem 0; box-shadow:0 4px 16px #1a493008; }
.small-muted { color:#647873; font-size:.88rem; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #e5ebe5; border-radius:15px; padding:12px 15px; }
.stButton>button { border-radius:12px; border:0; font-weight:600; }
div[data-testid="stTabs"] button { font-weight:600; }
section[data-testid="stSidebar"] { background:#f0f6f0; }
</style>
""", unsafe_allow_html=True)

def money(value: float, currency: str) -> str:
    if currency == "JPY":
        return f"¥{value:,.0f}"
    if currency == "IDR":
        return f"Rp {value:,.0f}"
    symbols = {"INR":"₹", "USD":"$", "GBP":"£", "EUR":"€", "THB":"฿", "AUD":"A$","AED":"د.إ"}
    return f"{symbols.get(currency, currency + ' ')}{value:,.0f}"

def usd_inr(local_cost: float, currency: str, rate: float) -> tuple[float, float]:
    usd = local_cost / rate
    return usd, usd * 83.0

def haversine(a: tuple[float,float], b: tuple[float,float]) -> float:
    r = 6371
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = math.radians(b[0]-a[0])
    dl = math.radians(b[1]-a[1])
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))

def season_for_month(month: int) -> str:
    if month in (12,1,2): return "Winter"
    if month in (3,4): return "Spring"
    if month in (5,6): return "Summer"
    if month in (7,8,9): return "Monsoon"
    return "Autumn"

def get_destination(city: str) -> dict:
    for d in DESTINATIONS:
        if d["city"] == city:
            return d
    return DESTINATIONS[0]

def recommend_destinations(vibe: str, budget: str, start_date: date, interests: list[str]) -> list[dict]:
    season = season_for_month(start_date.month)
    scored = []
    for d in DESTINATIONS:
        score = 0
        if vibe == "Any" or vibe in d["vibes"]: score += 4
        if budget == d["budget"]: score += 3
        elif budget == "Moderate": score += 1
        if season in d["season"]: score += 2
        score += min(3, len(set(interests) & set(d["tags"])) )
        scored.append((score, d))
    return [d for _, d in sorted(scored, key=lambda x: x[0], reverse=True)[:3]]

def cost_scale(budget: str) -> float:
    return {"Budget":0.72, "Moderate":1.0, "Luxury":1.8}[budget]

def attraction_cost(base: float, budget: str, currency: str) -> float:
    # Catalogue costs are stored in the destination's common local currency.
    # This factor changes comfort/dining spend assumptions, not official entry prices.
    if currency == "INR" and base < 10000:
        return round(base * cost_scale(budget), 0)
    return round(base * cost_scale(budget), 0)

def cluster_attractions(dest: dict, days: int, interests: list[str], pace: str, budget: str) -> list[list[dict]]:
    """Greedy nearest-neighbour grouping: assign high-relevance seed, then nearby stops.
    This is a heuristic over the local catalogue, not live routing or traffic data."""
    items = []
    for name, category, lat, lon, cost in dest["attractions"]:
        relevance = 1 if category in interests or (category == "Cultural" and "History" in interests) else 0
        items.append({"name":name, "category":category, "lat":lat, "lon":lon,
                      "base_cost":cost, "relevance":relevance})
    # Ensure each day has varied options while favoring the selected interests.
    items.sort(key=lambda x: (-x["relevance"], x["name"]))
    per_day = {"Relaxed":3, "Moderate":4, "Fast-Paced":5}[pace]
    per_day = min(per_day, max(2, math.ceil(len(items)/days)))
    remaining = items[:]
    result = []
    for day in range(days):
        if not remaining: remaining = items[:]
        cluster = [remaining.pop(0)]
        while len(cluster) < per_day and remaining:
            last = cluster[-1]
            nearest_idx = min(range(len(remaining)), key=lambda i: haversine(
                (last["lat"], last["lon"]), (remaining[i]["lat"], remaining[i]["lon"])))
            cluster.append(remaining.pop(nearest_idx))
        result.append(cluster)
    return result

def make_item(slot: str, time: str, attraction: dict, dest: dict, budget: str,
              currency: str, rate: float, note: str = "") -> dict:
    base = attraction["base_cost"]
    # For food, include a meal allowance; for free attractions retain zero.
    if attraction["category"] == "Food" and base == 0:
        base = {"Budget":350, "Moderate":700, "Luxury":1600}[budget]
    cost = attraction_cost(base, budget, currency)
    usd, inr = usd_inr(cost, currency, rate)
    return {"time":time, "slot":slot, "activity":attraction["name"],
            "category":attraction["category"], "cost":cost, "currency":currency,
            "usd":round(usd,2), "inr":round(inr,0), "note":note,
            "lat":attraction["lat"], "lon":attraction["lon"]}

def generate_itinerary(prefs: dict) -> dict:
    dest = get_destination(prefs["destination"])
    days = prefs["days"]
    clusters = cluster_attractions(dest, days, prefs["interests"], prefs["pace"], prefs["budget"])
    itinerary = []
    for day_idx, cluster in enumerate(clusters, 1):
        # Arrange the day in slot order and choose the closest relevant item to each slot category.
        chosen = []
        pool = cluster[:]
        for _, slot_name, category in SLOT_DEFS:
            preferred = [x for x in pool if x["category"] == category]
            item = preferred[0] if preferred else pool[0] if pool else cluster[0]
            chosen.append(item)
            if item in pool and len(pool) > 1: pool.remove(item)
        day_items = []
        for (time, slot_name, _), item in zip(SLOT_DEFS, chosen):
            note = "Nearby cluster to reduce unnecessary transit."
            if item["category"] == "Food" and "vegetarian" in prefs.get("dietary","").lower():
                note = "Ask the venue to confirm vegetarian preparation and cross-contact needs."
            day_items.append(make_item(slot_name, time, item, dest, prefs["budget"],
                                       prefs["currency"], prefs["rate"], note))
        # Keep running cumulative trip spend on each item.
        itinerary.append({"day":day_idx, "date":(prefs["start_date"]+timedelta(days=day_idx-1)).isoformat(),
                          "items":day_items, "cluster_center":cluster[0]["name"]})
    running = 0
    for day in itinerary:
        for item in day["items"]:
            running += item["cost"]
            item["cumulative"] = running
    return {"id":f"trip-{date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
            "created_at":date.today().isoformat(), "preferences":prefs,
            "destination_info":dest, "itinerary":itinerary, "estimated_total":running,
            "currency":prefs["currency"]}

def try_llm_enhance(prefs: dict, api_key: str, provider: str, prompt: str) -> str | None:
    """Optional live copy helper. Planning works without this provider call."""
    if not api_key:
        return None
    try:
        if provider == "Gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            return getattr(response, "text", None)
        if provider == "Groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"You are a careful travel-planning assistant. Do not invent current opening hours or claim live availability."},
                          {"role":"user","content":prompt}],
                temperature=0.5, max_tokens=600)
            return response.choices[0].message.content
    except Exception as exc:
        st.warning(f"AI enhancement unavailable; continuing in demo mode. Details: {type(exc).__name__}")
    return None

def swap_activity(trip: dict, day_number: int, item_index: int, instruction: str) -> None:
    """Modify one slot using local catalogue matching; preserves every other day/slot."""
    prefs = trip["preferences"]
    dest = trip["destination_info"]
    current = trip["itinerary"][day_number-1]["items"][item_index]
    text = instruction.lower()
    candidates = dest["attractions"][:]
    if "vegetarian" in text:
        candidates = [a for a in candidates if a[1] == "Food"]
    elif "market" in text:
        candidates = [a for a in candidates if "market" in a[0].lower() or a[1] == "Shopping"]
    elif "outdoor" in text or "nature" in text:
        candidates = [a for a in candidates if a[1] in ("Adventure","Leisure")]
    elif "museum" in text:
        candidates = [a for a in candidates if "museum" in a[0].lower() or a[1] == "History"]
    elif "food" in text or "lunch" in text or "dining" in text:
        candidates = [a for a in candidates if a[1] == "Food"]
    if not candidates:
        candidates = dest["attractions"][:]
    # Avoid choosing the same item where possible.
    candidates = [a for a in candidates if a[0] != current["activity"]] or candidates
    old_lat, old_lon = current.get("lat", dest["lat"]), current.get("lon", dest["lon"])
    # Prefer nearby options for reduced transit.
    selected = min(candidates, key=lambda a: haversine((old_lat,old_lon),(a[2],a[3])))
    new_item = {"name":selected[0],"category":selected[1],"lat":selected[2],"lon":selected[3],"base_cost":selected[4]}
    updated = make_item(current["slot"], current["time"], new_item, dest, prefs["budget"],
                        prefs["currency"], prefs["rate"], f"Updated from your request: {instruction}")
    trip["itinerary"][day_number-1]["items"][item_index] = updated
    running = 0
    for day in trip["itinerary"]:
        for item in day["items"]:
            running += item["cost"]
            item["cumulative"] = running
    trip["estimated_total"] = running

def build_pdf(trip: dict) -> bytes:
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm,
                            topMargin=16*mm, bottomMargin=16*mm, title="Travel Itinerary")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="HeroTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=22, leading=27, textColor=colors.HexColor("#1F6657"),
                              alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], textColor=colors.HexColor("#647873"),
                              alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name="Day", parent=styles["Heading2"], textColor=colors.HexColor("#1F6657"),
                              spaceBefore=12, spaceAfter=7))
    styles.add(ParagraphStyle(name="Tiny", parent=styles["Normal"], fontSize=8, leading=10))
    story = []
    prefs = trip["preferences"]
    dest = trip["destination_info"]
    story += [Paragraph("Your Journey, Thoughtfully Planned", styles["HeroTitle"]),
              Paragraph(f"{dest['city']} · {prefs['start_date'].strftime('%d %b %Y')} · {prefs['days']} days", styles["Sub"]),
              Paragraph(f"<b>Travel style:</b> {prefs['budget']} · {prefs['party']} · {prefs['pace']} pace", styles["Normal"]),
              Paragraph(f"<b>Interests:</b> {', '.join(prefs['interests'])}", styles["Normal"]),
              Spacer(1, 8),
              Paragraph(f"<b>Estimated activity spend:</b> {money(trip['estimated_total'], trip['currency'])} "
                        f"(about ${trip['estimated_total']/prefs['rate']:,.0f} USD / ₹{trip['estimated_total']/prefs['rate']*83:,.0f} INR)",
                        styles["Normal"]), Spacer(1, 12)]
    for day in trip["itinerary"]:
        story.append(Paragraph(f"Day {day['day']} · {date.fromisoformat(day['date']).strftime('%A, %d %b')}", styles["Day"]))
        rows = [["Time", "Plan", "Est. cost"]]
        for item in day["items"]:
            rows.append([item["time"], f"<b>{item['slot']}</b><br/>{item['activity']}<br/><font color='#647873'>{item['note']}</font>",
                         money(item["cost"], item["currency"])])
        table = Table(rows, colWidths=[27*mm, 112*mm, 28*mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1F6657")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP"),
            ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE7DF")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F5F9F5")]),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.extend([table, Spacer(1, 8)])
    story += [PageBreak(), Paragraph("Before You Go", styles["Day"]),
              Paragraph("Emergency & practical checklist", styles["Heading3"])]
    checks = [
        "Save your accommodation address and a local-language version offline.",
        "Add local emergency number and nearest hospital to your phone before departure.",
        "Share your itinerary and check-in plan with a trusted contact.",
        "Confirm passport/visa rules, travel insurance, entry requirements and local advisories.",
        "Download offline maps; keep a backup payment method and a little local cash.",
        "Confirm opening hours, reservations, accessibility and transport on official sources.",
        "Keep copies of passport, insurance and key bookings stored securely offline.",
    ]
    for c in checks:
        story.append(Paragraph(f"☐ {c}", styles["Normal"])); story.append(Spacer(1,5))
    story += [Spacer(1,8), Paragraph("Useful emergency contacts (fill in before travel)", styles["Heading3"])]
    contact_rows = [["Contact", "Number / details"], ["Local emergency services", "________________________"],
                    ["Accommodation", "________________________"], ["Travel insurance", "________________________"],
                    ["Embassy / consulate", "________________________"], ["Trusted contact", "________________________"]]
    ct = Table(contact_rows, colWidths=[65*mm, 100*mm])
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DFF1E8")),
                            ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD9D0")),
                            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
                            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story.append(ct)
    story += [Spacer(1,14), Paragraph("Planning note: costs are illustrative estimates, not quotes. The catalogue uses approximate coordinates and does not include live traffic, availability, opening hours, or transport fares.", styles["Tiny"])]
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE7DF"))
        canvas.line(17*mm, 12*mm, A4[0]-17*mm, 12*mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#647873"))
        canvas.drawString(17*mm, 7*mm, "Personalized Travel Itinerary Planner")
        canvas.drawRightString(A4[0]-17*mm, 7*mm, f"Page {doc.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buff.getvalue()

def serializable_trip(trip: dict) -> dict:
    clean = json.loads(json.dumps(trip, default=str))
    return clean

def restore_trip(trip: dict) -> dict:
    p = trip["preferences"]
    p["start_date"] = date.fromisoformat(p["start_date"]) if isinstance(p["start_date"], str) else p["start_date"]
    return trip

if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []
if "current_trip" not in st.session_state:
    st.session_state.current_trip = None
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.markdown(f"""<div class="hero"><h1>🧭 {APP_NAME}</h1>
<p>Less tab-hopping. More meaningful moments. Build a trip that fits your pace, budget and kind of wonder.</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✨ Your travel brief")
    provider = st.selectbox("AI provider", ["Demo mode (no API)", "Gemini", "Groq"], help="Demo mode works without credentials. API keys are kept in this session only.")
    api_key = ""
    if provider != "Demo mode (no API)":
        api_key = st.text_input(f"{provider} API key", type="password", help="Never hard-code keys. For deployments, prefer Streamlit Secrets.")
        st.caption("The key is not written to trip history or exported PDFs.")
    st.markdown("---")
    destination_options = ["No fixed destination"] + [d["city"] for d in DESTINATIONS]
    destination_choice = st.selectbox("Destination", destination_options, index=0)
    vibe = st.selectbox("Trip vibe", ["Any"] + VIBES)
    days = st.slider("Trip duration", 1, 10, 4)
    start_date = st.date_input("Start date", value=date.today()+timedelta(days=30), min_value=date.today())
    budget = st.select_slider("Budget level", options=["Budget","Moderate","Luxury"], value="Moderate")
    party = st.selectbox("Travel party", ["Solo","Couple","Family","Friends"])
    pace = st.select_slider("Pace", options=["Relaxed","Moderate","Fast-Paced"], value="Moderate")
    interests = st.multiselect("Interests", INTERESTS, default=["Food","History"])
    dietary = st.text_input("Dietary needs (optional)", placeholder="e.g. vegetarian")
    country = st.selectbox("Local currency region", list(CURRENCY.keys()), index=0)
    currency, rate = CURRENCY[country]
    st.caption(f"Planner display currency: {currency}. FX rates are illustrative defaults, not live rates.")
    generate_clicked = st.button("✨ Build my trip", type="primary", use_container_width=True)

prefs = {"destination": destination_choice if destination_choice != "No fixed destination" else "",
         "vibe":vibe, "days":days, "start_date":start_date, "budget":budget,
         "party":party, "pace":pace, "interests":interests or ["Food"],
         "dietary":dietary, "currency":currency, "rate":rate, "country":country}
tabs = st.tabs(["🌍 Destination Recommender", "🗓️ Itinerary Builder", "🎨 Vibe & Activity Swap", "💾 Trips & PDF"])

with tabs[0]:
    st.subheader("Find a destination that fits your mood")
    st.write("Recommendations combine your vibe, budget tier, seasonal fit and selected interests. Weather fit is a broad seasonal heuristic, not a forecast.")
    recs = recommend_destinations(vibe, budget, start_date, interests)
    if destination_choice != "No fixed destination":
        fixed = get_destination(destination_choice)
        recs = [fixed] + [d for d in recs if d["city"] != fixed["city"]]
        recs = recs[:3]
    cols = st.columns(3)
    for col, d in zip(cols, recs):
        with col:
            st.markdown('<div class="plan-card">', unsafe_allow_html=True)
            st.markdown(f"### {d['city']}")
            st.caption(f"{d['country']} · Seasonal fit: {'Good match' if season_for_month(start_date.month) in d['season'] else 'Check local conditions'}")
            st.write(d["summary"])
            st.markdown("".join([f'<span class="pill">{tag}</span>' for tag in d["tags"]]), unsafe_allow_html=True)
            st.markdown(f"**Typical style:** {d['budget']} · **Vibes:** {', '.join(d['vibes'][:3])}")
            if st.button(f"Plan {d['city']}", key=f"rec_{d['city']}"):
                new_prefs = dict(prefs); new_prefs["destination"] = d["city"]
                st.session_state.current_trip = generate_itinerary(new_prefs)
                st.success(f"Draft itinerary created for {d['city']}. Open Itinerary Builder.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.info("Demo catalogue contains a curated set of sample destinations. For production expansion, connect a verified destination/weather/places API and cache results.")

with tabs[1]:
    st.subheader("Day-by-day itinerary")
    if generate_clicked:
        if destination_choice == "No fixed destination":
            recommended = recommend_destinations(vibe, budget, start_date, interests)[0]
            prefs["destination"] = recommended["city"]
            st.info(f"No fixed destination selected — starting with your strongest match: {recommended['city']}.")
        st.session_state.current_trip = generate_itinerary(prefs)
    trip = st.session_state.current_trip
    if not trip:
        st.markdown('<div class="plan-card"><h3>Your itinerary is waiting</h3><p>Set preferences in the sidebar, then choose <b>Build my trip</b>. Your plan will appear here.</p></div>', unsafe_allow_html=True)
    else:
        p = trip["preferences"]
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Destination", trip["destination_info"]["city"])
        m2.metric("Duration", f"{p['days']} days")
        m3.metric("Activity estimate", money(trip["estimated_total"], trip["currency"]))
        m4.metric("USD / INR estimate", f"${trip['estimated_total']/p['rate']:,.0f} / ₹{trip['estimated_total']/p['rate']*83:,.0f}")
        st.caption("Estimates cover the listed activities and meal allowances only; flights, lodging, local transit and taxes are excluded.")
        for day in trip["itinerary"]:
            with st.expander(f"Day {day['day']} · {date.fromisoformat(day['date']).strftime('%A, %d %b')} — {day['cluster_center']}", expanded=(day["day"]==1)):
                rows = []
                for item in day["items"]:
                    rows.append({"Time":item["time"],"Slot":item["slot"],"Activity":item["activity"],
                                 "Category":item["category"],f"Cost ({trip['currency']})":money(item["cost"],trip["currency"]),
                                 "USD":f"${item['usd']:,.2f}","INR":f"₹{item['inr']:,.0f}",
                                 "Trip running total":money(item["cumulative"],trip["currency"])})
                st.dataframe(rows, use_container_width=True, hide_index=True)
                for item in day["items"]:
                    st.markdown(f"**{item['time']} · {item['slot']}** — {item['activity']}  \n"
                                f"<span class='small-muted'>{item['note']}</span>", unsafe_allow_html=True)
        with st.expander("How the route clustering works"):
            st.write("A nearest-neighbour heuristic groups catalogue coordinates into day-sized clusters, then fills the four required time slots. It reduces obvious geographic jumps but is not a routing engine; verify routes, traffic, accessibility and opening times before travel.")
        if st.button("Save this trip to trip history", type="primary"):
            snapshot = serializable_trip(trip)
            st.session_state.saved_trips.insert(0, snapshot)
            st.success("Trip saved in this browser session. Export JSON below for durable storage.")

with tabs[2]:
    st.subheader("Make the plan feel more like you")
    trip = st.session_state.current_trip
    if not trip:
        st.info("Build an itinerary first, then swap a single slot without regenerating the rest.")
    else:
        day_choices = [f"Day {d['day']}" for d in trip["itinerary"]]
        chosen_day_label = st.selectbox("Choose day", day_choices)
        day_num = int(chosen_day_label.split()[-1])
        day = trip["itinerary"][day_num-1]
        slot_labels = [f"{i+1}. {item['slot']} — {item['activity']}" for i,item in enumerate(day["items"])]
        chosen_slot = st.selectbox("Choose the slot to change", slot_labels)
        item_idx = int(chosen_slot.split(".")[0])-1
        instruction = st.text_input("What would you like instead?", placeholder="e.g. Swap museum for outdoor market")
        quick = st.selectbox("Quick request", ["Custom request","Swap museum for outdoor market","Find vegetarian lunch spot","More outdoor / nature","More history","Lower-cost alternative"])
        if quick != "Custom request" and not instruction:
            instruction = quick
        st.caption("The local demo engine changes only the selected slot, keeps other days untouched, and recalculates running costs.")
        if st.button("🔁 Swap selected activity", type="primary"):
            if not instruction.strip():
                st.warning("Enter a swap request or choose a quick request.")
            else:
                if quick == "Lower-cost alternative":
                    instruction = "lower-cost food market"
                swap_activity(trip, day_num, item_idx, instruction)
                st.session_state.current_trip = trip
                st.success("One slot updated. Your other activities remain unchanged.")
                st.rerun()
        st.markdown("#### Selected day at a glance")
        st.dataframe([{"Time":x["time"],"Slot":x["slot"],"Activity":x["activity"],"Cost":money(x["cost"],x["currency"])} for x in trip["itinerary"][day_num-1]["items"]], use_container_width=True, hide_index=True)
        if provider != "Demo mode (no API)" and api_key and st.button("✨ Generate a natural-language travel tip"):
            tip = try_llm_enhance(prefs, api_key, provider,
                f"Give 3 concise, cautious travel tips for {trip['destination_info']['city']} for a {p['days'] if (p:=trip['preferences']) else days}-day {p['budget']} trip. Interests: {', '.join(p['interests'])}. Do not claim live opening hours or availability.")
            if tip: st.write(tip)

with tabs[3]:
    st.subheader("Trip library & offline guide")
    trip = st.session_state.current_trip
    if trip:
        st.markdown(f"**Current draft:** {trip['destination_info']['city']} · {trip['preferences']['days']} days · {money(trip['estimated_total'],trip['currency'])}")
        try:
            pdf_bytes = build_pdf(trip)
            st.download_button("📄 Download offline PDF guide", data=pdf_bytes,
                               file_name=f"{trip['destination_info']['city'].lower().replace(' ','_')}_itinerary.pdf",
                               mime="application/pdf", type="primary")
        except Exception as exc:
            st.error(f"PDF generation failed: {type(exc).__name__}. Please try again.")
        if st.button("Save current draft"):
            st.session_state.saved_trips.insert(0, serializable_trip(trip))
            st.success("Saved to session trip history.")
    else:
        st.info("Build or select a trip to export a PDF guide.")
    st.markdown("---")
    st.markdown("#### Saved trip history")
    saved = st.session_state.saved_trips
    if saved:
        options = [f"{x['destination_info']['city']} · {x['preferences']['days']} days · saved {x['created_at']} · {x['id']}" for x in saved]
        selected = st.selectbox("Select a saved trip", options)
        idx = options.index(selected)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Load selected trip"):
                st.session_state.current_trip = restore_trip(saved[idx])
                st.success("Loaded saved trip.")
                st.rerun()
        with c2:
            try:
                loaded = restore_trip(json.loads(json.dumps(saved[idx])))
                loaded["preferences"]["start_date"] = date.fromisoformat(loaded["preferences"]["start_date"])
                pdf = build_pdf(loaded)
                st.download_button("Download selected PDF", data=pdf,
                                   file_name=f"saved_trip_{idx+1}.pdf", mime="application/pdf")
            except Exception as exc:
                st.warning(f"Could not prepare selected PDF: {type(exc).__name__}")
        st.download_button("Export trip history (JSON)", data=json.dumps(saved, indent=2, ensure_ascii=False),
                           file_name="travel_trip_history.json", mime="application/json")
    else:
        st.caption("Saved trips persist for the current Streamlit session only. Download the JSON history to keep a copy.")
    st.markdown("---")
    st.markdown("#### Deployment & privacy notes")
    st.write("• No external database is required. Session history is intentionally ephemeral on Streamlit Community Cloud; export JSON for backup.")
    st.write("• API keys are password-masked and not saved into trip records. Use `st.secrets` for server-managed production credentials.")
    st.write("• For production-grade accuracy, plug in validated places, weather, maps/routing, exchange-rate and emergency-number providers; review provider terms and add caching/rate limits.")
    st.write("• PDF estimates are illustrative and should not be treated as confirmed prices, bookings or safety advice.")

st.markdown("---")
st.caption("Skill Wallet Capstone Project 4 · Personalized Travel Itinerary Planner · Demo-first, API-optional")
