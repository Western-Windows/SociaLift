// src/components/ActionCard.tsx
import { ArrowRight } from "./ArrowRight";

interface ActionCardProps {
  step: string;
  title: string;
  description: string;
  linkText: string;
}

export const ActionCard = ({ step, title, description, linkText }: ActionCardProps): JSX.Element => {
  return (
    <div className="w-[380px] min-h-[300px] bg-white rounded-[35px] shadow-[0px_10px_30px_#0000001a] flex flex-col p-[28px] px-[24px] transition-transform hover:-translate-y-2 duration-300">
      
      {/* Step Number */}
      <div className="w-full text-left [font-family:'Poppins',Helvetica] font-bold text-[#347bd1] text-[20px] tracking-[0.5px]">
        {step}
      </div>

      {/* Title */}
      <h3 className="mt-[20px] w-full text-center [font-family:'Poppins',Helvetica] font-bold text-[#347bd1] text-[28px] leading-[34px] tracking-[-0.5px]">
        {title}
      </h3>

      {/* Description (This perfectly recreates the bounding box highlighted in Picture 2) */}
      <p className="mt-[16px] w-[320px] mx-auto text-center [font-family:'Poppins',Helvetica] font-medium text-[#7a92b1] text-[15px] leading-[24px] tracking-[-0.2px]">
        {description}
      </p>

      {/* Footer Link (Pushed to the bottom right automatically) */}
      <div className="mt-auto pt-[20px] w-full flex justify-end items-center gap-[6px] cursor-pointer group">
        <span className="[font-family:'Poppins',Helvetica] font-bold text-[#e687d8] text-[16px] transition-opacity group-hover:opacity-80">
          {linkText}
        </span>
        <ArrowRight className="w-[18px] h-[18px] text-[#e687d8] transition-transform group-hover:translate-x-1" />
      </div>
      
    </div>
  );
};