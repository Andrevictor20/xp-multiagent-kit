# Common mistakes (`craft`)

| Thought | Reality |
|---|---|
| "Three pages are clear enough, I'll just build them" | Confirm the list first. It costs one message. |
| "I'll make buttons 52px here; the token says 44, but this audience needs bigger" | That's a system decision. Propose it through `craft-system`, then use it everywhere. |
| "The brief says teal, so I'll override the blue in this page's CSS" | Code wins. Flag the conflict and ask; never patch tokens locally. |
| "I'll show it, they'll tell me what's wrong" | Run `craft-critique` in self-check first, and say what it fixed. |
| "The decisions are in my message, that's enough" | Messages scroll away. Append them to `DESIGN.md`. |
| "This session can't stop for answers, so I'll make the calls myself and list them" | Ending your turn with the question *is* stopping. Do that; build nothing past the first open stop. |
| "To save a round trip I'll put both stops in one message" | Fine, if you then stop. Ask both, build nothing, wait. |

## Closing summary (the shape of your final message)

```
Made: <pages/elements> — <where: files or boards>
Decisions: <each, one line with its why> (also in DESIGN.md › Decisions log)
System changes: <pieces or tokens added/changed> — affects: <screens>
Self-check fixed: <what craft-critique changed before you saw it>
Open questions: <what the person still has to decide>
```
