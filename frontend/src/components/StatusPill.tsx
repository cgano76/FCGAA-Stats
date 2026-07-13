import type { ReactNode } from "react";

type StatusPillProps = {
  children: ReactNode;
  tone?: "ok" | "warning" | "neutral";
};

export function StatusPill({ children, tone = "neutral" }: StatusPillProps) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}
