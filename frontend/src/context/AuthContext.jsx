import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../api/app";
import { setAccessToken } from "../api/client";
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem("gt-user")); } catch { return null; } });
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("gt-token")));
  const persist = useCallback(next => { setUser(next); next ? localStorage.setItem("gt-user", JSON.stringify(next)) : localStorage.removeItem("gt-user"); }, []);
  useEffect(() => {
    if (!localStorage.getItem("gt-token")) { setLoading(false); return; }
    authApi.me().then(persist).catch(() => { setAccessToken(null); persist(null); }).finally(() => setLoading(false));
    const out = () => persist(null); window.addEventListener("globetrotter:unauthorized", out); return () => window.removeEventListener("globetrotter:unauthorized", out);
  }, [persist]);
  const finish = async promise => { const result = await promise; setAccessToken(result.access_token); persist(result.user); return result.user; };
  const value = useMemo(() => ({ user, loading, login: v => finish(authApi.login(v)), signup: v => finish(authApi.signup(v)), logout: () => { setAccessToken(null); persist(null); }, updateUser: persist }), [user, loading, persist]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
