import React from "react";
import { CHARACTERS } from "../stickman/characters";
import { ColdOpenScene, DataBeatScene, EndingScene, SplitCompareScene } from "../stickman/recipes";
import { SceneProps } from "./Video";

const S01: React.FC<SceneProps> = ({ dur }) => <ColdOpenScene dur={dur} hero={CHARACTERS.hero} hook={"IN 1939, THE DEADLIEST CONFLICT IN HUMAN H"} sub={"In 1939, the deadliest conflict in human history began when Germany invaded P..."} />;
const S02: React.FC<SceneProps> = ({ dur }) => <SplitCompareScene dur={dur} title={"KEY POINT 1"} left={{ character: CHARACTERS.hero, label: "BEFORE", pose: "shrug" }} right={{ character: CHARACTERS.expert, label: "AFTER", pose: "pointR" }} />;
const S03: React.FC<SceneProps> = ({ dur }) => <DataBeatScene dur={dur} hero={CHARACTERS.hero} value={100} suffix={"%"} caption={"By 1941, the war went global as the Soviet Union and the United States entered t"} />;
const S04: React.FC<SceneProps> = ({ dur }) => <SplitCompareScene dur={dur} title={"KEY POINT 3"} left={{ character: CHARACTERS.hero, label: "BEFORE", pose: "shrug" }} right={{ character: CHARACTERS.expert, label: "AFTER", pose: "pointR" }} />;
const S05: React.FC<SceneProps> = ({ dur }) => <DataBeatScene dur={dur} hero={CHARACTERS.hero} value={100} suffix={"%"} caption={"more than 70 million people lost their lives across land, sea, and air."} />;
const S06: React.FC<SceneProps> = ({ dur }) => <DataBeatScene dur={dur} hero={CHARACTERS.hero} value={100} suffix={"%"} caption={"In 1945, the Allies finally prevailed,"} />;
const S07: React.FC<SceneProps> = ({ dur }) => <EndingScene dur={dur} hero={CHARACTERS.hero} takeaway={"RESHAPING THE MODERN WORLD AND CREATING TH"} />;

export const GENERATED_SCENES = [
  { c: S01, from: 96 },
  { c: S02, from: 272 },
  { c: S03, from: 482 },
  { c: S04, from: 703 },
  { c: S05, from: 757 },
  { c: S06, from: 932 },
  { c: S07, from: 1009 },
];
export const GENERATED_DURATION = 1231;
