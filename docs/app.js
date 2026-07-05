var markers = [{"name": "Tarragon Cafe", "lat": 37.7713117, "lng": -122.4301572, "index": 0}, {"name": "Cato's Ale House", "lat": 37.824968, "lng": -122.254583, "index": 1}, {"name": "Pang", "lat": 37.7637699, "lng": -122.466458, "index": 2}, {"name": "Pizzeria Violetta", "lat": 37.8301052, "lng": -122.247712, "index": 3}, {"name": "Imperial Garden Seafood Restaurant", "lat": 37.7284618, "lng": -122.4042479, "index": 4}, {"name": "Sushi Easy", "lat": 37.7558203, "lng": -122.4208567, "index": 5}, {"name": "Dumpling Home", "lat": 37.775869, "lng": -122.4226658, "index": 6}, {"name": "My Father\u2019s Kitchen", "lat": 37.7850458, "lng": -122.439978, "index": 7}, {"name": "Yuanbao Jiaozi", "lat": 37.7635358, "lng": -122.4806711, "index": 8}, {"name": "Ebisu", "lat": 37.7644479, "lng": -122.4665197, "index": 9}, {"name": "Bella Trattoria", "lat": 37.7813547, "lng": -122.4609009, "index": 10}, {"name": "Harbin Hot Springs", "lat": 38.7864047, "lng": -122.6518822, "index": 11}];
var map = L.map('map').setView([37.77, -122.45], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19
}).addTo(map);

var defaultStyle = { radius: 8,  fillColor: '#b8883a', color: '#fff', weight: 2,   opacity: 1, fillOpacity: 0.9 };
var activeStyle  = { radius: 12, fillColor: '#e0aa50', color: '#fff', weight: 2.5, opacity: 1, fillOpacity: 1   };

var cardsByIndex = {};
document.querySelectorAll('.card').forEach(function(card) {
  cardsByIndex[parseInt(card.dataset.index)] = card;
});

var circlesByIndex = {};
markers.forEach(function(m) {
  var card = cardsByIndex[m.index];
  var circle = L.circleMarker([m.lat, m.lng], Object.assign({}, defaultStyle))
    .addTo(map)
    .bindPopup('<b>' + m.name + '</b>');

  circle.on('mouseover', function() {
    circle.setStyle(activeStyle).openPopup();
    if (card) { card.classList.add('highlighted'); card.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
  });
  circle.on('mouseout', function() {
    circle.setStyle(defaultStyle);
    if (card) card.classList.remove('highlighted');
  });

  circlesByIndex[m.index] = circle;
});

document.querySelectorAll('.card').forEach(function(card) {
  var circle = circlesByIndex[parseInt(card.dataset.index)];
  if (!circle) return;
  card.addEventListener('mouseenter', function() { circle.setStyle(activeStyle); circle.openPopup(); map.panTo(circle.getLatLng()); });
  card.addEventListener('mouseleave', function() { circle.setStyle(defaultStyle); circle.closePopup(); });
});
