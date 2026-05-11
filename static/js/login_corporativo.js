document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginCorporativoForm');
  const modal = document.getElementById('modalCorporativo');
  const okButton = document.getElementById('okModalBtnCorporativo');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    modal.style.display = 'flex';
  });

  okButton.addEventListener('click', function () {
    const redirectUrl = form.getAttribute('data-url');
    window.location.href = redirectUrl;
  });
});

function fecharModalCorporativo() {
  document.getElementById('modalCorporativo').style.display = 'none';
}
