# How to Use PIPA Expert

[English](./HOW-TO-USE.md) | [한국어](../ko/HOW-TO-USE.md)

> This guide is written for **non-developers**. You don't need to understand Python, Git, or APIs. If you can type a question, you can use this tool.

---

## What You Need (One-Time Setup)

| What | Why | How to Get It |
|------|-----|---------------|
| **Claude Code** | This is the app that runs the agent | [Get started here](https://docs.anthropic.com/en/docs/claude-code/overview) — available as CLI, desktop app, or VS Code extension |
| **This repository** | Contains the legal knowledge base + agent | Download from GitHub (see below) |

That's it. No databases, no servers, no API keys to configure (unless you want to refresh the legal data yourself).

---

## Downloading the Repository

You need a local copy of this project on your computer.

### If you have Git installed

Open a terminal and run:

```bash
git clone <repository-url>
```

This creates a `PIPA-expert` folder with all the legal data and agent files. Copy the current repository URL from your hosting page.

### If you don't have Git

1. Go to this repository's main hosting page
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the downloaded file to a folder of your choice (e.g., `Documents/PIPA-expert`)

---

## Starting the Agent

### Option A: Desktop App / VS Code

1. Open Claude Code
2. Open the `PIPA-expert` folder you downloaded
3. Type `/agents/pipa-agent` to activate the PIPA expert persona

### Option B: Terminal (CLI)

```bash
cd PIPA-expert
claude
```

Then type `/agents/pipa-agent` to activate the agent.

---

## Asking Questions

Just type your question in natural language. The agent understands both **Korean and English**, and responds in the language you use.

### Simple Lookups

> "개인정보보호법 제15조 보여줘"

> "What does Article 17 of PIPA say about the provision of personal information?"

> "개인정보 처리 통합 안내서 가이드라인 찾아줘"

### Legal Analysis

> "맞춤형 광고를 위해 행태정보를 수집할 때 동의 구조는 어떻게 설계해야 해?"

> "Can a data processor use personal information for AI model training under PIPA?"

> "정보통신망법과 개인정보보호법의 동의 규정 차이점은?"

### Cross-Referencing

> "제15조의 시행령 위임 조문은?"

> "가명정보 처리 관련 가이드라인 전부 보여줘"

> "제3자 제공에 관한 조문과 관련 시행령, 가이드라인을 교차 확인해 줘"

---

## Requesting a Legal Opinion (DOCX)

When you need a formal document — not just a chat answer — ask for a legal opinion:

> "맞춤형 광고 동의 구조 재설계 방안에 대한 법률의견서 작성해줘"

> "Draft a legal opinion on cross-border data transfers under PIPA. DOCX format."

> "제3자 제공 관련 법률의견서를 DOCX로 만들어줘"

The agent will:
1. Research across the full knowledge base (550 searchable statute files + 46 guidelines)
2. Draft a structured opinion with verified citations
3. Run the fact-checker to verify every legal reference
4. Generate a professional DOCX file saved to `${PIPA_OUTPUT_DIR:-output/opinions/}`

If the issue turns on a branch article such as `제7조의2`, ask the agent to verify directly against `law.go.kr` as well. The current local statute index is still flattened at the base article-number level for some laws.

---

## Understanding the Output

### Citation Tags

Every legal reference in the agent's output is tagged so you know how reliable it is:

| Tag | What It Means | Should You Trust It? |
|-----|--------------|---------------------|
| `[VERIFIED] [Grade A]` | Matched exactly against the statute text or PIPC guideline in the KB | High confidence — but always double-check critical points |
| `[VERIFIED] [Grade B]` | From a PIPC enforcement decision or court ruling in the KB | Good confidence — these are authoritative but secondary |
| `[UNVERIFIED]` | Found via web search, not in the local knowledge base | Verify independently before relying on it |
| `[INSUFFICIENT]` | The agent couldn't find enough evidence | The agent is being honest — don't guess, consult a lawyer |
| `[CONTRADICTED]` | Different sources say different things | Both sides are shown — you decide which applies |

### Source Grades

| Grade | What's In It | Can You Rely On It Alone? |
|-------|-------------|--------------------------|
| **A** | PIPA statute text, enforcement decrees, PIPC official guidelines | Yes |
| **B** | PIPC enforcement decisions, court precedents | Yes, but cross-check with Grade A recommended |
| **C** | Law firm analyses, academic papers | No — use as commentary only |
| **D** | News articles, AI summaries | Excluded from the system entirely |

---

## Adding Your Own Sources

Got a PIPC enforcement decision, a law firm newsletter, or an academic paper you want the agent to know about?

### Step 1: Drop the file

Place any file (PDF, DOCX, HTML) into the `${PIPA_INBOX_DIR:-library/inbox/}` folder.

### Step 2: Tell the agent

> "inbox에 파일 넣었어, ingest 해줘"

or simply:

> "/ingest"

### Step 3: Done

The agent will:
- Convert the file to Markdown
- Automatically classify its trust level (Grade A, B, or C)
- Extract metadata (title, date, keywords, related PIPA articles)
- Place it in the correct folder
- Update the search indexes

Your new source is now searchable and citable in future opinions.

### What to Add (Examples)

| You Have | What Happens |
|----------|-------------|
| PIPC official guideline PDF | Classified as Grade A, filed under guidelines |
| PIPC enforcement decision | Classified as Grade B, filed under decisions |
| Kim & Chang newsletter on PIPA amendments | Classified as Grade C, filed under reference |
| News article about data breach fine | Rejected as Grade D with a warning |

---

## Tips for Best Results

### Be Specific

| Instead of | Try |
|-----------|-----|
| "개인정보보호법에 대해 알려줘" | "개인정보보호법 제15조의 적법처리 근거 6가지는?" |
| "이거 합법이야?" | "제3자 제공 시 동의 없이 가명처리된 정보를 제공할 수 있는지 분석해 줘" |
| "데이터 수집 어떻게 해?" | "정보통신망법상 행태정보 수집 시 동의 요건과 개인정보보호법상 요건 비교" |

### Ask for Counterarguments

> "이 처리에 정당한 이익을 근거로 삼는 것에 반대하는 논거는?"

The agent has a built-in adversarial mode — it will look for exceptions, contrary precedents, and alternative interpretations. But it helps to ask explicitly.

### Request the Fact-Check Report

For important opinions, ask to see the verification results:

> "이 의견서의 팩트체크 리포트 보여줘"

This shows you exactly which citations were verified, which had issues, and the overall confidence score.

---

## Refreshing the Legal Data

The statute data is collected from the [Open Law API](https://open.law.go.kr) (Korea's official legal data service). To refresh:

```bash
python3 scripts/fetch-pipa-from-api.py --oc YOUR_EMAIL_ID
```

You need a free Open Law API account. The `--oc` parameter is your registered email ID. We recommend refreshing monthly or when you know a law has been amended.

---

## What This Tool Does NOT Do

- **It does not provide legal advice.** It's a research assistant that helps you find and organize legal sources faster. A qualified lawyer must review the output.
- **It does not know about your specific contracts or internal policies** — unless you add them via the ingest system.
- **It does not automatically update.** The legal data is a snapshot. Run the refresh script periodically or add new sources via ingest.
- **It currently covers Korean privacy law only.** For EU/GDPR, use the separate `GDPR-expert` repository.

---

## Getting Help

- **Something looks wrong?** Ask the agent: "제15조 인용을 검증해줘"
- **Need a different format?** Just ask: "마크다운 요약으로 줘" or "DOCX로 만들어줘"
- **Agent seems stuck?** Try rephrasing your question or breaking it into smaller parts


---

> **Remember:** This is a power tool, not an autopilot. It makes legal research dramatically faster and more thorough, but the final judgment always belongs to a qualified human.
