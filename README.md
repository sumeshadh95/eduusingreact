# CoursePilot AI

**Turning Xamk courses into trend-based year-round short programmes.**

CoursePilot AI is a Streamlit and React demo app that shows how AI can turn a trending topic into a Xamk short programme (3 ECTS), summarize the source course material with Gemini or OpenAI, recommend a duration and price, personalize the learning experience for a nursing student, generate marketing content, and estimate income end-to-end in a single live walkthrough.

## Quick Start

### 1. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure AI

Copy `.env.example` to `.env` and add your Gemini API key:

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=AIza...
```

> **Note:** The app works fully offline without an API key. Hardcoded fallback content is used when the key is missing or the API call fails.

### 4. Run the original Streamlit app

```bash
streamlit run app.py
```

## React / Vite Frontend

This copy also includes a migrated React + Vite frontend with a Xamk-inspired UI kit style. The React UI calls a local FastAPI backend (`backend.py`) that reuses the original `services/*` logic, so Gemini/OpenAI generation stays server-side and still reads the key from `.env`.

```bash
pip install -r requirements.txt
npm install
npm run dev
```

`npm run dev` starts both services:

- React/Vite: `http://127.0.0.1:5173/`
- FastAPI backend: `http://127.0.0.1:8000/`

Open:

```bash
http://127.0.0.1:5173/
```

For a production build:

```bash
npm run build
```

## What This Demo Shows

1. **Trend Dashboard** — A trending topic ("Game Development", score 92) is identified.
2. **Course Matching** — The trend is matched to an existing Xamk course (94% match).
3. **AI Summary** — Course material is summarized by Gemini/OpenAI (or offline fallback).
4. **Programme Generation** — A 2-week, 3 ECTS programme is generated with AI and can be regenerated live.
5. **Personalized Learning** — The programme is adapted for a nursing student with AI-generated chapters and playable mini-game prompts.
6. **Teacher Availability & Recruitment** — Internal teachers and probable external teaching candidates are ranked, with AI-generated outreach email drafts.
7. **Marketing Content** — Website copy, social posts, partner emails, brochure text, and visual assets are generated.
8. **Income Estimation** — Revenue, profit, and break-even analysis.

## Important Notes

- **All data is mock.** Trends, courses, teachers, and material are hardcoded JSON/TXT files for demo purposes.
- **No real integrations.** Peppi, SharePoint, payments, LinkedIn, social-ad, and auth integrations are future work.
- **LinkedIn is connector-ready.** Official LinkedIn Talent Solutions / RSC access requires approved partner credentials, so the demo uses a local recruitment pool unless those env vars are configured.
- **AI keys are optional.** The demo is fully functional offline with fallback content.

## Tech Stack

- Python 3.10+
- Streamlit
- python-dotenv
- requests
- openai (Python SDK, optional fallback provider)
- React
- Vite
- lucide-react

## Future Work

- Real Peppi/SharePoint course catalog integration
- Multi-trend dashboard with live trend scoring
- Editable inputs with live recalculation
- Interactive mini-games (currently concept cards only)
- Multi-profile personalization (business, design, international students)
- Export programme as PDF / push marketing to LinkedIn
- Authentication and multi-user state
