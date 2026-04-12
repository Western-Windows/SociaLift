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
import type { JSX } from "react";

export const HomePage = (): JSX.Element => {
  return (
    <div
      className="flex min-h-screen w-full justify-center overflow-x-hidden bg-gradient-to-r from-[#6271e1] to-[#a27bd6]"
    >
      <div
        id="top"
        className="relative w-full max-w-[1920px] shrink-0 overflow-hidden bg-[#eeeaf3] px-4 py-6 sm:px-8"
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