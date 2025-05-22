// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import type { SimpleMCPServerMetadata } from "../mcp";

import { resolveServiceURL } from "./resolve-service-url";

export async function queryMCPServerMetadata(config: SimpleMCPServerMetadata) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(resolveServiceURL("mcp/server/metadata"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      if (response.status === 504) {
        throw new Error("Server connection timed out. Please try again later.");
      }
      throw new Error(`Server error (${response.status}): ${await response.text()}`);
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error("Request timed out. The server may be overloaded or unreachable.");
    }
    throw error;
  }
}
