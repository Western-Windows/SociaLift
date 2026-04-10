const navItems = [
  { label: "Home", active: true },
  { label: "Dashboard & Calendar", active: false },
  { label: "Post Generation", active: false },
];

export const HomeNavSection = (): JSX.Element => {
  return (
    <div className="absolute top-[18px] left-0 w-[1536px] h-[90px] z-50">
      <div className="absolute top-[9px] left-0 w-[1536px] h-[81px]">
        {/* Nav Links */}
        <div className="absolute top-1 left-4 w-[1536px] h-[72px] flex items-center">
          <nav className="inline-flex mt-[-0.8px] h-[34px] ml-[490px] w-[620px] relative items-end gap-8">
            {navItems.map((item) => (
              <a
                key={item.label}
                href="#"
                className={`relative w-fit mt-[-1.00px] cursor-pointer transition-opacity hover:opacity-80 ${
                  item.active
                    ? "[font-family:'Poppins',Helvetica] font-semibold text-[#07265c]"
                    : "[font-family:'Poppins',Helvetica] font-normal text-white"
                } text-[20px] tracking-[0] leading-[normal] no-underline`}
              >
                {item.label}
              </a>
            ))}
          </nav>
        </div>

        {/* Logo */}
        <img
          className="absolute top-0 left-[150px] w-[76px] h-[81px] aspect-[0.93]"
          alt="Socialift logo"
          src="https://c.animaapp.com/hFv7aPLp/img/socialift-logo-5@2x.png"
        />
      </div>

      {/* User Avatar */}
      <div className="absolute top-[0px] left-[1388px] w-[90px] h-[90px] bg-[#fffdfd] rounded-[45px] shadow-[0px_4px_4px_#00000040] flex items-center justify-center cursor-pointer hover:scale-105 transition-transform">
        <img
          className="w-[60px] h-[60px] object-cover"
          alt="User Profile"
          src="https://c.animaapp.com/hFv7aPLp/img/user-tie-hair--1--1@2x.png"
        />
      </div>
    </div>
  );
};