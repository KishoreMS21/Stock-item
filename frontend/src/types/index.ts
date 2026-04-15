export interface User {
  id: number;
  email: string;
  full_name: string | null;
}

export interface Business {
  id: number;
  name: string;
  currency: string;
}

export interface Product {
  id: number;
  business_id: number;
  sku: string;
  name: string;
  category: string | null;
  unit_cost: number;
  unit_price: number;
  stock_on_hand: number;
  reorder_point: number;
  min_stock: number;
}

export interface Expense {
  id: number;
  business_id: number;
  amount: number;
  category: "operations" | "marketing" | "inventory" | "salaries" | "other";
  description: string | null;
  incurred_at: string;
}

export interface SaleItem {
  product_id: number;
  quantity: number;
  unit_price: number;
}

export interface Sale {
  id: number;
  business_id: number;
  customer: string | null;
  total: number;
  sold_at: string;
  items: SaleItem[];
}

export interface SeriesPoint {
  date: string;
  value: number;
}

export interface KpiCard {
  label: string;
  value: number;
  delta_pct: number | null;
}

export interface Dashboard {
  revenue_30d: number;
  expenses_30d: number;
  profit_30d: number;
  profit_margin_pct: number;
  inventory_value: number;
  low_stock_count: number;
  revenue_series: SeriesPoint[];
  expense_series: SeriesPoint[];
  kpis: KpiCard[];
}
