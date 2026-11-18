import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { CastActor, CharacterDef } from "./characters";
import { Stage } from "./common";
import { Burst, COL, Caption, Dust, FONT, Slam, countUp, ease, fmt } from "./fx";
import { useLayout } from "./layout";
import { P, addPose, idle } from "./stick";

export type ColdOpenProps = {
  dur: number;
  hero: CharacterDef;
  hook: string;
  sub?: string;
  hitAt?: number;
};

/** Cold open: character reacts to a slamming hook title + optional subtitle. */
export const ColdOpenScene: React.FC<ColdOpenProps> = ({ hero, hook, sub, hitAt = 12 }) => {
  const f = useCurrentFrame();
  const { cx, ground, groundY, isVertical, safe } = useLayout();
  const scale = isVertical ? 0.95 : 1;
  const titleY = isVertical ? safe.top + 120 : safe.top + 160;

  return (
    <Stage
      hits={[hitAt]}
      power={20}
      svg={
        <>
          <CastActor
            character={hero}
            f={f}
            scale={scale}
            base={{ x: cx, y: groundY(scale) }}
            keys={[
              { f: 0, p: P.stand },
              { f: hitAt, p: { ...P.shock, head: -18 } },
              { f: hitAt + 18, p: P.shrug },
            ]}
            mod={(t, p) => addPose(p, idle(t, 1))}
          />
          <Burst x={cx} y={titleY + 40} at={hitAt} f={f} size={130} color={COL.orange} />
          <Dust x={cx} y={ground} at={hitAt} f={f} />
        </>
      }
      html={
        <>
          <Slam f={f} at={hitAt} x={cx} y={titleY} size={isVertical ? 84 : 110} color={COL.ink}>
            {hook}
          </Slam>
          {sub && (
            <Caption f={f} at={hitAt + 14} x={cx} y={titleY + (isVertical ? 110 : 130)} size={isVertical ? 34 : 40}>
              {sub}
            </Caption>
          )}
        </>
      }
    />
  );
};

export type SplitCompareProps = {
  dur: number;
  left: { character: CharacterDef; label: string; pose?: keyof typeof P };
  right: { character: CharacterDef; label: string; pose?: keyof typeof P };
  title?: string;
  hitAt?: number;
};

/** Side-by-side comparison of two characters/concepts, responsive to 16:9 and 9:16. */
export const SplitCompareScene: React.FC<SplitCompareProps> = ({ left, right, title, hitAt = 10 }) => {
  const f = useCurrentFrame();
  const { cx, rx, groundY, isVertical, safe } = useLayout();
  const scale = isVertical ? 0.85 : 1;
  const lx = rx(0.27);
  const rxPos = rx(0.73);
  const labelY = isVertical ? safe.top + 200 : safe.top + 170;

  return (
    <Stage
      hits={[hitAt]}
      power={14}
      svg={
        <>
          <CastActor
            character={left.character}
            f={f}
            scale={scale}
            facing={1}
            base={{ x: lx, y: groundY(scale) }}
            keys={[{ f: 0, p: P[left.pose ?? "pointR"] }]}
            mod={(t, p) => addPose(p, idle(t, 2))}
          />
          <CastActor
            character={right.character}
            f={f}
            scale={scale}
            facing={-1}
            base={{ x: rxPos, y: groundY(scale) }}
            keys={[{ f: 0, p: P[right.pose ?? "shrug"] }]}
            mod={(t, p) => addPose(p, idle(t, 5))}
          />
        </>
      }
      html={
        <>
          {title && (
            <Slam f={f} at={0} x={cx} y={safe.top + 60} size={isVertical ? 64 : 84} color={COL.ink}>
              {title}
            </Slam>
          )}
          <Caption f={f} at={hitAt} x={lx} y={labelY} bg={left.character.color} size={isVertical ? 30 : 36}>
            {left.label}
          </Caption>
          <Caption f={f} at={hitAt + 6} x={rxPos} y={labelY} bg={right.character.color} size={isVertical ? 30 : 36}>
            {right.label}
          </Caption>
        </>
      }
    />
  );
};

export type DataBeatProps = {
  dur: number;
  hero: CharacterDef;
  value: number;
  prefix?: string;
  suffix?: string;
  caption: string;
  countStart?: number;
  countEnd?: number;
};

/** Animated number counter beat with character cheer reaction. */
export const DataBeatScene: React.FC<DataBeatProps> = ({
  hero,
  value,
  prefix = "",
  suffix = "",
  caption,
  countStart = 8,
  countEnd = 42,
}) => {
  const f = useCurrentFrame();
  const { cx, groundY, isVertical, safe } = useLayout();
  const scale = isVertical ? 0.9 : 1;
  const num = countUp(f, countStart, countEnd, value);
  const numY = isVertical ? safe.top + 160 : safe.top + 180;

  return (
    <Stage
      hits={[countEnd]}
      power={16}
      svg={
        <>
          <CastActor
            character={hero}
            f={f}
            scale={scale}
            base={{ x: cx, y: groundY(scale) }}
            keys={[
              { f: 0, p: P.think },
              { f: countEnd, p: P.cheer },
            ]}
            mod={(t, p) => addPose(p, idle(t, 3))}
          />
          <Burst x={cx} y={numY} at={countEnd} f={f} size={140} color={COL.gold} />
        </>
      }
      html={
        <>
          <div
            style={{
              position: "absolute",
              left: safe.left,
              width: safe.width,
              top: numY - 70,
              textAlign: "center",
              fontFamily: FONT.comic,
              fontSize: isVertical ? 110 : 140,
              color: COL.ink,
            }}
          >
            {`${prefix}${fmt(num)}${suffix}`}
          </div>
          <Caption f={f} at={countStart} x={cx} y={numY + (isVertical ? 110 : 130)} size={isVertical ? 34 : 40}>
            {caption}
          </Caption>
        </>
      }
    />
  );
};

export type StationItem = {
  title: string;
  character: CharacterDef;
  pose?: keyof typeof P;
};

export type StationPanProps = {
  dur: number;
  stations: StationItem[];
};

/** Camera-panning scene across multiple stations, zooming out at the end. */
export const StationPanScene: React.FC<StationPanProps> = ({ dur, stations }) => {
  const f = useCurrentFrame();
  const { width, cx, groundY, isVertical, safe } = useLayout();
  const count = Math.max(1, stations.length);
  const panEnd = Math.max(20, dur - 35);
  const step = width;
  const maxCamX = (count - 1) * step;
  const camX = interpolate(f, [10, panEnd], [0, maxCamX], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const zoomOut = ease(f, panEnd, dur - 5, 1, Math.max(0.32, 1 / count));

  return (
    <Stage
      cam={{ x: camX, z: zoomOut }}
      svg={
        <>
          {stations.map((st, i) => (
            <g key={i} transform={`translate(${i * step}, 0)`}>
              <CastActor
                character={st.character}
                f={f}
                scale={isVertical ? 0.9 : 1}
                base={{ x: cx, y: groundY(isVertical ? 0.9 : 1) }}
                keys={[{ f: 0, p: P[st.pose ?? "stand"] }]}
                mod={(t, p) => addPose(p, idle(t, i + 1))}
              />
            </g>
          ))}
        </>
      }
      html={
        <div
          style={{
            position: "absolute",
            top: safe.top + 40,
            left: safe.left,
            width: safe.width,
            textAlign: "center",
            fontFamily: FONT.title,
            fontWeight: 800,
            fontSize: isVertical ? 48 : 64,
            color: COL.ink,
          }}
        >
          {stations[Math.min(count - 1, Math.floor((camX / Math.max(1, maxCamX)) * count))]?.title}
        </div>
      }
    />
  );
};

export type EndingProps = {
  dur: number;
  hero: CharacterDef;
  takeaway: string;
  credit?: string;
};

/** Ending scene: hero cheer + takeaway slam + optional source credit. */
export const EndingScene: React.FC<EndingProps> = ({ hero, takeaway, credit }) => {
  const f = useCurrentFrame();
  const { cx, groundY, isVertical, safe } = useLayout();
  const scale = isVertical ? 0.95 : 1;
  const titleY = isVertical ? safe.top + 140 : safe.top + 180;

  return (
    <Stage
      hits={[8]}
      power={16}
      svg={
        <CastActor
          character={hero}
          f={f}
          scale={scale}
          base={{ x: cx, y: groundY(scale) }}
          keys={[
            { f: 0, p: P.stand },
            { f: 8, p: P.cheer },
          ]}
          mod={(t, p) => addPose(p, idle(t, 4))}
        />
      }
      html={
        <>
          <Slam f={f} at={8} x={cx} y={titleY} size={isVertical ? 76 : 100} color={COL.orange}>
            {takeaway}
          </Slam>
          {credit && (
            <Caption f={f} at={20} x={cx} y={titleY + (isVertical ? 110 : 130)} size={isVertical ? 28 : 32}>
              {credit}
            </Caption>
          )}
        </>
      }
    />
  );
};
