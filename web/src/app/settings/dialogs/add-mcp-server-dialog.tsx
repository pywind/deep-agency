// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Loader2, MonitorX, Globe } from "lucide-react";
import { useCallback, useState } from "react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "~/components/ui/dialog";
import { Input } from "~/components/ui/input";
import { queryMCPServerMetadata } from "~/core/api";
import {
  type MCPServerMetadata,
  type SimpleMCPServerMetadata,
  type SimpleSSEMCPServerMetadata,
  type SimpleStdioMCPServerMetadata,
} from "~/core/mcp";
import { Tabs, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Plus, X } from "lucide-react";

export function AddMCPServerDialog({
  onAdd,
}: {
  onAdd?: (servers: MCPServerMetadata[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [serverName, setServerName] = useState("");
  const [connectionType, setConnectionType] = useState<"stdio" | "sse">("stdio");
  const [url, setUrl] = useState("");
  const [command, setCommand] = useState("python");
  const [args, setArgs] = useState("-m mcp_server");
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  
  const handleSave = useCallback(async () => {
    if (!serverName.trim()) {
      setError("Server name is required");
      return;
    }
    
    if (connectionType === "sse" && !url.trim()) {
      setError("URL is required for SSE connection");
      return;
    }
    
    if (connectionType === "stdio" && !command.trim()) {
      setError("Command is required for Standard IO connection");
      return;
    }
    
    const serverConfig: SimpleMCPServerMetadata = 
      connectionType === "sse" 
        ? {
            transport: "sse",
            name: serverName.trim(),
            url: url.trim()
          } as SimpleSSEMCPServerMetadata
        : {
            transport: "stdio",
            name: serverName.trim(),
            command: command.trim(),
            args: args.trim().split(" ")
          } as SimpleStdioMCPServerMetadata;
    
    setProcessing(true);
    
    try {
      setError(null);
      const metadata = await queryMCPServerMetadata(serverConfig);
      onAdd?.([{ ...metadata, name: serverName.trim(), enabled: true }]);
      
      // Reset form
      setServerName("");
      setUrl("");
      setCommand("python");
      setArgs("-m mcp_server");
      setOpen(false);
    } catch (e) {
      console.error(e);
      // Display more helpful error message
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError(`Failed to add server: ${serverName}. Please check server connection.`);
      }
    } finally {
      setProcessing(false);
    }
  }, [serverName, connectionType, url, command, args, onAdd]);
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus size={16} className="mr-1" />
          Add Server
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add New Server
          </DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <label htmlFor="name" className="text-sm font-medium">
              Server Name
            </label>
            <Input
              id="name"
              value={serverName}
              onChange={(e) => setServerName(e.target.value)}
              placeholder="e.g., api-service, data-processor"
            />
          </div>
          
          <div className="grid gap-2">
            <label className="text-sm font-medium">
              Connection Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <Button
                type="button"
                variant={connectionType === "stdio" ? "default" : "outline"}
                className="justify-start"
                onClick={() => setConnectionType("stdio")}
              >
                <MonitorX className="mr-2 h-4 w-4" />
                Standard IO
              </Button>
              <Button
                type="button"
                variant={connectionType === "sse" ? "default" : "outline"}
                className="justify-start"
                onClick={() => setConnectionType("sse")}
              >
                <Globe className="mr-2 h-4 w-4" />
                SSE
              </Button>
            </div>
          </div>
          
          {connectionType === "sse" ? (
            <div className="grid gap-2">
              <label htmlFor="url" className="text-sm font-medium">
                URL
              </label>
              <Input
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="e.g., http://localhost:8000/events"
              />
            </div>
          ) : (
            <div className="grid gap-2">
              <label htmlFor="command" className="text-sm font-medium">
                Command
              </label>
              <Input
                id="command"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="e.g., python"
              />
              <label htmlFor="args" className="text-sm font-medium">
                Arguments
              </label>
              <Input
                id="args"
                value={args}
                onChange={(e) => setArgs(e.target.value)}
                placeholder="e.g., -m mcp_server"
              />
            </div>
          )}
        </div>

        <DialogFooter>
          <div className="flex w-full items-center justify-between">
            <div className="text-destructive text-sm">
              {error}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setOpen(false)}>
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
              <Button 
                onClick={handleSave}
                disabled={processing}
              >
                {processing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <Plus className={processing ? "hidden" : "mr-2 h-4 w-4"} />
                Add Server
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
