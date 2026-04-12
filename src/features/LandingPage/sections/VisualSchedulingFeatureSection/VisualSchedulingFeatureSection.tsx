export const VisualSchedulingFeatureSection = (): JSX.Element => {
  const features = [
    {
      icon: "https://c.animaapp.com/hFv7aPLp/img/icon-2@2x.png",
      title: "Complete Overview: ",
      description:
        "Access a visual calendar for planning and scheduling all your posts.",
      wrapperClass: "ml-0 w-[533.57px] mt-0 flex gap-[13.9px]",
      textClass:
        "mt-0 w-[490.52px] h-[83.21px] [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]",
    },
    {
      icon: "https://c.animaapp.com/hFv7aPLp/img/icon-2@2x.png",
      title: "Editorial Control: ",
      description:
        "Manage recurring posts and editorial calendars effortlessly.",
      wrapperClass: "ml-[2.0px] w-[619.66px] mt-[23.0px] flex gap-[13.9px]",
      textClass:
        "mt-0 w-[576.61px] h-[55.47px] [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]",
    },
    {
      icon: "https://c.animaapp.com/hFv7aPLp/img/icon-2@2x.png",
      title: "Time-Saving Automation: ",
      description:
        "Automate scheduling and posting to reduce the labor cost of social media management.",
      wrapperClass: "ml-0 w-[585.62px] mt-[26.8px] flex gap-[13.9px]",
      textClass:
        "mt-0 w-[542.58px] h-[83.21px] [font-family:'Inter',Helvetica] font-normal text-[#07265c] text-[23px] tracking-[0] leading-[28.8px]",
    },
  ];

  const calendarHours = ["09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"];
  
  const calendarDays = [
    { label: "Monday 12", left: "0", width: "6.37%" },
    { label: "Tuesday 13", left: "15.54%", width: "6.66%" },
    { label: "Wednesday 14", left: "30.34%", width: "8.40%" },
    { label: "Thursday 15", left: "46.51%", width: "7.24%" },
    { label: "Friday 16", left: "63.09%", width: "5.21%" },
    { label: "Saturday 17", left: "78.00%", width: "6.95%" },
    { label: "Sunday 18", left: "94.06%", width: "6.08%" },
  ];

  return (
    <>
      {/* 1. The Text Content */}
      <div className="absolute h-[565px] top-[1899px] left-[146px] flex justify-end items-end min-w-[1093px]">
        <div className="mb-0 flex justify-end items-end min-w-[1093px]">
          <div className="w-[1093px] h-[565px] mb-0 flex">
            <div className="mt-0 w-[1092.87px] h-[565.06px] ml-0 relative">
              <img
                className="absolute top-[5px] left-[615px] w-[453px] h-[411px]"
                alt="Vector"
                src="https://c.animaapp.com/hFv7aPLp/img/vector.svg"
              />

              <div className="absolute top-px left-px w-[615px] h-[185px] flex flex-col gap-[30.4px]">
                <p className="ml-0 w-[611.21px] h-[99.47px] mt-0 [font-family:'Poppins',Helvetica] font-bold text-[#07265c] text-[46.1px] tracking-[-0.96px] leading-[51.9px]">
                  1. Visual Scheduling & Calendar
                </p>

                <p className="ml-0 w-[611.21px] h-[55.47px] opacity-80 [font-family:'Poppins',Helvetica] font-normal text-[#080a47] text-[25px] tracking-[0] leading-[28.8px]">
                  Take the stress out of planning by visually organizing your
                  social media pipeline.
                </p>
              </div>

              <div className="absolute w-[620px] h-[272px] top-[293px] left-2.5 flex flex-col">
                {features.map((feature, index) => (
                  <div key={index} className={feature.wrapperClass}>
                    <img
                      className="mt-0 w-[27.11px] h-[27.55px]"
                      alt="Icon"
                      src={feature.icon}
                    />
                    <p className={feature.textClass}>
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

      {/* 2. The Calendar UI Graphic */}
      <div className="absolute top-[1795px] left-[862px] w-[587px] h-[728px] flex">
        <div className="w-[587.2px] flex">
          <div className="w-[587.2px] h-[727.98px] relative">
            
            {/* ---> THE VECTOR BACKGROUND: REDUCED SIZE AND ADJUSTED POSITION <--- */}
            <img
              className="absolute top-[115px] left-[130px] w-[550px] h-[550px] object-contain pointer-events-none"
              alt="Vector Background Right"
              src="https://c.animaapp.com/hFv7aPLp/img/vector.svg"
            />
            {/* ----------------------------------- */}

            <div className="absolute w-[calc(100%_-_184px)] top-0 left-[184px] h-[365px] rounded-[46.8px]">
              <div className="absolute w-[calc(100%_-_4px)] top-[65px] left-0.5 h-[365px] bg-white rounded-[22.5px] shadow-[0px_21.6px_43.2px_#26334d0d]" />

              <div className="absolute w-[calc(100%_-_4px)] top-[102px] left-0.5 h-[303px] flex flex-col">
                {Array.from({ length: 13 }).map((_, i) => (
                  <div
                    key={i}
                    className={`ml-0 mr-0 flex-1 max-h-px ${i === 0 ? "mt-0" : "mt-[24.2px]"} bg-grey-blue-97`}
                    style={
                      i === 1 ? { marginTop: "24.6px" } : i === 2 ? { marginTop: "24.2px" } : {}
                    }
                  />
                ))}
              </div>

              <div className="absolute top-[110px] left-2 w-[11px] h-[311px]">
                <div className="absolute w-[46.30%] top-[calc(50.00%_-_129px)] left-[26.68%] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-80 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                  09
                </div>

                <img
                  className="absolute w-[100.00%] h-[3.47%] top-0 left-0"
                  alt="Icon"
                  src="https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-8.svg"
                />

                {calendarHours.slice(1).map((hour, index) => {
                  const positions = [
                    "top-[calc(50.00%_-_103px)]", "top-[calc(50.00%_-_78px)]", "top-[calc(50.00%_-_53px)]",
                    "top-[calc(50.00%_-_28px)]", "top-[calc(50.00%_-_3px)]", "top-[calc(50.00%_+_23px)]",
                    "top-[calc(50.00%_+_48px)]", "top-[calc(50.00%_+_73px)]", "top-[calc(50.00%_+_98px)]",
                    "top-[calc(50.00%_+_123px)]", "top-[calc(50.00%_+_149px)]",
                  ];
                  const leftPositions = [
                    "left-[calc(50.00%_-_3px)]", "left-[calc(50.00%_-_3px)]", "left-[calc(50.00%_-_3px)]",
                    "left-[calc(50.00%_-_2px)]", "left-[calc(50.00%_-_2px)]", "left-[calc(50.00%_-_2px)]",
                    "left-[calc(50.00%_-_2px)]", "left-[calc(50.00%_-_2px)]", "left-[calc(50.00%_-_2px)]",
                    "left-[calc(50.00%_-_2px)]", "left-[calc(50.00%_-_2px)]",
                  ];
                  return (
                    <div
                      key={index}
                      className={`absolute ${positions[index]} ${leftPositions[index]} [font-family:'Roboto',Helvetica] font-bold text-grey-blue-80 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap`}
                    >
                      {hour}
                    </div>
                  );
                })}
              </div>

              <div className="absolute w-[85.63%] h-0 top-[30.60%] left-[9.82%]">
                {calendarDays.map((day, index) => (
                  <div
                    key={index}
                    className="absolute [font-family:'Roboto',Helvetica] font-bold text-grey-blue-60 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap"
                    style={{
                      width: day.width,
                      top: "calc(50.00% - 4px)",
                      left: day.left,
                    }}
                  >
                    {day.label}
                  </div>
                ))}
              </div>

              <div className="absolute w-[calc(100%_-_30px)] h-[61.08%] top-[35.52%] left-[27px]">
                <div className="absolute w-0 top-[-27px] left-0 h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[13.78%] h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[28.23%] h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[42.68%] h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[57.13%] h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[71.58%] h-[328px] bg-grey-blue-97" />
                <div className="absolute w-0 top-[-27px] left-[86.03%] h-[328px] bg-grey-blue-97" />

                <div className="absolute w-[13.49%] top-[50px] left-[14.26%] h-[22px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-orange-5 rounded-[1.8px] border-[0.72px] border-solid border-[#ff6633]" />
                  <div className="absolute top-[13px] left-[5px] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px] whitespace-nowrap">
                    Post 2
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-orange rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      11:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.49%] top-[25px] left-[43.26%] h-[23px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-orange-5 rounded-[1.8px] border-[0.72px] border-solid border-[#ff6633]" />
                  <div className="absolute top-[13px] left-1 w-[38px] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px]">
                    Post 4
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-orange rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      10:00
                    </div>
                  </div>
                </div>
                
                 <div className="absolute w-[13.49%] top-px left-0 h-[47px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-green-5 rounded-[1.8px] border-[0.72px] border-solid border-[#28cc38]" />
                  <div className="absolute top-[13px] left-[3px] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px] whitespace-nowrap">
                    Post 1
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-green rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      09:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.49%] top-[101px] left-[43.26%] h-[22px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-[23px] bg-teal-blue-5 rounded-[1.8px] border-[0.72px] border-solid border-[#33beff]" />
                  <div className="w-[21.83%] top-[calc(50.00%_+_2px)] left-[10.71%] absolute [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px] whitespace-nowrap">
                    Post 5
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-teal-blue rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      13:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.49%] top-[101px] left-[14.35%] h-[22px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-purple-5 rounded-[1.8px] border-[0.72px] border-solid border-[#8833ff]" />
                  <div className="top-[calc(50.00%_+_2px)] left-1 w-[38px] absolute [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px]">
                    Post 3
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-purple rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      13:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.49%] top-[51px] left-[86.61%] h-[22px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-yellow-5 rounded-[1.8px] border-[0.72px] border-solid border-[#cc7428]" />
                  <div className="absolute w-[75.00%] top-[calc(50.00%_+_2px)] left-[7.14%] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px]">
                    Post 7
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-bronze rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      11:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.49%] h-[10.08%] top-[67.84%] left-[86.37%]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-6 bg-tiffany-5 rounded-[1.8px] border-[0.72px] border-solid border-[#2ee6ca]" />
                  <div className="w-[75.00%] top-[50.00%] left-[7.14%] absolute [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px]">
                    Post 8
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-tiffany rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      15:00
                    </div>
                  </div>
                </div>

                <div className="absolute w-[13.68%] top-[201px] left-0 h-[73px]">
                  <div className="absolute w-[calc(100%_+_1px)] -top-px -left-px h-[74px] bg-teal-blue-5 rounded-[1.8px] border-[0.72px] border-solid border-[#33beff]" />
                  <div className="top-[calc(50.00%_-_23px)] left-1.5 absolute [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px] whitespace-nowrap">
                    The Amazing Hubble
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-teal-blue rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      17:00
                    </div>
                  </div>
                  <img
                    className="absolute top-1 left-[19px] w-[7px] h-[7px]"
                    alt="Avatar image"
                    src="https://c.animaapp.com/mnq63gf4Bct2xt/img/avatar-image-1.svg"
                  />
                  <img
                    className="absolute top-1 left-7 w-[7px] h-[7px]"
                    alt="Avatar image"
                    src="https://c.animaapp.com/mnq63gf4Bct2xt/img/avatar-image.svg"
                  />
                </div>

                <div className="absolute w-[13.49%] top-[25px] left-[57.71%] h-[72px]">
                  <div className="absolute w-[calc(100%_+_2px)] -top-px -left-px h-[25px] bg-yellow-5 rounded-[1.8px] border-[0.72px] border-solid border-[#ffcb33]" />
                  <div className="absolute top-3.5 left-[5px] w-[38px] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-50 text-[3.6px] tracking-[0] leading-[7.2px]">
                    Post 6
                  </div>
                  <div className="inline-flex h-[7px] items-center gap-[3.6px] px-[2.52px] py-0 absolute top-1 left-1 bg-yellow rounded-[1.8px]">
                    <div className="relative w-fit mt-[-0.76px] mb-[-0.04px] [font-family:'Roboto',Helvetica] font-black text-white text-[2.9px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      10:00
                    </div>
                  </div>
                </div>
              </div>

              <img
                className="absolute w-full top-[222px] left-0 h-1"
                alt="Now"
                src="https://c.animaapp.com/mnq63gf4Bct2xt/img/now.svg"
              />

              <div className="absolute w-[calc(100%_-_24px)] top-[75px] left-3 h-[15px]">
                <button className="all-[unset] box-border inline-flex h-4 items-center justify-center gap-[3.6px] px-[7.2px] py-[3.6px] absolute -top-px -left-px bg-white rounded-[7.2px] border-[0.72px] border-solid border-[#f5f6f7] shadow-[0px_0.72px_1.8px_#26334d08]">
                  <div className="relative w-fit mt-[-0.76px] [font-family:'Roboto',Helvetica] font-black text-grey-blue-60 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                    Today
                  </div>
                </button>

                <div className="absolute top-px left-[145px] w-[92px] h-3.5">
                  <div className="absolute -top-px left-[calc(50.00%_-_47px)] w-4 h-4 flex items-center justify-center bg-white rounded-[36px] border-[0.72px] border-solid border-[#f5f6f7] shadow-[0px_0.72px_1.8px_#26334d08]">
                    <img
                      className="mt-[-2.4px] h-[10.08px] ml-[-2.4px] w-[10.08px]"
                      alt="Icon"
                      src="https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-6.svg"
                    />
                  </div>

                  <div className="absolute -top-px left-[calc(50.00%_+_28px)] w-4 h-4 flex items-center justify-center bg-white rounded-[36px] border-[0.72px] border-solid border-[#f5f6f7] shadow-[0px_0.72px_1.8px_#26334d08]">
                    <img
                      className="mt-[-2.4px] h-[10.08px] ml-[-2.4px] w-[10.08px]"
                      alt="Icon"
                      src="https://c.animaapp.com/mnq63gf4Bct2xt/img/icon-7.svg"
                    />
                  </div>

                  <p className="absolute top-1 left-[calc(50.00%_-_19px)] [font-family:'Roboto',Helvetica] font-bold text-grey-blue-60 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                    May 21 – 26, 2045
                  </p>
                </div>

                <div className="inline-flex items-center absolute top-px right-px shadow-[0px_0.72px_1.8px_#26334d08]">
                  <div className="inline-flex h-[16.4px] items-center justify-center gap-[3.6px] pl-[7.2px] pr-[5.4px] py-[5.4px] relative flex-[0_0_auto] mt-[-1.00px] mb-[-1.00px] ml-[-1.00px] bg-white rounded-[10.8px_0px_0px_10.8px] border-[0.72px] border-solid border-[#f5f6f7]">
                    <div className="relative w-fit mt-[-2.56px] [font-family:'Roboto',Helvetica] font-black text-grey-blue-80 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      Year
                    </div>
                  </div>

                  <div className="inline-flex h-[16.4px] items-center justify-center gap-[3.6px] p-[5.4px] relative flex-[0_0_auto] mt-[-1.00px] mb-[-1.00px] bg-white border-[0.72px] border-solid border-[#f5f6f7]">
                    <div className="relative w-fit mt-[-2.56px] [font-family:'Roboto',Helvetica] font-black text-grey-blue-60 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      Week
                    </div>
                  </div>

                  <div className="inline-flex h-[16.4px] items-center justify-center gap-[3.6px] p-[5.4px] relative flex-[0_0_auto] mt-[-1.00px] mb-[-1.00px] bg-white border-[0.72px] border-solid border-[#f5f6f7]">
                    <div className="relative w-fit mt-[-2.56px] [font-family:'Roboto',Helvetica] font-black text-grey-blue-80 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      Month
                    </div>
                  </div>

                  <div className="inline-flex h-[16.4px] items-center justify-center gap-[3.6px] pl-[5.4px] pr-[7.2px] py-[5.4px] relative flex-[0_0_auto] mt-[-1.00px] mb-[-1.00px] mr-[-1.00px] bg-white rounded-[0px_10.8px_10.8px_0px] border-[0.72px] border-solid border-[#f5f6f7]">
                    <div className="relative w-fit mt-[-2.56px] [font-family:'Roboto',Helvetica] font-black text-grey-blue-80 text-[4.3px] text-center tracking-[0] leading-[7.2px] whitespace-nowrap">
                      Day
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <img
              className="absolute top-[276px] left-0 w-[463px] h-[452px] object-cover"
              alt="Date picker"
              src="https://c.animaapp.com/mnq63gf4Bct2xt/img/date-picker-1.png"
            />
          </div>
        </div>
      </div>
    </>
  );
};