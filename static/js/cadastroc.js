document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("cadastroForm");
  const modal = document.getElementById("modal");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const res = await fetch("/cadastroc", {
        method: "POST",
        body: formData
      });

      const result = await res.json();
      console.log("Resposta do servidor:", result);

      if (result.status === "success") {
        modal.style.display = "flex";
      } else {
        alert(result.message);
      }
    } catch (err) {
      console.error("Erro no cadastro:", err);
      alert("Erro ao conectar com o servidor.");
    }
  });
});

// Funções da modal
function fecharModal() {
  document.getElementById("modal").style.display = "none";
}

function confirmarEnvio() {
  fecharModal();
  // Redireciona para login após cadastro
  window.location.href = "/loginc";
}
