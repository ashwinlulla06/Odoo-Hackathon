import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AppShell from "../components/AppShell";
import { deleteTrip, listTrips } from "../api/trips";

const imagery = ["https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&w=1000&q=80"];

export default function DashboardPage() {
  const [trips, setTrips] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const dayCount = useMemo(() => trips.reduce((total, trip) => total + tripDays(trip), 0), [trips]);
  async function refresh() { setLoading(true); setError(""); try { setTrips(await listTrips()); } catch (err) { setError(err.message || "We couldn't load your journeys."); } finally { setLoading(false); } }
  useEffect(() => { refresh(); }, []);
  async function remove(id) { if (!window.confirm("Delete this journey? This cannot be undone.")) return; const before = trips; setTrips(trips.filter((trip) => trip.id !== id)); try { await deleteTrip(id); } catch (err) { setTrips(before); window.alert(err.message || "Could not delete that journey."); } }
  return <AppShell wide><section className="hero"><div><p className="eyebrow">Your corner of the world</p><h1 className="display">Journeys worth<br />remembering.</h1><p className="lede">Sketch the route, collect the small moments, and leave room for the unexpected.</p><div className="stats"><Stat value={trips.length} label="journeys planned" /><Stat value={dayCount} label="days out there" /><Stat value={currency(trips.reduce((total, trip) => total + Number(trip.total_budget || 0), 0))} label="travel fund" /></div></div><Link className="primary" to="/trips/new">Start a new journey <span>→</span></Link></section>{error && <div className="alert">{error}<button onClick={refresh}>Try again</button></div>}{loading ? <div className="loading">Loading your journeys</div> : trips.length ? <section className="trip-grid">{trips.map((trip, index) => <TripCard key={trip.id} trip={trip} image={imagery[index % imagery.length]} onDelete={() => remove(trip.id)} />)}</section> : <section className="empty"><div className="empty-mark">✦</div><h2>The map is waiting.</h2><p>Your next favourite story starts with a pin.</p><Link to="/trips/new" className="primary">Plan my first trip</Link></section>}</AppShell>;
}
function Stat({ value, label }) { return <div><strong>{value}</strong><span>{label}</span></div>; }
function TripCard({ trip, image, onDelete }) { return <article className="trip-card"><div className="trip-image" style={{ backgroundImage: `url(${trip.cover_image_url || image})` }}><span className="trip-chip">{trip.is_public ? "Shared" : "In the works"}</span></div><div className="trip-content"><span className="trip-date">{date(trip.start_date)} — {date(trip.end_date)}</span><h2>{trip.name}</h2><p>{trip.description || "A new chapter, waiting for its first detail."}</p><div className="trip-footer"><span>{trip.total_budget ? currency(trip.total_budget) : "Budget to be set"}</span><div><Link to={`/trips/${trip.id}`}>Open ↗</Link><button onClick={onDelete}>Delete</button></div></div></div></article>; }
function date(value) { return value ? new Date(`${value}T12:00:00`).toLocaleDateString("en-IN", { day: "numeric", month: "short" }) : "TBD"; }
function currency(value) { return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0); }
function tripDays(trip) { return trip.start_date && trip.end_date ? Math.max(1, Math.round((new Date(trip.end_date) - new Date(trip.start_date)) / 86400000) + 1) : 0; }
