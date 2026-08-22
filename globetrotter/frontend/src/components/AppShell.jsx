import { Link, NavLink } from "react-router-dom";

export default function AppShell({ children, wide = false }) {
  return <div className="app-shell">
    <header className="topbar">
      <Link to="/trips" className="brand" aria-label="Globe Trotter home"><span className="brand-orb">✦</span><span>globe<em>trotter</em></span></Link>
      <nav><NavLink to="/trips" className={({ isActive }) => isActive ? "nav-active" : ""}>My journeys</NavLink><Link to="/trips/new" className="nav-new">Plan a trip <b>+</b></Link></nav>
      <span className="avatar">GT</span>
    </header>
    <main className={wide ? "page page-wide" : "page"}>{children}</main>
  </div>;
}
