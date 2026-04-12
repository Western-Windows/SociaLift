import {
  AnalyticsSection,
  DashboardPreviewSection,
  FeatureCardsCarouselSection,
  FooterSection,
  IntelligentCommentingSection,
  MessengerAutomationFeatureSection,
  ProductFeatureOverviewSection,
  VisualSchedulingFeatureSection,
} from "../../LandingPage/sections/index.ts";
import { DynamicPersonaBuilderSection } from "../../LandingPage/sections/DynamicPersonaBuilderSection/DynamicPersonaBuilderSection.tsx";
import { HomeHeroSection } from "./../sections/HomeHeroSection.tsx";
import { HomeNavSection } from "./../sections/HomeNavSection.tsx";

export const HomePage = (): JSX.Element => {
  return (
    <div
      className="flex min-h-screen w-full justify-center overflow-x-hidden"
      style={{ background: "linear-gradient(90deg, #6271e1 0%, #a27bd6 100%)" }}
    >
      <div
        id="top"
        className="relative h-[6731.4px] w-[1536px] shrink-0 overflow-hidden bg-[#eeeaf3]"
      >
        <div id="hero">
          <HomeHeroSection />
        </div>
        <HomeNavSection />

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

        <MessengerAutomationFeatureSection />
        <FooterSection />
      </div>
    </div>
  );
};