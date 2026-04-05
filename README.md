---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Email Triage - OpenEnv Simulation

A real-world OpenEnv-compliant simulation where an AI agent assumes the role of a Customer Support or Triage Engineer. The agent learns to read, classify, route, and reply to inbound emails. 

## Motivation

Most RL environments focus on games, navigation, or basic manipulation. In contrast, **Email Triage** tests an agent's ability to reason, formulate polite responses, handle customer refund policies, and sort large bulks of text using structured semantic labeling. This genuinely reflects real-world knowledge worker tasks.

## Setup Instructions

### Local Development
1. Install requirements: `pip install -r requirements.txt`
2. Run the API: `uvicorn main:app --host 0.0.0.0 --port 7860`
3. Optional, Validate Environment: `openenv validate`

### Running Inference Baseline
You can use the baseline script `inference.py` to evaluate your agent:
```bash
export API_BASE_URL="api_url_here"
export OPENAI_API_KEY="your_api_key_here"
export MODEL_NAME="gpt-4o-mini"
python inference.py
```

### Deploying to Hugging Face Spaces
This repository is optimized for HF Spaces as a Docker space.

## Environment Mechanics

### Observation Space
The observation space is a fully typed Pydantic model returning the current state of the inbox:
- `emails`: List of `Email` objects (sender, body, folder, label, replied context).
- `task_context`: Dynamic instructions with rules and the target goal (changes per difficulty).
- `scheduled_meetings`: Tracked external scheduling state.
- `last_action_feedback`: Status string of the last operation.

### Action Space
The agent can interact with the environment via structured tool calling:
- `view_email`: Focuses on an email.
- `classify`: Applies a label (e.g. 'Spam', 'Resolved').
- `reply`: Drafts a reply to an email (can include things like 'refund' processing).
- `move_to_folder`: Moves newsletters/urgent items.
- `schedule_meeting`: Places a meeting on the calendar.
- `submit`: Concludes the current task episode.

## Task Difficulties & Rewards
The environment offers progressive difficulty grades, automatically producing a scalable `0.0-1.0` reward signal based on partial progression:
- **Easy**: Isolate and classify a Phishing/Spam email (binary 1.0 reward).
- **Medium**: Customer complaint mitigation. The agent must formulate a reply, apologize, optionally offer a refund (+0.5), and label it resolved (+0.5).
- **Hard**: Triage a completely mixed inbox of promos, regular mail, and executive requests that trigger secondary actions like scheduling a meeting with the sales department. Partial rewards granted dynamically for moving correct subsets of the inbox. 
