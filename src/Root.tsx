import "./index.css";
import React from "react";
import { Composition } from "remotion";
import { Video as TestSmoke, DURATION as TestSmoke_DURATION } from "./test-smoke/Video";
import { Video as CompoundDemo, DURATION as CompoundDemo_DURATION } from "./compound-demo/Video";
import { Video as Ww2Short, DURATION as Ww2Short_DURATION } from "./ww2-short/Video";
// stickman-video:imports

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TestSmoke"
        component={TestSmoke}
        durationInFrames={TestSmoke_DURATION}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ music: 0.35, sfx: 0.8, voice: "", captions: false }}
      />
      <Composition
        id="CompoundDemo"
        component={CompoundDemo}
        durationInFrames={CompoundDemo_DURATION}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ music: 0.35, sfx: 0.8, voice: "", captions: false }}
      />
      <Composition
        id="Ww2Short"
        component={Ww2Short}
        durationInFrames={Ww2Short_DURATION}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ music: 0.35, sfx: 0.8, voice: "", captions: false }}
      />
      {/* stickman-video:compositions */}
    </>
  );
};
