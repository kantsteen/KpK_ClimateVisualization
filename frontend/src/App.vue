<script setup>
import { onMounted, ref } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const mapContainer = ref(null)

onMounted(async () => {

  const response = await fetch('http://localhost:8000/api/co2?year=2023')
  const co2Data = await response.json()
  
  
  const co2ByCountry = {}
  for (const country of co2Data){
    co2ByCountry[country.code] = country.value
  }

  // Find the max value for scaling colors
  const maxCo2 = Math.max(...co2Data.map(d => d.value))

  const colorExpression = [
    'match',
    ['get', 'iso_3166_1_alpha_3']
  ]

  for (const country of co2Data) {
    const intensity = country.value / maxCo2
    const red = 255
    const green = Math.round(255 * (1 - intensity))
    const blue = Math.round(255 * (1 - intensity))
    const color = `rgb(${red}, ${green}, ${blue})`
    
    // Matches a country's code with it's calculated RGB color
    colorExpression.push(country.code, color)
  }
  // Default color for countries with no data
  colorExpression.push('#cccccc')

  // Create the map
  const map = new mapboxgl.Map({
    container: mapContainer.value,
    //projection: 'naturalEarth',
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
      
      const co2Value = co2ByCountry[isoCode]

      let html = `<strong>${countryName}</strong><br>`
      if (co2Value !== undefined){
        html += `CO2: ${co2Value.toFixed(2)} Mt`
      } else {
        html += `CO2: No data`
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
<div ref="mapContainer" class="map-container"></div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100vh;
}
</style>
