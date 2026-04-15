import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Product } from "../types";

export default function ProductsPage() {
  const { businessId } = useActiveBusiness();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["products", businessId],
    enabled: !!businessId,
    queryFn: async () => {
      const { data } = await api.get<Product[]>("/api/products", { params: { business_id: businessId } });
      return data;
    },
  });

  const [form, setForm] = useState({
    sku: "",
    name: "",
    category: "",
    unit_cost: "",
    unit_price: "",
    stock_on_hand: "",
    reorder_point: "",
    min_stock: "",
  });

  const create = useMutation({
    mutationFn: async () =>
      api.post("/api/products", {
        business_id: businessId,
        sku: form.sku,
        name: form.name,
        category: form.category || null,
        unit_cost: Number(form.unit_cost) || 0,
        unit_price: Number(form.unit_price) || 0,
        stock_on_hand: Number(form.stock_on_hand) || 0,
        reorder_point: Number(form.reorder_point) || 0,
        min_stock: Number(form.min_stock) || 0,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["products", businessId] });
      setForm({ sku: "", name: "", category: "", unit_cost: "", unit_price: "", stock_on_hand: "", reorder_point: "", min_stock: "" });
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
      <h1 className="text-2xl font-semibold">Products</h1>

      <form onSubmit={submit} className="bg-white rounded-xl shadow p-4 grid grid-cols-4 gap-3">
        <Input label="SKU" value={form.sku} onChange={(v) => setForm({ ...form, sku: v })} required />
        <Input label="Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} required />
        <Input label="Category" value={form.category} onChange={(v) => setForm({ ...form, category: v })} />
        <Input label="Unit cost" type="number" value={form.unit_cost} onChange={(v) => setForm({ ...form, unit_cost: v })} />
        <Input label="Unit price" type="number" value={form.unit_price} onChange={(v) => setForm({ ...form, unit_price: v })} />
        <Input label="Stock on hand" type="number" value={form.stock_on_hand} onChange={(v) => setForm({ ...form, stock_on_hand: v })} />
        <Input label="Reorder point" type="number" value={form.reorder_point} onChange={(v) => setForm({ ...form, reorder_point: v })} />
        <Input label="Min stock" type="number" value={form.min_stock} onChange={(v) => setForm({ ...form, min_stock: v })} />
        <div className="col-span-4 flex justify-end">
          <button
            disabled={create.isPending}
            className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {create.isPending ? "Saving…" : "Add product"}
          </button>
        </div>
      </form>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="p-3">SKU</th>
              <th className="p-3">Name</th>
              <th className="p-3">Category</th>
              <th className="p-3">Stock</th>
              <th className="p-3">Reorder pt</th>
              <th className="p-3">Unit cost</th>
              <th className="p-3">Unit price</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).length === 0 && (
              <tr>
                <td className="p-4 text-slate-500" colSpan={7}>No products yet.</td>
              </tr>
            )}
            {(data ?? []).map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-3 font-mono">{p.sku}</td>
                <td className="p-3">{p.name}</td>
                <td className="p-3">{p.category ?? "—"}</td>
                <td className={`p-3 ${p.stock_on_hand <= p.reorder_point ? "text-red-600 font-semibold" : ""}`}>
                  {p.stock_on_hand}
                </td>
                <td className="p-3">{p.reorder_point}</td>
                <td className="p-3">{p.unit_cost}</td>
                <td className="p-3">{p.unit_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
  type = "text",
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="flex flex-col text-sm">
      <span className="text-slate-600 mb-1">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="border rounded px-3 py-2"
      />
    </label>
  );
}
