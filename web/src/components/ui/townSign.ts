/**
 * “Street sign” chrome — adapted from Texture Town for Fish Tank.
 */
export const townSignInteract = [
  "rounded-[5px]",
  "border-2",
  "transition-[transform,box-shadow,filter] duration-150 ease-out",
  "shadow-[0_3px_0_rgb(0_0_0_/_0.28),inset_0_1px_0_rgb(255_255_255_/_0.11)]",
  "hover:-translate-y-0.5 hover:shadow-[0_4px_0_rgb(0_0_0_/_0.22),inset_0_1px_0_rgb(255_255_255_/_0.14)]",
  "hover:brightness-[1.03]",
  "active:translate-y-px active:shadow-[0_1px_0_rgb(0_0_0_/_0.38),inset_0_2px_5px_rgb(0_0_0_/_0.14)]",
  "active:brightness-[0.98]",
].join(" ");

export const townSignFocus =
  "focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base";
