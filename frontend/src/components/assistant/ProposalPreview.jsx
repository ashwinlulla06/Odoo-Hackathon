import ProposalActions from "./ProposalActions";

const money = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 2,
});

export default function ProposalPreview({ proposal, applying, onApply }) {
  if (!proposal) return null;

  const warnings = proposal.warnings || [];
  const items = proposal.items || [];

  return (
    <section
      aria-live="polite"
      style={{
        marginTop: 20,
        padding: 20,
        border: "1px solid #dbeafe",
        borderRadius: 12,
        background: "#f8fbff",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
        <div>
          <span
            style={{
              display: "inline-block",
              borderRadius: 999,
              padding: "4px 9px",
              background: proposal.source === "gemini" ? "#ede9fe" : "#e2e8f0",
              color: proposal.source === "gemini" ? "#5b21b6" : "#334155",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            {proposal.source === "gemini" ? "Gemini plan" : "Reliable fallback plan"}
          </span>
          <h3 style={{ margin: "10px 0 4px" }}>{proposal.summary || "Suggested itinerary"}</h3>
        </div>
        <div style={{ textAlign: "right", whiteSpace: "nowrap" }}>
          <div style={{ color: "#64748b", fontSize: 12 }}>Estimated activity cost</div>
          <strong>{money.format(Number(proposal.estimated_total || 0))}</strong>
        </div>
      </div>

      {warnings.length > 0 && (
        <div style={{ marginTop: 14, padding: 12, borderRadius: 8, background: "#fff7ed" }}>
          <strong>Things to note</strong>
          <ul style={{ margin: "6px 0 0", paddingLeft: 20 }}>
            {warnings.map((warning, index) => (
              <li key={`${warning}-${index}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ marginTop: 16, display: "grid", gap: 10 }}>
        {items.length === 0 && <p>No activities were available for this trip.</p>}
        {items.map((item, index) => (
          <article
            key={`${item.stop_id}-${item.activity_id}-${item.day_index}-${index}`}
            style={{ padding: 14, borderRadius: 8, background: "white", border: "1px solid #e2e8f0" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <strong>{item.name}</strong>
              <span>{money.format(Number(item.cost || 0))}</span>
            </div>
            <div style={{ marginTop: 4, color: "#475569", fontSize: 14 }}>
              Day {item.day_index} · {item.time_slot || "Time flexible"}
            </div>
            {item.notes && <p style={{ margin: "6px 0 0", color: "#64748b" }}>{item.notes}</p>}
          </article>
        ))}
      </div>

      <ProposalActions status={proposal.status} applying={applying} onApply={onApply} />
    </section>
  );
}
