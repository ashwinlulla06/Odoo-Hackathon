import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import "./styles.css";

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30000, retry: 1 } } });

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter><QueryClientProvider client={queryClient}><ThemeProvider><AuthProvider><App /></AuthProvider></ThemeProvider></QueryClientProvider></BrowserRouter>
  </StrictMode>,
);
