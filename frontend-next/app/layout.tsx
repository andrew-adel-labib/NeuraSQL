import type { Metadata } from "next";

import { Geist, Geist_Mono } from "next/font/google";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "QBS AI Analytics",
  description:
    "Enterprise conversational SQL AI analytics platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`
        ${geistSans.variable}
        ${geistMono.variable}
        h-full
        scroll-smooth
        antialiased
      `}
    >
      <body
        className="
          min-h-screen
          bg-[#020817]
          text-white
          overflow-hidden
          font-sans
        "
      >
        {children}
      </body>
    </html>
  );
}