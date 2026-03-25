# Skill Spec Reference

Canonical rules for authoring and reviewing skills.
Load this before drafting or reviewing any SKILL.md.

---

## File Structure

```
skill-name/              ← kebab-case, matches name field exactly
├── SKILL.md             ← required
├── CHANGELOG.md         ← required
├── scripts/             ← optional: Python/Bash helpers
├── references/          ← optional: API docs, tables, schemas, style guides
└── assets/              ← optional: templates, fonts, icons
```

No `README.md` inside the skill folder. READMEs go at repo root.

---

## Frontmatter Rules

```yaml
---
name: skill-name-in-kebab-case
description: What + when + negative trigger (max 1024 chars, no < or >)
compatibility: network/tool requirements (optional, 1-500 chars)
metadata:
  author: Name
  version: 1.0.0
  category: category-name
  tags: [tag1, tag2]
---
```

### `name` field
- kebab-case ONLY: `my-skill` not `my_skill` or `MySkill`
- Must match the folder name exactly
- No spaces, no capitals, no underscores
- Must not start with `claude` or `anthropic`

### `description` field
- Must include WHAT the skill does AND WHEN to use it
- Must include at least one negative trigger: `Do NOT use for...`
- Under 1024 characters — hard limit, will be truncated if exceeded
- No XML angle brackets: no `<` or `>`
- Use plain text, no markdown formatting
- Include specific phrases users would actually say
- Make it slightly "pushy" — Claude undertriggers naturally, so be explicit
  about edge cases and adjacent use cases you want to capture
- Focus on user *intent*, not skill *implementation*

---

## Progressive Disclosure

| Level | Content | When loaded |
|-------|---------|-------------|
| 1 | Frontmatter (name + description) | Always — injected into every prompt |
| 2 | SKILL.md body | When agent decides skill is relevant |
| 3 | references/ files | Only when body explicitly directs agent there |

**Level 2 (SKILL.md body):**
- Step-by-step workflow
- Examples with User/Response pairs
- Brief lookup tables (< 20 rows)
- Notes and caveats
- Target: under 500 lines

**Level 3 (references/):**
- API documentation
- Tables with > 20 rows
- API response schemas
- Style guides and checklists referenced by name in the body
- Any content the agent only needs occasionally

When approaching the 500-line limit, add a layer of hierarchy in the body
and push detail to references/ with clear pointers on when to read each file.

---

## Body Structure (Recommended)

```markdown
# Skill Name

One-line overview.

## When to Use

- Trigger scenario 1
- Trigger scenario 2

**Do not use for**: [negative trigger sentence]

## Instructions

### Step 1: [Name]
[What to DO, not just what to know]

### Step N: [Name]

### Pre-output checklist (for output/document skills)
- [ ] Did X?
- [ ] Loaded references/Y.md if Z applies?

## Examples

### Example 1: [Short name]
User asks: "..."
Response:
1. ...

## Notes

- Edge cases, API limits, caveats
```

---

## Quality Checklist

Run before presenting any skill to the user.

**Naming**
- [ ] Folder is kebab-case
- [ ] `name` field matches folder name exactly
- [ ] No underscores, capitals, or spaces in name or folder

**Frontmatter**
- [ ] `description` includes WHAT and WHEN
- [ ] `description` includes at least one negative trigger
- [ ] No XML angle brackets anywhere in frontmatter
- [ ] `compatibility` field notes any network or tool requirements
- [ ] `metadata` has author, version, category, tags

**Instructions**
- [ ] Steps are numbered and in a logical order
- [ ] Each step says what TO DO, not just what to know
- [ ] Security-sensitive steps validate inputs before acting
- [ ] Error handling or fallback behaviour is documented
- [ ] Output-generating skills have a pre-output checklist step

**Progressive disclosure**
- [ ] Frontmatter description is sufficient for routing without reading body
- [ ] SKILL.md body is under 500 lines
- [ ] Tables > 20 rows are in references/, linked from body
- [ ] API schemas are in references/, not inline
- [ ] Large lookup data is in references/, not inline

**Testing**
- [ ] evals.json exists with at least 3 output quality evals
- [ ] trigger-evals.json exists with at least 12 queries (mix of should/shouldn't)
- [ ] Output quality baseline has been run and recorded
- [ ] Triggering baseline has been run (or flagged as pending for Claude Code)

**Housekeeping**
- [ ] CHANGELOG.md exists with at least a [1.0.0] entry
- [ ] No README.md inside the skill folder

---

## Common Violations (Most Frequent First)

1. Underscore in folder name or `name` field — `my_skill` → `my-skill`
2. Missing negative trigger in description
3. Level 3 content (tables, schemas) inline in SKILL.md body
4. Vague description without user-intent phrases ("Helps with projects")
5. Missing `compatibility` field for network-dependent skills
6. No `CHANGELOG.md`
7. Instructions say "validate things" instead of specific validation steps
8. No evals — skill shipped without any baseline
9. `README.md` inside the skill folder
10. Description > 1024 characters (silently truncated)
