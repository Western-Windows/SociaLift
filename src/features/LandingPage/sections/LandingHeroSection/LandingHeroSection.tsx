export const LandingHeroSection = (): JSX.Element => {
  return (
    <div className="absolute top-0 left-0 w-[1536px] h-[1190px] bg-[#fff9f3]">
      <div className="absolute top-0 left-0 w-[1536px] h-[1190px]">
        <img
          className="absolute top-[584px] left-[-3464px] w-[1536px] h-[1190px]"
          alt="Bg"
          src="/img/BG.svg"
        />

        <img
          className="absolute top-0 left-0 w-[1536px] h-[1190px] aspect-[1.9] object-cover"
          alt="Main BG"
          src="https://c.animaapp.com/hFv7aPLp/img/main-bg.png"
        />

        <img
          className="absolute top-[512px] left-[634px] w-[902px] h-[678px]"
          alt="Shape"
          src="https://c.animaapp.com/hFv7aPLp/img/shape.svg"
        />

        <img
          className="absolute top-[289px] left-0 w-[833px] h-[902px]"
          alt="Shape"
          src="https://c.animaapp.com/hFv7aPLp/img/shape-1.svg"
        />

        <img
          className="absolute top-[659px] left-[228px] w-[1033px] h-[532px]"
          alt="Dash board"
          src="https://c.animaapp.com/hFv7aPLp/img/dash-board.png"
        />
        <img
          className="absolute top-[567px] left-[1230px] w-[113px] h-[131px]"
          alt="Shape"
          src="https://c.animaapp.com/hFv7aPLp/img/shape-2@2x.png"
        />

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
      </div>
      <div className="absolute w-[892px] h-[236px] top-[308px] left-[322px] flex flex-col gap-[27px]">
        <div className="w-[896px] h-[147px] flex flex-col gap-[31px]">
          <h1 className="w-[892px] h-[85px] [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[76.8px] text-center tracking-[0] leading-[84.5px]">
            Welcome to SociaLift!
          </h1>

          <p className="ml-12 w-[796.8px] h-[31px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#07265c] text-3xl text-center tracking-[-0.48px] leading-[30.7px]">
            <span className="tracking-[-0.14px]">Why make it, if you can </span>
            <span className="font-bold tracking-[-0.14px]">automate</span>
            <span className="tracking-[-0.14px]"> it.</span>
          </p>
        </div>

        <div className="ml-[326px] w-60 flex">
          <div className="w-60 h-[62.4px] relative">
            <div className="flex flex-col w-60 h-[62px] items-center justify-center gap-[9.6px] px-[19.2px] py-[15.36px] absolute top-0 left-0 bg-[#07265c] rounded-[96px]">
              <div className="inline-flex items-center justify-center gap-[8.64px] relative flex-[0_0_auto]">
                <div className="relative flex items-center justify-end w-fit mt-[-0.96px] [font-family:'Inter',Helvetica] font-semibold text-[#fff9f3] text-[15.4px] text-right tracking-[0] leading-[23.0px] whitespace-nowrap">
                  {""}
                </div>
              </div>
            </div>
            <div className="absolute top-3 left-[39px] w-[182px] h-[38px] flex gap-[14.4px]">
              <img
                className="w-[38.4px] h-[38.4px]"
                alt="Play button"
                src="https://c.animaapp.com/hFv7aPLp/img/play-button@2x.png"
              />

              <div className="mt-[6.7px] w-[127px] h-[25px] opacity-80 [font-family:'Inter',Helvetica] font-semibold text-white text-lg tracking-[0] leading-[25.0px] whitespace-nowrap">
                WATCH VIDEO
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};