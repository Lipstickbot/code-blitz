import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "BlitzCode — тренировка алгоритмов и соревнования",
  description:
    "BlitzCode помогает решать задачи, участвовать в блиц-матчах и отслеживать прогресс на удобной платформе для программистов.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className="min-h-screen overflow-x-hidden bg-void text-ink">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
