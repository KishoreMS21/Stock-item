import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const setToken = useAuth((s) => s.setToken);
  const navigate = useNavigate();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const { data } = await api.post("/api/auth/register", {
        email,
        password,
        full_name: fullName,
      });
      setToken(data.access_token);
      navigate("/");
    } catch {
      setError("Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 bg-white p-8 rounded-xl shadow">
        <h1 className="text-2xl font-semibold">Create account</h1>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <input
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
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
        <button className="w-full bg-slate-900 text-white py-2 rounded">Register</button>
        <p className="text-sm text-slate-600">
          Have an account? <Link to="/login" className="text-slate-900 underline">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
