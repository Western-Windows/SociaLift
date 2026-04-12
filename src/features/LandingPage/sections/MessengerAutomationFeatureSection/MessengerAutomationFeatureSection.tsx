import messengerPic from "../../../../../messengerpic.svg";
import rectangle from "../../../../../rectangle.svg";

export const MessengerAutomationFeatureSection = (): JSX.Element => {
  return (
    <div className="absolute top-[4345px] left-[104px] z-10 h-[461px] w-[383px]">
      <img
        className="absolute left-1 top-[357px] h-[64px] w-[376px] object-cover"
        alt="Rectangle"
        src={rectangle}
      />

      <img
        className="absolute left-0 top-0 h-[461px] w-[383px] object-contain"
        alt="Messenger"
        src={messengerPic}
      />
    </div>
  );
};