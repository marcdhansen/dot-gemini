---
name: skill-recommender
description: Find relevant skills using vector search. Embeds skill descriptions with nomic-embed-text via Ollama, stores vectors in SQLite, returns top 3-5 relevant skills by cosine similarity. Query latency < 50ms. Includes feedback loop from skill ratings.
disable-model-invocation: true
allowed-tools: Bash
---

# Skill Recommender with Vector Search

Find relevant skills automatically using vector embeddings.

## Usage

```bash
# Rebuild the skill index (run once or when skills change)
python -m agent_harness.scripts.skill_recommender_cli rebuild

# Recommend skills for a task
python -m agent_harness.scripts.skill_recommender_cli recommend -q "code review for bugs"

# Show statistics
python -m agent_harness.scripts.skill_recommender_cli stats

# Rate a skill (feedback loop)
python -m agent_harness.scripts.skill_recommender_cli rate --skill code-review --rating 5
```

## Features

1. **Vector Embeddings**: Uses nomic-embed-text via Ollama for high-quality embeddings
2. **SQLite Storage**: Efficient local storage of skill metadata and embeddings
3. **Cosine Similarity**: Semantic matching based on skill descriptions
4. **Feedback Loop**: Ratings from retrospective affect future recommendations
5. **Low Latency**: Targets <50ms query time

## Integration

The skill recommender can be integrated into the planning phase:

```python
from agent_harness.skill_recommender import recommend_skills

# Get skill recommendations for a task
recommendations, latency = recommend_skills(
    "code review for bugs",
    top_k=5
)

for rec in recommendations:
    print(f"- {rec.skill.name}: {rec.similarity:.2f}")
```

## Database Location

`~/.agent/data/skill_recommender.db`

## Configuration

- **Embedding Model**: nomic-embed-text:latest
- **Skills Directory**: ~/.gemini/antigravity/skills/
- **Top K**: 3-5 skills returned
- **Rating Scale**: 1-5 (3 = neutral, 5 = excellent)
