import React from "react";
import LandingHeader from "./LandingHeader";
import LandingHero from "./LandingHero";
import LandingHowItWorks from "./LandingHowItWorks";
import LandingFeatures from "./LandingFeatures";
import LandingFooter from "./LandingFooter";

interface LandingPageProps {
  onSignIn: () => void;
  onSignUp: () => void;
}

export default function LandingPage({ onSignIn, onSignUp }: LandingPageProps) {
  return (
    <div className="min-h-screen font-sans bg-gradient-to-br from-[#E3F2FD] to-[#BBDEFB]">
      <LandingHeader onSignIn={onSignIn} onSignUp={onSignUp} />
      <main>
        <LandingHero onGetStarted={onSignUp} />
        <LandingHowItWorks onJoinNow={onSignUp} />
        <LandingFeatures />
      </main>
      <LandingFooter />
    </div>
  );
}
