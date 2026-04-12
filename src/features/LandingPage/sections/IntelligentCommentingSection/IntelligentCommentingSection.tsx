const commentingBullets = [
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon.png",
    title: "Instant Interaction: ",
    description:
      "The integrated chatbot automatically replies to your Facebook comments to ensure timely responses.",
    wrapperClass: "w-[533px] flex gap-[13.9px]",
    textClass: "w-[490px] h-[83.12px]",
  },
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-1.png",
    title: "Responsible Communication: ",
    description:
      "Reviewer mechanisms monitor all comment replies to ensure safe and accurate interactions.",
    wrapperClass: "w-[619px] mt-[24.9px] flex gap-[13.9px]",
    textClass: "w-[576px] h-[55.41px]",
  },
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-2.png",
    title: "Streamlined Management: ",
    description:
      "Transform audience engagement from a burdensome task into a streamlined growth engine.",
    wrapperClass: "w-[585px] mt-[48.6px] flex gap-[13.9px]",
    textClass: "w-[542px] h-[83.12px]",
  },
];

export const IntelligentCommentingSection = (): JSX.Element => {
  return (
    <>
      {/* Above vector */}
      <div className="absolute top-[0px] left-[815px] w-[717px] h-[1366px] flex">
        <div className="w-[717.27px] flex">
          <div className="w-[717.27px] flex">
            <div className="w-[717.27px] h-[1365.97px] ml-0 flex flex-col relative isolate">
              <img
                className="relative ml-[103.9px] w-[613.41px] h-[693.23px] mt-0 -z-10 pointer-events-none"
                alt="Vector"
                src="https://c.animaapp.com/mnq63gf4Bct2xt/img/vector-1.svg"
              />

              <div className="ml-0 w-[614.56px] h-[185.16px] mt-[160.4px] flex flex-col gap-[30.4px]">
                <p className="w-[610.56px] h-[99.36px] [font-family:'Poppins',Helvetica] font-normal text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.8px]">
                  <span className="font-bold tracking-[-0.44px]">
                    6. Intelligent Commenting
                  </span>
                </p>

                <p className="w-[610.56px] h-[55.41px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
                  Never miss an opportunity to interact with your followers on
                  your public posts.
                </p>
              </div>

              <div className="ml-[12.1px] w-[617px] h-[295.12px] mt-[32.0px] flex flex-col">
                {commentingBullets.map((point, index) => (
                  <div key={index} className={point.wrapperClass}>
                    <img
                      className="w-[27.08px] h-[27.52px]"
                      alt="Icon"
                      src={point.icon}
                    />
                    <p
                      className={`${point.textClass} [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]`}
                    >
                      <span className="font-semibold">{point.title}</span>
                      <span className="[font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]">
                        {point.description}
                      </span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. The Comments Mockup UI */}
      {/* ---> FIX: Added rounded-[40px] to the wrapper below so the shadow curves with the card <--- */}
      <div className="absolute top-[934px] left-[181px] w-[391px] h-[327px] rounded-[40px] shadow-[0px_4px_10px_#00000026]">
        <div className="flex flex-col w-[391px] h-[327px] items-start absolute top-0 left-0 bg-[#ffffff] rounded-[40px] shadow-[0px_2px_3px_#00000040]">
          <div className="flex flex-col items-start gap-2.5 px-4 py-0 relative self-stretch w-full flex-[0_0_auto]" />
          <div className="flex flex-col items-start gap-2.5 pt-0 pb-3 px-4 relative self-stretch w-full flex-[0_0_auto]" />
        </div>

        <div className="top-[66px] flex w-[390px] items-start gap-2 px-4 py-3 absolute left-px rounded-[40px]">
          <img
            className="relative w-8 h-8 object-cover"
            alt="Commenter avatar"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/commenteravatar.png"
          />

          <div className="inline-flex flex-col items-start gap-[3px] relative flex-[0_0_auto]">
            <div className="flex flex-col w-[304px] items-start gap-[1.06px] px-[6.37px] py-[5.31px] relative flex-[0_0_auto] bg-[#f0f2f5] rounded-[10.61px]">
              <div className="relative w-[295.53px] mt-[-0.53px] mr-[-4.27px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#000000] text-[12.7px] tracking-[0] leading-[normal]">
                Mike Johnson
              </div>

              <p className="relative w-[295.53px] mr-[-4.27px] [font-family:'Poppins',Helvetica] font-normal text-[#1e1e1e] text-[14.9px] tracking-[0] leading-[19.8px]">
                Hey! Do you have pink girls shirts?
              </p>
            </div>

            <div className="inline-flex items-start gap-3 relative flex-[0_0_auto]">
              <div className="relative w-fit mt-[-1.00px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                Like
              </div>

              <div className="relative w-fit mt-[-1.00px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                Reply
              </div>

              <div className="relative w-fit mt-[-1.00px] [font-family:'Helvetica-Regular',Helvetica] font-normal text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                5m
              </div>
            </div>
          </div>
        </div>

        <div className="top-[163px] flex w-[390px] items-start gap-2 px-4 py-3 absolute left-px rounded-[40px]">
          <img
            className="relative w-8 h-8"
            alt="Commenter avatar"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/commenteravatar-1.png"
          />

          <div className="inline-flex flex-col items-start gap-[3px] relative flex-[0_0_auto]">
            <div className="flex flex-col w-[304px] items-start gap-[1.06px] px-[6.37px] py-[5.31px] relative flex-[0_0_auto] bg-[#f0f2f5] rounded-[10.61px]">
              <div className="relative w-[295.53px] mt-[-0.53px] mr-[-4.27px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#000000] text-[12.7px] tracking-[0] leading-[normal]">
                SociaLift
              </div>

              <p className="relative w-[295.53px] mr-[-4.27px] [font-family:'Poppins',Helvetica] font-normal text-transparent text-[14.9px] tracking-[0] leading-[19.8px]">
                <span className="text-[#1e1e1e]">
                  Yes, we do! Check this out <br />
                </span>

                <span className="text-[#009dff]">www.fashion.com</span>
              </p>
            </div>

            <div className="inline-flex items-start gap-3 relative flex-[0_0_auto]">
              <div className="relative w-fit mt-[-1.00px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                Like
              </div>

              <div className="relative w-fit mt-[-1.00px] [font-family:'Arial-Bold',Helvetica] font-bold text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                Reply
              </div>

              <div className="relative w-fit mt-[-1.00px] [font-family:'Helvetica-Regular',Helvetica] font-normal text-[#1e1e1e99] text-[11px] tracking-[0] leading-[normal] whitespace-nowrap">
                5m
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};