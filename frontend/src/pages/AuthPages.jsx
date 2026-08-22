import { useState } from "react";
import { Eye, EyeOff, MapPin, Plane, Sparkles } from "lucide-react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AuthLayout({ mode }) {
  const signup = mode === "signup"; const { user, login, signup: register } = useAuth(); const navigate = useNavigate(); const location = useLocation();
  const [show, setShow] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", password: "", city: "", country: "" });
  if (user) return <Navigate to="/" replace />;
  const submit = async e => { e.preventDefault(); setBusy(true); setError(""); try { await (signup ? register(form) : login({ email: form.email, password: form.password })); navigate(location.state?.from || "/", { replace: true }); } catch (err) { setError(err.message); } finally { setBusy(false); } };
  return <div className="auth-page">
    <section className="auth-story"><div className="auth-brand"><Plane/>GlobeTrotter</div><div className="auth-quote"><span className="passport-stamp"><MapPin/> JOURNEY 2026</span><h1>Plan beautifully.<br/><em>Travel freely.</em></h1><p>Turn a wish list into a thoughtful, day-by-day journey—with a little help from your AI travel companion.</p><div className="auth-proof"><Sparkles/> Smart plans. Honest budgets. Unforgettable days.</div></div></section>
    <section className="auth-panel"><form className="auth-card" onSubmit={submit}><span className="eyebrow">{signup ? "Start your travel journal" : "Welcome back"}</span><h2>{signup ? "Create your account" : "Continue your journey"}</h2><p>{signup ? "One minute from your next adventure." : "Your itineraries are waiting for you."}</p>
      {signup && <div className="form-row"><label>First name<input required value={form.first_name} onChange={e=>setForm({...form,first_name:e.target.value})}/></label><label>Last name<input required value={form.last_name} onChange={e=>setForm({...form,last_name:e.target.value})}/></label></div>}
      <label>Email address<input required type="email" autoComplete="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} placeholder="you@example.com"/></label>
      <label>Password<div className="password-field"><input required minLength={8} type={show?"text":"password"} autoComplete={signup?"new-password":"current-password"} value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/><button type="button" onClick={()=>setShow(!show)} aria-label="Toggle password visibility">{show?<EyeOff/>:<Eye/>}</button></div></label>
      {signup && <div className="form-row"><label>Home city<input value={form.city} onChange={e=>setForm({...form,city:e.target.value})}/></label><label>Country<input value={form.country} onChange={e=>setForm({...form,country:e.target.value})}/></label></div>}
      {error && <div className="field-error">{error}</div>}<button className="primary-button wide" disabled={busy}>{busy ? "Preparing…" : signup ? "Create account" : "Sign in"}</button>
      <p className="auth-switch">{signup ? "Already a traveller? " : "New to GlobeTrotter? "}<Link to={signup?"/login":"/signup"}>{signup?"Sign in":"Create an account"}</Link></p>
    </form></section>
  </div>;
}
export const LoginPage = () => <AuthLayout mode="login"/>;
export const SignupPage = () => <AuthLayout mode="signup"/>;
