"use client";

import { motion, useReducedMotion } from "framer-motion";
import { AbijaMascot } from "./abija-mascot";

export function AnimatedMascot() {
  const reduceMotion = useReducedMotion();
  return (
    <motion.div
      className="mx-auto mb-6 grid size-[92px] place-items-center"
      animate={reduceMotion ? undefined : { y: [0, -5, 0], rotate: [-2, 2, -2] }}
      transition={reduceMotion ? undefined : { duration: 4, repeat: Infinity, ease: "easeInOut" }}
    >
      <AbijaMascot className="size-full drop-shadow-[0_9px_14px_rgba(93,57,29,0.12)]" />
    </motion.div>
  );
}
