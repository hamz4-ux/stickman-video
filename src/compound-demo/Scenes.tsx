import React from "react";
import { CHARACTERS } from "../stickman/characters";
import { ColdOpenScene, DataBeatScene, EndingScene, SplitCompareScene } from "../stickman/recipes";
import { SceneProps } from "./Video";

const S01: React.FC<SceneProps> = ({ dur }) => <ColdOpenScene dur={dur} hero={CHARACTERS.hero} hook={"MOST PEOPLE THINK SAVING MONEY IS JUST ABO"} sub={"Most people think saving money is just about putting cash in a jar."} />;
const S02: React.FC<SceneProps> = ({ dur }) => <SplitCompareScene dur={dur} title={"KEY POINT 1"} left={{ character: CHARACTERS.hero, label: "BEFORE", pose: "shrug" }} right={{ character: CHARACTERS.expert, label: "AFTER", pose: "pointR" }} />;
const S03: React.FC<SceneProps> = ({ dur }) => <DataBeatScene dur={dur} hero={CHARACTERS.hero} value={100} suffix={"%"} caption={"After 30 years,"} />;
const S04: React.FC<SceneProps> = ({ dur }) => <DataBeatScene dur={dur} hero={CHARACTERS.hero} value={100} suffix={"%"} caption={"100 dollars can grow into more than 1000 dollars without adding a single extra c"} />;
const S05: React.FC<SceneProps> = ({ dur }) => <EndingScene dur={dur} hero={CHARACTERS.hero} takeaway={"START EARLY, STAY CONSISTENT, AND LET TIME"} />;

export const GENERATED_SCENES = [
  { c: S01, from: 96 },
  { c: S02, from: 272 },
  { c: S03, from: 459 },
  { c: S04, from: 502 },
  { c: S05, from: 701 },
];
export const GENERATED_DURATION = 911;
