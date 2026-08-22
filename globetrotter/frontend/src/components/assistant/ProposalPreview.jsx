export default function ProposalPreview({ proposal }) {
  if (!proposal) return <div className="proposal-empty">Choose an option and a smart fallback proposal will appear here.</div>;
  return <div className="proposal"><span className="eyebrow">{proposal.title}</span><p>{proposal.message}</p><ul>{proposal.suggestions.map((suggestion) => <li key={suggestion}>{suggestion}</li>)}</ul></div>;
}
