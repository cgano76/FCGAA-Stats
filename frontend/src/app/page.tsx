import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Database,
  FileText,
  ShieldCheck
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { MetricCard } from "@/components/MetricCard";
import { StatusPill } from "@/components/StatusPill";
import { mvpFilters } from "@/lib/navigation";

const importSteps = [
  "Televersement PDF",
  "Extraction automatique",
  "Controle des anomalies",
  "Validation humaine",
  "Integration des valeurs sourcees"
];

export default function Home() {
  return (
    <AppShell>
      <section className="hero" id="dashboard">
        <div>
          <StatusPill tone="ok">MVP prudent</StatusPill>
          <h1>Tableau de bord OGA</h1>
          <p>
            Consultation des statistiques FCGAA selon abonnement, avec separation
            Conventionnel/BIO, validation humaine et source obligatoire pour chaque valeur.
          </p>
        </div>
        <div className="hero-panel">
          <ShieldCheck size={22} />
          <strong>Regle active</strong>
          <span>Aucun chiffre affiche sans source validee.</span>
        </div>
      </section>

      <section className="metrics-grid" aria-label="Chiffres cles">
        <MetricCard label="Statut cotisation" value="A parametrer" source="Source : module OGA" />
        <MetricCard label="Derniere cloture validee" />
        <MetricCard label="Imports PDF" value="Aucun import valide" source="Source : workflow import" />
        <MetricCard label="Analyses IA" value="Non generees" source="Source : base validee + Mistral" />
      </section>

      <section className="section" id="search">
        <div className="section-heading">
          <div>
            <StatusPill>Recherche MVP</StatusPill>
            <h2>Filtres indispensables</h2>
          </div>
        </div>
        <div className="filter-row">
          {mvpFilters.map((filter) => (
            <button key={filter} type="button" className="filter-chip">
              {filter}
            </button>
          ))}
        </div>
      </section>

      <section className="two-columns">
        <article className="section" id="import">
          <div className="section-heading">
            <div>
              <StatusPill tone="warning">Import</StatusPill>
              <h2>PDF source principale</h2>
            </div>
            <FileText aria-hidden="true" />
          </div>
          <ol className="step-list">
            {importSteps.map((step) => (
              <li key={step}>
                <CheckCircle2 size={17} aria-hidden="true" />
                {step}
              </li>
            ))}
          </ol>
        </article>

        <article className="section" id="validation">
          <div className="section-heading">
            <div>
              <StatusPill tone="warning">Validation</StatusPill>
              <h2>Valeurs a verifier</h2>
            </div>
            <Database aria-hidden="true" />
          </div>
          <div className="empty-state">
            <AlertTriangle size={21} aria-hidden="true" />
            <p>
              Aucun tableau extrait pour le moment. Les valeurs importees resteront en brouillon
              tant qu'un administrateur ne les aura pas validees.
            </p>
          </div>
        </article>
      </section>

      <section className="section" id="comparison">
        <div className="section-heading">
          <div>
            <StatusPill>Comparaison</StatusPill>
            <h2>2025 vs 2024</h2>
          </div>
          <ArrowRight aria-hidden="true" />
        </div>
        <div className="comparison-shell">
          <div>
            <strong>Conventionnel</strong>
            <span>Donnee non disponible</span>
          </div>
          <div>
            <strong>BIO</strong>
            <span>Donnee non disponible</span>
          </div>
          <div>
            <strong>Alerte echantillon</strong>
            <span>Declenchee seulement avec populations validees</span>
          </div>
        </div>
      </section>

      <section className="two-columns">
        <article className="section" id="ai">
          <StatusPill tone="ok">Mistral</StatusPill>
          <h2>Analyse IA institutionnelle</h2>
          <p>
            L'IA produit des syntheses uniquement a partir de valeurs validees en base.
            Les recherches externes restent des contextes cites et ne remplacent jamais les chiffres FCGAA.
          </p>
        </article>

        <article className="section" id="exports">
          <StatusPill>Exports</StatusPill>
          <h2>Excel, CSV, PDF, PNG</h2>
          <p>
            Chaque export inclut la source, la date de generation et la mention
            "Donnees issues des recueils statistiques FCGAA".
          </p>
        </article>
      </section>
    </AppShell>
  );
}

