import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider, useTheme } from "./context/ThemeContext";

function providers(route="/login") {
  const client=new QueryClient({defaultOptions:{queries:{retry:false}}});
  return render(<MemoryRouter initialEntries={[route]}><QueryClientProvider client={client}><ThemeProvider><AuthProvider><App/></AuthProvider></ThemeProvider></QueryClientProvider></MemoryRouter>);
}
test("shows the real login screen for a guest", async () => {
  providers();
  expect(await screen.findByRole("heading",{name:/continue your journey/i})).toBeInTheDocument();
  expect(screen.getByRole("button",{name:/sign in/i})).toBeInTheDocument();
});
function ThemeProbe(){const {theme,toggle}=useTheme();return <button onClick={toggle}>{theme}</button>}
test("persists the dark theme choice", () => {
  render(<ThemeProvider><ThemeProbe/></ThemeProvider>);
  fireEvent.click(screen.getByRole("button",{name:"light"}));
  expect(localStorage.getItem("gt-theme")).toBe("dark");
  expect(document.documentElement.dataset.theme).toBe("dark");
});
