<script setup>
import { onMounted, ref } from 'vue'
import TemperatureTimeline from './TemperatureTimeline.vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'


mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const mapContainer = ref(null)
const currentMetric = ref('co2') // mayb switch to co2_per_capita

let co2Data = []
let map = null

function buildColorExpression(data, metric) {
  const values = data.map(d => d[metric])
  const maxValue = Math.max(...values)

  const expression = ['match', ['get', 'iso_3166_1_alpha_3']]
  
  for (const country of data) {
    const value = country[metric]
    const intensity = value / maxValue
    const red = 255
    const green = Math.round(255 * (1- intensity))
    const blue = Math.round(255 * (1-intensity))
    expression.push(country.code, `rgb(${red}, ${green}, ${blue})`)
  }

  expression.push('#cccccc')
  return expression
}

function updateMapColors() {
  if (!map || !map.isStyleLoaded()) return

  const colorExpression = buildColorExpression(co2Data, currentMetric.value)
  map.setPaintProperty('country-fills', 'fill-color', colorExpression)
}

function toggleMetric(metric){
  currentMetric.value = metric
  updateMapColors()
}

onMounted(async () => {

  const response = await fetch('http://localhost:8000/api/co2?year=2023')
  co2Data = await response.json() // remove 'const'?
  
  
  const co2ByCountry = {}
  for (const country of co2Data) {
    co2ByCountry[country.code] = {
      co2: country.co2,
      co2_per_capita: country.co2_per_capita
    }
  }

  // Create the map
  map = new mapboxgl.Map({
    container: mapContainer.value,
    projection: 'naturalEarth',
    style: 'mapbox://styles/mapbox/standard',
    center: [10.4, 55.4],
    zoom: 3
  })

  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  })

  map.on('load', () => {
    map.addSource('countries', {
      type: 'vector',
      url: 'mapbox://mapbox.country-boundaries-v1'
    })

    const colorExpression = buildColorExpression(co2Data, currentMetric.value)

    map.addLayer({
      id: 'country-fills',
      type: 'fill',
      source: 'countries',
      'source-layer': 'country_boundaries',
      paint: {
        'fill-color': colorExpression,
        'fill-opacity': 0.7
      }
    })

    map.on('mousemove', 'country-fills', (e) => {
      map.getCanvas().style.cursor = 'pointer'

      const feature = e.features[0]
      const countryName = feature.properties.name_en 
      const isoCode = feature.properties.iso_3166_1_alpha_3 
      
      const countryData = co2ByCountry[isoCode]

      let html = `<strong>${countryName}</strong><br>`
      if (countryData) {
        html += `Total CO2: ${countryData.co2.toFixed(2)} Mt <br>`
        html += `CO2 per capita: ${countryData.co2_per_capita.toFixed(2)} t`
      } else {
        html += `No data`
      }

      popup.setLngLat(e.lngLat).setHTML(html).addTo(map)
    })

    map.on('mouseleave', 'country-fills', () => {
      map.getCanvas().style.cursor = ''
      popup.remove()
    })

  })
})
</script>

<template>
  <div class="controls">
    <button @click="toggleMetric('co2')":class="{ active: currentMetric === 'co2'}">
      Total CO2
    </button>
    <button @click="toggleMetric('co2_per_capita')":class="{active: currentMetric === 'co2_per_capita'}">
      CO2 Per Capita
    </button>
  </div>
<div ref="mapContainer" class="map-container"></div>

<div class="bottom-grid">
  <div class="card">
    <TemperatureTimeline />
  </div>

  <div class="card">
    <h3>More charts</h3>
    <p>(CO2 trend, sea level, osv.).</p>
  </div>
</div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100vh;
}

/* override mapheight to make grid visible */
.map-container {
  height: 65vh;
}

.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1;
  display: flex;
  gap: 5px;
}

.controls button {
  padding: 8px 16px;
  border: none;
  background: white;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2)
}

.controls button:hover {
  background: #f0f0f0;
}

.controls button.active {
  background: #3388ff;
  color: white;
}
/* Bottom grid layout */
.bottom-grid {
  height: 35vh;
  padding: 12px;
  background: #f6f7f9;
  display: grid;
  grid-template-columns: 2fr 1fr; /* wide chart + side box */
  gap: 12px;
  overflow: visible;
}

.card {
  background: white;
  border: 1px solid #e6e8ee;
  border-radius: 10px;
  padding: 12px;
}

.card h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.card p {
  margin: 0;
  font-size: 13px;
  color: #555;
}

/* responsive: stack cards on small screens */
@media (max-width: 900px) {
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}
</style>
