// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { memo, useCallback, useEffect, useState } from "react";

import { cn } from "~/lib/utils";
import { isValidURL } from "~/core/utils/url";

import { Tooltip } from "./tooltip";

function Image({
  className,
  imageClassName,
  imageTransition,
  src,
  alt,
  fallback = null,
}: {
  className?: string;
  imageClassName?: string;
  imageTransition?: boolean;
  src: string;
  alt: string;
  fallback?: React.ReactNode;
}) {
  const [, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [validatedSrc, setValidatedSrc] = useState<string | null>(null);

  useEffect(() => {
    setIsError(false);
    setIsLoading(true);
    
    // Validate URL before setting source
    if (src && isValidURL(src)) {
      setValidatedSrc(src);
    } else {
      console.warn(`Invalid or incomplete image URL: "${src}"`);
      setIsError(true);
      setValidatedSrc(null); // Explicitly set to null, not empty string
    }
  }, [src]);

  const handleLoad = useCallback(() => {
    setIsError(false);
    setIsLoading(false);
  }, []);
  const handleError = useCallback(
    (e: React.SyntheticEvent<HTMLImageElement>) => {
      e.currentTarget.style.display = "none";
      console.warn(`Markdown: Image "${e.currentTarget.src}" failed to load`);
      setIsError(true);
    },
    [],
  );
  return (
    <span className={cn("block w-fit overflow-hidden", className)}>
      {isError || !validatedSrc ? (
        fallback
      ) : (
        <Tooltip title={alt ?? "No caption"}>
          <img
            className={cn(
              "size-full object-cover",
              imageTransition && "transition-all duration-200 ease-out",
              imageClassName,
            )}
            src={validatedSrc}
            alt={alt}
            onLoad={handleLoad}
            onError={handleError}
          />
        </Tooltip>
      )}
    </span>
  );
}

export default memo(Image);
