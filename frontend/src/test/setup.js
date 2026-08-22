import "@testing-library/jest-dom/vitest";
import React from "react";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
globalThis.React = React;
afterEach(() => { cleanup(); localStorage.clear(); });
Object.defineProperty(window, "matchMedia", { writable: true, value: query => ({ matches:false, media:query, onchange:null, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){}, dispatchEvent(){return false;} }) });
