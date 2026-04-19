/**
 * Side-view fish silhouettes (head right, tail left) in a shared 200×100 viewBox.
 * Used for canvas clip + SVG guide overlay.
 */
export type FishBodyModel = {
  id: string;
  name: string;
  description: string;
  pathD: string;
  viewW: number;
  viewH: number;
};

export const DEFAULT_FISH_BODY_ID = "classic";

export const FISH_BODY_MODELS: readonly FishBodyModel[] = [
  {
    id: "classic",
    name: "Streamline",
    description: "Balanced profile — good default.",
    pathD:
      "M 188 50 C 188 26 152 12 112 10 L 38 6 Q 8 50 38 94 L 112 90 C 152 88 188 74 188 50 Z",
    viewW: 200,
    viewH: 100,
  },
  {
    id: "bubble",
    name: "Bubble",
    description: "Round reef-fish body.",
    pathD:
      "M 182 50 C 182 14 118 6 72 18 C 28 28 10 42 10 50 C 10 58 28 72 72 82 C 118 94 182 86 182 50 Z",
    viewW: 200,
    viewH: 100,
  },
  {
    id: "arrow",
    name: "Arrow",
    description: "Sleek and speedy.",
    pathD:
      "M 196 50 C 196 42 165 32 110 30 L 32 28 Q 8 50 32 72 L 110 70 C 165 68 196 58 196 50 Z",
    viewW: 200,
    viewH: 100,
  },
  {
    id: "sail",
    name: "Sail",
    description: "Tall angelfish-style outline.",
    pathD:
      "M 184 50 C 184 8 88 4 52 28 L 36 50 L 52 72 C 88 96 184 92 184 50 Z",
    viewW: 200,
    viewH: 100,
  },
  {
    id: "disc",
    name: "Disc",
    description: "Compressed tall body.",
    pathD:
      "M 178 50 C 178 22 128 10 78 16 C 38 22 18 38 18 50 C 18 62 38 78 78 84 C 128 90 178 78 178 50 Z",
    viewW: 200,
    viewH: 100,
  },
  {
    id: "minnow",
    name: "Minnow",
    description: "Compact with a wider tail.",
    pathD:
      "M 168 50 C 168 32 128 24 88 28 L 42 32 Q 18 50 42 68 L 88 72 C 128 76 168 68 168 50 Z",
    viewW: 200,
    viewH: 100,
  },
] as const;

export const getFishBodyModel = (id: string): FishBodyModel => {
  const m = FISH_BODY_MODELS.find((x) => x.id === id);
  return m ?? FISH_BODY_MODELS[0];
};
