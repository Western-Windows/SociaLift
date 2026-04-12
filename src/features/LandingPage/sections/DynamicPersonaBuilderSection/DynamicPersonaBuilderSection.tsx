// src/screens/LandingPage/sections/DynamicPersonaBuilderSection.tsx

const personaBubbles = [
  {
    bubbleClass:
      "top-[2785px] left-[430px] w-[95px] h-[93px] rounded-[47.39px/46.58px]",
    imgClass:
      "absolute top-[2795px] left-[451px] w-[66px] h-[66px] aspect-[1] object-cover",
    alt: "Character",
    src: "https://c.animaapp.com/hFv7aPLp/img/character-1@2x.png",
  },
  {
    bubbleClass:
      "top-[2864px] left-[580px] w-[53px] h-[53px] rounded-[26.33px]",
    imgClass:
      "absolute top-[2874px] left-[591px] w-[31px] h-[31px] aspect-[1] object-cover",
    alt: "Alien",
    src: "https://c.animaapp.com/hFv7aPLp/img/alien-1@2x.png",
  },
  {
    bubbleClass:
      "top-[2837px] left-[257px] w-[52px] h-[52px] rounded-[25.92px]",
    imgClass:
      "absolute top-[2845px] left-[265px] w-[35px] h-[35px] aspect-[1] object-cover",
    alt: "User tie hair",
    src: "https://c.animaapp.com/hFv7aPLp/img/user-tie-hair--1--1@2x.png",
  },
  {
    bubbleClass:
      "top-[2980px] left-[231px] w-[78px] h-[78px] rounded-[38.88px]",
    imgClass:
      "absolute top-[2993px] left-[250px] w-[47px] h-[47px] aspect-[1] object-cover",
    alt: "Builder",
    src: "https://c.animaapp.com/hFv7aPLp/img/builder-1@2x.png",
  },
  {
    bubbleClass:
      "top-[3083px] left-[375px] w-[110px] h-[110px] rounded-[55.08px]",
    imgClass:
      "absolute top-[3100px] left-[403px] w-[68px] h-[68px] aspect-[1] object-cover",
    alt: "Artist",
    src: "https://c.animaapp.com/hFv7aPLp/img/artist-1@2x.png",
  },
  {
    bubbleClass:
      "top-[3031px] left-[559px] w-[83px] h-[83px] rounded-[41.72px]",
    imgClass:
      "absolute top-[3044px] left-[580px] w-14 h-14 aspect-[1] object-cover",
    alt: "Following",
    src: "https://c.animaapp.com/hFv7aPLp/img/following-1@2x.png",
  },
];

const personaFeatures = [
  {
    iconSrc: "https://c.animaapp.com/hFv7aPLp/img/icon-3@2x.png",
    iconAlt: "Icon",
    top: "2990px",
    left: "822px",
    width: "534px",
    height: "83px",
    boldText: "Guided Setup: ",
    bodyText:
      "Collect inputs regarding your target audience, working hours, and market details through intuitive startup prompts.",
  },
  {
    iconSrc: "https://c.animaapp.com/hFv7aPLp/img/icon-4@2x.png",
    iconAlt: "Icon",
    top: "3106px",
    left: "824px",
    width: "620px",
    height: "55px",
    boldText: "Dynamic Profiles: ",
    bodyText:
      "Build and update a persona profile that customizes content creation and engagement strategies.",
  },
  {
    iconSrc: "https://c.animaapp.com/hFv7aPLp/img/icon-5@2x.png",
    iconAlt: "Icon",
    top: "3222px",
    left: "822px",
    width: "586px",
    height: "83px",
    boldText: "Authentic Engagement: ",
    bodyText:
      "Adapt strategies to your specific business niche to ensure engagement remains relevant and personalized.",
  },
];

export const DynamicPersonaBuilderSection = (): JSX.Element => {
  return (
    <>
      <img
        className="absolute top-[2671px] left-[49px] w-[723px] h-[670px]"
        alt="Vector"
        src="https://c.animaapp.com/hFv7aPLp/img/vector-1.svg"
      />

      <p className="absolute top-[2826px] left-[812px] w-[611px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
        Strengthen your brand&#39;s authenticity by letting the AI learn exactly
        who you are and who you serve.
      </p>

      <div className="absolute top-[2696px] left-[812px] w-[611px] [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.9px]">
        2. Dynamic Persona Builder
      </div>

      {personaFeatures.map((feature, index) => (
        <div
          key={index}
          className="absolute flex gap-[13.9px]"
          style={{
            top: feature.top,
            left: feature.left,
            width: feature.width,
            height: feature.height,
          }}
        >
          <img
            className="mt-0 w-[27.11px] h-[27.55px]"
            alt={feature.iconAlt}
            src={feature.iconSrc}
          />
          <p className="mt-0 [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]">
            <span className="font-semibold">{feature.boldText}</span>
            <span className="[font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]">
              {feature.bodyText}
            </span>
          </p>
        </div>
      ))}

      <div className="absolute top-[2757px] left-[173px] w-[543px] h-[449px] bg-white rounded-[49px] shadow-[0px_4px_10px_#00000040]" />

      <div className="absolute top-[2922px] left-[calc(50.00%_-_434px)] w-[326px] [text-shadow:0px_3.24px_3.24px_#00000040] [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[40.5px] tracking-[0] leading-[40.5px]">
        Choose from multiple personas!
      </div>

      {personaBubbles.map((bubble, index) => (
        <div key={index}>
          <div
            className={`absolute bg-white border-[0.81px] border-solid border-[#07265c] shadow-[0px_3.24px_31.59px_2.43px_#07265c40] ${bubble.bubbleClass}`}
          />
          <img className={bubble.imgClass} alt={bubble.alt} src={bubble.src} />
        </div>
      ))}
    </>
  );
};