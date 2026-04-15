import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const nav = [
  { to: "/", label: "Dashboard" },
  { to: "/products", label: "Products" },
  { to: "/sales", label: "Sales" },
  { to: "/expenses", label: "Expenses" },
  { to: "/insights", label: "AI Insights" },
];

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const logout = useAuth((s) => s.logout);

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-slate-900 text-slate-100 p-6 space-y-6">
        <div className="text-lg font-semibold">IES</div>
        <nav className="space-y-1">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className={`block px-3 py-2 rounded ${
                location.pathname === n.to ? "bg-slate-700" : "hover:bg-slate-800"
              }`}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <button
          onClick={() => {
            logout();
            navigate("/login");
          }}
          className="text-sm text-slate-400 hover:text-slate-100"
        >
          Logout
        </button>
      </aside>
      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}
