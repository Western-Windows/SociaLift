// src/screens/LandingPage/sections/LandingPage.tsx
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
import { useState, type JSX } from "react";
import { VideoModal } from "../../../components/VideoModal";
export const LandingPage = (): JSX.Element => {
  const navigate = useNavigate();

  const handleSignIn = () => navigate("/signin");
  const handleSignUp = () => navigate("/signup");
  const [isVideoOpen, setIsVideoOpen] = useState(false);
  const handleWatchVideo = () => setIsVideoOpen(true);


  return (
    <div
      className="flex min-h-screen w-full justify-center overflow-x-hidden bg-gradient-to-r from-[#6271e1] to-[#a27bd6]"
    >
      <div
        id="top"
        className="relative w-full max-w-[1920px] shrink-0 overflow-hidden bg-[#eeeaf3] px-4 py-6 sm:px-8"
        data-model-id="124:747"
      >
        <div id="hero">
          <LandingHeroSection />
        </div>
        <PrimaryNavSection onSignIn={handleSignIn} onSignUp={handleSignUp} />

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

        <div className="absolute left-px top-[5057px] h-[1675px] w-[1536px]">
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