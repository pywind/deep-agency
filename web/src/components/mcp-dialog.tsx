// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import { Blocks, ExternalLink, PencilRuler, Trash } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Tooltip } from "~/components/deer-flow/tooltip";
import { Button } from "~/components/ui/button";
import {
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Switch } from "~/components/ui/switch";
import type { MCPServerMetadata } from "~/core/mcp";
import { useSettings } from "~/core/store";
import { cn } from "~/lib/utils";

import { AddMCPServerDialog } from "../app/settings/dialogs/add-mcp-server-dialog";

export function MCPDialog() {
  const { settings, updateSettings } = useSettings();
  const [servers, setServers] = useState<MCPServerMetadata[]>(
    settings.mcp.servers,
  );
  const [newlyAdded, setNewlyAdded] = useState(false);
  
  useEffect(() => {
    setServers(settings.mcp.servers);
  }, [settings.mcp.servers]);
  
  const stdioServers = servers.filter(s => s.transport === "stdio");
  const sseServers = servers.filter(s => s.transport === "sse");

  const handleAddServers = useCallback(
    (servers: MCPServerMetadata[]) => {
      const merged = mergeServers(settings.mcp.servers, servers);
      setServers(merged);
      updateSettings({ mcp: { ...settings.mcp, servers: merged } });
      setNewlyAdded(true);
      setTimeout(() => {
        setNewlyAdded(false);
      }, 1000);
    },
    [updateSettings, settings],
  );
  
  const handleDeleteServer = useCallback(
    (name: string) => {
      const merged = settings.mcp.servers.filter(
        (server) => server.name !== name,
      );
      setServers(merged);
      updateSettings({ mcp: { ...settings.mcp, servers: merged } });
    },
    [updateSettings, settings],
  );
  
  const handleToggleServer = useCallback(
    (name: string, enabled: boolean) => {
      const merged = settings.mcp.servers.map((server) =>
        server.name === name ? { ...server, enabled } : server,
      );
      setServers(merged);
      updateSettings({ mcp: { ...settings.mcp, servers: merged } });
    },
    [updateSettings, settings],
  );

  const animationProps = {
    initial: { backgroundColor: "gray" },
    animate: { backgroundColor: "transparent" },
    transition: { duration: 1 },
    style: {
      transition: "background-color 1s ease-out",
    },
  };

  return (
    <DialogContent className="sm:max-w-[900px]">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2 text-xl">
          <Blocks className="h-6 w-6" />
          MCP Server Configuration
        </DialogTitle>
      </DialogHeader>
      
      <div className="py-2">
        <p className="text-muted-foreground">Manage and configure your MCP servers</p>
      </div>

      <div className="flex justify-between mb-6">
        <AddMCPServerDialog onAdd={handleAddServers} />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-card rounded-lg p-4 shadow-sm">
          <div className="text-muted-foreground">Total Servers</div>
          <div className="text-4xl font-bold">{servers.length}</div>
        </div>
        <div className="bg-card rounded-lg p-4 shadow-sm">
          <div className="text-muted-foreground">Stdio Servers</div>
          <div className="text-4xl font-bold">{stdioServers.length}</div>
        </div>
        <div className="bg-card rounded-lg p-4 shadow-sm">
          <div className="text-muted-foreground">SSE Servers</div>
          <div className="text-4xl font-bold">{sseServers.length}</div>
        </div>
      </div>

      <div className="border rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-6">Server List</h3>
        
        {servers.length === 0 ? (
          <div className="text-center text-muted-foreground py-16">
            No servers configured. Click "Add Server" to get started.
          </div>
        ) : (
          <ul id="mcp-servers-list" className="flex flex-col gap-4 max-h-[400px] overflow-y-auto">
            {servers.map((server) => {
              const isNew =
                server.createdAt &&
                server.createdAt > Date.now() - 1000 * 60 * 60 * 1;
              return (
                <motion.li
                  className={
                    "!bg-card group relative overflow-hidden rounded-lg border pb-2 shadow duration-300"
                  }
                  key={server.name}
                  {...(isNew && newlyAdded && animationProps)}
                >
                  <div className="absolute top-3 right-2">
                    <Tooltip title="Enable/disable server">
                      <div className="flex items-center gap-2">
                        <Switch
                          id="airplane-mode"
                          checked={server.enabled}
                          onCheckedChange={(checked) => {
                            handleToggleServer(server.name, checked);
                          }}
                        />
                      </div>
                    </Tooltip>
                  </div>
                  <div className="absolute top-1 right-12 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                    <Tooltip title="Delete server">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteServer(server.name)}
                      >
                        <Trash />
                      </Button>
                    </Tooltip>
                  </div>
                  <div
                    className={cn(
                      "flex flex-col items-start px-4 py-2",
                      !server.enabled && "text-muted-foreground",
                    )}
                  >
                    <div
                      className={cn(
                        "mb-2 flex items-center gap-2",
                        !server.enabled && "opacity-70",
                      )}
                    >
                      <div className="text-lg font-medium">{server.name}</div>
                      {!server.enabled && (
                        <div className="bg-primary text-primary-foreground h-fit rounded px-1.5 py-0.5 text-xs">
                          Disabled
                        </div>
                      )}
                      <div className="bg-primary text-primary-foreground h-fit rounded px-1.5 py-0.5 text-xs">
                        {server.transport}
                      </div>
                      {isNew && (
                        <div className="bg-primary text-primary-foreground h-fit rounded px-1.5 py-0.5 text-xs">
                          New
                        </div>
                      )}
                    </div>
                    <ul
                      className={cn(
                        "flex flex-wrap items-center gap-2",
                        !server.enabled && "opacity-70",
                      )}
                    >
                      <PencilRuler size={16} />
                      {server.tools.map((tool) => (
                        <li
                          key={tool.name}
                          className="text-muted-foreground border-muted-foreground w-fit rounded-md border px-2"
                        >
                          <Tooltip key={tool.name} title={tool.description}>
                            <div className="w-fit text-sm">{tool.name}</div>
                          </Tooltip>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="text-muted-foreground text-center text-sm mt-4 border-t pt-4">
        More MCP servers available on the web, e.g.{" "}
        <a href="https://mcp.composio.dev" target="_blank" rel="noopener noreferrer" className="text-blue-500 inline-flex items-center">
          mcp.composio.dev <ExternalLink className="h-3 w-3 ml-1" />
        </a>{" "}
        and{" "}
        <a href="https://mcp.run" target="_blank" rel="noopener noreferrer" className="text-blue-500 inline-flex items-center">
          mcp.run <ExternalLink className="h-3 w-3 ml-1" />
        </a>
      </div>
    </DialogContent>
  );
}

function mergeServers(
  existing: MCPServerMetadata[],
  added: MCPServerMetadata[],
): MCPServerMetadata[] {
  const serverMap = new Map(existing.map((server) => [server.name, server]));

  for (const addedServer of added) {
    addedServer.createdAt = Date.now();
    addedServer.updatedAt = Date.now();
    serverMap.set(addedServer.name, addedServer);
  }

  const result = Array.from(serverMap.values());
  result.sort((a, b) => b.createdAt - a.createdAt);
  return result;
} 