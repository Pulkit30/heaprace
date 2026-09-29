"use client";

import { useRef, useState, type PointerEvent, type RefObject } from "react";

/**
 * Drag-to-resize for two panes inside `container`. Returns the first pane's size in percent
 * and props to spread onto the divider element.
 */
export function useSplit(
  container: RefObject<HTMLElement | null>,
  axis: "x" | "y",
  initial: number,
  [min, max]: [number, number],
) {
  const [percent, setPercent] = useState(initial);
  const dragging = useRef(false);

  const onPointerMove = (e: PointerEvent) => {
    if (!dragging.current || !container.current) return;
    const rect = container.current.getBoundingClientRect();
    const p = axis === "x" ? ((e.clientX - rect.left) / rect.width) * 100 : ((e.clientY - rect.top) / rect.height) * 100;
    setPercent(Math.min(max, Math.max(min, p)));
  };

  const handleProps = {
    role: "separator",
    "aria-orientation": axis === "x" ? ("vertical" as const) : ("horizontal" as const),
    onPointerDown: (e: PointerEvent) => {
      dragging.current = true;
      e.currentTarget.setPointerCapture(e.pointerId);
      document.body.style.userSelect = "none";
    },
    onPointerMove,
    onPointerUp: () => {
      dragging.current = false;
      document.body.style.userSelect = "";
    },
  };

  return [percent, handleProps] as const;
}
