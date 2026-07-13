import Image from "next/image";
import type { ReactNode } from "react";
import { modules } from "@/lib/navigation";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Image
            src="/logo-fcgaa-rond.jpg"
            alt="Logo FCGAA"
            width={66}
            height={66}
            priority
          />
          <div>
            <strong>FCGAA Stats</strong>
            <span>Observatoire agricole</span>
          </div>
        </div>

        <nav className="nav-list" aria-label="Navigation principale">
          {modules.map((item) => {
            const Icon = item.icon;
            return (
              <a key={item.label} href={item.href}>
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
