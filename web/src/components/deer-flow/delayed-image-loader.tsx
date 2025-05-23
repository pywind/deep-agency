// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useEffect, useState } from "react";
import { useStore } from "~/core/store";
import { isIncompleteURL } from "~/core/utils/url";

import Image from "./image";

/**
 * DelayedImageLoader component that waits for streaming to complete before loading images
 * This prevents UI lag and errors from incomplete URLs during streaming
 */
interface DelayedImageLoaderProps {
  src: string;
  alt: string;
  className?: string;
  imageClassName?: string;
  imageTransition?: boolean;
  fallback?: React.ReactNode;
}

export function DelayedImageLoader(props: DelayedImageLoaderProps) {
  const { src, ...rest } = props;
  const [shouldRender, setShouldRender] = useState(false);
  const isStreaming = useStore((state) => state.responding);

  // Only render the image when streaming is complete and URL doesn't appear incomplete
  useEffect(() => {
    if (!isStreaming && !isIncompleteURL(src)) {
      // Add a small delay to ensure all streaming content is processed
      const timer = setTimeout(() => {
        setShouldRender(true);
      }, 200);
      
      return () => clearTimeout(timer);
    } else {
      setShouldRender(false);
    }
  }, [isStreaming, src]);

  // Show loading placeholder while streaming - using span instead of div to prevent HTML nesting issues
  if (!shouldRender) {
    return props.fallback || (
      <span className={`bg-accent animate-pulse inline-block h-40 w-40 rounded-md ${props.className || ''}`} />
    );
  }

  // Once streaming is complete, render the image
  return <Image src={src} {...rest} />;
} 