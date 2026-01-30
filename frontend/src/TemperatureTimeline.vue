<template>
  <div class="timeline">
    <div class="header">
      <h3>Temperature timeline (NASA GISTEMP)</h3>
      <div class="sub">
        Annual temperature anomaly (°C) relative to the 1951–1980 baseline
      </div>
    </div>

    <div ref="container" class="chart"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import * as d3 from "d3";

const container = ref(null);
let timerId = null;

onMounted(async () => {
  const res = await fetch("http://localhost:8000/api/temperature");
  const raw = await res.json();

  const data = raw
    .map(d => ({ year: +d.year, temp: +d.temperature }))
    .filter(d => Number.isFinite(d.year) && Number.isFinite(d.temp))
    .sort((a, b) => a.year - b.year);

  // chart sizes
  const margin = { top: 18, right: 22, bottom: 42, left: 60 };
  const width = 900;
  const height = 340;

  const svg = d3
    .select(container.value)
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .style("width", "100%")
    .style("height", "auto");

  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  // scales
  const x = d3.scaleLinear()
    .domain(d3.extent(data, d => d.year))
    .range([0, innerW]);

  // padding so line doesn’t touch edges
  const yExtent = d3.extent(data, d => d.temp);
  const yPad = 0.1;
  const y = d3.scaleLinear()
    .domain([yExtent[0] - yPad, yExtent[1] + yPad])
    .nice()
    .range([innerH, 0]);

  // gridlines (horizontal)
  const yGrid = d3.axisLeft(y).tickSize(-innerW).tickFormat(() => "");
  g.append("g")
    .attr("class", "grid")
    .call(yGrid)
    .call(gr => gr.selectAll(".tick line").attr("opacity", 0.2))
    .call(gr => gr.select(".domain").remove());

  // axes
  g.append("g")
    .attr("transform", `translate(0,${innerH})`)
    .call(
      d3.axisBottom(x)
        .tickFormat(d3.format("d"))
        .ticks(10)
    );

  g.append("g")
    .call(d3.axisLeft(y).ticks(6));

  // axis labels
  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 36)
    .attr("text-anchor", "middle")
    .style("font-size", "12px")
    .text("Year");

  g.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -innerH / 2)
    .attr("y", -45)
    .attr("text-anchor", "middle")
    .style("font-size", "12px")
    .text("Anomaly (°C)");

  // baseline at 0°C
  g.append("line")
    .attr("x1", 0)
    .attr("x2", innerW)
    .attr("y1", y(0))
    .attr("y2", y(0))
    .attr("stroke", "currentColor")
    .attr("opacity", 0.35)
    .attr("stroke-dasharray", "4 4");

  // line path
  const line = d3.line()
    .x(d => x(d.year))
    .y(d => y(d.temp));

  const path = g.append("path")
    .attr("fill", "none")
    .attr("stroke", "currentColor")
    .attr("stroke-width", 2.5);

  // current-year indicator
  const marker = g.append("circle")
    .attr("r", 4.5)
    .attr("fill", "currentColor")
    .style("opacity", 0);

  const guide = g.append("line")
    .attr("y1", 0)
    .attr("y2", innerH)
    .attr("stroke", "currentColor")
    .style("opacity", 0);

  const yearLabel = g.append("text")
    .attr("x", innerW)
    .attr("y", -4)
    .attr("text-anchor", "end")
    .style("font-size", "14px")
    .style("font-weight", "700");

  // tooltip (simple)
  const tooltip = d3
    .select(container.value)
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // invisible overlay for mouse interactions
  g.append("rect")
    .attr("width", innerW)
    .attr("height", innerH)
    .attr("fill", "transparent")
    .on("mousemove", (event) => {
      const [mx] = d3.pointer(event);
      const hoveredYear = Math.round(x.invert(mx));

      // find closest point by year
      const idx = d3.bisector(d => d.year).left(data, hoveredYear);
      const clampedIdx = Math.max(0, Math.min(data.length - 1, idx));
      const d = data[clampedIdx];

      tooltip
        .style("opacity", 1)
        .style("left", `${event.offsetX + 12}px`)
        .style("top", `${event.offsetY + 12}px`)
        .html(`<strong>${d.year}</strong><br/>${d.temp.toFixed(2)} °C`);
    })
    .on("mouseleave", () => {
      tooltip.style("opacity", 0);
    });

  // animation (15–30 seconds total)
  const totalDurationMs = 20000; // 20s
  const stepMs = Math.max(20, Math.floor(totalDurationMs / data.length));

  let i = 1;
  timerId = window.setInterval(() => {
    const slice = data.slice(0, i);

    // Update the line with a small transition to feel smoother
    path
      .datum(slice)
      .transition()
      .duration(Math.min(120, stepMs))
      .ease(d3.easeLinear)
      .attr("d", line);

    const last = slice[slice.length - 1];

    marker
      .style("opacity", 1)
      .attr("cx", x(last.year))
      .attr("cy", y(last.temp));

    guide
      .style("opacity", 0.18)
      .attr("x1", x(last.year))
      .attr("x2", x(last.year));

    yearLabel.text(String(last.year));

    i += 1;
    if (i > data.length) {
      window.clearInterval(timerId);
      timerId = null;
    }
  }, stepMs);
});

onBeforeUnmount(() => {
  if (timerId) window.clearInterval(timerId);
});
</script>

<style scoped>
.timeline {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  width: 100%;
  position: relative;
}

/* tooltip */
.tooltip {
  position: absolute;
  pointer-events: none;
  background: white;
  border: 1px solid #e6e8ee;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

/* gridlines */
.grid .tick line {
  stroke: currentColor;
}
</style>
