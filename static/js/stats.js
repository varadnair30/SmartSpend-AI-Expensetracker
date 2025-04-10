document.addEventListener("DOMContentLoaded", function() {
  const ctx = document.getElementById('myChart').getContext('2d');

  const myChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Red', 'Blue', 'Yellow'],
      datasets: [{
        label: 'Expenses by Category',
        data: [12, 19, 3],
        backgroundColor: ['red', 'blue', 'yellow'],
        borderColor: ['darkred', 'darkblue', 'darkyellow'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true
    }
  });
});
