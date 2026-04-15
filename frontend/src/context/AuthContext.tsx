import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  businessId: number | null;
  setToken: (t: string | null) => void;
  setBusinessId: (id: number | null) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      businessId: null,
      setToken: (t) => set({ token: t }),
      setBusinessId: (id) => set({ businessId: id }),
      logout: () => set({ token: null, businessId: null }),
    }),
    { name: "ies-auth" },
  ),
);
