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

I kept thinking about **teamLab’s *Sketch Aquarium*** while building this. If you have not seen it: you colour a fish on a sheet, they scan it in, and suddenly your drawing is swimming in a huge projected tank with everyone else’s. It is a lovely trick. You made something small and silly on paper, and the room treats it like a real fish for a minute.

Fish Tank is trying for a similar **“hey, that’s mine”** moment, just with different ingredients. Same idea of a **shared body shape** so every fish fits the world, and a **wall of other people’s fish** instead of one perfect animation. The big difference is scale and setup. teamLab’s version is built for **museums**—big space, scanning desks, the whole room feels like water. Mine is **deliberately smaller**: you draw on a **phone or tablet**, the picture goes to the cloud, and TouchDesigner shows **up to twenty** fish in a **simple grid**. No wraparound screens, no ticket hall—more like something you could run in a bar, a studio night, or a degree show corner.

I am not claiming Fish Tank is in the same league. teamLab’s work is polished and enormous; mine is a weekend-and-evenings stack of web plus realtime video. But the **heart** is similar: drawing is not just for you, it is an offer to the room. If you put a mark in, the tank is supposed to **answer back**. *Sketch Aquarium* proved that idea works at world-class level. Fish Tank is my stab at the same kindness on a **DIY** budget.

---

## 5. Reflection: improvements and future possibilities

If I repeated the project, I would **test on the final projector earlier**: colour, gamma, and motion that look balanced on a laptop often need another pass at ten feet. I would also document **operator and storage names** for whoever runs the venue night—installation art fails in handover as often as in code.

**Future directions** might include: gentle **sound** tied to arrivals (chime, underwater bump) with volume capped for mixed-use spaces; **marking fish as “released”** after a time so the queue tells a story of turnover; **CORS and rate limits** hardened for a fully public URL; or a **second screen** that shows only names as credits. A richer **archival** layer—exporting a nightly collage—would connect the ephemeral wall to documentation. None of that is required for the core idea; the core idea is already there: send a fish, watch the tank acknowledge you.

---

## 6. Submission

**Submission link:** *[Add the same link provided for your final submission, or a separate documentation link, when your course shares it.]*

---

*Word count for rubric: approximately 1,000–1,200 words (check with your word processor; adjust section 5 or 4 by a sentence or two if your template requires a stricter bound).*
