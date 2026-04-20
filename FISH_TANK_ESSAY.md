# Fish Tank — Final project write-up

## 1. Introduction: concept, theme, and intent

Fish Tank is a participatory installation in two places at once. On a phone or tablet, you draw a fish inside a simple body shape, name it, and send it. On a larger surface in the venue—usually a projector or big screen—that drawing appears among a school of others, each in its own tile, all gently in motion. You do not install an app; the browser is the door.

The **concept** is a shared aquarium built from strangers’ marks: everyone contributes a small creature, and the room reads as one living wall rather than twenty separate videos. The **theme** is playful co-presence—your gesture is anonymous enough to feel low-stakes, yet specific enough (your colours, your line, your title) to feel owned. The **intent** is to make technology feel like a pond rather than a billboard: something that ripples when people touch it, instead of only broadcasting a fixed message.

There is a deliberate **tension in time**. Your fish does not always appear the instant you tap send; a short gap opens while the system catches up. That pause can read as frustration or as anticipation. We treat it as part of the metaphor—the tank has its own rhythm, like water that settles after you disturb it—while still keeping the delay small enough that trust is not broken.

---

## 2. Workflow and tools

Work moved in three layers: **capture**, **storage**, and **display**.

**Capture** is a small web app (Vite, React, TypeScript, Tailwind CSS) tuned for touch: colour palette, brush size, undo, and a canvas clipped to a fish silhouette so exports stay consistent. The page posts the name and a PNG-ready image to a hosted backend.

**Storage** uses **Supabase** (a Postgres database plus object storage) so each submission has a row (name, status, path to the image) and the texture file lives in a bucket the venue can read. **Netlify** hosts the static site and **serverless functions** that accept uploads and expose a simple “who is pending?” API for the venue. An API key keeps the live queue private from random scrapers while still allowing the installation machine to poll.

**Display** runs in **TouchDesigner** on a machine at the venue. A timer triggers a background poll; the network stores the latest JSON, applies texture URLs to a grid of **Movie File In** operators driving materials on twenty simple 3D fish rigs, composites tiles onto a canvas, and sends the result to **Perform** output for the projector. The web team and the real-time scene share only that contract—list of fish, URLs, labels—so either side can evolve without rewriting the other.

---

## 3. Key technical and creative challenges

**Readability at distance.** A phone drawing must survive projection. We constrained the body shape and kept the grid of cells large enough that silhouettes and colour blocks read from the back of a room. Creative challenge: generosity versus freedom—the template reduces anxiety and unifies the look; it also limits expressiveness, which we accepted as a trade-off for a crowded wall.

**Transparency and “ghost fish.”** Kiosk output is PNG with alpha; TouchDesigner’s PBR path needed careful alpha handling (premultiply, cutout threshold, side lighting) so edges did not read as grey halos or vanishing bodies. That was less glamorous than new features but essential for the piece to feel finished.

**Performance under load.** Early approaches that re-evaluated heavy expressions per vertex, per fish, caused hitches when twenty textures updated. We addressed it by keeping the richest deformation cheap (constant formulas on the mesh) and pushing only light, per-fish “personality” to parameters that evaluate once per object. Polling runs in a **background thread** with results applied on the main thread so HTTP did not stall the whole frame.

**Stable composition.** When a new fish arrives, the wall should not reshuffle every occupant like a sorted list; that reads as glitchy in a physical space. We assign **stable slots**: newcomers fill gaps or replace the oldest occupant, so most fish keep their place. That is a creative decision (calm, readable grid) implemented as a small state machine in the apply step.

---

## 4. Comparison with a reference work

A close reference is **teamLab’s *Sketch Aquarium*** (part of their museum and touring programmes). In that work, visitors **colour a fish on a prepared sheet**, **scan or register** the drawing, and **watch it released** into a large, immersive **digital aquarium** where it swims alongside creatures other people made. The emotional beat is the same one Fish Tank chases: a private, low-stakes doodle becomes **public and alive**—your mark is no longer only on paper or glass but **in a world shared with strangers**.

The **rhymes** are obvious: a **template body** so every contribution fits the system; **bright, readable** marks; and a **collective tank** rather than a single-hero screen. The **differences** are instructive. *Sketch Aquarium* is built for **physical venues** with teamLab’s scanning pipeline and **room-scale projection**; fish often **move through a continuous underwater scene**. Fish Tank is **smaller and web-first**: drawing happens in the **browser**, images travel through **cloud storage**, and TouchDesigner **tiles** a fixed number of fish on a **stable grid**—a deliberate choice for clarity in bars, studios, or classrooms rather than a full immersive wrap. Where teamLab foregrounds **wonder and scale**, Fish Tank foregrounds **portability and handoff**: one URL, one API key, one machine with Perform out.

That contrast is not a ranking. It clarifies **intent**: both pieces argue that **participatory drawing** and **real-time graphics** can belong together, but they **allocate budget** differently—museum spectacle versus **DIY infrastructure**. Fish Tank is a **homage in spirit** to the same contract *Sketch Aquarium* makes with its audience: *if you draw, the tank will answer*.

---

## 5. Reflection: improvements and future possibilities

If I repeated the project, I would **test on the final projector earlier**: colour, gamma, and motion that look balanced on a laptop often need another pass at ten feet. I would also document **operator and storage names** for whoever runs the venue night—installation art fails in handover as often as in code.

**Future directions** might include: gentle **sound** tied to arrivals (chime, underwater bump) with volume capped for mixed-use spaces; **marking fish as “released”** after a time so the queue tells a story of turnover; **CORS and rate limits** hardened for a fully public URL; or a **second screen** that shows only names as credits. A richer **archival** layer—exporting a nightly collage—would connect the ephemeral wall to documentation. None of that is required for the core idea; the core idea is already there: send a fish, watch the tank acknowledge you.

---

## 6. Submission

**Submission link:** *[Add the same link provided for your final submission, or a separate documentation link, when your course shares it.]*

---

*Word count for rubric: approximately 1,000–1,200 words (check with your word processor; adjust section 5 or 4 by a sentence or two if your template requires a stricter bound).*
