import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import CreateTripPage from "./pages/CreateTripPage";
import TripBuilderPage from "./pages/TripBuilderPage";
import "./styles.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/trips" replace />} />
        <Route path="/trips" element={<DashboardPage />} />
        <Route path="/trips/new" element={<CreateTripPage />} />
        <Route path="/trips/:tripId" element={<TripBuilderPage />} />
        <Route path="*" element={<Navigate to="/trips" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
