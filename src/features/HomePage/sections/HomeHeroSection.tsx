import { ActionCard } from "../../../components/ActionCard.tsx";

export const HomeHeroSection = (): JSX.Element => {
  const cards = [
    {
      step: "Step | 01",
      title: "Provide company information",
      description: "Helps provide instant, automated answers to frequently asked questions about your business.",
      linkText: "Go to form",
    },
    {
      step: "Step | 02",
      title: "Provide products database",
      description: "Helps provide instant, automated answers about your products and services.",
      linkText: "Go to form",
    },
    {
      step: "Step | 03",
      title: "Choose your persona",
      description: "Strengthen your brand's authenticity by letting our AI learn exactly who you are and who you serve for better posts generation, DM replying, and comment replying.",
      linkText: "Take quiz",
    },
  ];

  return (
    <div className="absolute top-0 left-0 w-[1536px] h-[1190px]">
      {/* REMOVED the solid blue main-bg.png image from here 
        so the gradient underneath can shine through!
      */}

      {/* Background vectors (The white curves are kept!) */}
      <img
        className="absolute top-0 left-0 w-44 h-[885px]"
        alt="Vector"
        src="https://c.animaapp.com/hFv7aPLp/img/vector-642.svg"
      />
      <img
        className="absolute top-[277px] left-[1375px] w-[161px] h-[910px]"
        alt="Vector"
        src="https://c.animaapp.com/hFv7aPLp/img/vector-643.svg"
      />

      {/* Main Text Content */}
      <div className="absolute w-[1000px] top-[260px] left-[268px] flex flex-col items-center gap-[20px]">
        <h1 className="w-full [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[70px] text-center tracking-[0]">
          Welcome to SociaLift!
        </h1>

        <p className="w-[796.8px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#07265c] text-3xl text-center tracking-[-0.48px]">
          <span className="tracking-[-0.14px]">Why make it, if you can </span>
          <span className="font-bold tracking-[-0.14px]">automate</span>
          <span className="tracking-[-0.14px]"> it.</span>
        </p>
      </div>

      {/* Let's Get Started Section */}
      <div className="absolute top-[520px] w-full flex justify-center items-center">
        <div className="relative inline-flex items-center">
          <img
            className="absolute right-[96%] top-[40px] w-[70px] object-contain mr-[20px] -scale-x-100 rotate-[260deg]"
            alt="Decorative dashes left"
            src="https://c.animaapp.com/hFv7aPLp/img/shape-2@2x.png"
          />
          <h2 className="[font-family:'Poppins',Helvetica] font-semibold text-[#0f2f65] text-[64px] text-center tracking-[-1.92px] leading-[68px] whitespace-nowrap">
            Lets get you started!
          </h2>
          <img
            className="absolute left-[100%] top-[-30px] w-[70px] object-contain ml-[15px]"
            alt="Decorative dashes right"
            src="https://c.animaapp.com/hFv7aPLp/img/shape-2@2x.png"
          />
        </div>
      </div>

      {/* The 3 Action Cards Wrapper */}
      <div className="absolute top-[680px] w-full flex justify-center gap-[30px]">
        {cards.map((card, idx) => (
          <ActionCard
            key={idx}
            step={card.step}
            title={card.title}
            description={card.description}
            linkText={card.linkText}
          />
        ))}
      </div>
    </div>
  );
};