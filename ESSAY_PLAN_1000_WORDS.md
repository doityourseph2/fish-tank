# Essay plan: Fish Tank installation (~1000 words)

Use this as a **structure and prompt sheet** for a short reflective essay. Aim for **plain language**: audience can be curious visitors, tutors, or a general reader—**not** a technical paper. Skip formulas; talk about **ideas, flow, and why it’s engaging**.

**Target length:** ~1000 words (roughly 6–8 short paragraphs, or 4 sections × ~250 words).

**Tone:** Process-focused, personal where it fits (“we built…”, “the interesting part was…”), concrete examples over jargon.

---

## 1. Opening hook (~120–150 words)

**Purpose:** Say what the installation *is* in one breath, then why it matters.

**Prompts:**

- What does a visitor *do*? (Draw a fish, name it, see it appear “in the tank.”)
- What does the *room* see? (A live screen, many fish, a sense of a shared pool.)
- One sentence on the **feeling** you wanted (playful? communal? magical latency between phone and wall?).

**Avoid:** Listing every technology in sentence one.

---

## 2. The stack in human terms (~200–250 words)

**Purpose:** Explain the **pipeline** without lecturing on code.

**Prompts (pick what’s true for your build):**

- **Web / kiosk:** Why a browser? (Accessible, no app install, drawing on a tablet or phone.)
- **Cloud bit:** Drawings go somewhere central (database + file storage)—think “mailbox for fish,” not “REST API.”
- **TouchDesigner / venue:** The “tank” is a real-time scene that **asks** that mailbox for the latest visitors’ fish and **shows** them on a big surface.
- **One interesting friction:** Things are not instant—there is a small gap between **submit** and **appear**. Is that a bug or a feature? (Anticipation, rhythm of the room.)

**Avoid:** UUIDs, hashes, sine/cosine, Netlify vs Supabase feature lists unless one sentence clarifies “hosted web + database.”

---

## 3. Design choices that shape the experience (~250–300 words)

**Purpose:** Show *judgment*—what you decided and why it’s interesting.

**Prompts:**

- **Drawing inside a fish shape:** Why constrain the canvas? (Everyone’s art fits the same “body,” reads clearly on the 3D fish, feels fair in a grid.)
- **Colour, brush, undo:** Small UX details that make strangers willing to participate.
- **Many fish at once:** A **school** rather than one hero fish—shared wall, no single spotlight (unless you want to argue the opposite).
- **Stable slots / queue:** New fish appear without shuffling everyone else’s position—why that matters for a calm, readable wall.
- **Motion / “swimming”:** You can describe it as **gentle, repeating movement** so the wall feels alive, not like a slideshow—*without* explaining frequencies or tuning constants.

**Optional one-liner:** Each submission can have a **subtle, consistent** character in how it moves (same fish, same habit)—interesting for “the tank remembers you a little” without saying “deterministic hash.”

---

## 4. Process: how you actually made it (~200–250 words)

**Purpose:** Honest **making-of**—iteration, problems, wins.

**Prompts:**

- What did you build **first** (web, database, empty TD scene)?
- A **problem** you hit (performance, transparency, polling, resolution limits, venue screen) and how you **simplified** or fixed it—that’s often the most readable part.
- **Collaboration with tools:** e.g. sketch → prototype → install script → test on site.
- What you’d tell a future you: one thing to start earlier, or one thing you’d keep.

**Avoid:** File names and repo trees unless one example helps (e.g. “one script reloads all twenty fish textures”).

---

## 5. Closing (~120–150 words)

**Purpose:** Zoom out—meaning, not features.

**Prompts:**

- What question does the piece ask? (Participation? Attention? Shared authorship? Play in public space?)
- Who is it **for**—kids, late-night crowd, museum, bar?
- A single **image** or moment you want the reader to remember (e.g. “the first time a stranger saw their fish swim”).

---

## Word-count checklist

| Section              | Target words |
|----------------------|-------------|
| Hook                 | 120–150     |
| Stack / pipeline     | 200–250     |
| Design & experience  | 250–300     |
| Process / iteration  | 200–250     |
| Closing              | 120–150     |
| **Total**            | **~900–1100** |

Trim or expand the middle sections to land on 1000.

---

## Words and phrases to favour

- Live, queue, submit, appear, wall, school, rhythm, gentle motion, participation, constraint, playful, communal, latency, iteration, calm grid, readable from far away.

## Things to skip or simplify in this essay

- Exact equations, trigonometry, hashes, API route names, slot-index formulas.
- Long toolchains (“Vite, Tailwind, serverless…”)—bundle into “a small web app and hosted backend.”

---

## Optional title ideas (pick or adapt)

- *Fish Tank: Drawing a Live Wall*
- *From Phone to Tank: A Participatory Screen*
- *Twenty Fish and a Queue: Building a Social Aquarium*

---

*End of plan — write the essay in a separate doc or below this file if you prefer.*
