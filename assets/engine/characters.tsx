import React from "react";
import { COL } from "./fx";
import { Actor, Joints, Key, Pose } from "./stick";

export type Accessory = "tie" | "scarf" | "tophat" | "crown" | "cap" | "glasses" | "none";
export type Face = "none" | "eyes" | "angry" | "sad" | "happy";

export type CharacterDef = {
  id: string;
  color: string;
  accessory?: Accessory;
  face?: Face;
  label?: string;
  scale?: number;
};

/** Default reusable character presets for consistent identity across scenes. */
export const CHARACTERS = {
  hero: { id: "hero", color: COL.orange, accessory: "none", face: "eyes", label: "YOU", scale: 1 },
  expert: { id: "expert", color: COL.blue, accessory: "glasses", face: "eyes", label: "EXPERT", scale: 1 },
  skeptic: { id: "skeptic", color: COL.purple, accessory: "cap", face: "eyes", label: "SKEPTIC", scale: 1 },
  banker: { id: "banker", color: COL.green, accessory: "tophat", face: "eyes", label: "BANK", scale: 1.05 },
  vip: { id: "vip", color: COL.gold, accessory: "crown", face: "happy", label: "VIP", scale: 1 },
} as const satisfies Record<string, CharacterDef>;

/** Helper to define a typed per-series or per-video character registry. */
export const defineCharacters = <T extends Record<string, CharacterDef>>(defs: T): T => defs;

export type CastActorProps = {
  character: CharacterDef;
  f: number;
  keys: Key[];
  base?: Partial<Pose>;
  scale?: number;
  facing?: 1 | -1 | ((f: number) => 1 | -1);
  face?: Face;
  label?: string;
  mod?: (f: number, p: Pose) => Pose;
  trails?: boolean;
  opacity?: number;
  draw?: number;
  children?: (j: Joints) => React.ReactNode;
  behind?: (j: Joints) => React.ReactNode;
};

/** Renders an Actor using a CharacterDef preset while allowing per-scene overrides. */
export const CastActor: React.FC<CastActorProps> = ({
  character,
  scale,
  face,
  label,
  ...rest
}) => (
  <Actor
    color={character.color}
    accessory={character.accessory}
    scale={scale ?? character.scale ?? 1}
    face={face ?? character.face ?? "eyes"}
    label={label ?? character.label}
    {...rest}
  />
);
