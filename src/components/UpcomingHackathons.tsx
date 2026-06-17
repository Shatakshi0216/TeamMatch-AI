import React from "react";
import { Calendar, MapPin, Award, Users, ArrowRight } from "lucide-react";

interface Hackathon {
  id: string;
  name: string;
  organizer: string;
  date: string;
  location: string;
  prize: string;
  description: string;
  tags: string[];
  interestFilter: string;
}

const HACKATHONS: Hackathon[] = [
  {
    id: "ethindia",
    name: "EthIndia 2026",
    organizer: "Devfolio",
    date: "Dec 4 - 6, 2026",
    location: "Bengaluru, India",
    prize: "$50,000+ USD",
    description: "Asia's biggest Ethereum hackathon. Build the decentralized future alongside thousands of Web3 developers, designers, and creators.",
    tags: ["Web3", "Blockchain", "Solidity", "Security"],
    interestFilter: "Web3"
  },
  {
    id: "hackmit",
    name: "HackMIT 2026",
    organizer: "MIT",
    date: "Sep 19 - 20, 2026",
    location: "MIT (Boston, USA)",
    prize: "$20,000+ USD",
    description: "MIT's premier undergraduate hackathon. Gathering 1,000 of the world's brightest minds to hack, learn, and showcase innovative tech products.",
    tags: ["AI", "SaaS", "Hardware", "FinTech"],
    interestFilter: "AI"
  },
  {
    id: "sih",
    name: "Smart India Hackathon 2026",
    organizer: "Ministry of Education, India",
    date: "Aug 12 - 15, 2026",
    location: "Delhi, India (Nodal Centers)",
    prize: "₹1,00,000 per problem statement",
    description: "A nationwide initiative to provide students with a platform to solve some of the pressing problems we face in our daily lives.",
    tags: ["HealthTech", "EdTech", "IoT", "SaaS"],
    interestFilter: "HealthTech"
  },
  {
    id: "google-solution",
    name: "Google Solution Challenge 2026",
    organizer: "Google Developer Student Clubs",
    date: "May 15 - June 30, 2026",
    location: "Global (Online)",
    prize: "$3,000 - $12,000 USD",
    description: "Solve one or more of the United Nations 17 Sustainable Development Goals using Google technologies and APIs.",
    tags: ["AI", "Google Cloud", "Flutter", "SaaS"],
    interestFilter: "AI"
  }
];

interface UpcomingHackathonsProps {
  setActiveTab: (tab: string) => void;
  setSearchInterests: (interests: string) => void;
}

const UpcomingHackathons: React.FC<UpcomingHackathonsProps> = ({ setActiveTab, setSearchInterests }) => {
  const handleFindTeammates = (interest: string) => {
    setSearchInterests(interest);
    setActiveTab("find-teammates");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Upcoming Hackathons</h2>
        <p className="text-slate-500 text-sm mt-0.5">Explore premier developer hackathons and find your dream team to win.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {HACKATHONS.map((h) => (
          <div key={h.id} className="bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-[0_8px_30px_rgb(37,99,235,0.08)] transition-all p-6 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">{h.organizer}</span>
                  <h3 className="text-lg font-bold text-slate-900 mt-2">{h.name}</h3>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
                  <Award size={14} /> {h.prize}
                </div>
              </div>

              <p className="text-slate-500 text-sm leading-relaxed mb-4">{h.description}</p>

              <div className="space-y-2 mb-6 text-xs text-slate-500">
                <div className="flex items-center gap-2">
                  <Calendar size={14} className="text-indigo-500 shrink-0" />
                  <span>{h.date}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin size={14} className="text-red-500 shrink-0" />
                  <span>{h.location}</span>
                </div>
              </div>
            </div>

            <div>
              <div className="flex flex-wrap gap-1.5 mb-6">
                {h.tags.map(tag => (
                  <span key={tag} className="px-2 py-0.5 rounded-full bg-slate-50 text-slate-600 border border-slate-100 text-xs font-medium">
                    {tag}
                  </span>
                ))}
              </div>

              <button
                onClick={() => handleFindTeammates(h.interestFilter)}
                className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-bold transition-all text-sm flex items-center justify-center gap-2 shadow-md shadow-blue-500/10"
              >
                <Users size={16} /> Find Teammates <ArrowRight size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UpcomingHackathons;
