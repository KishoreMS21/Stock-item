import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Product, Sale } from "../types";

export default function SalesPage() {
  const { businessId } = useActiveBusiness();
  const qc = useQueryClient();

  const products = useQuery({
    queryKey: ["products", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<Product[]>("/api/products", { params: { business_id: businessId } })).data,
  });

  const sales = useQuery({
    queryKey: ["sales", businessId],
    enabled: !!businessId,
    queryFn: async () => (await api.get<Sale[]>("/api/sales", { params: { business_id: businessId } })).data,
  });

  const [customer, setCustomer] = useState("");
  const [productId, setProductId] = useState("");
  const [qty, setQty] = useState("1");
  const [price, setPrice] = useState("");

  const create = useMutation({
    mutationFn: async () =>
      api.post("/api/sales", {
        business_id: businessId,
        customer: customer || null,
        items: [
          {
            product_id: Number(productId),
            quantity: Number(qty),
            unit_price: Number(price),
          },
        ],
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sales", businessId] });
      qc.invalidateQueries({ queryKey: ["products", businessId] });
      setCustomer("");
      setQty("1");
      setPrice("");
    },
  });

  const onPick = (id: string) => {
    setProductId(id);
    const p = products.data?.find((x) => String(x.id) === id);
    if (p && !price) setPrice(String(p.unit_price));
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!businessId || !productId) return;
    create.mutate();
  };

  if (!businessId) return <p className="text-slate-500">Create a business first.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Sales</h1>

      <form onSubmit={submit} className="bg-white rounded-xl shadow p-4 grid grid-cols-4 gap-3">
        <label className="flex flex-col text-sm col-span-2">
          <span className="text-slate-600 mb-1">Product</span>
          <select
            value={productId}
            onChange={(e) => onPick(e.target.value)}
            required
            className="border rounded px-3 py-2"
          >
            <option value="">Select a product…</option>
            {(products.data ?? []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.sku} — {p.name} (stock: {p.stock_on_hand})
              </option>
            ))}
          </select>
        </label>
        <Input label="Quantity" type="number" value={qty} onChange={setQty} required />
        <Input label="Unit price" type="number" value={price} onChange={setPrice} required />
        <Input label="Customer (optional)" value={customer} onChange={setCustomer} />
        <div className="col-span-4 flex justify-end">
          <button
            disabled={create.isPending || !productId}
            className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {create.isPending ? "Saving…" : "Record sale"}
          </button>
        </div>
        {create.isError && (
          <p className="col-span-4 text-sm text-red-600">
            Sale failed — check stock availability.
          </p>
        )}
      </form>

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
            {(sales.data ?? []).length === 0 && (
              <tr>
                <td className="p-4 text-slate-500" colSpan={4}>No sales yet.</td>
              </tr>
            )}
            {(sales.data ?? []).map((s) => (
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
