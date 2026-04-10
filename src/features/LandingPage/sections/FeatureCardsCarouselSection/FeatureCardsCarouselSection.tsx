// src/screens/LandingPage/sections/FeatureCardsCarouselSection/FeatureCardsCarouselSection.tsx
import { InfiniteScroller } from "../../../../components/InfiniteScroller";
import { useNavigate } from "react-router-dom";

const featureCards = [
  {
    number: "01",
    title: "Visual Scheduling & Calendar",
    description:
      "Plan and organize your social media activities with an easy-to-use calendar.",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/calendar-clock-1.png",
    iconAlt: "Calendar clock",
    discoverLeftOffset: "left-[229px]",
  },
  {
    number: "02",
    title: "Dynamic Persona Builder",
    description:
      "Customize strategies based on your specific audience, working hours, and market niche.",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/user-tie-hair-1.png",
    iconAlt: "User tie hair",
    discoverLeftOffset: "left-[229px]",
  },
  {
    number: "03",
    title: " AI Content Generation",
    description:
      "Enhance posts automatically using a large language model optimized for your platform.",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/write-1.png",
    iconAlt: "Write",
    discoverLeftOffset: "left-[222px]",
  },
  {
    number: "04",
    title: "Automated Messenger",
    description:
      "Deliver timely, consistent replies safely through our integrated Facebook chatbot.",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/conversation-1.png",
    iconAlt: "Conversation",
    discoverLeftOffset: "left-[230px]",
  },
  {
    number: "05",
    title: "Analytics Dashboard",
    description:
      "Track your growth and make smarter decisions with analytics-driven insights and performance analysis",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/dashboard--1--1.png",
    iconAlt: "Dashboard",
    discoverLeftOffset: "left-[229px]",
  },
  {
    number: "06",
    title: "Intelligent Commenting",
    description:
      " Engage your audience effortlessly by automatically replying to page comments.",
    icon: "https://c.animaapp.com/mn52tbe7U6Iu7j/img/comment-1.png",
    iconAlt: "Comment",
    discoverLeftOffset: "left-[229px]",
    extraClass: "mr-[-6.00px]",
  },
];

export const FeatureCardsCarouselSection = (): JSX.Element => {
  const navigate = useNavigate();

  return (
    <div className="absolute top-[1285px] left-0 w-[1536px] overflow-hidden z-10 py-4">
      <InfiniteScroller direction="forwards" speed="normal" pauseOnHover={true}>
        {featureCards.map((card, index) => (
          // Replaced shadcn Card with a standard div to prevent double borders
          <div
            key={index}
            className={`relative w-[386px] h-[382px] bg-white rounded-[20px] border border-solid border-[#2e3975] shadow-[0px_4px_10px_#00000020] p-0 overflow-hidden flex-shrink-0 ${card.extraClass || ""}`}
          >
            <div className="absolute top-[21px] left-[22px] [font-family:'Manrope',Helvetica] font-extrabold text-[#2e3975] text-[22px] tracking-[0] leading-[normal]">
              {card.number}
            </div>
            
            <img
              className="absolute top-14 left-[165px] w-[60px] h-[60px] object-cover"
              alt={card.iconAlt}
              src={card.icon}
            />
            
            <div className="absolute top-[135px] left-[42px] w-[276px] [font-family:'Manrope',Helvetica] font-extrabold text-[#2e3975] text-3xl text-center tracking-[-0.90px] leading-[34px]">
              {card.title}
            </div>
            
            <div className="absolute top-[220px] left-[45px] w-[270px] [font-family:'Manrope',Helvetica] font-medium text-[#07265c] text-sm text-center tracking-[-0.28px] leading-[26px]">
              {card.description}
            </div>

            {/* ========== INTERACTIVE DISCOVER MORE BUTTON ========== */}
            <button 
              onClick={() => navigate("/discover")}
              className={`group absolute top-[315px] ${card.discoverLeftOffset} inline-flex items-center justify-center gap-[6px] cursor-pointer outline-none focus:ring-2 focus:ring-[#07265c]/20 transition-all duration-200 hover:opacity-80 active:scale-95 bg-transparent border-none p-2 rounded-md`}
              aria-label={`Discover more about ${card.title}`}
            >
              <span className="[font-family:'Manrope',Helvetica] font-bold text-[#2e3975] text-[15px] tracking-[0] leading-[normal] transition-colors duration-200 group-hover:text-[#4a3aff]">
                Discover More
              </span>
              <svg 
                className="transition-transform duration-200 group-hover:translate-x-1"
                width="16" 
                height="16" 
                viewBox="0 0 16 16" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M3.33331 8H12.6666" stroke="currentColor" className="text-[#2e3975] group-hover:text-[#4a3aff]" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 3.33334L12.6667 8.00001L8 12.6667" stroke="currentColor" className="text-[#2e3975] group-hover:text-[#4a3aff]" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            {/* ========================================================= */}
          </div>
        ))}
      </InfiniteScroller>
    </div>
  );
};