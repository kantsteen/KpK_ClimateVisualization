import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";

createApp({
  template: `
    <section>
      <h1>Temperature Timeline (Story 8)</h1>

      <p v-if="loading">Loading…</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <div v-else>
        <p>
          Baseline: <b>{{ meta.baseline }}</b> • Unit: <b>{{ meta.unit }}</b><br />
          Years: <b>{{ meta.start_year }}–{{ meta.end_year }}</b><br />
          Points: <b>{{ series.length }}</b>
        </p>

        <h3>First 5 points</h3>
        <pre>{{ series.slice(0, 5) }}</pre>

        <h3>Current year (demo)</h3>
        <p><b>{{ currentYear }}</b></p>

        <button @click="play" :disabled="playing || !series.length">Play</button>
        <button @click="pause" :disabled="!playing">Pause</button>
      </div>
    </section>
  `,

  data() {
    return {
      loading: true,
      error: "",
      meta: { baseline: "", unit: "", start_year: null, end_year: null },
      series: [],
      currentYear: null,
      timer: null,
      playing: false,
    };
  },

  async mounted() {
    try {
      const res = await fetch("http://localhost:8000/api/temperature/historical");
      if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);

      const json = await res.json();
      this.meta = json.meta;
      this.series = json.series;

      this.currentYear = this.series[0]?.year ?? null;
    } catch (e) {
      this.error = e?.message ?? "Unknown error";
    } finally {
      this.loading = false;
    }
  },

  methods: {
    play() {
      if (!this.series.length) return;
      this.playing = true;

      const durationMs = 20000; // 15-30 sek (fx 20 sek)
      const msPerStep = Math.max(10, Math.floor(durationMs / this.series.length));

      let i = 0;
      this.currentYear = this.series[i].year;

      this.timer = setInterval(() => {
        i += 1;
        if (i >= this.series.length) {
          this.pause();
          return;
        }
        this.currentYear = this.series[i].year;
      }, msPerStep);
    },

    pause() {
      this.playing = false;
      if (this.timer) clearInterval(this.timer);
      this.timer = null;
    },
  },

  beforeUnmount() {
    if (this.timer) clearInterval(this.timer);
  },
}).mount("#app");
