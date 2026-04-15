import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Expense } from "../types";

export default function ExpensesPage() {
  const { businessId } = useActiveBusiness();
  const { data } = useQuery({
    queryKey: ["expenses", businessId],
    enabled: !!businessId,
    queryFn: async () => {
      const { data } = await api.get<Expense[]>("/api/expenses", { params: { business_id: businessId } });
      return data;
    },
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Expenses</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="p-3">Date</th>
              <th className="p-3">Category</th>
              <th className="p-3">Description</th>
              <th className="p-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((x) => (
              <tr key={x.id} className="border-t">
                <td className="p-3">{new Date(x.incurred_at).toLocaleDateString()}</td>
                <td className="p-3 capitalize">{x.category}</td>
                <td className="p-3">{x.description ?? "—"}</td>
                <td className="p-3 text-right font-mono">{x.amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
