$(document).ready(function() {
  // Inicialização da DataTable
  const tabela = $('#tabelaDevolucoes').DataTable({
    pageLength: 10,
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
    }
  });

  // Filtro por status
  $('.filtro').on('click', function() {
    const status = $(this).data('status');
    if (status === "Todos") {
      tabela.column(4).search("").draw(); // limpa filtro
    } else {
      tabela.column(4).search(status).draw(); // aplica filtro
    }
  });

  // Gráfico de devoluções por motivo
  const ctx = document.getElementById('graficoDevolucoes').getContext('2d');
  const graficoDevolucoes = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,   // variável passada pelo Flask
      datasets: [{
        label: 'Quantidade',
        data: valores,  // variável passada pelo Flask
        backgroundColor: '#32bcae'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Motivos de Devolução' }
      }
    }
  });
});
