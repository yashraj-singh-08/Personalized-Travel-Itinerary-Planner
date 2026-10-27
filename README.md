# Personalized Travel Itinerary Planner
**Skill Wallet Capstone Project 4** — a demo-first Streamlit travel SaaS prototype.

## Features
- Secure password-masked Gemini/Groq API key input, plus no-key demo mode.
- Trip preference sidebar for destination/vibe, dates, duration, budget, party, pace, interests, dietary notes and currency region.
- Seasonal/budget/mood destination recommendations from a curated local catalogue.
- Day-by-day itinerary with four time slots, approximate coordinate clustering, itemized activity/meal estimates, running cumulative totals and USD/INR conversions.
- Single-slot activity swaps that preserve the rest of the itinerary.
- Session-based trip history, JSON backup, and PDF export with pre-travel and emergency-contact checklists.
- Responsive Streamlit layout and custom wanderlust-inspired styling.

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Demo mode works without an API key.

## Optional AI provider
Choose Gemini or Groq in the sidebar and enter an API key. The key field is password-masked and is not stored in trip history/PDFs. For deployment, prefer a server-side secret in `.streamlit/secrets.toml` or Streamlit Community Cloud Secrets rather than entering a personal key. Never commit secrets to source control.

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and this README to a GitHub repository.
2. Create a new app in Streamlit Community Cloud and select `app.py`.
3. Deploy. Demo mode has no database or API-key dependency.

## Architecture and production caveats
- **UI:** Streamlit tabs, sidebar preference controls, activity swap controls, trip history and download actions.
- **Planner:** deterministic local catalogue, season/budget/mood scoring, nearest-neighbour geographic grouping, estimate calculations.
- **AI adapter:** optional Gemini/Groq natural-language tip helper. The core planner is independent of the LLM.
- **Persistence:** `st.session_state`; intentionally ephemeral and database-free. Users can export trip history as JSON. For durable multi-user SaaS persistence, add an authenticated storage layer.
- **PDF:** ReportLab-generated A4 guide, itinerary tables, pre-trip checklist and emergency contact placeholders.
- **Accuracy:** sample attractions and coordinates are approximate; cost estimates and FX rates are illustrative. The planner does not query live weather, opening hours, traffic, booking inventory, transit fares or emergency numbers. Verify all details using official sources before travel.
- **Security:** use secrets management for deployment, apply API quotas/rate limits, add authentication if handling private trip data, and avoid logging keys or personal travel details.
- **Routing:** clustering is a transparent heuristic, not a road-routing optimizer. A production release should use a mapping provider's route matrix, opening-hour checks, and accessibility/transit constraints.
