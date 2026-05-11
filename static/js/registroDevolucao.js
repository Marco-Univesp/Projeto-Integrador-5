async function carregarMinhasDevolucoes() {
  // Mostra spinner enquanto carrega
  myReturnsContainer.innerHTML = '<div class="spinner"></div>';

  const cliente_id = localStorage.getItem("cliente_id");
  if (!cliente_id) {
    myReturnsContainer.innerHTML = "<p>Faça login para ver suas devoluções.</p>";
    return;
  }

  try {
    const res = await fetch(`/minhas_devolucoes/${cliente_id}`);
    if (!res.ok) throw new Error("Resposta inválida do servidor");

    const data = await res.json();

    if (!Array.isArray(data) || !data.length) {
      myReturnsContainer.innerHTML = "<p>Nenhuma devolução registrada.</p>";
      return;
    }

    myReturnsContainer.innerHTML = ""; // limpa spinner

    data.forEach(d => {
      const card = document.createElement("div");
      card.className = "return-item";
      card.dataset.id = d.id;
      card.dataset.imagens = JSON.stringify(d.images || []);

      card.innerHTML = `
        <p><strong>Pedido:</strong> ${d.order_number}</p>
        <p><strong>Motivo:</strong> ${d.reason}</p>
        <p><strong>Status:</strong> ${d.status}</p>
      `;

      card.addEventListener("click", () => abrirModalReturn(d.id, 0));
      myReturnsContainer.appendChild(card);
    });

  } catch (err) {
    console.error("Erro ao carregar devoluções:", err);
    myReturnsContainer.innerHTML = "<p style='color:orange;'>Não foi possível carregar suas devoluções agora.</p>";
  }
}
