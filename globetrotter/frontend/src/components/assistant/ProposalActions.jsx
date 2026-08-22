export default function ProposalActions({ proposal, onApply, onDiscard }) {
  if (!proposal) return null;
  return <div className="proposal-actions"><button className="button small" onClick={onApply}>Apply notes</button><button className="text-button" onClick={onDiscard}>Discard</button></div>;
}
