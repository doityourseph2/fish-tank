/**
 * Default silhouette constants (classic body). Prefer `fishBodyModels` for multi-shape.
 */
import { getFishBodyModel, DEFAULT_FISH_BODY_ID } from "./fishBodyModels";

const _classic = getFishBodyModel(DEFAULT_FISH_BODY_ID);

export const FISH_VIEW_W = _classic.viewW;
export const FISH_VIEW_H = _classic.viewH;
export const FISH_PATH_D = _classic.pathD;
