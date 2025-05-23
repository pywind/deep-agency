// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useState, useEffect } from "react";
import { cn } from "~/lib/utils";
import { isValidURLWithConstructor } from "~/core/utils/url";

export function FavIcon({
  className,
  url,
  title,
}: {
  className?: string;
  url: string;
  title?: string;
}) {
  const [validIconUrl, setValidIconUrl] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const fallbackIcon = "https://perishablepress.com/wp/wp-content/images/2021/favicon-standard.png";

  useEffect(() => {
    if (!url) {
      setHasError(true);
      return;
    }

    try {
      if (isValidURLWithConstructor(url)) {
        const urlObj = new URL(url);
        setValidIconUrl(urlObj.origin + "/favicon.ico");
        setHasError(false);
      } else {
        console.warn(`Invalid URL provided to FavIcon: ${url}`);
        setHasError(true);
      }
    } catch (e) {
      console.warn(`Error processing URL in FavIcon: ${url}`, e);
      setHasError(true);
    }
  }, [url]);

  // Determine the source to use - fallback for errors or when validIconUrl is null or empty
  const imgSrc = hasError || !validIconUrl ? fallbackIcon : validIconUrl;
  
  return (
    <img
      className={cn("bg-accent h-4 w-4 rounded-full shadow-sm", className)}
      width={16}
      height={16}
      src={imgSrc}
      alt={title}
      onError={(e) => {
        console.warn(`Failed to load favicon from: ${validIconUrl}`);
        e.currentTarget.src = fallbackIcon;
        setHasError(true);
      }}
    />
  );
}
