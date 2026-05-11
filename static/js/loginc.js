document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const res = await fetch("/loginc", {
        method: "POST",
        body: formData
      });

      const result = await res.json();
      console.log("Resposta do servidor:", result);

      if (result && result.status === "success") {
        // ✅ Redireciona automaticamente para o menu do cliente
        window.location.href = "/menu_cliente";
      } else {
        // ⚠️ Mostra mensagem de erro no login
        document.getElementById("loginErro").textContent =
          result.message || "Erro no login.";
      }
    } catch (err) {
      console.error("Erro no login:", err);
      document.getElementById("loginErro").textContent =
        "Erro ao conectar com o servidor.";
    }
  });
});
