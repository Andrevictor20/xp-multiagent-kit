# Common mistakes (`craft-system`)

| Thought | Reality |
|---|---|
| "I'll build the whole guide in one go: tokens and ten components" | Ten components on unapproved foundations means ten reworks. Foundations, stop, then components. |
| "The audit found problems, I'll just fix them" | The person may disagree with half of the fixes. Report, stop, fix only what they pick. |
| "I kept the originals in a backup folder, so fixing is safe" | A backup doesn't make the person agree with the fixes. Report first. |
| "Buttons have hover and disabled, good enough" | A states matrix has every state × every variant: normal, hover, pressed, focus, disabled, loading, selected. |
| "`--teal-600` is a token" | It's a value. Components need roles (`--color-primary`) so the value can change in one place. |
| "This screen needs a slightly different card" | Make it a variant of the card, or use the card. A one-off is the start of drift. |

## Defaults (an existing guide overrides them)

| Default | Why |
|---|---|
| On hover, bordered pieces only darken the border | A changing background on cards and fields feels heavy |
| Hover is subtler than selected | When hover looks like selected, people think two things are chosen |
| Selecting never changes font weight | A weight change shifts the text's width |
| Placeholders are lighter than muted text | Otherwise a placeholder reads as entered text |
| Items in stacked lists and menus have a small gap, never touching | Touching highlights merge into one block |
| The focus ring only appears from the keyboard | A ring after a mouse click looks like a bug |
| Loading keeps the element's exact size | Layout shift |
| Shadows only on floating things (menus, popovers, dialogs, toasts), at two strengths | Shadows everywhere flatten the hierarchy they were meant to create |
| At most one primary action per screen | Two primaries means the screen didn't decide |
