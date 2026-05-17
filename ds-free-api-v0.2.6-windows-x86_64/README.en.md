<p align="center"><br>
  <img src="https://raw.githubusercontent.com/NIyueeE/ds-free-api/main/assets/logo.svg" width="81" height="66"><br>
</p><br>
<br>
<h1 align="center">DS-Free-API</h1><br>
<br>
<p align="center"><br>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/NIyueeE/ds-free-api.svg"></a><br>
  <img src="https://img.shields.io/github/v/release/NIyueeE/ds-free-api.svg"><br>
  <img src="https://img.shields.io/badge/rust-1.95.0+-93450a.svg"><br>
  <img src="https://github.com/NIyueeE/ds-free-api/actions/workflows/ci.yml/badge.svg"><br>
</p><br>
<p align="center"><br>
  <img src="https://img.shields.io/github/stars/NIyueeE/ds-free-api.svg"><br>
  <img src="https://img.shields.io/github/forks/NIyueeE/ds-free-api.svg"><br>
  <img src="https://img.shields.io/github/last-commit/NIyueeE/ds-free-api.svg"><br>
</p><br>
<br>
[中文](README.md)<br>
<br>
A Rust API proxy that translates DeepSeek's free web chat into standard OpenAI and Anthropic-compatible API protocols (supports chat completions and messages, including streaming and tool calling).<br>

## Highlights
<br>
- **Zero-cost API proxy**: Uses DeepSeek's free web interface — no official API key needed, get OpenAI/Anthropic-compatible endpoints for free<br>
- **Dual protocol support**: Both OpenAI Chat Completions and Anthropic Messages API, drop-in compatible with mainstream clients<br>
- **Tool call ready**: Full OpenAI function calling implementation with a 3-tier self-healing pipeline (text repair → JSON repair → model fallback), covering 10+ malformed formats<br>
- **File upload ready**: Inline data URL files in OpenAI `file`/`image_url` content parts and Anthropic `image`/`document` content blocks are automatically uploaded to DeepSeek sessions; HTTP URLs trigger search mode so the model can access link content directly<br>
- **Web admin panel**: Built-in dashboard for account pool status, API key management, request logs, and hot-reloadable config — ready out of the box<br>
- **Built with Rust**: Single binary + single TOML config, cross-platform native performance (web panel compiled in at build time)<br>
- **Multi-account pool**: Idle-aware round-robin selection (DashMap lock-free reads), horizontal scaling for concurrency<br>

## Quick Start

### Binary Usage
<br>
1. Download and extract the archive for your platform from [releases](https://github.com/NIyueeE/ds-free-api/releases)<br>
2. Copy `config.example.toml` to `config.toml` and fill in accounts (optional — you can also configure via the admin panel after startup)<br>
3. Run `./ds-free-api`<br>
4. Visit `http://127.0.0.1:22217/admin` to set an admin password, then manage API keys and accounts from the panel<br>
<br>
```bash<br>
./ds-free-api<br>
./ds-free-api -c /path/to/config.toml<br>
RUST_LOG=debug ./ds-free-api<br>
```<br>
<br>
> **Concurrency**: The free API has session-level rate limits. This project has built-in rate-limit detection + exponential backoff retry for stability.<br>
> Recommended parallelism = accounts / 2. Supports starting without `config.toml` and adding accounts via the admin panel.<br>

### Docker Usage
<br>
```bash<br>
docker compose -f docker-compose.yaml up -d<br>
```<br>
<br>
Refer to the [sample compose file](./docker/docker-compose.yaml) for reference.<br>
<br>
The admin panel is at `http://localhost:22217/admin`. Set your admin password on first visit.<br>
The `config/` and `data/` directories are bind-mounted into the container — config changes persist to the host automatically.<br>

### Free Test Accounts
<br>
All accounts use password `test12345`:<br>
<br>
```text<br>
idyllic4202@wplacetools.com<br>
espialeilani+grace@gmail.com<br>
ar.r.o.g.anc.e.p.c.hz.xp@gmail.com<br>
theobald2798+gladden@gmail.com<br>
vj.zh.z.h.d.b.b.d.udhj.db@gmail.com<br>
```<br>
<br>
> **Tool call tag hallucination**: Built-in fuzzy matching handles variations (full-width `｜`<=>`|`, `▁`<=>`_`) for most formats.<br>
> If the model outputs a different fallback tag, add it via the admin panel or in `config.toml` under `[deepseek]`:<br>
><br>
> ```toml<br>
> tool_call.extra_starts = ["<|tool_call_begin|>", "<tool_calls>", "<tool_call>"]<br>
> tool_call.extra_ends = ["<|tool_call_end|>", "</tool_calls>", "</tool_call>"]<br>
> ```<br>

## API Endpoints
<br>
| Method | Path | Description |<br>
|--------|------|-------------|<br>
| GET    | `/`   | Redirect to admin panel |<br>
| GET    | `/health` | Health check |<br>
| POST   | `/v1/chat/completions` | Chat completions (streaming + tool calls) |<br>
| GET    | `/v1/models` | List models |<br>
| GET    | `/v1/models/{id}` | Model details |<br>
| POST   | `/anthropic/v1/messages` | Anthropic Messages (streaming + tool calls) |<br>
| GET    | `/anthropic/v1/models` | List models (Anthropic format) |<br>
| GET    | `/anthropic/v1/models/{id}` | Model details (Anthropic format) |<br>
<br>
The admin panel is at `/admin` — on first visit you'll be guided to set an admin password.<br>

## Model Mapping
<br>
The `model_types` config in `config.toml` (default `["default", "expert"]`) maps to model IDs:<br>
<br>
| OpenAI Model ID    | DeepSeek Mode  |<br>
| ------------------ | -------------- |<br>
| `deepseek-default` | Fast mode      |<br>
| `deepseek-expert`  | Expert mode    |<br>
<br>
Optional aliases via `model_aliases`, aligned by index with `model_types`. Empty strings are skipped:<br>
<br>
```toml<br>
# model_aliases = ["", "deepseek-v4-pro"]  → deepseek-v4-pro maps to expert (index 1)
model_aliases = []<br>
```<br>
<br>
The Anthropic compatibility layer uses the same model IDs via `/anthropic/v1/messages`.<br>

### Capability Toggles
<br>
- **Deep thinking**: Enabled by default. To explicitly disable, include `"reasoning_effort": "none"` in the request body.<br>
- **Web search**: Enabled by default (DeepSeek injects a stronger system prompt in search mode, improving tool call adherence). To explicitly disable, include `"web_search_options": {"search_context_size": "none"}` in the request body.<br>
- **File upload**: Inline files (data URL) are auto-uploaded to DeepSeek sessions; HTTP URLs trigger search mode:<br>
<br>
  **OpenAI endpoint:**<br>
  ```json<br>
  {"type": "file", "file": {"file_data": "data:text/plain;base64,...", "filename": "doc.txt"}}<br>
  {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}<br>
  {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}<br>
  ```<br>
<br>
  **Anthropic endpoint:**<br>
  ```json<br>
  {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}<br>
  {"type": "document", "source": {"type": "base64", "media_type": "text/plain", "data": "..."}}<br>
  {"type": "image", "source": {"type": "url", "url": "https://example.com/img.jpg"}}<br>
  ```<br>

## Web Admin Panel
<br>
Visit `http://127.0.0.1:22217/admin` after starting the server:<br>
<br>
- **Dashboard**: Request statistics, account pool status at a glance<br>
- **Accounts**: View/add/remove accounts, manually re-login accounts in Error state<br>
- **API Keys**: Create/delete API keys, masked display<br>
- **Models**: Available models with details<br>
- **Config**: Current runtime config (sensitive fields masked)<br>
- **Logs**: Recent request logs and runtime logs<br>
<br>
<p align="center"><br>
  <img src="https://raw.githubusercontent.com/NIyueeE/ds-free-api/main/assets/web_p1.png" alt="Dashboard Overview" width="700"><br>
  <br>
  <em>Dashboard overview</em><br>
</p><br>
<br>
<p align="center"><br>
  <img src="https://raw.githubusercontent.com/NIyueeE/ds-free-api/main/assets/web_p2.png" alt="Config Page" width="700"><br>
  <br>
  <em>Config editor page</em><br>
</p><br>
<br>
On first visit, you'll be guided to set an admin password (stored as bcrypt hash), then issued a JWT (24h validity). Password reset revokes old tokens.<br>

## Environment Variables
<br>
| Variable | Default | Description |<br>
|----------|---------|-------------|<br>
| `RUST_LOG` | `info` | Log level (`trace` / `debug` / `info` / `warn` / `error`) |<br>
| `DS_DATA_DIR` | `.` (current dir) | Data directory for `logs/runtime.log` and `stats.json` |<br>
| `DS_CONFIG_PATH` | `./config.toml` | Config file path (lower priority than `-c` flag) |<br>

## Security
<br>
- **Admin panel**: JWT authentication + bcrypt password hash + login rate limiting (5 failures → 5-minute lockout)<br>
- **API access**: API keys created via the admin panel (HashSet O(1) lookup)<br>
- **CORS**: Configurable allowed origins, defaults to `http://localhost:22217`<br>
- **Sensitive data**: Account IDs masked in response headers, request bodies excluded from logs, persisted files at 0600 permissions<br>

## Development

### Design Philosophy
<br>
**A single `config.toml` reflects all runtime state.** Admin panel changes are instantly persisted to `config.toml` and hot-reloaded into the running service.<br>
<br>
**No unnecessary runtime system dependencies.** The project prioritizes pure Rust or statically-linked dependencies (e.g., `rustls` → `rquest` with BoringSSL), ensuring a single binary with no external `.so`/`.dll` requirements — download and run.<br>

### Architecture Diagram
<br>
```mermaid<br>
flowchart TB<br>
    %% ===== Theme =====<br>
    classDef client fill:#eff6ff,stroke:#3b82f6,stroke-width:3px,color:#1d4ed8,rx:14,ry:14<br>
    classDef gateway fill:#fffbeb,stroke:#f59e0b,stroke-width:3px,color:#92400e,rx:12,ry:12<br>
    classDef openai_adapter fill:#f8fafc,stroke:#0a9e7b,stroke-width:2px,color:#334155,rx:10,ry:10<br>
    classDef anthropic_compat fill:#f8fafc,stroke:#d07354,stroke-width:2px,color:#334155,rx:10,ry:10<br>
    classDef ds_core fill:#f8fafc,stroke:#3964fe,stroke-width:2px,color:#1e40af,rx:10,ry:10<br>
    classDef external fill:#fef2f2,stroke:#ef4444,stroke-width:3px,color:#991b1b,rx:6,ry:6<br>
<br>
    %% ===== Nodes =====<br>
    Client(["Client"]):::client<br>
<br>
    subgraph GW ["HTTP Gateway Layer"]<br>
        Handler(["Router / Auth / Serialization"]):::gateway<br>
    end<br>
<br>
    subgraph PL ["Protocol Layer"]<br>
        direction TB<br>
<br>
        subgraph AC ["Anthropic Compat"]<br>
            A2O["Request<br/>Anthropic → OpenAI"]:::anthropic_compat<br>
            O2A["Response<br/>OpenAI → Anthropic"]:::anthropic_compat<br>
        end<br>
<br>
        subgraph OA ["OpenAI Adapter"]<br>
            ReqPipe["Request Pipeline<br/>Validation / Tool Extraction / Prompt Building"]:::openai_adapter<br>
            RespPipe["Response Pipeline<br/>SSE Parsing / Format Conversion / Tool Repair"]:::openai_adapter<br>
        end<br>
    end<br>
<br>
    subgraph CL ["Core Layer (ds_core)"]<br>
        Pool["Account Pool Rotation"]:::ds_core<br>
        PoW["PoW Solver"]:::ds_core<br>
        Session["Session Orchestration<br/>Create/Destroy / History Upload"]:::ds_core<br>
    end<br>
<br>
    DeepSeek[("DeepSeek API")]:::external<br>
<br>
    %% ===== Connections =====<br>
    Client -->|"HTTP Request"| Handler<br>
<br>
    Handler -->|"OpenAI Request"| ReqPipe<br>
    Handler -->|"Anthropic Request"| A2O<br>
    A2O -->|"OpenAI Request"| ReqPipe<br>
<br>
    ReqPipe --> Pool<br>
    Pool --> PoW<br>
    PoW --> Session<br>
    Session -->|"completion endpoint"| DeepSeek<br>
<br>
    Session -.->|"DeepSeek SSE Stream"| RespPipe<br>
    RespPipe -.->|"OpenAI Response"| Handler<br>
    RespPipe -.->|"OpenAI Response"| O2A<br>
    O2A -.->|"Anthropic Response"| Handler<br>
<br>
    %% ===== Subgraph Styles =====<br>
    style GW fill:#fffbeb,stroke:#f59e0b,stroke-width:2px,stroke-dasharray: 5 5<br>
    style PL fill:#fafafa,stroke:#94a3b8,stroke-width:2px<br>
    style AC fill:#fdf0ec,stroke:#d07354,stroke-width:2px<br>
    style OA fill:#e6f7f3,stroke:#0a9e7b,stroke-width:2px<br>
    style CL fill:#eef2ff,stroke:#3964fe,stroke-width:2px,stroke-dasharray: 5 5<br>
```<br>

### Data Pipeline

#### OpenAI (chat_completions) Pipeline:
<br>
```mermaid<br>
flowchart TB<br>
    %% ===== Theme =====<br>
    classDef ds_core fill:#eef2ff,stroke:#3964fe,stroke-width:2.5px,color:#1e40af,rx:10,ry:10<br>
    classDef openai_adapter fill:#e6f7f3,stroke:#0a9e7b,stroke-width:2.5px,color:#065f46,rx:10,ry:10<br>
    classDef step fill:#fffbeb,stroke:#f59e0b,stroke-width:1.5px,color:#334155,rx:6,ry:6<br>
<br>
    subgraph RQ ["Request Pipeline"]<br>
        direction TB<br>
        Q1["ChatCompletionsRequest"]:::openai_adapter<br>
        Q2["Validation + Defaults"]:::step<br>
        Q3["Extract tools/files + inject prompts"]:::step<br>
        Q4["Build DeepSeek native tag prompt"]:::step<br>
        Q5["Model mapping + capability toggles"]:::step<br>
        Q6["Retry with exp. backoff<br/>1s→2s→4s→8s→16s"]:::step<br>
        Q7["ChatRequest"]:::ds_core<br>
    end<br>
<br>
    subgraph RS1 ["Non-streaming Response"]<br>
        direction TB<br>
        OR1["ds_core SSE stream"]:::ds_core<br>
        OR2["SSE frame parse<br/>ContentDelta / Usage"]:::step<br>
        OR3["State machine merge<br/>contiguous text / accumulate usage"]:::step<br>
        OR4["Chunk aggregation<br/>concat content / reasoning / tool_calls"]:::step<br>
        OR5["ChatCompletionsResponse"]:::openai_adapter<br>
    end<br>
<br>
    subgraph RS2 ["Streaming Response"]<br>
        direction TB<br>
        OS1["ds_core SSE stream"]:::ds_core<br>
        OS2["SSE frame parse + state machine"]:::step<br>
        OS3["Chunk conversion<br/>DsFrame → ChatCompletionsResponseChunk"]:::step<br>
        OS4["Tool call XML parse"]:::step<br>
        OS5["Malformed tool call repair"]:::step<br>
        OS6["Stop sequence detect + obfuscation"]:::step<br>
        OS7["ChatCompletionsResponseChunk"]:::openai_adapter<br>
    end<br>
<br>
    Q1 --> Q2 --> Q3 --> Q4 --> Q5 --> Q6 --> Q7<br>
    OR1 --> OR2 --> OR3 --> OR4 --> OR5<br>
    OS1 --> OS2 --> OS3 --> OS4 --> OS5 --> OS6 --> OS7<br>
<br>
    style RQ fill:#f8fafc,stroke:#0a9e7b,stroke-width:2px<br>
    style RS1 fill:#f8fafc,stroke:#0a9e7b,stroke-width:2px<br>
    style RS2 fill:#f8fafc,stroke:#0a9e7b,stroke-width:2px<br>
```<br>

#### Anthropic (messages) Pipeline:
<br>
```mermaid<br>
flowchart TB<br>
    %% ===== Theme =====<br>
    classDef oai fill:#e6f7f3,stroke:#0a9e7b,stroke-width:2.5px,color:#065f46,rx:10,ry:10<br>
    classDef anth fill:#fdf0ec,stroke:#d07354,stroke-width:2.5px,color:#7c3a2a,rx:10,ry:10<br>
    classDef step fill:#fffbeb,stroke:#f59e0b,stroke-width:1.5px,color:#334155,rx:6,ry:6<br>
<br>
    subgraph RQ ["Request Pipeline"]<br>
        direction TB<br>
        Q1["MessagesRequest"]:::anth<br>
        Q2["Message expansion<br/>System prepend / text merge / image+document mapping"]:::step<br>
        Q3["Tool mapping<br/>ToolUnion → OpenAI Tool"]:::step<br>
        Q4["Capability toggle mapping<br/>thinking → reasoning_effort"]:::step<br>
        Q5["ChatCompletionsRequest"]:::oai<br>
    end<br>
<br>
    subgraph RS3 ["Non-streaming Response"]<br>
        direction TB<br>
        AR1["ChatCompletionsResponse"]:::oai<br>
        AR2["Content decomposition<br/>reasoning → Thinking<br/>content → Text<br/>tool_calls → ToolUse"]:::step<br>
        AR3["ID mapping<br/>chatcmpl → msg<br/>call → toolu"]:::step<br>
        AR4["MessagesResponse"]:::anth<br>
    end<br>
<br>
    subgraph RS4 ["Streaming Response"]<br>
        direction TB<br>
        AS1["ChatCompletionsResponseChunk stream"]:::oai<br>
        AS2["Chunk state machine<br/>block type switch / index progression"]:::step<br>
        AS3["Event mapping<br/>content → text_delta<br/>reasoning → thinking_delta<br/>tool_calls → input_json_delta"]:::step<br>
        AS4["MessagesResponseChunk"]:::anth<br>
    end<br>
<br>
    Q1 --> Q2 --> Q3 --> Q4 --> Q5<br>
    AR1 --> AR2 --> AR3 --> AR4<br>
    AS1 --> AS2 --> AS3 --> AS4<br>
<br>
    style RQ fill:#f8fafc,stroke:#d07354,stroke-width:2px<br>
    style RS3 fill:#f8fafc,stroke:#d07354,stroke-width:2px<br>
    style RS4 fill:#f8fafc,stroke:#d07354,stroke-width:2px<br>
```<br>
<br>
For detailed development guide (building, testing, Docker deployment, e2e testing, etc.), see [docs/en/development.md](./docs/en/development.md).<br>

## License
<br>
[GNU General Public License v3.0](LICENSE)<br>
<br>
[DeepSeek's official API](https://platform.deepseek.com/top_up) is very affordable — please support the official service.<br>
<br>
This project was born from the desire to try the latest models in DeepSeek's web interface during grayscale testing.<br>
<br>
**Commercial use is strictly prohibited** to avoid putting pressure on official servers. Use at your own risk.<br>
