// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useEffect, useState } from "react";
import { useStore } from "~/core/store";
import { isIncompleteURL } from "~/core/utils/url";

import { FavIcon } from "./fav-icon";

/**
 * DelayedFavIconLoader component that waits for streaming to complete before loading favicons
 * This prevents UI lag and errors from incomplete URLs during streaming
 */
interface DelayedFavIconLoaderProps {
  url: string;
  title?: string;
  className?: string;
}

export function DelayedFavIconLoader(props: DelayedFavIconLoaderProps) {
  const { url, ...rest } = props;
  const [shouldRender, setShouldRender] = useState(false);
  const isStreaming = useStore((state) => state.responding);

  // Only render the favicon when streaming is complete and URL doesn't appear incomplete
  useEffect(() => {
    if (!isStreaming && !isIncompleteURL(url)) {
      // Add a small delay to ensure all streaming content is processed
      const timer = setTimeout(() => {
        setShouldRender(true);
      }, 200);
      
      return () => clearTimeout(timer);
    } else {
      setShouldRender(false);
    }
  }, [isStreaming, url]);

  // Render a placeholder while streaming - using span instead of div to prevent HTML nesting issues
  if (!shouldRender) {
    return (
      <span className={`bg-accent animate-pulse inline-block h-4 w-4 rounded-full shadow-sm ${props.className || ''}`} />
    );
  }

  // Once streaming is complete, render the favicon
  return <FavIcon url={url} {...rest} />;
} 