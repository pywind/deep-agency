// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import "~/styles/globals.css";

import { type Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";

import { ThemeProviderWrapper } from "~/components/deer-flow/theme-provider-wrapper";
import { PassiveWheelProvider } from "~/components/deer-flow/passive-wheel-provider";
import { env } from "~/env";

import { Toaster } from "../components/deer-flow/toaster";

export const metadata: Metadata = {
  title: "💡 Deep Agency",
  description:
    "Deep Exploration and Efficient Research, an AI tool that combines language models with specialized tools for research tasks.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

// Optimized font loading configuration
const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
  display: "swap", // Use swap to prevent FOUT (Flash of Unstyled Text)
  preload: false, // Disable automatic preload to prevent unused preload warnings
  fallback: ["system-ui", "sans-serif"], // Fallback fonts
  adjustFontFallback: true, // Automatically adjust font metrics to minimize layout shift
  weight: ["400", "500", "600", "700"], // Specify exact weights needed
});

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geist.variable}`} suppressHydrationWarning>
      <head>
        {/* Define isSpace function globally to fix markdown-it issues with Next.js + Turbopack
          https://github.com/markdown-it/markdown-it/issues/1082#issuecomment-2749656365 */}
        <Script id="markdown-it-fix" strategy="beforeInteractive">
          {`
            if (typeof window !== 'undefined' && typeof window.isSpace === 'undefined') {
              window.isSpace = function(code) {
                return code === 0x20 || code === 0x09 || code === 0x0A || code === 0x0B || code === 0x0C || code === 0x0D;
              };
            }
          `}
        </Script>
      </head>
      <body className="bg-app" suppressHydrationWarning>
        <PassiveWheelProvider>
          <ThemeProviderWrapper>{children}</ThemeProviderWrapper>
        </PassiveWheelProvider>
        <Toaster />
      </body>
    </html>
  );
}
