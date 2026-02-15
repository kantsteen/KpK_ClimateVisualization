<script setup>
import { onMounted, ref } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const mapContainer = ref(null)
let map = null

onMounted(async () => {
  // Load the GeoJSON file from the public folder
  const response = await fetch('http://localhost:8000/api/flood-zones?scenario=SSP585medium&year=2110')
  const floodData = await response.json()

  console.log('Loaded flood data:', floodData.features.length, 'polygons')

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/standard',
    center: [12.0933, 55.6907],
    zoom: 13.8,
    maxBounds: [[11.60, 55.60], [12.15, 56.00]], // Roskilde Fjord bounds
    maxZoom: 16,
    minZoom: 3
  })

  map.on('load', () => {
    map.addSource('flood-zones', {
      type: 'geojson',
      data: floodData
    })

    map.addLayer({
      id: 'flood-fill',
      type: 'fill',
      source: 'flood-zones',
      paint: {
        'fill-color': '#0080ff',
        'fill-opacity': 0.4
      }
    })

    map.addLayer({
      id: 'flood-outline',
      type: 'line',
      source: 'flood-zones',
      paint: {
        'line-color': '#004080',
        'line-width': 2
      }
    })
  })

  // Tooltip
  const popup = new mapboxgl.Popup({
    closeOnClick: false,
    closeButton: false
  })

  map.on('mousemove', 'flood-fill', (e) => {
    map.getCanvas().style.cursor = 'pointer'

    const feature = e.features[0]
    const area = feature.properties.name
    const rise = feature.properties.sea_level_rise_m

    let html = `<strong>${area}</strong><br>Havstigning: ${rise} m`
    popup.setLngLat(e.lngLat).setHTML(html).addTo(map)
  })

  map.on('mouseleave', 'flood-fill', () => {
    map.getCanvas().style.cursor = ''
    popup.remove()
  })
})
</script>

<template>
  <div ref="mapContainer" class="sea-level-map"></div>
</template>

<style scoped>
.sea-level-map {
  width: 100%;
  height: 1000px;
}
</style>