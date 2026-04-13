import {
  AnalyticsSection,
  DashboardPreviewSection,
  FeatureCardsCarouselSection,
  FooterSection,
  IntelligentCommentingSection,
  LandingHeroSection,
  MessengerAutomationFeatureSection,
  PrimaryNavSection,
  ProductFeatureOverviewSection,
  VisualSchedulingFeatureSection,
} from "./index.ts";
import { DynamicPersonaBuilderSection } from "./DynamicPersonaBuilderSection";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { VideoModal } from "../../../components/VideoModal";

export const LandingPage = (): JSX.Element => {
  const navigate = useNavigate();

  const handleSignIn = () => navigate("/signin");
  const handleSignUp = () => navigate("/signup");
  const [isVideoOpen, setIsVideoOpen] = useState(false);
  const handleWatchVideo = () => setIsVideoOpen(true);


  return (
    <div
      className="flex min-h-screen w-full justify-center overflow-x-hidden"
      style={{ background: "linear-gradient(90deg, #6271e1 0%, #a27bd6 100%)" }}
    >
      <div
        id="top"
        // Changed w-[1536px] to w-full max-w-[1536px] for responsiveness
        className="relative h-[6650.0px] w-full max-w-[1536px] shrink-0 overflow-hidden bg-[#eeeaf3]"
        data-model-id="124:747"
      >
        <div id="hero">
          <LandingHeroSection />
        </div>
        <PrimaryNavSection />

        <button
          type="button"
          onClick={handleSignIn}
          className="absolute right-[210px] top-[26px] z-10 h-[48px] w-[145px] cursor-pointer rounded-[8px] bg-transparent outline-none transition-colors hover:bg-white/2"
          aria-label="Sign in"
        />
        <button
          type="button"
          onClick={handleSignUp}
          className="absolute right-[40px] top-[26px] z-10 h-[48px] w-[150px] cursor-pointer rounded-[8px] bg-transparent outline-none transition-colors hover:bg-white/20"
          aria-label="Sign up"
        />
        <button
          type="button"
          onClick={handleWatchVideo}
          className="absolute left-[calc(50%-110px)] top-[474px] z-10 h-[60px] w-[225px] cursor-pointer rounded-full bg-transparent outline-none transition-colors hover:bg-white/20"
          aria-label="Watch video"
        />

        <div id="features">
          <FeatureCardsCarouselSection />
        </div>

        <VisualSchedulingFeatureSection />

        <DynamicPersonaBuilderSection />

        <ProductFeatureOverviewSection />
        <DashboardPreviewSection />

        {/* Changed w-[1536px] to w-full */}
        <div className="absolute left-px top-[5057px] h-[1675px] w-full">
          <AnalyticsSection />
          <IntelligentCommentingSection />
        </div>
        
        <VideoModal
          isOpen={isVideoOpen}
          onClose={() => setIsVideoOpen(false)}
          videoUrl="https://www.youtube.com/embed/EEvopkbc4FE"
        />
        <MessengerAutomationFeatureSection />
        <FooterSection />
      </div>
    </div>
  );
};