<script setup>
import { onMounted, ref } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const mapContainer = ref(null)

onMounted(async () => {
  // Step 1: Fetch CO2 data from our backend
  const response = await fetch('http://localhost:8000/api/co2?year=2023&metric=total')
  const co2Data = await response.json()
  
  console.log('Received data:', co2Data.length, 'countries')
  console.log('First 3:', co2Data.slice(0, 3))

  // Step 2: Find the max value (for scaling colors)
  const maxCo2 = Math.max(...co2Data.map(d => d.value))
  console.log('Max CO2:', maxCo2)

  // Step 3: Build the color expression
  // Format: ['match', ['get', 'iso_code'], 'DNK', '#ff0000', 'DEU', '#00ff00', ... , '#cccccc']
  const colorExpression = [
    'match',
    ['get', 'iso_3166_1_alpha_3']
  ]

  for (const country of co2Data) {
    // Calculate color intensity (0 = white, 1 = dark red)
    const intensity = country.value / maxCo2
    const red = 255
    const green = Math.round(255 * (1 - intensity))
    const blue = Math.round(255 * (1 - intensity))
    const color = `rgb(${red}, ${green}, ${blue})`
    
    colorExpression.push(country.code, color)
  }

  // Default color for countries with no data
  colorExpression.push('#cccccc')

  // Step 4: Create the map
  const map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/light-v11',
    center: [10.4, 55.4],
    zoom: 3
  })

  map.on('load', () => {
    map.addSource('countries', {
      type: 'vector',
      url: 'mapbox://mapbox.country-boundaries-v1'
    })

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
  })
})
</script>

<template>
<div ref="mapContainer" class="map-container"></div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100vh;
}
</style>
