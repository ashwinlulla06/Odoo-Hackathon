import { apiRequest } from "./client";

function proposalPath(tripId, proposalId = "") {
  const base = `/api/v1/trips/${encodeURIComponent(tripId)}/planner/proposals`;
  return proposalId ? `${base}/${encodeURIComponent(proposalId)}` : base;
}

export function createProposal(tripId, input) {
  return apiRequest(proposalPath(tripId), {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getProposal(tripId, proposalId) {
  return apiRequest(proposalPath(tripId, proposalId));
}

export function applyProposal(tripId, proposalId) {
  return apiRequest(`${proposalPath(tripId, proposalId)}/apply`, {
    method: "POST",
  });
}
