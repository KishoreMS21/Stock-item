import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const setToken = useAuth((s) => s.setToken);
  const navigate = useNavigate();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const { data } = await api.post("/api/auth/login", { email, password });
      setToken(data.access_token);
      navigate("/");
    } catch {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 bg-white p-8 rounded-xl shadow">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full border rounded px-3 py-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full border rounded px-3 py-2"
        />
        <button className="w-full bg-slate-900 text-white py-2 rounded">Sign in</button>
        <p className="text-sm text-slate-600">
          No account? <Link to="/register" className="text-slate-900 underline">Register</Link>
        </p>
      </form>
    </div>
  );
}
