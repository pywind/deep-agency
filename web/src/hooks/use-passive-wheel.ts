"use client";

// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useEffect } from 'react';

/**
 * Hook that adds passive wheel event listeners to improve scroll performance
 * 
 * This addresses the warning:
 * "Handling of 'wheel' input event was delayed due to main thread being busy.
 * Consider marking event handler as 'passive' to make the page more responsive."
 */
export function usePassiveWheel() {
  useEffect(() => {
    // Add support for passive wheel events at the document level
    // This improves scrolling performance across the entire app
    
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    
    // Override addEventListener to make wheel events passive by default
    EventTarget.prototype.addEventListener = function(type, listener, options) {
      if (type === 'wheel' || type === 'mousewheel' || type === 'touchstart' || type === 'touchmove') {
        let newOptions = options;
        
        // If options is a boolean, convert to an object
        if (typeof options === 'boolean') {
          newOptions = {
            capture: options,
            passive: true
          };
        } else if (options === undefined) {
          newOptions = { passive: true };
        } else if (typeof options === 'object' && options !== null && !('passive' in options)) {
          // Clone the options object to avoid mutating the original
          newOptions = { ...options, passive: true };
        }
        
        // Call the original method with the modified options
        return originalAddEventListener.call(this, type, listener, newOptions);
      }
      
      // For other event types, use the original behavior
      return originalAddEventListener.call(this, type, listener, options);
    };
    
    // Clean up on unmount
    return () => {
      EventTarget.prototype.addEventListener = originalAddEventListener;
    };
  }, []);
} 