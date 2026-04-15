import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";

interface Alert {
  id: number;
  kind: string;
  severity: "info" | "warning" | "critical";
  message: string;
}

interface Recommendation {
  id: number;
  title: string;
  rationale: string;
  action: string | null;
}

interface StockForecast {
  product_id: number;
  product_name: string;
  current_stock: number;
  days_until_stockout: number | null;
  reorder_qty_suggested: number;
}

const SEV_COLOR: Record<Alert["severity"], string> = {
  info: "bg-slate-100 text-slate-800",
  warning: "bg-amber-100 text-amber-900",
  critical: "bg-red-100 text-red-900",
};

export default function InsightsPage() {
  const { businessId } = useActiveBusiness();
  const qc = useQueryClient();

  const alerts = useQuery({
    queryKey: ["ai-alerts", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<Alert[]>("/api/ai/alerts", { params: { business_id: businessId } })).data,
  });

  const recs = useQuery({
    queryKey: ["ai-recs", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<Recommendation[]>("/api/ai/recommendations", { params: { business_id: businessId } })).data,
  });

  const stock = useQuery({
    queryKey: ["ai-stock", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<StockForecast[]>("/api/ai/forecast/stock", { params: { business_id: businessId } })).data,
  });

  const ack = useMutation({
    mutationFn: async (id: number) => api.post(`/api/ai/alerts/${id}/ack`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ai-alerts", businessId] }),
  });

  if (!businessId) return <p className="text-slate-500">Create a business first.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">AI Insights</h1>

      <Section title="Risk Alerts">
        <div className="space-y-2">
          {(alerts.data ?? []).length === 0 && <p className="text-slate-500 text-sm">No open alerts.</p>}
          {(alerts.data ?? []).map((a) => (
            <div key={a.id} className={`flex justify-between items-start p-3 rounded ${SEV_COLOR[a.severity]}`}>
              <div>
                <div className="text-xs uppercase font-semibold">{a.kind.replace("_", " ")}</div>
                <div>{a.message}</div>
              </div>
              <button onClick={() => ack.mutate(a.id)} className="text-xs underline">Acknowledge</button>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Recommendations">
        <div className="grid grid-cols-2 gap-3">
          {(recs.data ?? []).length === 0 && <p className="text-slate-500 text-sm col-span-2">No recommendations yet.</p>}
          {(recs.data ?? []).map((r) => (
            <div key={r.id} className="bg-white rounded-xl p-4 shadow">
              <div className="font-semibold">{r.title}</div>
              <div className="text-sm text-slate-600 mt-1">{r.rationale}</div>
              {r.action && <div className="text-sm mt-2 text-slate-900">{r.action}</div>}
            </div>
          ))}
        </div>
      </Section>

      <Section title="Stock Forecast">
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-100 text-left">
              <tr>
                <th className="p-3">Product</th>
                <th className="p-3">Stock</th>
                <th className="p-3">Days until stockout</th>
                <th className="p-3">Suggested reorder</th>
              </tr>
            </thead>
            <tbody>
              {(stock.data ?? []).map((s) => (
                <tr key={s.product_id} className="border-t">
                  <td className="p-3">{s.product_name}</td>
                  <td className="p-3">{s.current_stock}</td>
                  <td className={`p-3 ${s.days_until_stockout !== null && s.days_until_stockout <= 7 ? "text-red-600 font-semibold" : ""}`}>
                    {s.days_until_stockout ?? "—"}
                  </td>
                  <td className="p-3">{s.reorder_qty_suggested}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Advisor Chatbot">
        <Chatbot businessId={businessId} />
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function Chatbot({ businessId }: { businessId: number }) {
  const [q, setQ] = useState("");
  const [log, setLog] = useState<{ role: "user" | "ai"; text: string }[]>([]);

  const mut = useMutation({
    mutationFn: async (question: string) =>
      (await api.post<{ answer: string }>("/api/ai/chat", { question }, { params: { business_id: businessId } })).data,
    onSuccess: (data) => setLog((l) => [...l, { role: "ai", text: data.answer }]),
  });

  const send = (e: FormEvent) => {
    e.preventDefault();
    if (!q.trim()) return;
    setLog((l) => [...l, { role: "user", text: q }]);
    mut.mutate(q);
    setQ("");
  };

  return (
    <div className="bg-white rounded-xl shadow p-4 space-y-3">
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {log.length === 0 && (
          <p className="text-slate-500 text-sm">
            Try: "Should I reorder my top product now?" or "Why is my profit decreasing?"
          </p>
        )}
        {log.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <span className={`inline-block px-3 py-2 rounded ${m.role === "user" ? "bg-slate-900 text-white" : "bg-slate-100"}`}>
              {m.text}
            </span>
          </div>
        ))}
      </div>
      <form onSubmit={send} className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask your AI advisor…"
          className="flex-1 border rounded px-3 py-2"
        />
        <button disabled={mut.isPending} className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50">
          {mut.isPending ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
