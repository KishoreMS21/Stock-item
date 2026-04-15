import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Sale } from "../types";

export default function SalesPage() {
  const { businessId } = useActiveBusiness();
  const { data } = useQuery({
    queryKey: ["sales", businessId],
    enabled: !!businessId,
    queryFn: async () => {
      const { data } = await api.get<Sale[]>("/api/sales", { params: { business_id: businessId } });
      return data;
    },
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Sales</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="p-3">Date</th>
              <th className="p-3">Customer</th>
              <th className="p-3">Items</th>
              <th className="p-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((s) => (
              <tr key={s.id} className="border-t">
                <td className="p-3">{new Date(s.sold_at).toLocaleDateString()}</td>
                <td className="p-3">{s.customer ?? "—"}</td>
                <td className="p-3">{s.items.length}</td>
                <td className="p-3 text-right font-mono">{s.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
