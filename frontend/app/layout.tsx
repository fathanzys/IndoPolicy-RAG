import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import Sidebar from "../components/Sidebar";
import styles from "./layout.module.css";

// Menggunakan font Inter untuk tampilan clean corporate/tech
const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SGO Virtual Assistant - Bank Indonesia",
  description: "Asisten Cerdas Kebijakan Internal",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className={inter.className}>
        <div className={styles.dashboard}>
          <Sidebar />
          <main className={styles.mainContent}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}