document.addEventListener("DOMContentLoaded", function () {
  const ticketsCtx = document.getElementById('ticketsChart');
  if (!ticketsCtx) return;

  // Read data from dataset attributes
  const newTickets = ticketsCtx.dataset.new;
  const inProgress = ticketsCtx.dataset.inProgress;
  const resolved = ticketsCtx.dataset.resolved;
  const rejected = ticketsCtx.dataset.rejected;

  new Chart(ticketsCtx, {
    type: 'doughnut',
    data: {
      labels: ['New','In Progress','Resolved','Rejected'],
      datasets: [{
        data: [newTickets, inProgress, resolved, rejected],
        backgroundColor: ['#0d6efd','#0dcaf0','#198754','#dc3545']
      }]
    }
  });
});
