"use client";

import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import * as React from "react";

import { cn } from "~/lib/utils";

// Force ScrollAreaPrimitive to use passive wheel events
if (typeof window !== 'undefined') {
  // Add an empty passive wheel event listener to hint the browser
  // that wheel events in this component should be treated as passive
  document.addEventListener('wheel', () => {}, { passive: true });
  document.addEventListener('touchmove', () => {}, { passive: true });
}

function ScrollArea({
  className,
  children,
  ref,
  ...props
}: React.ComponentProps<typeof ScrollAreaPrimitive.Root>) {
  // Add ref for the viewport to ensure we can access it
  const viewportRef = React.useRef<HTMLDivElement>(null);
  
  // Combine refs if provided
  const combinedRef = React.useMemo(() => {
    if (!ref) return viewportRef;
    
    return (node: HTMLDivElement) => {
      // @ts-ignore - we know this is a ref
      if (typeof ref === 'function') ref(node);
      else if (ref) ref.current = node;
      
      viewportRef.current = node;
    };
  }, [ref]);
  
  // Ensure wheel events are passive
  React.useEffect(() => {
    if (!viewportRef.current) return;
    
    // Set passive wheel events on the viewport
    const viewportElement = viewportRef.current;
    const wheelOptions = { passive: true };
    
    // Empty functions as we just want to ensure passivity
    viewportElement.addEventListener('wheel', () => {}, wheelOptions);
    viewportElement.addEventListener('touchmove', () => {}, wheelOptions);
    
    return () => {
      viewportElement.removeEventListener('wheel', () => {});
      viewportElement.removeEventListener('touchmove', () => {});
    };
  }, []);

  return (
    <ScrollAreaPrimitive.Root
      data-slot="scroll-area"
      className={cn("relative", className)}
      {...props}
    >
      <ScrollAreaPrimitive.Viewport
        data-slot="scroll-area-viewport"
        className="focus-visible:ring-ring/50 size-full rounded-[inherit] transition-[color,box-shadow] outline-none focus-visible:ring-[3px] focus-visible:outline-1"
        // https://github.com/stackblitz-labs/use-stick-to-bottom/issues/15
        ref={combinedRef}
      >
        {children}
      </ScrollAreaPrimitive.Viewport>
      <ScrollBar />
      <ScrollAreaPrimitive.Corner />
    </ScrollAreaPrimitive.Root>
  );
}

function ScrollBar({
  className,
  orientation = "vertical",
  ...props
}: React.ComponentProps<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>) {
  return (
    <ScrollAreaPrimitive.ScrollAreaScrollbar
      data-slot="scroll-area-scrollbar"
      orientation={orientation}
      className={cn(
        "flex touch-none p-px transition-colors select-none",
        orientation === "vertical" &&
          "h-full w-2.5 border-l border-l-transparent",
        orientation === "horizontal" &&
          "h-2.5 flex-col border-t border-t-transparent",
        className,
      )}
      {...props}
    >
      <ScrollAreaPrimitive.ScrollAreaThumb
        data-slot="scroll-area-thumb"
        className="bg-border relative flex-1 rounded-full"
      />
    </ScrollAreaPrimitive.ScrollAreaScrollbar>
  );
}

export { ScrollArea, ScrollBar };
