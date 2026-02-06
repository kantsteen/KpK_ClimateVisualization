<template>
  <div class="country-selector" ref="selectorRef">
    <div class="selected-countries">
      <span
        v-for="code in modelValue"
        :key="code"
        class="chip"
        :style="{ backgroundColor: colorMap[code] || '#999' }"
      >
        {{ getCountryName(code) }}
        <button class="remove-btn" @click="removeCountry(code)">&times;</button>
      </span>
      <input
        v-if="modelValue.length < maxCountries"
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="Search countries..."
        @focus="showDropdown = true"
        @input="showDropdown = true"
      />
    </div>

    <ul v-if="showDropdown && filteredCountries.length > 0" class="dropdown">
      <li
        v-for="country in filteredCountries"
        :key="country.code"
        @click="addCountry(country.code)"
      >
        {{ country.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  countries: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Array,
    required: true
  },
  colorMap: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const maxCountries = 10
const searchQuery = ref('')
const showDropdown = ref(false)
const selectorRef = ref(null)

const filteredCountries = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return props.countries
    .filter(c => !props.modelValue.includes(c.code))
    .filter(c => c.name.toLowerCase().includes(query))
    .slice(0, 20)
})

function getCountryName(code) {
  const country = props.countries.find(c => c.code === code)
  return country ? country.name : code
}

function addCountry(code) {
  if (props.modelValue.length < maxCountries && !props.modelValue.includes(code)) {
    emit('update:modelValue', [...props.modelValue, code])
  }
  searchQuery.value = ''
  showDropdown.value = false
}

function removeCountry(code) {
  emit('update:modelValue', props.modelValue.filter(c => c !== code))
}

function handleClickOutside(event) {
  if (selectorRef.value && !selectorRef.value.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.country-selector {
  position: relative;
  width: 100%;
}

.selected-countries {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 6px;
  border: 1px solid #e6e8ee;
  border-radius: 6px;
  background: #fff;
  min-height: 36px;
  align-items: center;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 14px;
  font-size: 12px;
  color: white;
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0 2px;
  opacity: 0.8;
}

.remove-btn:hover {
  opacity: 1;
}

.search-input {
  flex: 1;
  min-width: 120px;
  border: none;
  outline: none;
  font-size: 13px;
  padding: 4px;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #e6e8ee;
  border-radius: 6px;
  margin-top: 4px;
  padding: 0;
  list-style: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dropdown li {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
}

.dropdown li:hover {
  background: #f0f4f8;
}
</style>
