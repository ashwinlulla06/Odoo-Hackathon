import { useState } from "react";
import { applyProposal, createProposal } from "../../api/recommendations";
import ProposalPreview from "./ProposalPreview";

const initialForm = {
  goal: "balanced",
  preferences: "culture, food",
  dailyBudget: "",
  notes: "",
  useLlm: true,
};

export default function AgentPanel({ tripId, onApplied }) {
  const [form, setForm] = useState(initialForm);
  const [proposal, setProposal] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value, checked, type } = event.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  async function handleGenerate(event) {
    event.preventDefault();
    if (!tripId) return;

    setGenerating(true);
    setError("");
    setProposal(null);

    try {
      const result = await createProposal(tripId, {
        goal: form.goal,
        preferences: form.preferences
          .split(",")
          .map((preference) => preference.trim())
          .filter(Boolean),
        daily_budget: form.dailyBudget === "" ? null : Number(form.dailyBudget),
        notes: form.notes.trim() || null,
        use_llm: form.useLlm,
      });
      setProposal(result);
    } catch (requestError) {
      setError(requestError.message || "Could not generate a proposal.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleApply() {
    if (!proposal?.id) return;

    setApplying(true);
    setError("");
    try {
      const result = await applyProposal(tripId, proposal.id);
      const responseFields = result && typeof result === "object" ? result : {};
      const updatedProposal = {
        ...proposal,
        ...responseFields,
        status: responseFields.status || "applied",
      };
      setProposal(updatedProposal);
      onApplied?.(updatedProposal);
    } catch (requestError) {
      setError(requestError.message || "Could not apply this proposal.");
    } finally {
      setApplying(false);
    }
  }

  return (
    <aside
      style={{
        maxWidth: 760,
        padding: 22,
        borderRadius: 14,
        border: "1px solid #e2e8f0",
        background: "white",
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.06)",
      }}
    >
      <h2 style={{ margin: 0 }}>AI itinerary assistant</h2>
      <p style={{ color: "#64748b" }}>
        Choose your travel style. You can review the suggestion before it changes your trip.
      </p>

      {!tripId ? (
        <p role="alert" style={{ color: "#b45309" }}>
          Save the trip and add at least one stop before generating an itinerary.
        </p>
      ) : (
        <form onSubmit={handleGenerate} style={{ display: "grid", gap: 14 }}>
          <label>
            Planning goal
            <select
              name="goal"
              value={form.goal}
              onChange={updateField}
              style={{ display: "block", width: "100%", marginTop: 5, padding: 9 }}
            >
              <option value="balanced">Balanced</option>
              <option value="budget">Budget friendly</option>
              <option value="relaxed">Relaxed</option>
              <option value="packed">See as much as possible</option>
            </select>
          </label>

          <label>
            Interests (comma-separated)
            <input
              name="preferences"
              value={form.preferences}
              onChange={updateField}
              placeholder="culture, food, nature"
              style={{ display: "block", boxSizing: "border-box", width: "100%", marginTop: 5, padding: 9 }}
            />
          </label>

          <label>
            Daily activity budget (optional)
            <input
              name="dailyBudget"
              type="number"
              min="0"
              step="0.01"
              value={form.dailyBudget}
              onChange={updateField}
              style={{ display: "block", boxSizing: "border-box", width: "100%", marginTop: 5, padding: 9 }}
            />
          </label>

          <label>
            Extra notes (optional)
            <textarea
              name="notes"
              value={form.notes}
              onChange={updateField}
              rows="3"
              placeholder="Prefer relaxed mornings"
              style={{ display: "block", boxSizing: "border-box", width: "100%", marginTop: 5, padding: 9 }}
            />
          </label>

          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input name="useLlm" type="checkbox" checked={form.useLlm} onChange={updateField} />
            Use Gemini when available
          </label>

          <button
            type="submit"
            disabled={generating}
            style={{
              justifySelf: "start",
              padding: "10px 16px",
              border: 0,
              borderRadius: 8,
              background: "#0f172a",
              color: "white",
              cursor: generating ? "default" : "pointer",
              fontWeight: 700,
            }}
          >
            {generating ? "Building your itinerary…" : "Generate itinerary"}
          </button>
        </form>
      )}

      {error && (
        <p role="alert" style={{ marginTop: 14, padding: 10, borderRadius: 8, color: "#b91c1c", background: "#fef2f2" }}>
          {error}
        </p>
      )}

      <ProposalPreview proposal={proposal} applying={applying} onApply={handleApply} />
    </aside>
  );
}
