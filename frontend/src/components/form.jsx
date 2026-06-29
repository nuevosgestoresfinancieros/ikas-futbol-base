import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

export const Field = ({ label, value, onChange, type = "text", testid, placeholder, ...rest }) => (
  <div className="space-y-1.5">
    <Label className="text-xs font-bold text-slate-600">{label}</Label>
    <Input
      type={type}
      data-testid={testid}
      value={value ?? ""}
      placeholder={placeholder}
      onChange={(e) => onChange(type === "number" ? (e.target.value === "" ? "" : Number(e.target.value)) : e.target.value)}
      className="h-11"
      {...rest}
    />
  </div>
);

export const Area = ({ label, value, onChange, testid, rows = 3 }) => (
  <div className="space-y-1.5">
    <Label className="text-xs font-bold text-slate-600">{label}</Label>
    <Textarea data-testid={testid} value={value ?? ""} rows={rows} onChange={(e) => onChange(e.target.value)} />
  </div>
);

export const SelectField = ({ label, value, onChange, options, testid, placeholder }) => (
  <div className="space-y-1.5">
    <Label className="text-xs font-bold text-slate-600">{label}</Label>
    <Select value={value || ""} onValueChange={onChange}>
      <SelectTrigger className="h-11" data-testid={testid}>
        <SelectValue placeholder={placeholder || "—"} />
      </SelectTrigger>
      <SelectContent>
        {options.map((o) => (
          <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
);

export const SwitchField = ({ label, checked, onChange, testid }) => (
  <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
    <Label className="text-sm font-medium text-slate-700">{label}</Label>
    <Switch data-testid={testid} checked={!!checked} onCheckedChange={onChange} />
  </div>
);
