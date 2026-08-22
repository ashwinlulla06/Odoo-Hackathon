import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { lazy, Suspense } from "react";
import { useAuth } from "./context/AuthContext";
import AppShell from "./components/AppShell";

const named = (loader, name) => lazy(() => loader().then(module => ({ default: module[name] })));
const authPages=()=>import("./pages/AuthPages"), tripPages=()=>import("./pages/TripPages"), explorePages=()=>import("./pages/ExplorePages"), accountPages=()=>import("./pages/ProfileAdminPages");
const LoginPage=named(authPages,"LoginPage"), SignupPage=named(authPages,"SignupPage");
const DashboardPage=lazy(()=>import("./pages/DashboardPage"));
const TripsPage=named(tripPages,"TripsPage"), CreateTripPage=named(tripPages,"CreateTripPage"), TripBuilderPage=named(tripPages,"TripBuilderPage"), ItineraryPage=named(tripPages,"ItineraryPage"), BudgetPage=named(tripPages,"BudgetPage");
const DiscoverPage=named(explorePages,"DiscoverPage"), CommunityPage=named(explorePages,"CommunityPage"), PublicTripPage=named(explorePages,"PublicTripPage");
const ProfilePage=named(accountPages,"ProfilePage"), AdminPage=named(accountPages,"AdminPage");

function Protected() {
  const { user, loading } = useAuth(); const location = useLocation();
  if (loading) return <div className="page-loader"><span className="spinner" />Opening your travel journal…</div>;
  return user ? <Outlet /> : <Navigate to="/login" replace state={{ from: location.pathname }} />;
}
function AdminOnly() { const { user } = useAuth(); return user?.is_admin ? <AdminPage /> : <Navigate to="/" replace />; }
export default function App() { return <Suspense fallback={<div className="page-loader"><span className="spinner"/>Preparing your journey…</div>}><Routes>
  <Route path="/login" element={<LoginPage />} /><Route path="/signup" element={<SignupPage />} /><Route path="/share/:slug" element={<PublicTripPage />} />
  <Route element={<Protected />}><Route element={<AppShell />}>
    <Route index element={<DashboardPage />} /><Route path="trips" element={<TripsPage />} /><Route path="trips/new" element={<CreateTripPage />} />
    <Route path="trips/:id/build" element={<TripBuilderPage />} /><Route path="trips/:id/itinerary" element={<ItineraryPage />} /><Route path="trips/:id/budget" element={<BudgetPage />} />
    <Route path="discover" element={<DiscoverPage />} /><Route path="community" element={<CommunityPage />} /><Route path="profile" element={<ProfilePage />} /><Route path="admin" element={<AdminOnly />} />
  </Route></Route><Route path="*" element={<Navigate to="/" replace />} />
</Routes></Suspense>; }
