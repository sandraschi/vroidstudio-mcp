import { useCallback, useEffect, useMemo, useState } from "react";
import {
  FolderOpen,
  Loader2,
  Monitor,
  Play,
  RefreshCw,
  Save,
  Sparkles,
  Upload,
} from "lucide-react";
import {
  ArchetypeRow,
  callVroidTool,
  fetchHealth,
  parseArchetypes,
  OutputFile,
  ToolResult,
} from "../lib/api";

function ResultPanel({ data }: { data: ToolResult | null }) {
  if (!data) return null;
  const ok = data.success !== false;
  return (
    <pre
      className={`text-xs whitespace-pre-wrap p-4 rounded-xl overflow-auto max-h-80 border ${
        ok ? "text-emerald-300/90 bg-emerald-950/20 border-emerald-900/40" : "text-red-300/90 bg-red-950/20 border-red-900/40"
      }`}
    >
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

export default function VroidPage() {
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<ToolResult | null>(null);
  const [result, setResult] = useState<ToolResult | null>(null);
  const [archetypes, setArchetypes] = useState<ArchetypeRow[]>([]);
  const [templates, setTemplates] = useState<string[]>([]);

  const [archetypeId, setArchetypeId] = useState("quick_gal");
  const [templateName, setTemplateName] = useState("open_and_export");
  const [outputName, setOutputName] = useState("anime_gal.vrm");
  const [projectPath, setProjectPath] = useState("");
  const [savePath, setSavePath] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [resume, setResume] = useState(false);
  const [outputs, setOutputs] = useState<OutputFile[]>([]);

  const categories = useMemo(() => {
    const set = new Set(archetypes.map((a) => a.category));
    return Array.from(set).sort();
  }, [archetypes]);

  const refreshCatalog = useCallback(async () => {
    const [arch, tpl, st] = await Promise.all([
      callVroidTool("list_archetypes"),
      callVroidTool("list_templates"),
      callVroidTool("status"),
    ]);
    setArchetypes(parseArchetypes(arch));
    if (Array.isArray(tpl.templates)) setTemplates(tpl.templates as string[]);
    setResult(st);
    const out = await callVroidTool("list_outputs");
    if (Array.isArray(out.files)) setOutputs(out.files as OutputFile[]);
  }, []);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
    refreshCatalog();
  }, [refreshCatalog]);

  const run = useCallback(
    async (operation: string, extra: Record<string, unknown> = {}) => {
      setLoading(true);
      setResult(null);
      try {
        const data = await callVroidTool(operation, {
          output_name: outputName,
          archetype_id: archetypeId,
          template_name: templateName,
          project_path: projectPath,
          save_path: savePath,
          session_id: sessionId,
          resume,
          pick_sample: true,
          ...extra,
        });
        setResult(data);
        if (typeof data.session_id === "string" && data.session_id) {
          setSessionId(data.session_id);
        }
        if (operation === "list_outputs" && Array.isArray(data.files)) {
          setOutputs(data.files as OutputFile[]);
        }
      } catch (err) {
        setResult({ success: false, error: String(err) });
      } finally {
        setLoading(false);
      }
    },
    [outputName, archetypeId, templateName, projectPath, savePath, sessionId, resume],
  );

  const backendOk = health?.status === "ok";

  return (
    <div className="min-h-screen bg-[#0c0c0f] text-slate-100">
      <div className="max-w-5xl mx-auto p-6 space-y-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold flex items-center gap-2 text-white">
              <Monitor className="text-violet-400" size={26} />
              VRoid Studio MCP
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-xl">
              Shortcut-first GUI automation. Requires pywinauto-mcp on :10789 and VRoid Studio locally.
            </p>
          </div>
          <div
            className={`text-xs px-3 py-1.5 rounded-full border ${
              backendOk
                ? "border-emerald-800 text-emerald-400 bg-emerald-950/30"
                : "border-amber-800 text-amber-400 bg-amber-950/30"
            }`}
          >
            Backend {backendOk ? "online" : "check :10881"}
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Archetypes", value: archetypes.length || "—" },
            { label: "Templates", value: templates.length || "—" },
            { label: "Uptime", value: health?.uptime_s != null ? `${health.uptime_s}s` : "—" },
            { label: "Session", value: sessionId || "none" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <div className="text-xs uppercase tracking-wide text-slate-500">{s.label}</div>
              <div className="text-lg font-medium mt-1 truncate">{String(s.value)}</div>
            </div>
          ))}
        </section>

        <section className="rounded-xl border border-white/10 bg-white/[0.02] p-5 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-violet-300 flex items-center gap-2">
            <Sparkles size={16} /> Archetypes (55)
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-slate-400 block">
              Archetype
              <select
                value={archetypeId}
                onChange={(e) => setArchetypeId(e.target.value)}
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white"
              >
                {archetypes.length === 0 && <option value={archetypeId}>{archetypeId}</option>}
                {categories.map((cat) => (
                  <optgroup key={cat} label={cat}>
                    {archetypes
                      .filter((a) => a.category === cat)
                      .map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.display_name}
                        </option>
                      ))}
                  </optgroup>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-400 block">
              Export VRM filename
              <input
                value={outputName}
                onChange={(e) => setOutputName(e.target.value)}
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2"
              />
            </label>
          </div>
          <div className="flex flex-wrap gap-2">
            <ActionBtn loading={loading} onClick={() => run("run_archetype")} icon={Play} label="Run archetype" primary />
            <ActionBtn loading={loading} onClick={() => run("quick_gal_export")} icon={Upload} label="Quick gal" />
            <ActionBtn loading={loading} onClick={refreshCatalog} icon={RefreshCw} label="Refresh catalog" />
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-white/[0.02] p-5 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-violet-300 flex items-center gap-2">
            <FolderOpen size={16} /> .vroid projects
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-slate-400 block sm:col-span-2">
              Project path (.vroid)
              <input
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
                placeholder="D:\avatars\mychar.vroid"
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 font-mono text-sm"
              />
            </label>
            <label className="text-sm text-slate-400 block sm:col-span-2">
              Save as path (.vroid)
              <input
                value={savePath}
                onChange={(e) => setSavePath(e.target.value)}
                placeholder="D:\avatars\mychar_copy.vroid"
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 font-mono text-sm"
              />
            </label>
            <label className="text-sm text-slate-400 block">
              Template
              <select
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2"
              >
                {templates.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-400 block">
              Session id (resume)
              <input
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 font-mono text-sm"
              />
            </label>
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-400">
            <input type="checkbox" checked={resume} onChange={(e) => setResume(e.target.checked)} />
            Resume from last good step
          </label>
          <div className="flex flex-wrap gap-2">
            <ActionBtn loading={loading} onClick={() => run("open_project")} icon={FolderOpen} label="Open project" />
            <ActionBtn loading={loading} onClick={() => run("save_project")} icon={Save} label="Save" />
            <ActionBtn loading={loading} onClick={() => run("save_project_as")} icon={Save} label="Save as" />
            <ActionBtn loading={loading} onClick={() => run("open_and_export")} icon={Upload} label="Open + export VRM" />
            <ActionBtn loading={loading} onClick={() => run("run_template")} icon={Play} label="Run template" />
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-white/[0.02] p-5 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Tools</h2>
          <div className="flex flex-wrap gap-2">
            {[
              ["status", "Status"],
              ["launch", "Launch VRoid"],
              ["focus", "Focus"],
              ["screenshot", "Screenshot"],
              ["list_outputs", "List outputs"],
              ["list_shortcuts", "Shortcuts"],
              ["session_status", "Session status"],
            ].map(([op, label]) => (
              <ActionBtn key={op} loading={loading} onClick={() => run(op)} label={label} />
            ))}
          </div>
        </section>

        {outputs.length > 0 && (
          <section className="rounded-xl border border-white/10 bg-white/[0.02] p-5 space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Recent exports</h2>
            <ul className="text-sm space-y-1 font-mono text-slate-300">
              {outputs.map((file) => (
                <li key={file.name} className="flex items-center justify-between gap-4">
                  <a
                    href={`/api/v1/download/${encodeURIComponent(file.name)}`}
                    className="text-violet-400 hover:underline"
                    download
                  >
                    {file.name}
                  </a>
                  {file.size_kb != null && (
                    <span className="text-slate-500 text-xs">{file.size_kb} KB</span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        <ResultPanel data={result} />
      </div>
    </div>
  );
}

function ActionBtn({
  loading,
  onClick,
  label,
  icon: Icon,
  primary,
}: {
  loading: boolean;
  onClick: () => void;
  label: string;
  icon?: typeof Play;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      disabled={loading}
      onClick={onClick}
      className={`px-3 py-2 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 transition-colors ${
        primary
          ? "bg-violet-600 hover:bg-violet-500 text-white"
          : "bg-white/10 hover:bg-white/15 text-slate-200"
      }`}
    >
      {loading ? <Loader2 className="animate-spin" size={15} /> : Icon ? <Icon size={15} /> : null}
      {label}
    </button>
  );
}
