import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StageMatch | Trouvez votre stage idéal avec l'IA",
  description: "La plateforme intelligente qui matche votre CV avec les meilleures offres de stage et d'alternance en France.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
