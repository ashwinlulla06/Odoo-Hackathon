import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Bell, Compass, LayoutDashboard, LogOut, Menu, Moon, Plane, Plus, Route, Search, ShieldCheck, Sun, UserRound, Users, X } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const links = [["/", LayoutDashboard, "Overview"], ["/trips", Route, "My trips"], ["/discover", Compass, "Discover"], ["/community", Users, "Community"]];
export default function AppShell() {
  const [menu, setMenu] = useState(false); const [search, setSearch] = useState(""); const { user, logout } = useAuth(); const { theme, toggle } = useTheme(); const navigate = useNavigate();
  const submit = e => { e.preventDefault(); if (search.trim()) navigate(`/discover?q=${encodeURIComponent(search.trim())}`); };
  return <div className="app-shell">
    <aside className={`sidebar ${menu ? "open" : ""}`}>
      <div className="mobile-close"><button className="icon-button" onClick={() => setMenu(false)}><X /></button></div>
      <NavLink className="brand" to="/"><span className="brand-mark"><Plane size={20}/></span><span>GlobeTrotter</span></NavLink>
      <nav className="side-nav" aria-label="Primary navigation">{links.map(([to, Icon, label]) => <NavLink key={to} to={to} end={to === "/"} onClick={() => setMenu(false)}><Icon size={19}/>{label}</NavLink>)}</nav>
      <div className="sidebar-card"><span className="eyebrow">Travel journal</span><strong>Plan beautifully.</strong><small>Build, refine and share every journey.</small></div>
      <div className="nav-spacer" />
      {user?.is_admin && <NavLink className="admin-link" to="/admin"><ShieldCheck size={18}/> Admin</NavLink>}
      <NavLink className="profile-chip" to="/profile"><div className="avatar">{(user?.first_name?.[0] || "G") + (user?.last_name?.[0] || "T")}</div><div><strong>{user?.first_name || "Traveller"}</strong><span>{user?.email}</span></div><UserRound size={17}/></NavLink>
      <button className="logout-link" onClick={logout}><LogOut size={17}/> Sign out</button>
    </aside>
    {menu && <button className="scrim" aria-label="Close navigation" onClick={() => setMenu(false)} />}
    <main className="main-content">
      <header className="global-topbar">
        <button className="icon-button menu-button" onClick={() => setMenu(true)}><Menu /></button>
        <form className="global-search" onSubmit={submit}><Search size={18}/><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search cities, activities…" aria-label="Global search"/><kbd>Enter</kbd></form>
        <button className="icon-button" aria-label="Notifications"><Bell size={19}/></button>
        <button className="icon-button" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>{theme === "dark" ? <Sun size={19}/> : <Moon size={19}/>}</button>
        <button className="primary-button compact" onClick={() => navigate("/trips/new")}><Plus size={17}/> New trip</button>
      </header>
      <div className="page-content"><Outlet /></div>
    </main>
    <nav className="bottom-nav">{links.map(([to, Icon, label]) => <NavLink key={to} to={to} end={to === "/"}><Icon/><span>{label}</span></NavLink>)}</nav>
  </div>;
}

export function PageHead({ eyebrow, title, copy, actions }) { return <header className="page-head"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1>{copy && <p>{copy}</p>}</div>{actions && <div className="head-actions">{actions}</div>}</header>; }
export function EmptyState({ icon: Icon = Route, title, copy, action }) { return <div className="empty-state"><span className="empty-icon"><Icon/></span><h3>{title}</h3><p>{copy}</p>{action}</div>; }
export function ErrorState({ error }) { return <div className="notice error"><strong>We hit a travel snag.</strong><span>{error?.message || "Please try again."}</span></div>; }
export function LoadingCards() { return <div className="card-grid">{[1,2,3].map(x => <div className="skeleton-card" key={x}><span/><span/><span/></div>)}</div>; }
