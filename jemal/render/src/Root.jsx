import React, { useEffect, useRef, useState } from "react";
import { AbsoluteFill, Still, continueRender, delayRender } from "remotion";
import design from "../../jemal_carousel_design.json";
import { FONTS_CSS, SLIDE_CSS, buildSlide, fit, prepare } from "./core.generated.js";

// One still per slide, drawn by the same renderer the studio uses, from jemal_carousel_design.json.
const Slide = ({ id, n, portrait }) => {
  const ref = useRef(null);
  const [handle] = useState(() => delayRender(`carousel ${id} slide ${n}`));
  useEffect(() => {
    (async () => {
      const c = design.carousels.find((x) => x.id === id);
      const s = c.slides.find((x) => x.n === n);
      const photos = portrait && s.photo ? { [`${id}-${n}`]: portrait } : {};
      await prepare(c);
      await document.fonts.load("800 40px Montserrat");
      await document.fonts.load("500 20px Inter");
      const el = buildSlide(c, s, { photos, H: 1350 });
      ref.current.replaceChildren(el);
      fit(el);
      await document.fonts.ready;
      continueRender(handle);
    })();
  }, [id, n, portrait, handle]);
  return (
    <AbsoluteFill>
      <style>{FONTS_CSS + SLIDE_CSS}</style>
      <div ref={ref} />
    </AbsoluteFill>
  );
};

export const Root = () => (
  <Still id="Slide" component={Slide} width={1080} height={1350} defaultProps={{ id: 1, n: 1, portrait: null }} />
);
