<script setup>
import { onMounted, ref } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const mapContainer = ref(null)
const currentMetric = ref('co2') // mayb switch to co2_per_capita
const currentYear = ref(2024)
const minYear = 1950
const maxYear = 2024

let allData = []
let co2ByCountryByYear = {}
let map = null
let globalMaxCo2 = 0
let globalMaxCo2PerCapita = 0

function updateFeatureStates(year, metric) {
  if (!map || !map.isStyleLoaded()) return

  const yearData = co2ByCountryByYear[year]
  if (!yearData) return

  const maxValue = metric === 'co2' ? globalMaxCo2 : globalMaxCo2PerCapita

  for (const [code, data] of Object.entries(yearData)) {
    const value = data[metric]
    const intensity = value != null ? value / maxValue : 0

    map.setFeatureState(
      { source: 'countries', sourceLayer: 'country_boundaries', id: code },
      { intensity }
    )
  }
}

function toggleMetric(metric) {
  currentMetric.value = metric
  updateFeatureStates(currentYear.value, currentMetric.value)
}

function onYearChange(event) {
  currentYear.value = parseInt(event.target.value)
  updateFeatureStates(currentYear.value, currentMetric.value)
}

onMounted(async () => {

  const response = await fetch('http://localhost:8000/api/co2/all')
  allData = await response.json()


  for (const row of allData) {
    if (!co2ByCountryByYear[row.year]) {
      co2ByCountryByYear[row.year] = {}
    }
    co2ByCountryByYear[row.year][row.code] = {
      co2: row.co2,
      co2_per_capita: row.co2_per_capita
    }
  }

  globalMaxCo2 = allData.reduce((max, row) => {
    if (row.co2 != null && row.co2 > max) return row.co2
    return max
  }, 0)

  globalMaxCo2PerCapita = allData.reduce((max, row) => {
    if (row.co2_per_capita != null && row.co2_per_capita > max) return row.co2_per_capita
    return max
  }, 0)


  console.log('Global max CO2:', globalMaxCo2)
  console.log('Global max CO2 per capita:', globalMaxCo2PerCapita)
  console.log('Total rows:', allData.length)
  console.log('First 3 rows:', allData.slice(0, 3))
  console.log('Sample co2 values:', allData.slice(0, 10).map(row => row.co2))
  console.log('Sample co2_per_capita values:', allData.slice(0, 10).map(row => row.co2_per_capita))

  // Create the map
  map = new mapboxgl.Map({
    container: mapContainer.value,
    projection: 'naturalEarth',
    style: 'mapbox://styles/mapbox/light-v11',
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
      url: 'mapbox://mapbox.country-boundaries-v1',
      promoteId: { 'country_boundaries': 'iso_3166_1_alpha_3' }
    })

    map.addLayer({
      id: 'country-fills',
      type: 'fill',
      source: 'countries',
      'source-layer': 'country_boundaries',
      paint: {
        'fill-color': [
          'case',
          ['!=', ['feature-state', 'intensity'], null],
          [
            'interpolate',
            ['linear'],
            ['feature-state', 'intensity'],
            0, 'rgb(255, 255, 255)',
            1, 'rgb(255, 0, 0)'
          ],
          '#cccccc'
        ],
        'fill-opacity': 0.7,
        'fill-color-transition': { duration: 300, delay: 0 }
      }, 
    }, 'country-labels')

    // Set initial feature states
    updateFeatureStates(currentYear.value, currentMetric.value)

    map.on('mousemove', 'country-fills', (e) => {
      map.getCanvas().style.cursor = 'pointer'

      const feature = e.features[0]
      const countryName = feature.properties.name_en
      const isoCode = feature.properties.iso_3166_1_alpha_3

      const yearData = co2ByCountryByYear[currentYear.value]
      const countryData = yearData ? yearData[isoCode] : null

      let html = `<strong>${countryName}</strong> (${currentYear.value})<br>`
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
    <div class="metric-button">
      <button @click="toggleMetric('co2')" :class="{ active: currentMetric === 'co2' }">
        Total CO2
      </button>
      <button @click="toggleMetric('co2_per_capita')" :class="{ active: currentMetric === 'co2_per_capita' }">
        CO2 Per Capita
      </button>
    </div>

    <div class="year-slider">
      <label>Year: {{ currentYear }}</label>
      <input type="range" :min="minYear" :max="maxYear" :value="currentYear" @input="onYearChange">
    </div>
  </div>

  <div ref="mapContainer" class="map-container"></div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100vh;
}

.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1;
  display: flex;
  gap: 10px;
  flex-direction: column;
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.metric-buttons {
  padding: 8px 16px;
  border: none;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px;
}

.metric-buttons button:hover {
  background: #e0e0e0;
}

.metric-buttons button.active {
  background: #3388ff;
  color: white;
}

.year-slider {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.year-slider label {
  font-size: 14px;
  font-weight: bold;
}

.year-slider input {
  width: 200px;
  cursor: pointer;
}
</style>
