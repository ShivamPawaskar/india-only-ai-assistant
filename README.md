<div align="center">
  <img src="web/india-mark.svg" alt="India-Only AI Assistant mark" width="150" />

  <h1>India-Only AI Assistant</h1>

  <p>
    A focused browser-based AI assistant that answers India-related questions
    and politely refuses everything outside that scope.
  </p>

  <p>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-254f9d?style=for-the-badge&logo=python&logoColor=white" />
    <img alt="No framework" src="https://img.shields.io/badge/Backend-Standard%20Library-146b51?style=for-the-badge" />
    <img alt="Frontend" src="https://img.shields.io/badge/Frontend-HTML%20CSS%20JS-d96f24?style=for-the-badge" />
  </p>
</div>

---

## Why This Exists

Most AI assistants try to answer everything. This one is intentionally narrow:
it is designed to be helpful only for India-related topics such as history,
geography, culture, states, cities, festivals, sports, public life, science,
economy, and more.

If a user asks something unrelated to India, the model is instructed to return
exactly:

```text
I am sorry, I can only talk about India.
```

## Highlights

- Clean chat interface with a polished responsive layout
- India-only system prompt with strict refusal behavior
- Local Python web server using only the standard library
- Works with OpenCode Zen, OpenAI-compatible APIs, or local Ollama
- Simple `.env` configuration
- Offline tests with mocked model calls
- No frontend framework, no backend framework, no package lock-in

## Preview

The app opens as a focused chat workspace with:

- Provider and model status
- One-click starter prompts
- Live typing feedback
- Character counter
- Mobile-friendly layout
- A visual scope panel for supported India topics

## Tech Stack

| Layer | Choice |
| --- | --- |
| Backend | Python standard library HTTP server |
| Assistant logic | Provider-agnostic Python module |
| Frontend | HTML, CSS, and vanilla JavaScript |
| Config | `.env` file loaded by the app |
| Tests | Python `unittest` with mocked provider calls |

## Project Structure

```text
india_assistant.py      Core assistant prompt, config, and provider calls
web_app.py              Local web server and JSON API
web/index.html          Browser chat UI
web/styles.css          Responsive visual design
web/app.js              Chat behavior and loading states
web/india-mark.svg      App visual mark
test_cases.py           Offline unit tests
.env.example            Example environment configuration
requirements.txt        Dependency notes
README.md               Project documentation
```

## Quick Start

Clone the repository:

```powershell
git clone https://github.com/ShivamPawaskar/india-only-ai-assistant.git
cd india-only-ai-assistant
```

Create your environment file:

```powershell
copy .env.example .env
notepad .env
```

Add your provider settings. For OpenCode Zen, the default looks like this:

```text
ASSISTANT_PROVIDER=opencode
OPENCODE_API_KEY=your-opencode-api-key
OPENCODE_BASE_URL=https://opencode.ai/zen/v1
OPENCODE_MODEL=big-pickle
```

Start the website:

```powershell
python web_app.py
```

Open:

```text
http://127.0.0.1:8000
```

## Deploy To Vercel

This project includes Vercel-ready files:

- `api/index.py` as the serverless API entrypoint
- `vercel.json` for static rewrites from `/` to the `web/` UI

Install or run the Vercel CLI:

```powershell
npx vercel --version
```

Add your environment variables in the Vercel dashboard or with the CLI:

```powershell
npx vercel env add ASSISTANT_PROVIDER production
npx vercel env add OPENCODE_API_KEY production
npx vercel env add OPENCODE_BASE_URL production
npx vercel env add OPENCODE_MODEL production
```

For preview deployments, add the same variables to the `preview` environment.

Deploy:

```powershell
npx vercel --prod
```

## Provider Options

### OpenCode Zen

```text
ASSISTANT_PROVIDER=opencode
OPENCODE_API_KEY=your-opencode-api-key
OPENCODE_BASE_URL=https://opencode.ai/zen/v1
OPENCODE_MODEL=big-pickle
```

### OpenAI-Compatible API

```text
ASSISTANT_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### Ollama

```text
ASSISTANT_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
```

## Run Tests

```powershell
python test_cases.py
```

Expected result:

```text
Ran 6 tests

OK
```

## Example Questions

```text
Q: What is the capital of India?
A: New Delhi is the capital of India.

Q: Who was Akbar?
A: Akbar was the third Mughal emperor...

Q: What is the Eiffel Tower?
A: I am sorry, I can only talk about India.
```

## How The Guardrail Works

The app does not use Python keyword filtering. Instead, every request sends:

1. A system message defining the India-only scope
2. The user's question

The model decides whether the question is India-related. For unrelated prompts,
the required output is the fixed refusal sentence above.

## Security Notes

- Keep real API keys in `.env`
- Never commit `.env`
- `.env.example` is safe to share because it contains placeholder values only
- The browser talks to the local Python server, not directly to provider APIs

## Roadmap Ideas

- Add conversation export
- Add light and dark themes
- Add source-aware retrieval for Indian constitution, geography, and history
- Add a deployable version with server-side secret management

## License

This project is ready for learning, demos, and portfolio use. Add a license file
if you plan to publish it for wider reuse.
