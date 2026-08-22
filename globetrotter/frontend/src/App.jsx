import { useEffect, useState } from 'react';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CreateTripPage from './pages/CreateTripPage';
import TripBuilderPage from './pages/TripBuilderPage';
import ItineraryPage from './pages/ItineraryPage';
import PublicTripPage from './pages/PublicTripPage';

const routeFromPath = () => window.location.pathname || '/';

export default function App() {
  const [path, setPath] = useState(routeFromPath);
  const [ownerId, setOwnerId] = useState(() => localStorage.getItem('globetrotter_owner_id'));
  const navigate = (to) => { window.history.pushState({}, '', to); setPath(to); };

  useEffect(() => {
    const onPopState = () => setPath(routeFromPath());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const login = (id = 'user1') => { localStorage.setItem('globetrotter_owner_id', id); setOwnerId(id); navigate('/dashboard'); };
  const logout = () => { localStorage.removeItem('globetrotter_owner_id'); setOwnerId(null); navigate('/'); };
  const tripMatch = path.match(/^\/trips\/([^/]+)(?:\/(itinerary))?$/);
  const publicMatch = path.match(/^\/public\/([^/]+)$/);

  if (publicMatch) return <PublicTripPage tripId={publicMatch[1]} navigate={navigate} />;
  if (!ownerId) return <LoginPage onLogin={login} />;
  if (path === '/create') return <Shell navigate={navigate} logout={logout}><CreateTripPage ownerId={ownerId} navigate={navigate} /></Shell>;
  if (tripMatch) return <Shell navigate={navigate} logout={logout}>{tripMatch[2]
    ? <ItineraryPage tripId={tripMatch[1]} navigate={navigate} />
    : <TripBuilderPage tripId={tripMatch[1]} navigate={navigate} />}</Shell>;
  return <Shell navigate={navigate} logout={logout}><DashboardPage ownerId={ownerId} navigate={navigate} /></Shell>;
}

function Shell({ children, navigate, logout }) {
  return <div className="app-shell"><header className="topbar"><button className="brand" onClick={() => navigate('/dashboard')}>◉ GlobeTrotter</button><nav><button onClick={() => navigate('/dashboard')}>My trips</button><button className="button small" onClick={() => navigate('/create')}>Plan a trip</button><button className="text-button" onClick={logout}>Log out</button></nav></header>{children}</div>;
}
