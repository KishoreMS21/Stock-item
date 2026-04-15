import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import type { Business } from "../types";

export function useBusinesses() {
  return useQuery({
    queryKey: ["businesses"],
    queryFn: async () => {
      const { data } = await api.get<Business[]>("/api/businesses");
      return data;
    },
  });
}

export function useActiveBusiness() {
  const { data } = useBusinesses();
  const businessId = useAuth((s) => s.businessId);
  const setBusinessId = useAuth((s) => s.setBusinessId);

  useEffect(() => {
    if (!businessId && data && data.length > 0) setBusinessId(data[0].id);
  }, [businessId, data, setBusinessId]);

  return { businessId, businesses: data ?? [] };
}
