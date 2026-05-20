# AI QA Suite (MVP)

A lightweight Pytest-driven framework that automatically fetches code from AI models into memory and deterministically validates it against security flaws, syntax errors, and adversarial prompts — without executing arbitrary machine code unsafely.

---

## Project Architecture

```mermaid
graph TD
    A["📄 prompts.json\nPrompt Dataset"] -->|Loads Prompts| B["🧪 Pytest Orchestrator\ntest_ai_generator.py"]
    
    B -->|Session Fixture - Once Per Prompt| C["🌐 api_client.py\nHTTP POST"]
    C -->|minimax model| D(("☁️ OpenRouter API"))
    D -->|Raw Code String| C
    C -->|Cached in Memory + Written to Disk| E["💾 generated_outputs/\nprompt_N.txt"]
    C --> B

    B -->|Parametrize + Run Tests| F{"⚡ QA Validation Engine"}

    F -->|Test 1| T1["✅ Syntax Validation\nast.parse"]
    F -->|Test 2| T2["🚀 Executability\nexec in sandbox"]
    F -->|Test 3| T3["🧮 Functional Correctness\nassert func 2+3==5"]
    F -->|Test 4| T4["🔒 Security Audit\nRegex: password, eval, os.system"]
    F -->|Test 5| T5["🕵️ Prompt Leakage\nSYSTEM PROMPT keywords"]
    F -->|Test 6| T6["☣️ Toxic Content\nkill, hate, violence"]
    F -->|Test 7| T7["🤖 Hallucination\nLLM-as-a-Judge"]

    T1 --> R["📊 pytest-html\nreports/report.html"]
    T2 --> R
    T3 --> R
    T4 --> R
    T5 --> R
    T6 --> R
    T7 --> R

    %% Active tests - bright and vivid
    classDef active fill:#112240,stroke:#64ffda,stroke-width:3px,color:#64ffda;
    %% Inactive / planned tests - dull and muted
    classDef inactive fill:#1a1a2e,stroke:#444466,stroke-width:1px,color:#555577;
    %% Other nodes
    classDef default fill:transparent,stroke:#8892b0,stroke-width:2px,color:#ccd6f6;
    classDef highlight fill:#112240,stroke:#64ffda,stroke-width:2px,color:#64ffda;
    classDef api fill:#0d1117,stroke:#58a6ff,stroke-width:2px,color:#58a6ff;
    classDef engine fill:#233554,stroke:#ffb86c,stroke-width:2px,color:#e6f1ff;

    class A,B,C,E default;
    class D api;
    class R highlight;
    class F engine;
    class T1,T2,T3,T4 active;
    class T5,T6,T7 inactive;
```

---

## Execution Flow

### Phase 1 — Generation
Pytest loads `prompts.json`, and for each prompt, calls `generate_code()` once per session via the Minimax model. Responses are **cached in memory** and simultaneously **saved to `generated_outputs/`**.

### Phase 2 — QA Validation
All 7 test modules run against the cached code:

| Test | Method | Catches |
|------|--------|---------|
| Syntax Validation | `ast.parse()` | Broken brackets, invalid Python |
| Executability | `exec()` in sandboxed namespace | Runtime crashes |
| Functional Correctness | Predefined assertions | Wrong logic (e.g. sum returns wrong value) |
| Security Audit | Regex patterns | `password=`, `eval()`, `os.system()` |
| Prompt Leakage | Keyword scan | `SYSTEM PROMPT`, `INTERNAL INSTRUCTIONS` |
| Toxic Content | Keyword scan | `kill`, `bomb`, `hate`, `violence` |
| Hallucination | LLM-as-a-Judge | Fake libraries, nonexistent APIs |

### Phase 3 — Report
`pytest-html` compiles a dashboard at `reports/report.html` with all pass/fail results per prompt.

### Phase 4 — Teardown
The session fixture automatically clears the cached dictionary from memory and runs Python's garbage collector.

---

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key in .env
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE

# 3. Run the full suite
pytest tests/ -v -s --html=reports/report.html
```
