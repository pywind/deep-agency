// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { zodResolver } from "@hookform/resolvers/zod";
import { Settings, Check, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Switch } from "~/components/ui/switch";
import { Button } from "~/components/ui/button";
import { Badge } from "~/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import type { SettingsState } from "~/core/store";

import type { Tab } from "./types";

const generalFormSchema = z.object({
  autoAcceptedPlan: z.boolean(),
  enableBackgroundInvestigation: z.boolean(),
  maxPlanIterations: z.number().min(1, {
    message: "Max plan iterations must be at least 1.",
  }),
  maxStepNum: z.number().min(1, {
    message: "Max step number must be at least 1.",
  }),
  maxSearchResults: z.number().min(1, {
    message: "Max search results must be at least 1.",
  }),
  add_to_agents: z.array(z.string()).min(1, {
    message: "Select at least one agent.",
  }),
});

const agentOptions = [
  { value: "coordinator", label: "Coordinator" },
  { value: "researcher", label: "Researcher" },
  { value: "coder", label: "Coder" },
];

export const GeneralTab: Tab = ({
  settings,
  onChange,
}: {
  settings: SettingsState;
  onChange: (changes: Partial<SettingsState>) => void;
}) => {
  const generalSettings = useMemo(() => settings.general, [settings]);
  const form = useForm<z.infer<typeof generalFormSchema>>({
    resolver: zodResolver(generalFormSchema, undefined, undefined),
    defaultValues: generalSettings,
    mode: "all",
    reValidateMode: "onBlur",
  });

  const currentSettings = form.watch();
  useEffect(() => {
    let hasChanges = false;
    for (const key in currentSettings) {
      if (
        currentSettings[key as keyof typeof currentSettings] !==
        settings.general[key as keyof SettingsState["general"]]
      ) {
        hasChanges = true;
        break;
      }
    }
    if (hasChanges) {
      onChange({ general: currentSettings });
    }
  }, [currentSettings, onChange, settings]);

  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-lg font-medium">General</h1>
      </header>
      <main>
        <Form {...form}>
          <form className="space-y-8">
            <FormField
              control={form.control}
              name="autoAcceptedPlan"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="flex items-center gap-2">
                      <Switch
                        id="autoAcceptedPlan"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                      <Label className="text-sm" htmlFor="autoAcceptedPlan">
                        Allow automatic acceptance of plans
                      </Label>
                    </div>
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="maxPlanIterations"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Max plan iterations</FormLabel>
                  <FormControl>
                    <Input
                      className="w-60"
                      type="number"
                      defaultValue={field.value}
                      min={1}
                      onChange={(event) =>
                        field.onChange(parseInt(event.target.value || "0"))
                      }
                    />
                  </FormControl>
                  <FormDescription>
                    Set to 1 for single-step planning. Set to 2 or more to
                    enable re-planning.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="maxStepNum"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Max steps of a research plan</FormLabel>
                  <FormControl>
                    <Input
                      className="w-60"
                      type="number"
                      defaultValue={field.value}
                      min={1}
                      onChange={(event) =>
                        field.onChange(parseInt(event.target.value || "0"))
                      }
                    />
                  </FormControl>
                  <FormDescription>
                    By default, each research plan has 3 steps.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="maxSearchResults"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Max search results</FormLabel>
                  <FormControl>
                    <Input
                      className="w-60"
                      type="number"
                      defaultValue={field.value}
                      min={1}
                      onChange={(event) =>
                        field.onChange(parseInt(event.target.value || "0"))
                      }
                    />
                  </FormControl>
                  <FormDescription>
                    By default, each search step has 3 results.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="add_to_agents"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Agents to use MCP servers</FormLabel>
                  <FormControl>
                    <DropdownMenu>
                      <div className="w-full border rounded-md relative">
                        <div className="flex flex-wrap gap-1 p-2 min-h-10">
                          {field.value.length > 0 ? (
                            field.value.map((value) => {
                              const option = agentOptions.find(opt => opt.value === value);
                              return (
                                <Badge 
                                  key={value} 
                                  className="bg-secondary text-secondary-foreground"
                                >
                                  {option?.label}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      // Don't allow removing the last agent
                                      if (field.value.length > 1) {
                                        field.onChange(field.value.filter(v => v !== value));
                                      }
                                    }}
                                    className="ml-1 rounded-full hover:bg-muted"
                                  >
                                    <X className="h-3 w-3" />
                                  </button>
                                </Badge>
                              );
                            })
                          ) : (
                            <span className="text-muted-foreground text-sm">Select agents...</span>
                          )}
                        </div>
                        <DropdownMenuTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="absolute top-0 right-0 h-full px-3 hover:bg-transparent"
                          >
                            <span className="opacity-50">▼</span>
                          </Button>
                        </DropdownMenuTrigger>
                      </div>
                      <DropdownMenuContent className="w-60">
                        {agentOptions.map((option) => (
                          <DropdownMenuCheckboxItem
                            key={option.value}
                            checked={field.value.includes(option.value)}
                            onCheckedChange={(checked) => {
                              const updatedValue = checked
                                ? [...field.value, option.value]
                                : field.value.filter((value) => value !== option.value);
                                
                              // Ensure at least one agent is selected
                              if (updatedValue.length > 0 || !checked) {
                                field.onChange(updatedValue);
                              }
                            }}
                          >
                            {option.label}
                          </DropdownMenuCheckboxItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </FormControl>
                  <FormDescription>
                    Select which agents to use MCP for tasks. At least one agent must be selected.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
      </main>
    </div>
  );
};
GeneralTab.displayName = "";
GeneralTab.icon = Settings;
