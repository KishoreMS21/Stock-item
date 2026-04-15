import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Expense } from "../types";

const CATEGORIES: Expense["category"][] = ["operations", "marketing", "inventory", "salaries", "other"];

export default function ExpensesPage() {
  const { businessId } = useActiveBusiness();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["expenses", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<Expense[]>("/api/expenses", { params: { business_id: businessId } })).data,
  });

  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState<Expense["category"]>("other");
  const [description, setDescription] = useState("");

  const create = useMutation({
    mutationFn: async () =>
      api.post("/api/expenses", {
        business_id: businessId,
        amount: Number(amount),
        category,
        description: description || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expenses", businessId] });
      setAmount("");
      setDescription("");
      setCategory("other");
    },
  });

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!businessId) return;
    create.mutate();
  };

  if (!businessId) return <p className="text-slate-500">Create a business first.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Expenses</h1>

      <form onSubmit={submit} className="bg-white rounded-xl shadow p-4 grid grid-cols-4 gap-3">
        <label className="flex flex-col text-sm">
          <span className="text-slate-600 mb-1">Amount</span>
          <input
            type="number"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            className="border rounded px-3 py-2"
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="text-slate-600 mb-1">Category</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as Expense["category"])}
            className="border rounded px-3 py-2"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>
        <label className="flex flex-col text-sm col-span-2">
          <span className="text-slate-600 mb-1">Description</span>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Facebook ads for April"
            className="border rounded px-3 py-2"
          />
        </label>
        <div className="col-span-4 flex justify-end">
          <button
            disabled={create.isPending}
            className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {create.isPending ? "Saving…" : "Add expense"}
          </button>
        </div>
      </form>

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
            {(data ?? []).length === 0 && (
              <tr>
                <td className="p-4 text-slate-500" colSpan={4}>No expenses yet.</td>
              </tr>
            )}
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
