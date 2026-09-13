# ExploreEase 🧭

**ExploreEase** is an AI-powered travel recommendation system for India that converts natural-language travel requirements into **explainable, requirement-aware destination recommendations**.

The system combines:

* **LangChain** for RAG and AI components
* **LangGraph** for workflow orchestration
* **ChromaDB** for vector retrieval
* **Sentence Transformers** for local embeddings
* **Ollama** for local LLM inference
* Deterministic ranking and requirement-fit evaluation
* Claim-level groundedness evaluation

The current V1 focuses on **destination recommendation**. The planned V2 will evolve this into a complete travel-planning agent capable of generating itineraries, estimating budgets, recommending stay areas, and using live travel tools.

---

# ✨ What ExploreEase Does

A user can provide a natural-language request such as:

> I have 4 days and want a peaceful mountain trip with my girlfriend. My budget is low. I don't want extreme cold.

ExploreEase extracts the requirements, retrieves relevant destinations, ranks them against those requirements, evaluates the quality of the match, and selects the best available candidate.

Example:

```text
User Requirements
        ↓
4 days
mountains
low budget
couples
peaceful
avoid extreme cold
        ↓
Semantic Retrieval
        ↓
Candidate Ranking
        ↓
Requirement Fit
        ↓
Recommendation
        ↓
Manali
```

The system also identifies requirements that cannot currently be verified instead of automatically treating missing information as a mismatch.

---

# 🏗️ Architecture

```text
                         USER QUERY
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Query Analyzer    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Query Rewriter    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Chroma Retrieval  │
                  │   Semantic Search   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Destination Ranker  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Requirement Fit     │
                  │ Evaluation          │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Recommendation      │
                  │ Decision            │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Answer Generator    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Groundedness /      │
                  │ Claim Evaluation    │
                  └──────────┬──────────┘
                             │
                             ▼
                          RESPONSE
```

---

# 🧩 LangGraph Workflow

The V1 workflow is implemented as a LangGraph state graph:

```text
START
  │
  ▼
analyze_query
  │
  ▼
rewrite_query
  │
  ▼
retrieve_documents
  │
  ▼
rank_destinations
  │
  ▼
evaluate_requirement_fit
  │
  ▼
make_recommendation_decision
  │
  ▼
generate_answer
  │
  ▼
check_groundedness
  │
  ▼
END
```

Each stage operates as a separate node, making the pipeline modular and providing a foundation for conditional routing and tool usage in future versions.

---

# 📊 Dataset

The current travel knowledge base contains:

| Entity        |   Count |
| ------------- | ------: |
| Destinations  | **293** |
| Attractions   | **367** |
| Total records | **660** |

The dataset contains information including:

* Destination name
* State / Union Territory
* Region
* Description
* Travel styles
* Best-for categories
* Best months
* Ideal duration
* Budget tier
* Activities
* Food highlights
* Pros
* Cons
* Planning notes
* Data quality
* Verification status

The dataset intentionally does **not** fabricate dynamic information such as:

* Current weather
* Current temperature
* Live prices
* Opening hours
* Current ratings
* Availability

These are planned to be handled through live tools in V2.

---

# 🔍 Retrieval

ExploreEase uses:

```text
Sentence Transformers
        ↓
all-MiniLM-L6-v2
        ↓
384-dimensional embeddings
        ↓
ChromaDB
```

Each destination and attraction is converted into a LangChain `Document`.

The vector store performs semantic retrieval to identify candidate destinations relevant to the user's query.

### Important architectural distinction

Retrieval does **not** directly determine the recommendation.

Instead:

```text
Semantic Retrieval
        ↓
Candidate Set
        ↓
Deterministic Ranking
        ↓
Requirement Fit
        ↓
Recommendation
```

This separation makes the recommendation process more explainable.

---

# 🎯 Query Understanding

V1 uses a deterministic query analyzer.

It currently extracts:

* Intent
* Duration
* Budget
* Traveler type
* Preferences
* Activities
* Constraints
* Location type

For example:

```text
I have 4 days and want a peaceful mountain
trip with my girlfriend. My budget is low.
I don't want extreme cold.
```

becomes approximately:

```text
Intent:
destination_recommendation

Duration:
4 days

Location:
mountains

Budget:
low

Travelers:
couples

Preferences:
peaceful

Constraints:
avoid_extreme_cold
```

Using deterministic extraction for these fields makes the initial requirement representation predictable and inexpensive.

A richer travel profile is planned for V2.

---

# 🏆 Destination Ranking

After retrieval, candidates are scored against the extracted requirements.

V1 separates requirements into different categories.

### Hard requirements

* Location
* Duration
* Budget

### Soft requirements

* Traveler type
* Preferences
* Activities

The ranker also uses semantic similarity when exact matching is insufficient.

Example:

```text
Destination: Manali
Score: 50

Direct matches:
- duration
- couples

Possible matches:
- location

Unknown:
- peaceful
- extreme cold avoidance
```

---

# 🧠 Requirement Fit

The ranking score alone is not treated as a probability.

ExploreEase separately evaluates how much evidence exists for each requirement.

The system distinguishes:

```text
DIRECT MATCH
    ↓
Explicitly supported

SEMANTIC MATCH
    ↓
Likely semantic compatibility

POSSIBLE MATCH
    ↓
Potential compatibility, not verified

UNKNOWN
    ↓
Insufficient information

MISMATCH
    ↓
Evidence indicates a conflict
```

A key design principle is:

```text
UNKNOWN ≠ MISMATCH
```

For example, if the dataset doesn't contain enough climate information, the system should say:

> The current data does not verify whether extreme cold can be avoided.

It should **not** automatically say:

> Manali does not satisfy the requirement.

---

# 🧪 End-to-End Demo

## Input

```text
I have 4 days and want a peaceful mountain
trip with my girlfriend. My budget is low.
I don't want extreme cold.
```

## Extracted Requirements

```text
Intent:
destination_recommendation

Duration:
4 days

Location:
mountains

Budget:
low

Travelers:
couples

Preferences:
peaceful

Constraints:
avoid_extreme_cold
```

## Retrieved / Ranked Candidates

```text
Manali      Score: 50
Gulmarg     Score: 40
Rishikesh   Score: 40
```

## Recommendation Decision

```text
Recommendation:
Manali

Status:
partial_fit
```

## Final Response

```text
Recommendation: Manali

Why:
- Your 4-day trip fits the listed ideal duration of 4–6 days.
- Manali is explicitly listed as suitable for couples.
- The destination is a possible match for your requested
  mountain setting.

Limitations:
- The current data does not verify whether the destination
  is peaceful.
- The current data does not verify whether extreme cold
  can be avoided.
```

This demonstrates the complete V1 flow from **natural-language query → structured requirements → retrieval → ranking → requirement evaluation → recommendation → response**.

---

# ⚙️ Installation

## Prerequisites

Make sure you have installed:

* Python 3.10+
* Git
* Ollama

Verify Python:

```bash
python --version
```

Verify Git:

```bash
git --version
```

Verify Ollama:

```bash
ollama --version
```

---

# 📥 Setup

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ExploreEase
```

Replace `<YOUR_REPOSITORY_URL>` with your GitHub repository URL.

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

The main dependencies include:

```text
langchain
langchain-core
langchain-community
langchain-ollama
langchain-chroma
langchain-huggingface
langgraph
chromadb
sentence-transformers
pydantic
pydantic-settings
python-dotenv
```

---

# 🦙 Configure Ollama

ExploreEase uses Ollama for local LLM inference.

Start Ollama and pull the configured model:

```bash
ollama pull qwen3:1.7b
```

Verify that it is available:

```bash
ollama list
```

You should see:

```text
qwen3:1.7b
```

The application currently uses:

```python
LLM_MODEL = "qwen3:1.7b"
```

Ollama normally exposes the local service automatically.

No OpenAI API key or paid LLM API is required for the core local setup.

---

# 🗄️ Build the ChromaDB Vector Store

The dataset is expected at:

```text
data/india_travel_knowledge_base_v2_fully_populated.json
```

Run the ingestion script:

```bash
python -m app.scripts.ingest
```

The ingestion process:

```text
JSON Dataset
     ↓
Dataset Loader
     ↓
LangChain Documents
     ↓
Sentence Transformer Embeddings
     ↓
ChromaDB
```

The local vector database is stored under:

```text
data/chroma/
```

`data/chroma/` is excluded from Git because it is a generated local artifact.

---

# ▶️ Run the Application

After ingestion:

```bash
python -m app.main
```

The application will execute the complete LangGraph workflow.

---

# 🧪 Testing

The current V1 has been tested end-to-end using representative travel queries.

Example test:

```text
I have 4 days and want a peaceful mountain
trip with my girlfriend. My budget is low.
I don't want extreme cold.
```

The current implementation successfully:

* Parses the query
* Rewrites the query
* Retrieves destinations
* Ranks candidates
* Evaluates requirement fit
* Selects a recommendation
* Generates a grounded response
* Runs claim/groundedness evaluation

### Evaluation metrics

Formal accuracy metrics have **not yet been established**.

The current evaluation is primarily manual and component-level.

This is an intentional V1 limitation.

The V2 evaluation plan is to create a fixed benchmark of representative travel queries and measure:

```text
Query extraction accuracy
Ranking accuracy
Constraint satisfaction
Requirement-fit accuracy
Groundedness
End-to-end recommendation quality
```

This will allow the project to report quantitative performance rather than subjective demo results.

---

# 🧱 Project Structure

```text
ExploreEase/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   └── services.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   └── document_builder.py
│   │
│   ├── retrieval/
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   │
│   ├── query/
│   │   ├── analyzer.py
│   │   └── rewriter.py
│   │
│   ├── ranking/
│   │   ├── ranker.py
│   │   ├── requirement_fit.py
│   │   └── recommendation_decision.py
│   │
│   ├── generation/
│   │   └── answer_generator.py
│   │
│   ├── evaluation/
│   │   ├── groundedness_checker.py
│   │   └── claim_checker.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   └── scripts/
│       └── ingest.py
│
├── data/
│   ├── india_travel_knowledge_base_v2_fully_populated.json
│   └── chroma/
│
├── requirements.txt
├── .gitignore
└──
```
