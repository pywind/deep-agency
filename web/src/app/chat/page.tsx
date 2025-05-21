// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { GithubOutlined } from "@ant-design/icons";
import { Blocks, Settings } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Suspense, useState, useEffect } from "react";
import type { ReactNode } from "react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogTrigger,
} from "~/components/ui/dialog";

import { Logo } from "../../components/deer-flow/logo";
import { ThemeToggle } from "../../components/deer-flow/theme-toggle";
import { Tooltip } from "../../components/deer-flow/tooltip";
import { MCPDialog } from "~/components/mcp-dialog";
import { SettingsDialog } from "../settings/dialogs/settings-dialog";

const Main = dynamic(() => import("./main"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      Loading Application...
    </div>
  ),
});

interface HeaderButtonProps {
  title: string;
  icon: ReactNode;
  asChild?: boolean;
  href?: string;
  onClick?: () => void;
}

function HeaderButton({ title, icon, asChild, href, onClick }: HeaderButtonProps) {
  const buttonContent = (
    <Button variant="ghost" size="icon" onClick={onClick} asChild={asChild}>
      {asChild ? (
        <Link href={href!} target="_blank">
          {icon}
        </Link>
      ) : (
        icon
      )}
    </Button>
  );

  return (
    <Tooltip title={title}>
      {buttonContent}
    </Tooltip>
  );
}

export default function HomePage() {
  return (
    <div className="flex h-screen w-screen justify-center overscroll-none">
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4">
        <Logo />
        <div className="flex items-center gap-1">
          <HeaderButton 
            title="Find us on GitHub"
            icon={<GithubOutlined className="h-[1.2rem] w-[1.2rem]" />}
            asChild
            href="https://github.com/modelcontextprotocol"
          />
          <MCPConfigButton />
          <ThemeToggle />
          <SettingsButton />
        </div>
      </header>
      <Main />
    </div>
  );
}

function MCPConfigButton() {
  const [open, setOpen] = useState(false);
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <HeaderButton
          title="Configure MCP Servers"
          icon={<Blocks className="h-[1.2rem] w-[1.2rem]" />}
        />
      </DialogTrigger>
      <MCPDialog />
    </Dialog>
  );
}

function SettingsButton() {
  const [open, setOpen] = useState(false);
  
  useEffect(() => {
    const handleCloseSettingsDialog = () => {
      setOpen(false);
    };
    
    window.addEventListener('close-settings-dialog', handleCloseSettingsDialog);
    
    return () => {
      window.removeEventListener('close-settings-dialog', handleCloseSettingsDialog);
    };
  }, []);
  
  return (
    <Suspense>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <HeaderButton
            title="Settings"
            icon={<Settings className="h-[1.2rem] w-[1.2rem]" />}
          />
        </DialogTrigger>
        <SettingsDialog />
      </Dialog>
    </Suspense>
  );
}
