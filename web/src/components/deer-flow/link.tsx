import { useMemo, useState, useEffect } from "react";
import { useStore, useToolCalls } from "~/core/store";
import { Tooltip } from "./tooltip";
import { WarningFilled } from "@ant-design/icons";
import { isValidURL } from "~/core/utils/url";

export const Link = ({
  href,
  children,
  checkLinkCredibility = false,
}: {
  href: string | undefined;
  children: React.ReactNode;
  checkLinkCredibility: boolean;
}) => {
  const toolCalls = useToolCalls();
  const responding = useStore((state) => state.responding);
  const [validatedHref, setValidatedHref] = useState<string | null>(null);

  useEffect(() => {
    // Validate the URL before rendering
    if (href && isValidURL(href)) {
      setValidatedHref(href);
    } else if (href) {
      console.warn(`Invalid or incomplete URL detected: "${href}"`);
      setValidatedHref(null);
    }
  }, [href]);

  const credibleLinks = useMemo(() => {
    const links = new Set<string>();
    if (!checkLinkCredibility) return links;

    (toolCalls || []).forEach((call) => {
      if (call && call.name === "web_search" && call.result) {
        const result = JSON.parse(call.result) as Array<{ url: string }>;
        result.forEach((r) => {
          links.add(r.url);
        });
      }
    });
    return links;
  }, [toolCalls]);

  const isCredible = useMemo(() => {
    return checkLinkCredibility && validatedHref && !responding
      ? credibleLinks.has(validatedHref)
      : true;
  }, [credibleLinks, validatedHref, responding, checkLinkCredibility]);

  if (!validatedHref) {
    // If URL is invalid, just render the text without making it a link
    return <span>{children}</span>;
  }

  return (
    <span className="flex items-center gap-1.5">
      <a href={validatedHref} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
      {!isCredible && (
        <Tooltip
          title="This link might be a hallucination from AI model and may not be reliable."
          delayDuration={300}
        >
          <WarningFilled className="text-sx transition-colors hover:!text-yellow-500" />
        </Tooltip>
      )}
    </span>
  );
};
