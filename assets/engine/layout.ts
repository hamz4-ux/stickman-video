import { useVideoConfig } from "remotion";

export type SafeZone = {
  top: number;
  bottom: number;
  left: number;
  right: number;
  width: number;
  height: number;
};

export type StageLayout = {
  width: number;
  height: number;
  isVertical: boolean;
  cx: number;
  cy: number;
  ground: number;
  safe: SafeZone;
  /** Horizontal coordinate from 0..1 fraction of composition width */
  rx: (frac: number) => number;
  /** Vertical coordinate from 0..1 fraction of composition height */
  ry: (frac: number) => number;
  /** Hip y-coordinate so feet rest on the ground line for a given character scale */
  groundY: (scale?: number) => number;
};

export const getLayout = (width: number, height: number): StageLayout => {
  const isVertical = height > width;
  // Preserve 16:9 1080p ground line (852) for full backward compatibility;
  // for 9:16 vertical, place ground above the Shorts bottom UI safe zone.
  const ground = isVertical ? Math.round(height * 0.72) : Math.round((852 / 1080) * height);

  const top = isVertical ? Math.round(height * 0.14) : Math.round(height * 0.045);
  const bottom = isVertical ? Math.round(height * 0.22) : Math.round(height * 0.045);
  const left = Math.round(width * 0.05);
  const right = Math.round(width * 0.05);

  return {
    width,
    height,
    isVertical,
    cx: width / 2,
    cy: height / 2,
    ground,
    safe: {
      top,
      bottom,
      left,
      right,
      width: width - left - right,
      height: height - top - bottom,
    },
    rx: (frac: number) => width * frac,
    ry: (frac: number) => height * frac,
    groundY: (scale = 1) => ground - 92.5 * scale,
  };
};

export const useLayout = (): StageLayout => {
  const { width, height } = useVideoConfig();
  return getLayout(width, height);
};
