// TODO: wire to the real AI agent endpoint once it is available.
const pause = () => new Promise((resolve) => setTimeout(resolve, 450));

export async function generateItineraryProposal({ trip, stops }) {
  await pause();
  return {
    title: 'Smart fallback itinerary',
    message: `AI unavailable — using smart fallback for ${trip.name}.`,
    suggestions: stops.length
      ? stops.map((stop, index) => `Give section ${index + 1} one signature activity and an unhurried meal break.`)
      : ['Add a destination section first, then generate ideas for each day.'],
  };
}

export async function optimizeBudgetProposal({ trip }) {
  await pause();
  return {
    title: 'Smart fallback budget review',
    message: 'AI unavailable — using smart fallback. Review paid activities and keep one free experience per day.',
    suggestions: [`Current live budget: ${formatCurrency(trip.total_budget || 0)}.`],
  };
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
