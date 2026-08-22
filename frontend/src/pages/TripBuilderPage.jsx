import AgentPanel from "../components/assistant/AgentPanel";

export default function TripBuilderPage({ tripId, onProposalApplied }) {
  return (
    <main style={{ padding: 24 }}>
      <AgentPanel tripId={tripId} onApplied={onProposalApplied} />
    </main>
  );
}
