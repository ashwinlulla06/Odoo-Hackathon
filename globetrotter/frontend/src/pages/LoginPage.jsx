import { useState } from 'react';

const signupFields = [['firstName', 'First Name'], ['lastName', 'Last Name'], ['username', 'Username'], ['email', 'Email'], ['phone', 'Phone'], ['city', 'City'], ['country', 'Country'], ['password', 'Password']];

export default function LoginPage({ onLogin }) {
  const [signup, setSignup] = useState(false);
  const [form, setForm] = useState({ email: '', password: '' });
  const submit = (event) => { event.preventDefault(); onLogin('user1'); };
  return <main className="auth-page"><section className="auth-aside"><span className="eyebrow">YOUR NEXT STORY</span><h1>Plan the trip<br />you’ll remember.</h1><p>Bring every city, day, and little detour into one beautifully simple plan.</p></section><section className="auth-card"><div><span className="eyebrow">GLOBETROTTER</span><h2>{signup ? 'Create your account' : 'Welcome back'}</h2><p>{signup ? 'Start planning your next great escape.' : 'Sign in to continue planning your next escape.'}</p></div><form onSubmit={submit} className="form-grid">{signup && signupFields.slice(0, -1).map(([key, label]) => <label key={key}>{label}<input required name={key} value={form[key] || ''} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}{!signup && <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>}<label>Password<input required type="password" value={form.password || ''} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label><button className="button wide" type="submit">{signup ? 'Create account' : 'Log in'}</button></form><p className="muted">{signup ? 'Already have an account?' : 'New to GlobeTrotter?'} <button className="inline-link" onClick={() => setSignup(!signup)}>{signup ? 'Log in' : 'Sign up'}</button></p><small>Demo mode — this securely stores a local test profile only.</small></section></main>;
}
