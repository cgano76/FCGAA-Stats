import {
  BarChart3,
  BookOpen,
  FileCheck2,
  FileDown,
  Globe2,
  LayoutDashboard,
  LockKeyhole,
  Search,
  Sparkles,
  Upload,
  Users
} from "lucide-react";

export const modules = [
  { label: "Tableau de bord OGA", href: "#dashboard", icon: LayoutDashboard },
  { label: "Recherche", href: "#search", icon: Search },
  { label: "Import PDF", href: "#import", icon: Upload },
  { label: "Validation", href: "#validation", icon: FileCheck2 },
  { label: "Comparaisons", href: "#comparison", icon: BarChart3 },
  { label: "Analyses IA", href: "#ai", icon: Sparkles },
  { label: "Exports", href: "#exports", icon: FileDown },
  { label: "Referentiels", href: "#referentials", icon: BookOpen },
  { label: "OGA", href: "#ogas", icon: Users },
  { label: "Public", href: "#public", icon: Globe2 },
  { label: "Securite", href: "#security", icon: LockKeyhole }
];

export const mvpFilters = [
  "Cloture",
  "Recolte",
  "Profession",
  "Conventionnel ou BIO",
  "Zone",
  "Quartile",
  "Indicateur"
];

