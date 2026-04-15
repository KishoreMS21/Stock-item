import { useQuery } from "@tanstack/react-query";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Dashboard } from "../types";

export default function DashboardPage() {
  const { businessId } = useActiveBusiness();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard", businessId],
    enabled: !!businessId,
    queryFn: async () => {
      const { data } = await api.get<Dashboard>("/api/dashboard", { params: { business_id: businessId } });
      return data;
    },
  });

  if (!businessId) return <NoBusiness />;
  if (isLoading || !data) return <p className="text-slate-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Business Health</h1>
      <div className="grid grid-cols-4 gap-4">
        {data.kpis.map((k) => (
          <div key={k.label} className="bg-white rounded-xl p-4 shadow">
            <div className="text-xs text-slate-500">{k.label}</div>
            <div className="text-2xl font-semibold">{k.value.toLocaleString()}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Chart title="Revenue (30d)" series={data.revenue_series} />
        <Chart title="Expenses (30d)" series={data.expense_series} />
      </div>
      <div className="bg-white rounded-xl p-4 shadow">
        <div className="text-sm text-slate-500">Low-stock items</div>
        <div className="text-3xl font-semibold">{data.low_stock_count}</div>
      </div>
    </div>
  );
}

function Chart({ title, series }: { title: string; series: { date: string; value: number }[] }) {
  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="text-sm font-medium mb-2">{title}</div>
      <div style={{ width: "100%", height: 200 }}>
        <ResponsiveContainer>
          <LineChart data={series}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#0f172a" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function NoBusiness() {
  return <p className="text-slate-500">Create a business first.</p>;
}
