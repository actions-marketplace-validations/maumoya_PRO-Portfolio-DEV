# plan.json

```json
{
  "name": "Ada Lovelace",
  "job": "AI Engineer",
  "url": "https://ada.github.io/",
  "headline": "I build agents that ship.",
  "tagline": "Open-source AI tools for teams that want results they can measure.",
  "description": "Optional meta description, 150-160 chars. Defaults to the tagline.",
  "about": "Two or three sentences in the first person.",
  "links": {"github": "https://github.com/ada", "linkedin": "https://www.linkedin.com/in/ada", "email": "mailto:ada@example.com"},
  "langs": ["en", "es", "zh", "hi", "ar", "fr", "pt", "de", "ja", "it"],
  "sound": true,
  "skills": ["Python", "TypeScript", "LLM evals", "GitHub Actions"],
  "experience": [
    {"role": "Staff Engineer", "org": "Acme", "years": "2021-2025", "text": "Led the agent platform.", "keywords": "ai llm platform"}
  ],
  "projects": [
    {"repo": "engine", "title": "Analytical Engine", "pitch": "Turns punch cards into answers.",
     "proof": "1,200 stars", "tags": ["python", "math"], "demo": "https://ada.github.io/engine/",
     "image": "media/engine.gif", "alt": "The engine computing Bernoulli numbers"}
  ],
  "t": {"es": {"headline": "Construyo agentes que llegan a producción.", "p.engine.pitch": "Convierte tarjetas perforadas en respuestas."}}
}
```

Required: `name`, `url` (final https address, ends with `/`), `headline`, `tagline`, `projects`.
`projects[].repo` must match a repo name in repos.json; `build.py` refuses anything else.
Stars, language, last push and the code link come from GitHub, not from the plan.
`image` paths are relative to the site folder: copy the file there yourself.

## Copy rules

- Headline ≤8 words, a claim the projects prove. No "passionate", "ninja", "rockstar".
- Pitch: the benefit to the user of the project, one line. Not the stack (tags carry the stack).
- Proof: a number with its unit, quoted from the repo's README or GitHub data ("21% of a disk freed",
  "340 stars"). No source, no proof line.
- Order projects by what the audience cares about, not alphabetically.
- Search finds text on the page plus each card's `data-s` keywords (repo name, language, tags, topics)
  and each experience item's `keywords`; add the words a recruiter would type.

## Translating

Translation keys in `t.<lang>`: `headline`, `tagline`, `about`, `p.<repo>.pitch`, `p.<repo>.proof`, `xp.<index>`.
Missing keys fall back to English.

Translate the meaning, in the register a native professional would use on their own portfolio:
- Rewrite idioms and slogans instead of copying their structure ("ships" → es "llega a producción", not "envía").
- Keep product names, repo names, numbers and units unchanged; adapt number format only when a native reader expects it.
- Respect each language's conventions: German nouns capitalised and compound words, French spaces before `:`,
  Japanese and Chinese without spaces between words, Arabic right to left (the page flips automatically),
  Brazilian Portuguese (`pt`) not European.
- Afterwards read each language top to bottom as a native reader. Any line that sounds translated gets rewritten.
