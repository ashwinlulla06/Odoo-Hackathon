import { useQuery } from "@tanstack/react-query";
import { format, differenceInCalendarDays } from "date-fns";
import { ArrowRight, CalendarDays, Check, Compass, MapPin, Plus, Route, Sparkles, WalletCards } from "lucide-react";
import { Link } from "react-router-dom";
import { tripsApi, catalogApi } from "../api/app";
import { useAuth } from "../context/AuthContext";
import { EmptyState, ErrorState, LoadingCards, PageHead } from "../components/AppShell";

export default function DashboardPage() {
  const { user } = useAuth(); const trips = useQuery({ queryKey:["trips"], queryFn:tripsApi.list }); const cities = useQuery({ queryKey:["cities", "popular"], queryFn:()=>catalogApi.cities({page_size:3}) });
  const upcoming = trips.data?.filter(t => new Date(t.end_date) >= new Date()).sort((a,b)=>a.start_date.localeCompare(b.start_date)) || []; const lead = upcoming[0];
  const leadDetails = useQuery({queryKey:["trip",lead?.id],queryFn:()=>tripsApi.get(lead.id),enabled:!!lead});
  const heroImage = lead?.cover_image_url || leadDetails.data?.stops?.[0]?.city?.image_url;
  const steps = [{done:!!trips.data?.length,label:"Create your first trip"},{done:!!lead?.destination_count,label:"Add a destination"},{done:(lead?.total_budget||0)>0,label:"Build your itinerary"},{done:!!lead?.is_public,label:"Share your journey"}];
  return <>
    <PageHead eyebrow={format(new Date(), "EEEE, d MMMM")} title={`Good ${new Date().getHours()<12?"morning":new Date().getHours()<18?"afternoon":"evening"}, ${user?.first_name || "traveller"}.`} copy="Where will your curiosity take you next?" actions={<Link className="primary-button" to="/trips/new"><Plus/>Plan a new trip</Link>}/>
    {trips.isError && <ErrorState error={trips.error}/>} {trips.isLoading ? <LoadingCards/> : lead ? <section className="hero-card" style={heroImage?{backgroundImage:`linear-gradient(100deg,rgba(7,33,37,.94),rgba(7,33,37,.58)),url(${heroImage})`}:undefined}>
      <div className="hero-copy"><span className="status-pill"><span/> Next adventure</span><h2>{lead.name}</h2><p>{lead.description || "Your thoughtfully planned journey is taking shape."}</p><div className="trip-facts"><span><CalendarDays/> {format(new Date(lead.start_date+"T00:00:00"),"d MMM")} – {format(new Date(lead.end_date+"T00:00:00"),"d MMM yyyy")}</span><span><MapPin/> {lead.destination_count || 0} stops</span><span><WalletCards/> ₹{Number(lead.total_budget||0).toLocaleString("en-IN",{maximumFractionDigits:0})} planned</span></div><div className="button-row"><Link className="primary-button" to={`/trips/${lead.id}/build`}>Continue planning <ArrowRight/></Link><Link className="text-button" to={`/trips/${lead.id}/itinerary`}>View itinerary</Link></div></div>
      <div className="countdown"><small>Adventure begins in</small><strong>{Math.max(0,differenceInCalendarDays(new Date(lead.start_date+"T00:00:00"),new Date()))}</strong><span>days</span></div>
    </section> : <EmptyState icon={Route} title="Your first journey starts here" copy="Create a trip, choose your stops and let Gemini shape a day-by-day plan." action={<Link className="primary-button" to="/trips/new"><Plus/>Create a trip</Link>}/>}
    <div className="dashboard-grid">
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">Onboarding</span><h2>Build a trip that feels yours</h2></div><span className="score-ring">{steps.filter(s=>s.done).length}/4</span></div><div className="checklist">{steps.map((s,i)=><div className={s.done?"done":""} key={s.label}><span>{s.done?<Check/>:i+1}</span><p><strong>{s.label}</strong><small>{["Give the adventure a name and dates","Create the route across cities","Add activities yourself or ask Gemini","Publish when it feels just right"][i]}</small></p></div>)}</div></section>
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">Explore</span><h2>Destinations calling</h2></div><Link to="/discover">See all</Link></div>{cities.isLoading?<LoadingCards/>:<div className="mini-destinations">{cities.data?.items?.map(c=><Link to={`/discover?q=${c.name}`} key={c.id} className="mini-destination"><div style={{backgroundImage:`url(${c.image_url})`}}/><span><strong>{c.name}</strong><small>{c.country}</small></span><Compass/></Link>)}</div>}</section>
    </div>
    <section className="ai-banner"><span className="ai-orb"><Sparkles/></span><div><span className="eyebrow">Gemini travel companion</span><h2>A thoughtful itinerary, built around you.</h2><p>It only uses verified activities from our catalog—and asks you before changing anything.</p></div><Link className="secondary-button" to={lead?`/trips/${lead.id}/build`:"/trips/new"}>Plan with AI <ArrowRight/></Link></section>
  </>;
}

