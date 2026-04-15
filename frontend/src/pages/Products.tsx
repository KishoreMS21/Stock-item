import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { useActiveBusiness } from "../hooks/useBusiness";
import type { Product } from "../types";

export default function ProductsPage() {
  const { businessId } = useActiveBusiness();
  const { data } = useQuery({
    queryKey: ["products", businessId],
    enabled: !!businessId,
    queryFn: async () => {
      const { data } = await api.get<Product[]>("/api/products", { params: { business_id: businessId } });
      return data;
    },
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Products</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="p-3">SKU</th>
              <th className="p-3">Name</th>
              <th className="p-3">Stock</th>
              <th className="p-3">Reorder pt</th>
              <th className="p-3">Unit price</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-3 font-mono">{p.sku}</td>
                <td className="p-3">{p.name}</td>
                <td className={`p-3 ${p.stock_on_hand <= p.reorder_point ? "text-red-600 font-semibold" : ""}`}>
                  {p.stock_on_hand}
                </td>
                <td className="p-3">{p.reorder_point}</td>
                <td className="p-3">{p.unit_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
