// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Validates if a string is a complete, properly formatted URL
 * @param url The URL string to validate
 * @returns Boolean indicating if the URL is valid
 */
export function isValidURL(url?: string): boolean {
  // Explicitly handle empty strings and undefined/null values
  if (!url || url.trim() === '') return false;
  
  try {
    // Simple URL validation that ensures the URL is complete
    const pattern = /^(https?:\/\/|www\.)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(\/\S*)?$/;
    return pattern.test(url) && !url.includes("/:") && !url.endsWith(":");
  } catch (e) {
    return false;
  }
}

/**
 * Alternative URL validation that uses the URL constructor
 * @param url The URL string to validate
 * @returns Boolean indicating if the URL is valid
 */
export function isValidURLWithConstructor(url?: string): boolean {
  // Explicitly handle empty strings and undefined/null values
  if (!url || url.trim() === '') return false;
  
  try {
    // Check if URL can be constructed and has necessary parts
    const urlObj = new URL(url);
    return Boolean(urlObj.protocol && urlObj.host);
  } catch (e) {
    return false;
  }
}

/**
 * Detects if a URL appears to be incomplete or in the process of being built
 * This is helpful for identifying URLs that are still being streamed
 * @param url The URL string to check
 * @returns Boolean indicating if the URL seems to be incomplete
 */
export function isIncompleteURL(url?: string): boolean {
  if (!url || url.trim() === '') return true;

  // Check for common patterns that indicate an incomplete URL
  const incompletePatterns = [
    // URL missing protocol or ending without full domain
    /^www\.[a-zA-Z0-9-]+$/,
    /^https?:\/\/[a-zA-Z0-9-]*$/,
    
    // URL ending with partial domain components
    /\.[a-zA-Z]{1,2}$/,
    
    // URL containing placeholders or malformed segments
    /\/:/,
    /:$/,
    
    // URL missing parts after subdomain indicators
    /\/$/, 
    /\/[^/]*?\.$/
  ];

  return incompletePatterns.some(pattern => pattern.test(url));
} 