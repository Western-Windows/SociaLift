export const ProductFeatureOverviewSection = (): JSX.Element => {
  const aiContentFeatures = [
    {
      title: "Smart Enhancement: ",
      description:
        "Use a large language model to enhance posts according to your page insights and target audience.",
      wrapperClass: "ml-0.5 w-[533px] flex gap-[13.9px]",
      textClass: "w-[490px] h-[83.12px]",
      marginTop: "",
    },
    {
      title: "Brand Alignment: ",
      description:
        "Content creation is customized by your dynamic persona profile to maintain brand authenticity.",
      wrapperClass: "w-[619px] mt-[32.9px] flex gap-[13.9px]",
      textClass: "w-[576px] h-[55.41px]",
      marginTop: "mt-0",
    },
    {
      title: "Analytical Improvement: ",
      description:
        "Optimize audience engagement strategies through AI and analytics to improve both reach and brand perception.",
      wrapperClass: "ml-0.5 w-[585px] mt-[59.6px] flex gap-[13.9px]",
      textClass: "w-[542px] h-[83.12px]",
      marginTop: "mt-0",
    },
  ];

   const messengerFeatures = [
    {
      title: "Seamless Integration: ",
      description:
        "Deploy a generic chatbot integrated directly with Facebook Messenger.",
      wrapperClass: "w-[533px] flex gap-[13.9px]",
      textClass: "w-[490px] h-[83.12px]",
      marginTop: "",
      usePoppins: false,
    },
    {
      title: "Versatile Application: ",
      description:
        "Use the chatbot with any page type, whether you are selling clothes, food, or services.",
      wrapperClass: "ml-0 w-[619px] mt-[22.9px] flex gap-[13.9px]",
      textClass: "w-[576px] h-[55.41px]",
      marginTop: "mt-0",
      usePoppins: false,
    },
    {
      title: "Built-in Safeguards:",
      description:
        " Rely on reviewer bots to filter outputs, preventing model hallucinations and harmful responses.",
      wrapperClass: "ml-[5.0px] w-[585px] mt-[46.6px] flex gap-[13.9px]",
      textClass: "w-[542px] h-[83.12px]",
      marginTop: "mt-0",
      usePoppins: true,
    },
  ];
   return (
    <div className="absolute top-[3433px] left-0 w-[1536px] flex flex-col px-[13.6px] py-[87.7px] items-start min-h-[1650px] gap-[164px] bg-[#eeeaf3]">
      <div className="self-end flex items-start min-w-[1376px]">
        <div className="min-w-[1376px] flex items-start">
          <div className="w-[1376px] h-[673px] flex">
            <div className="w-[1376.48px] h-[673.14px] relative">
              <img
                className="absolute top-[33px] left-[665px] w-[632px] h-[573px]"
                alt="Vector"
                src="https://c.animaapp.com/hFv7aPLp/img/vector-2.svg"
              />

              <div className="absolute top-[27px] left-px w-[615px] h-[185px] flex flex-col gap-[30.4px]">
                <div className="w-[610.56px] h-[99.36px] [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.8px]">
                  3. AI Content Generation
                </div>

                <p className="w-[610.56px] h-[55.41px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
                  Create high-performing, platform-optimized posts without the
                  manual heavy lifting.
                </p>
              </div>



              <div className="absolute w-[617px] h-[314px] top-[261px] left-2 flex flex-col">
                {aiContentFeatures.map((feature, index) => (
                  <div key={index} className={feature.wrapperClass}>
                    <img
                      className={`${feature.marginTop} w-[27.08px] h-[27.52px]`}
                      alt="Icon"
                      src="https://c.animaapp.com/hFv7aPLp/img/icon-11@2x.png"
                    />
                    <p
                      className={`${feature.textClass} [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]`}
                    >
                      <span className="font-semibold">{feature.title}</span>
                      <span className="[font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]">
                        {feature.description}
                      </span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="ml-[5.84px] flex items-start min-w-[1420px]">
        <div className="min-w-[1420px] flex items-start">
          <div className="w-[1420px] h-[519px] flex">
            <div className="w-[1419.56px] h-[519.48px] ml-0 relative">
              <img
                className="absolute top-[25px] left-[30px] w-[480px] h-[438px]"
                alt="Vector"
                src="https://c.animaapp.com/hFv7aPLp/img/vector-3.svg"
              />

              <div className="absolute top-[11px] left-[780px] w-[615px] h-[185px] flex flex-col gap-[30.4px]">
                <div className="w-[610.56px] h-[99.36px] [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.8px]">
                  4. Automated Messenger
                </div>

                <p className="w-[610.56px] h-[55.41px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
                  Provide exceptional customer service around the clock without
                  risking your brand&#39;s reputation.
                </p>
              </div>
               <div className="absolute w-[617px] h-[291px] top-[228px] left-[803px] flex flex-col">
                {messengerFeatures.map((feature, index) => (
                  <div key={index} className={feature.wrapperClass}>
                    <img
                      className={`${feature.marginTop} w-[27.08px] h-[27.52px]`}
                      alt="Icon"
                      src="https://c.animaapp.com/hFv7aPLp/img/icon-11@2x.png"
                    />
                    <p
                      className={`${feature.textClass} [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]`}
                    >
                      <span className="font-semibold">{feature.title}</span>
                      {feature.usePoppins ? (
                        <span className="[font-family:'Poppins',Helvetica]">
                          {feature.description}
                        </span>
                      ) : (
                        <span className="[font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]">
                          {feature.description}
                        </span>
                      )}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};