import React, { useState } from "react";

type Direction = "forwards" | "reverse";
type Speed = "fast" | "normal" | "slow";

interface InfiniteScrollerProps {
  children: React.ReactNode;
  direction?: Direction;
  speed?: Speed;
  pauseOnHover?: boolean;
  className?: string;
}

const speedMap: Record<Speed, string> = {
  fast: "20s",
  normal: "40s",
  slow: "80s",
};

export const InfiniteScroller = ({
  children,
  direction = "forwards",
  speed = "normal",
  pauseOnHover = true,
  className = "",
}: InfiniteScrollerProps): JSX.Element => {
  const [isHovered, setIsHovered] = useState(false);
  
  const animationPlayState = pauseOnHover && isHovered ? "paused" : "running";
  // "forwards" is an animation-fill-mode, not a valid direction. Fallback to "normal".
  const animDirection = direction === "reverse" ? "reverse" : "normal";
  
  // The gap matching your original design
  const gap = "37px";

  return (
    <div
      className={className}
      style={{
        overflow: "hidden",
        width: "100%",
        position: "relative",
        display: "flex",
        gap: gap,
      }}
      onMouseEnter={() => pauseOnHover && setIsHovered(true)}
      onMouseLeave={() => pauseOnHover && setIsHovered(false)}
    >
      {/* Render two identical tracks for a seamless infinite loop */}
      {[0, 1].map((trackIndex) => (
        <div
          key={trackIndex}
          aria-hidden={trackIndex === 1 ? "true" : undefined}
          style={{
            display: "flex",
            flexDirection: "row",
            flexWrap: "nowrap",
            width: "max-content",
            gap: gap,
            paddingTop: "8px",
            paddingBottom: "8px",
            // Uses your Tailwind marquee keyframes instead of the broken 'scroll' keyword
            animation: `marquee ${speedMap[speed]} ${animDirection} linear infinite`,
            animationPlayState,
            // Provides the missing variable for the Tailwind calc() equation
            ["--gap" as string]: gap,
          }}
        >
          {React.Children.map(children, (child, index) => (
            <div
              key={index}
              style={{
                display: "block",
                flex: "0 0 auto",
                flexShrink: 0,
                flexGrow: 0,
                minWidth: 0,
              }}
            >
              {child}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};