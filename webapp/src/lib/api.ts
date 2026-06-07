const API = "/api/v1";

export type ToolResult = Record<string, unknown>;

export async function callVroidTool(
  operation: string,
  args: Record<string, unknown> = {},
): Promise<ToolResult> {
  const res = await fetch(`${API}/control/tool`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tool: "vroid_studio",
      arguments: { operation, ...args },
    }),
  });
  const data = (await res.json()) as ToolResult;
  if (!res.ok) {
    return { success: false, error: data.detail ?? res.statusText };
  }
  return data;
}

export async function fetchHealth(): Promise<ToolResult> {
  const res = await fetch("/health");
  return (await res.json()) as ToolResult;
}

export type OutputFile = { name: string; size_kb?: number };

export type ArchetypeRow = {
  id: string;
  display_name: string;
  category: string;
  template: string;
};

export function parseArchetypes(result: ToolResult): ArchetypeRow[] {
  const rows = result.archetypes;
  if (!Array.isArray(rows)) return [];
  return rows as ArchetypeRow[];
}
