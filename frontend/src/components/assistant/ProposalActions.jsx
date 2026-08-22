export default function ProposalActions({ status, applying, onApply }) {
  const isApplied = status === "applied";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 18 }}>
      <button
        type="button"
        onClick={onApply}
        disabled={applying || isApplied}
        style={{
          border: 0,
          borderRadius: 8,
          padding: "10px 16px",
          background: isApplied ? "#d1fae5" : "#2563eb",
          color: isApplied ? "#065f46" : "white",
          cursor: applying || isApplied ? "default" : "pointer",
          fontWeight: 700,
        }}
      >
        {isApplied ? "Added to itinerary" : applying ? "Applying…" : "Apply itinerary"}
      </button>
      {!isApplied && (
        <span style={{ color: "#64748b", fontSize: 13 }}>
          Your trip changes only after you apply this proposal.
        </span>
      )}
    </div>
  );
}
