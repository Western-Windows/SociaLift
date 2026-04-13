import postedByOurAiBot from "../../../../../postedbyouraibot.svg";

export const DashboardPreviewSection = (): JSX.Element => {
  return (
    <div className="absolute top-[3630px] left-[881px] h-[480px] w-[623px]">
      <img
        className="h-full w-full object-contain"
        alt="Posted by our AI bot"
        src={postedByOurAiBot}
      />
    </div>
  );
};