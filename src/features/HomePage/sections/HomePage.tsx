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
// import { HomeNavSection } from "./../sections/HomeNavSection.tsx";

export const HomePage = (): JSX.Element => {
  return (
    <div
      className="flex min-h-screen justify-center overflow-x-hidden"
      style={{ background: "linear-gradient(90deg, #6271e1 0%, #a27bd6 100%)" }}
    >
      <div
        id="top"
        // Added max-w-[1536px] to constrain maximum width while staying fluid on smaller screens
        className="relative z-0 h-[6650.0px] w-full max-w-[1536px] shrink-0 overflow-hidden"
      >
        <div className="absolute top-[1190px] left-0 w-full h-[calc(100%-1190px)] bg-[#eeeaf3] -z-10" />

        <div id="hero">
          <HomeHeroSection />
        </div>
        {/* <HomeNavSection /> */}

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

        <MessengerAutomationFeatureSection />
        <FooterSection />
      </div>
    </div>
  );
};