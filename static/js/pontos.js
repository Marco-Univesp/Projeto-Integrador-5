// Lista de pontos de coleta
const pontos = [
  { nome: "Coleta Centro", lat: -23.55052, lng: -46.633308 },
  { nome: "Coleta Zona Norte", lat: -23.4800, lng: -46.6200 },
  { nome: "Coleta Zona Sul", lat: -23.6800, lng: -46.6200 }
];

// Função para obter localização do usuário
function getUserLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showNearestPoint, showError);
  } else {
    document.getElementById("resultado").innerText = "Geolocalização não suportada.";
  }
}

// Fórmula de Haversine para calcular distância
function calcularDistancia(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI/180) * Math.cos(lat2 * Math.PI/180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Mostra ponto mais próximo e rota automaticamente
function showNearestPoint(position) {
  const userLat = position.coords.latitude;
  const userLng = position.coords.longitude;

  let menorDistancia = Infinity;
  let pontoMaisProximo = null;

  pontos.forEach(p => {
    const dist = calcularDistancia(userLat, userLng, p.lat, p.lng);
    if (dist < menorDistancia) {
      menorDistancia = dist;
      pontoMaisProximo = p;
    }
  });

  // URL para abrir no Google Maps
  const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${pontoMaisProximo.lat},${pontoMaisProximo.lng}&travelmode=driving`;

  // Exibe resultado com link para Google Maps
  document.getElementById("resultado").innerHTML =
    `O ponto mais próximo é: ${pontoMaisProximo.nome} (${menorDistancia.toFixed(2)} km) 
     <a href="${googleMapsUrl}" target="_blank" style="margin-left:10px; padding:6px 12px; background:#004aad; color:white; text-decoration:none; border-radius:5px;">
       Abrir no Google Maps
     </a>`;

  // Inicializa o mapa
  const map = L.map('map').setView([userLat, userLng], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  // Marcador do usuário
  L.marker([userLat, userLng]).addTo(map).bindPopup("Você está aqui").openPopup();

  // Marcadores dos pontos
  pontos.forEach(p => {
    L.marker([p.lat, p.lng]).addTo(map).bindPopup(p.nome);
  });

  // Cria a rota automaticamente sem painel de instruções
  L.Routing.control({
    waypoints: [
      L.latLng(userLat, userLng),
      L.latLng(pontoMaisProximo.lat, pontoMaisProximo.lng)
    ],
    router: L.Routing.osrmv1({
      serviceUrl: 'https://router.project-osrm.org/route/v1'
    }),
    language: 'pt-BR',
    routeWhileDragging: false,
    show: false // 🔹 oculta o painel de instruções
  }).addTo(map);
}

// Mensagem de erro
function showError(error) {
  document.getElementById("resultado").innerText = "Não foi possível obter sua localização.";
}

// Executa ao carregar a página
getUserLocation();