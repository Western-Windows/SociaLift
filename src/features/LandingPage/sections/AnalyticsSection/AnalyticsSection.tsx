// src/screens/LandingPage/sections/AnalyticsSection/AnalyticsSection.tsx

const analyticsBullets = [
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-3.png",
    title: "Data-Driven Decisions: ",
    description:
      "Rely on analytics-driven insights to guide your ongoing social media strategy and decisions",
    wrapperClass: "ml-0 w-[533px] flex gap-[13.9px]",
    textClass: "w-[490px] h-[83.12px]",
  },
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-4.png",
    title: "Maximize Impact: ",
    description:
      "Optimize your audience engagement strategies through analytics to significantly improve your reach and brand perception.",
    wrapperClass: "ml-[0.4px] w-[619px] mt-[36.3px] flex gap-[13.9px]",
    textClass: "w-[576px] h-[55.41px]",
  },
  {
    icon: "https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-5.png",
    title: "Streamlined Analysis: ",
    description:
      "Eliminate the time-consuming and inefficient task of manual performance analysis so you can focus on core operations.",
    wrapperClass: "w-[585px] mt-[89.3px] flex gap-[13.9px]",
    textClass: "w-[542px] h-[83.12px]",
  },
];

export const AnalyticsSection = (): JSX.Element => {
  return (
    <>
      {/* 1. The Text Content */}
      <div className="absolute top-[103px] left-[93px] w-[627px] h-[1249px] flex z-0">
        <div className="w-[627.45px] flex">
          <div className="w-[627.45px] flex">
            <div className="w-[627.45px] h-[1249.28px] ml-0 flex flex-col">
              <div className="ml-0 w-[614.56px] h-[185.16px] flex flex-col gap-[30.4px]">
                <p className="w-[610.56px] h-[99.36px] [font-family:'Poppins',Helvetica] font-normal text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.8px]">
                  <span className="font-bold tracking-[-0.44px]">
                    5. Analytics Dashboard
                  </span>
                </p>

                <p className="w-[610.56px] h-[55.41px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
                  Understand your audience and track your growth with clear,
                  actionable data.
                </p>
              </div>

              <div className="ml-[10.1px] w-[617.37px] h-[347.25px] mt-[32.0px] flex flex-col">
                {analyticsBullets.map((point, index) => (
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

              {/* Added -z-10 so this background vector stays behind everything else */}
              <img
                className="ml-[2.4px] w-[557.84px] h-[495.63px] mt-[189.2px] -z-10"
                alt="Vector"
                src="https://c.animaapp.com/mnq63gf4Bct2xt/img/vector-2.svg"
              />
            </div>
          </div>
        </div>
      </div>

      {/* 2. The Dashboard Charts UI */}
      {/* Added z-10 to the wrapper so the entire dashboard renders strictly ABOVE any vectors */}
      <div className="absolute top-[115px] left-[800px] w-[698px] h-[475px] z-10">
        
        {/* Added -z-10 so this specific shape sits behind the dashboard background */}
        <img
          className="absolute w-[36.49%] h-[53.66%] top-[46.34%] left-0 -z-10"
          alt="Shape"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/shape-1.svg"
        />

        <div className="absolute w-[84.81%] h-[84.47%] top-[9.44%] left-[9.46%] bg-[#f5f9ff] rounded-[9.43px]" />

        <div className="w-[13.01%] top-[calc(50.00%_-_138px)] left-[25.93%] [font-family:'HK_Grotesk-Bold',Helvetica] font-bold tracking-[0.12px] leading-[18.9px] absolute text-[#183b56] text-[14.2px] whitespace-nowrap">
          Post Overview
        </div>

        <div className="absolute w-[85.09%] h-[7.38%] top-[9.23%] left-[9.32%] bg-[#ffffff] rounded-[9.43px_9.43px_0px_0px]" />

        <div className="absolute w-[5.02%] h-[84.89%] top-[9.23%] left-[9.32%] bg-[#ffffff] rounded-[9.43px_0px_0px_9.43px] shadow-[0.59px_0px_0px_#f3f3f3]" />

        <img
          className="absolute w-[2.03%] h-[2.98%] top-[11.43%] left-[10.81%]"
          alt="Circle"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/circle.png"
        />
        
        <img
          className="absolute top-[137px] left-[121px] w-[118px] h-[57px]"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item.png"
        />

        <img
          className="absolute top-[137px] left-[254px] w-[118px] h-[57px]"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item-1.png"
        />

        <img
          className="absolute top-[137px] left-[387px] w-[118px] h-[57px]"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item-2.png"
        />

        <div className="absolute top-[137px] left-[520px] w-[118px] h-[57px] bg-[#f5f9ff] rounded-[4.72px] border-[0.59px] border-dashed border-[#b3bac5]" />

        <div className="absolute w-[12.42%] h-[4.72%] top-[21.12%] left-[78.90%] overflow-hidden">
          <div className="absolute w-[102.31%] h-[108.93%] top-[-4.46%] left-0 bg-[#ffffff] rounded-[2.36px]" />

          <div className="absolute top-[calc(50.00%_-_4px)] left-[calc(50.00%_+_28px)] [font-family:'Font_Awesome_5_Free-Solid',Helvetica] font-normal text-[#183b56] text-[7.1px] text-center tracking-[0] leading-[normal] whitespace-nowrap">
            chevron-down
          </div>
        </div>

        <div className="absolute top-[209px] left-[121px] w-[383px] h-[153px]">
          <div className="absolute w-[100.52%] h-[101.30%] top-0 left-0 bg-[#ffffff] rounded-[4.72px] shadow-[0px_11.79px_27.71px_#0000000d]" />

          <div className="absolute w-[10.46%] h-[18.46%] top-[33.85%] left-[84.15%] overflow-hidden">
            <div className="absolute w-[100.00%] top-[calc(50.00%_-_5px)] left-0 [font-family:'HK_Grotesk-Bold',Helvetica] font-bold text-[#183b56] text-[14.2px] tracking-[0.12px] leading-[18.9px] whitespace-nowrap">
              25,3K
            </div>

            <div className="absolute w-[41.18%] h-[12.50%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
          </div>

          <div className="absolute w-[8.92%] h-[18.46%] top-[63.08%] left-[84.15%]">
            <div className="absolute w-[98.28%] top-[calc(50.00%_-_5px)] left-0 [font-family:'HK_Grotesk-Bold',Helvetica] font-bold text-[#183b56] text-[14.2px] tracking-[0.12px] leading-[18.9px] whitespace-nowrap">
              +120
            </div>

            <div className="absolute w-[48.28%] h-[12.50%] top-0 left-0 bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="absolute w-[7.38%] h-[2.31%] top-[9.23%] left-[87.69%] bg-[#b3bac5] rounded-[1.18px]" />

          <img
            className="absolute top-[33px] left-6 w-[271px] h-[100px]"
            alt="Line"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/line.png"
          />

          <div className="absolute top-[87px] left-[33px] w-[15px] h-[45px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[86.84%] top-[13.16%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-[58px] left-[71px] h-[74px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-full top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[92.06%] top-[7.94%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-[70px] left-[110px] h-[63px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[90.57%] top-[9.43%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-[75px] left-[148px] h-[57px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[89.58%] top-[10.42%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-16 left-[186px] h-[68px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[91.38%] top-[8.62%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-[46px] left-[225px] h-[86px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[93.15%] top-[6.85%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>

          <div className="top-10 left-[263px] h-[92px] absolute w-[15px]">
            <div className="absolute w-[30.77%] h-[100.00%] top-0 left-0 bg-[#f9ad12] rounded-[1.18px]" />
            <div className="absolute w-[30.77%] h-[93.59%] top-[6.41%] left-[69.23%] bg-[#36b37e] rounded-[1.18px]" />
          </div>
        </div>

        <img
          className="absolute top-[376px] left-[121px] w-56 h-[88px]"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item-3.png"
        />

        <img
          className="absolute top-[376px] left-[360px] w-36 h-[88px]"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item-4.png"
        />

        <div className="absolute top-[215px] left-[513px] w-[138px] h-[138px] flex">
          <div className="mt-0 w-[137.97px] h-[137.97px] ml-0 relative">
            <div className="absolute top-9 left-9 w-[66px] h-[66px]">
              <div className="absolute top-[23px] left-2.5 w-[50px] h-5 flex flex-col gap-[2.3px]">
                <div className="ml-[9.9px] w-[25.76px] h-[12.65px] mt-0 [font-family:'Inter',Helvetica] font-normal text-icon-05 text-[12.5px] tracking-[0] leading-[12.5px] whitespace-nowrap">
                  75%
                </div>

                <div className="ml-0 w-[45.76px] h-[4.83px] opacity-50 [font-family:'Inter',Helvetica] font-normal text-[#121212] text-[4.7px] tracking-[0.12px] leading-[4.7px] whitespace-nowrap">
                  Projects Completed
                </div>
              </div>

              <img
                className="absolute -top-0.5 -left-0.5 w-[70px] h-[70px]"
                alt="Group"
                src="https://c.animaapp.com/mnq63gf4Bct2xt/img/group-195.png"
              />
            </div>

            <div className="absolute top-0 left-px w-[138px] h-[138px] rounded-[68.99px] border-[0.63px] border-dashed border-zinc-700 opacity-10" />

            <div className="absolute top-[17px] left-[17px] w-[103px] h-[103px] rounded-[51.74px] border-[0.63px] border-dashed border-zinc-700 opacity-10" />
          </div>
        </div>

        <img
          className="absolute top-[360px] left-[492px] w-[173px] h-36"
          alt="Item"
          src="https://c.animaapp.com/mnq63gf4Bct2xt/img/item-5.png"
        />

        <div className="absolute w-[3.89%] h-0 top-[23.11%] left-[80.51%] bg-[#b3bac5] rounded-[1.18px]" />

        <div className="absolute w-[2.11%] h-0 top-[23.11%] left-[84.98%] bg-[#5a7184] rounded-[1.18px] opacity-10" />

        <div className="absolute top-[94px] left-[525px] w-[175px] h-[81px]">
          <div className="absolute w-[97.71%] h-[102.47%] top-0 left-0 bg-[#ffffff] rounded-[6.75px] shadow-[0px_10.02px_23px_#0000000d]" />

          <div className="absolute w-[20.26%] top-[calc(50.00%_-_21px)] left-[41.87%] [font-family:'HK_Grotesk-Bold',Helvetica] font-bold text-[#183b56] text-[14.2px] tracking-[0.12px] leading-[18.9px] whitespace-nowrap">
            398K
          </div>

          <div className="absolute w-[30.35%] top-[calc(50.00%_+_1px)] left-[41.87%] [font-family:'Open_Sans',Helvetica] font-normal text-[#5a7184] text-[10.6px] tracking-[0] leading-[18.9px] whitespace-nowrap">
            Total Likes
          </div>

          <div className="absolute w-[23.18%] h-[50.00%] top-[24.77%] left-[11.48%] flex items-center justify-center">
            <img
              className="absolute inset-0 w-full h-full object-contain"
              alt="Thumbs up background"
              src="/Shape.svg"
            />
            <img
              className="relative w-[11.8px] h-[11.8px] object-contain"
              alt="Thumbs up"
              src="/thumbs-up.svg"
            />
          </div>
        </div>

        <div className="absolute w-[22.59%] h-[41.86%] top-0 left-[2.81%] bg-[#ffffff] rounded-[5.66px] shadow-[0px_11.79px_27.71px_#0000000d]" />

        <div className="absolute w-[6.25%] h-[3.11%] top-[35.50%] left-[6.81%] overflow-hidden">
          <div className="absolute w-[77.92%] top-[calc(50.00%_-_7px)] left-[22.71%] [font-family:'Open_Sans',Helvetica] font-normal text-[#5a7184] text-[9.9px] tracking-[0] leading-[14.2px] whitespace-nowrap">
            Images
          </div>

          <img
            className="absolute w-[9.73%] h-[28.80%] top-[33.60%] left-0"
            alt="Oval"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/shape.svg"
          />
        </div>

        <div className="absolute w-[5.91%] h-[3.11%] top-[35.50%] left-[15.53%]">
          <img
            className="absolute w-[10.29%] h-[28.80%] top-[33.60%] left-0"
            alt="Oval"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/shape.svg"
          />

          <div className="absolute w-[75.11%] top-[calc(50.00%_-_7px)] left-[24.00%] [font-family:'Open_Sans',Helvetica] font-normal text-[#5a7184] text-[9.9px] tracking-[0] leading-[14.2px] whitespace-nowrap">
            Videos
          </div>
        </div>

        <div className="absolute top-[65px] left-[58px] w-[81px] h-[81px]">
          <img
            className="absolute top-[-3px] left-[-3px] w-[87px] h-[88px]"
            alt="Line"
            src="https://c.animaapp.com/mnq63gf4Bct2xt/img/line-1.png"
          />

          <div className="absolute top-6 left-6 w-9 h-[34px]">
            <img
              className="absolute top-[calc(50.00%_-_9px)] left-[calc(50.00%_-_9px)] w-[18px] h-[18px] object-contain"
              alt="Oval"
              src="https://c.animaapp.com/mnq63gf4Bct2xt/img/oval.svg"
            />

            <img
              className="absolute top-[calc(50.00%_-_7px)] left-[calc(50.00%_-_7px)] w-[12.7px] h-[12.7px] object-contain"
              alt="Upload"
              src="/upload.svg"
            />
          </div>
        </div>

        <div className="w-[8.87%] top-[calc(50.00%_-_214px)] left-[9.65%] [font-family:'HK_Grotesk-SemiBold',Helvetica] font-semibold tracking-[0.14px] leading-[17.0px] absolute text-[#183b56] text-[14.2px] whitespace-nowrap">
          Post Type
        </div>
      </div>
    </>
  );
};