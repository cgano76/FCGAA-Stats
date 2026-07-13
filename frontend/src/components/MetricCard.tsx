type MetricCardProps = {
  label: string;
  value?: string;
  source?: string;
};

export function MetricCard({ label, value = "Donnee non disponible", source }: MetricCardProps) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{source ?? "Source attendue : valeur validee en base"}</small>
    </article>
  );
}

