const footerNavLinks = [
  { label: "About", width: "w-[66px]" },
  { label: "Features", width: "w-[108px]" },
  { label: "Works", width: "w-[79px]" },
  { label: "Support", width: "w-[91px]" },
];

export const FooterSection = (): JSX.Element => {
  return (
    <div className="absolute top-[6564px] left-0 w-[1537px] h-[167px] flex bg-[url(https://c.animaapp.com/mn52tbe7U6Iu7j/img/footer-section.png)] bg-[100%_100%]">
      <footer className="mt-[68px] w-[1351.91px] ml-[97.0px] flex items-end bg-transparent">
        <div className="mb-0 w-[1351.91px] ml-0 flex">
          <div className="mt-0 w-[1351.91px] h-[63px] ml-0 flex flex-col gap-[33px]">
            <img
              className="ml-[55.1px] w-[1296.84px] h-px -mt-px"
              alt="Line"
              src="https://c.animaapp.com/mn52tbe7U6Iu7j/img/line-205.svg"
            />

            <div className="w-[1338px] h-[30px] items-start gap-[68px] inline-flex relative">
              <div className="relative w-[382.25px] mt-[-2.00px] ml-[-1.00px] [font-family:'Inter',Helvetica] font-extrabold text-[#eeeaf3] text-xl tracking-[0] leading-[26px]">
                © Copyright 2026, All Rights Reserved
              </div>

              <div className="inline-flex items-center gap-3 relative flex-[0_0_auto]">
                <div className="items-center gap-3 flex-[0_0_auto] inline-flex relative">
                  {footerNavLinks.map((link, index) => (
                    <button
                      type="button"
                      key={index}
                      className={`relative ${link.width} mt-[-2.00px] ${index === 0 ? "ml-[-1.00px]" : ""} cursor-pointer bg-transparent p-0 text-left [font-family:'Inter',Helvetica] font-extrabold text-[#eeeaf3] text-xl tracking-[0] leading-[30px] transition-colors duration-200 hover:text-white hover:underline hover:decoration-2 hover:underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70`}
                    >
                      {link.label}
                    </button>
                  ))}
                </div>
              </div>

              <a
                href="https://github.com/Western-Windows/SociaLift"
                target="_blank"
                rel="noopener noreferrer"
                className="relative w-[25.52px] h-[24.73px]"
              >
                <img
                  className="w-full h-full"
                  alt="GitHub"
                  src="https://c.animaapp.com/mn52tbe7U6Iu7j/img/4.png"
                />
              </a>

              <div className="relative w-[346.23px] mt-[-2.00px] [font-family:'Inter',Helvetica] font-extrabold text-[#eeeaf3] text-xl text-right tracking-[0] leading-[26px] whitespace-nowrap">
                <button
                  type="button"
                  className="cursor-pointer bg-transparent p-0 [font-family:'Inter',Helvetica] font-extrabold text-[#eeeaf3] text-xl tracking-[0] leading-[26px] transition-colors duration-200 hover:text-white hover:underline hover:decoration-2 hover:underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
                >
                  Privacy Policy
                </button>
                <span className="mx-2">•</span>
                <button
                  type="button"
                  className="cursor-pointer bg-transparent p-0 [font-family:'Inter',Helvetica] font-extrabold text-[#eeeaf3] text-xl tracking-[0] leading-[26px] transition-colors duration-200 hover:text-white hover:underline hover:decoration-2 hover:underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
                >
                  Terms & Conditions
                </button>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
