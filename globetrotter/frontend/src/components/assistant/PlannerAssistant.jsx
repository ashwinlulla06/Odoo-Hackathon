import { useState } from 'react';
import { generateItineraryProposal, optimizeBudgetProposal } from '../../api/recommendations';
import ProposalPreview from './ProposalPreview';
import ProposalActions from './ProposalActions';

export default function PlannerAssistant({ trip, stops }) {
  const [proposal, setProposal] = useState(null); const [working, setWorking] = useState(false); const [notice, setNotice] = useState('');
  const makeProposal = async (kind) => { setWorking(true); setNotice(''); try { setProposal(kind === 'itinerary' ? await generateItineraryProposal({ trip, stops }) : await optimizeBudgetProposal({ trip, stops })); } finally { setWorking(false); } };
  return <aside className="assistant"><div><span className="eyebrow">PLANNER ASSISTANT</span><h3>A little help, when you want it.</h3><p className="muted">AI unavailable — using smart fallback.</p></div><div className="assistant-buttons"><button disabled={working} onClick={() => makeProposal('itinerary')}>✦ Generate itinerary</button><button disabled={working} onClick={() => makeProposal('budget')}>◌ Optimize budget</button></div><ProposalPreview proposal={proposal} /><ProposalActions proposal={proposal} onApply={() => setNotice('Notes applied to your planning session. Add any suggestion you like below.')} onDiscard={() => { setProposal(null); setNotice('Proposal discarded.'); }} />{notice && <p className="success">{notice}</p>}</aside>;
}
