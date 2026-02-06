<template>
  <div class="comparison-chart">
    <div class="header">
      <h3>CO2 Emissions by Country</h3>
      <div class="sub">Compare emissions trends across countries (1950–2024)</div>
    </div>

    <CountrySelector
      :countries="countryList"
      v-model="internalSelectedCountries"
      :colorMap="colorMap"
    />

    <div ref="chartContainer" class="chart"></div>

    <div v-if="selectedCountries.length === 0" class="empty-state">
      Select countries above to compare their CO2 emissions
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'
import CountrySelector from './CountrySelector.vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  selectedCountries: {
    type: Array,
    required: true
  },
  metric: {
    type: String,
    default: 'co2'
  }
})

const emit = defineEmits(['update:selectedCountries'])

const chartContainer = ref(null)
let svg = null
let tooltip = null

const internalSelectedCountries = computed({
  get: () => props.selectedCountries,
  set: (value) => emit('update:selectedCountries', value)
})

const countryList = computed(() => {
  const seen = new Map()
  for (const row of props.data) {
    if (!seen.has(row.code)) {
      seen.set(row.code, row.country)
    }
  }
  return Array.from(seen.entries())
    .map(([code, name]) => ({ code, name }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

const colorMap = computed(() => {
  const colors = d3.schemeTableau10
  const map = {}
  for (const country of countryList.value) {
    const hash = hashCode(country.code)
    map[country.code] = colors[Math.abs(hash) % colors.length]
  }
  return map
})

function hashCode(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return hash
}

function getCountryName(code) {
  const country = countryList.value.find(c => c.code === code)
  return country ? country.name : code
}

function drawChart() {
  if (!chartContainer.value || props.selectedCountries.length === 0) {
    if (svg) {
      d3.select(chartContainer.value).select('svg').remove()
      svg = null
    }
    return
  }

  const margin = { top: 20, right: 120, bottom: 40, left: 70 }
  const width = 900
  const height = 300

  d3.select(chartContainer.value).select('svg').remove()
  d3.select(chartContainer.value).select('.tooltip').remove()

  svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .style('width', '100%')
    .style('height', 'auto')

  const innerW = width - margin.left - margin.right
  const innerH = height - margin.top - margin.bottom

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const filteredData = props.data.filter(d => props.selectedCountries.includes(d.code))

  const dataByCountry = d3.group(filteredData, d => d.code)

  const x = d3.scaleLinear()
    .domain([1950, 2024])
    .range([0, innerW])

  const yMax = d3.max(filteredData, d => d[props.metric]) || 1
  const y = d3.scaleLinear()
    .domain([0, yMax * 1.1])
    .nice()
    .range([innerH, 0])

  const yGrid = d3.axisLeft(y).tickSize(-innerW).tickFormat(() => '')
  g.append('g')
    .attr('class', 'grid')
    .call(yGrid)
    .call(gr => gr.selectAll('.tick line').attr('opacity', 0.15))
    .call(gr => gr.select('.domain').remove())

  g.append('g')
    .attr('transform', `translate(0,${innerH})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(10))

  g.append('g')
    .call(d3.axisLeft(y).ticks(6).tickFormat(d => {
      if (d >= 1000) return `${d / 1000}k`
      return d
    }))

  g.append('text')
    .attr('x', innerW / 2)
    .attr('y', innerH + 35)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .text('Year')

  const yLabel = props.metric === 'co2' ? 'CO₂ Emissions (Mt)' : 'CO₂ per Capita (t)'
  g.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -innerH / 2)
    .attr('y', -55)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .text(yLabel)

  const line = d3.line()
    .defined(d => d[props.metric] != null)
    .x(d => x(d.year))
    .y(d => y(d[props.metric]))

  for (const [code, countryData] of dataByCountry) {
    const sortedData = countryData.sort((a, b) => a.year - b.year)
    const isWorld = code === 'OWID_WRL'

    g.append('path')
      .datum(sortedData)
      .attr('fill', 'none')
      .attr('stroke', colorMap.value[code] || '#999')
      .attr('stroke-width', isWorld ? 2.5 : 2)
      .attr('stroke-dasharray', isWorld ? '6 3' : null)
      .attr('d', line)
      .attr('class', 'line')
      .attr('data-code', code)
  }

  const legend = svg.append('g')
    .attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`)

  props.selectedCountries.forEach((code, i) => {
    const isWorld = code === 'OWID_WRL'
    const legendRow = legend.append('g')
      .attr('transform', `translate(0, ${i * 18})`)

    legendRow.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 6)
      .attr('y2', 6)
      .attr('stroke', colorMap.value[code] || '#999')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', isWorld ? '4 2' : null)

    legendRow.append('text')
      .attr('x', 25)
      .attr('y', 10)
      .style('font-size', '11px')
      .text(getCountryName(code))
  })

  tooltip = d3.select(chartContainer.value)
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0)

  const bisector = d3.bisector(d => d.year).left

  const hoverLine = g.append('line')
    .attr('class', 'hover-line')
    .attr('y1', 0)
    .attr('y2', innerH)
    .attr('stroke', '#999')
    .attr('stroke-width', 1)
    .attr('stroke-dasharray', '3 3')
    .style('opacity', 0)

  g.append('rect')
    .attr('width', innerW)
    .attr('height', innerH)
    .attr('fill', 'transparent')
    .on('mousemove', (event) => {
      const [mx] = d3.pointer(event)
      const hoveredYear = Math.round(x.invert(mx))

      hoverLine
        .attr('x1', x(hoveredYear))
        .attr('x2', x(hoveredYear))
        .style('opacity', 0.5)

      let html = `<strong>${hoveredYear}</strong><br/>`
      for (const [code, countryData] of dataByCountry) {
        const idx = bisector(countryData.sort((a, b) => a.year - b.year), hoveredYear)
        const clampedIdx = Math.max(0, Math.min(countryData.length - 1, idx))
        const d = countryData[clampedIdx]
        if (d && d.year === hoveredYear) {
          const value = d[props.metric]
          const unit = props.metric === 'co2' ? 'Mt' : 't'
          html += `<span style="color:${colorMap.value[code]}">\u25CF</span> ${getCountryName(code)}: ${value?.toFixed(2) || 'N/A'} ${unit}<br/>`
        }
      }

      tooltip
        .style('opacity', 1)
        .style('left', `${event.offsetX + 15}px`)
        .style('top', `${event.offsetY - 10}px`)
        .html(html)
    })
    .on('mouseleave', () => {
      tooltip.style('opacity', 0)
      hoverLine.style('opacity', 0)
    })
}

watch(
  () => [props.selectedCountries, props.metric, props.data],
  () => drawChart(),
  { deep: true }
)

onMounted(() => {
  drawChart()
})

onBeforeUnmount(() => {
  if (tooltip) tooltip.remove()
})
</script>

<style scoped>
.comparison-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.header h3 {
  margin: 0;
  font-size: 14px;
}

.sub {
  font-size: 12px;
  color: #555;
}

.chart {
  flex: 1;
  width: 100%;
  position: relative;
  min-height: 0;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #888;
  font-size: 13px;
}

.tooltip {
  position: absolute;
  pointer-events: none;
  background: white;
  border: 1px solid #e6e8ee;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  z-index: 10;
  line-height: 1.5;
}

.grid .tick line {
  stroke: currentColor;
}
</style>
