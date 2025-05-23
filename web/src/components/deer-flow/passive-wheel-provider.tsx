"use client";

// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { usePassiveWheel } from "~/hooks/use-passive-wheel";

/**
 * Client component that applies passive wheel event handling
 * This is separated from the server components like layout.tsx
 */
export function PassiveWheelProvider({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  // Apply the passive wheel optimization hook
  usePassiveWheel();
  
  // Just render children, no additional DOM elements
  return <>{children}</>;
} 