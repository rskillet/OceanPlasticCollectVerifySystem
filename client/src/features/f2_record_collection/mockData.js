// Temporary F2 preview data. Replace with GET /api/boats?active=true later.
export const PREVIEW_BOATS = [
  { id: 1, code: 'HC-14', name: 'Harbor Cleaner', capacity_kg: 1800, active: true },
  { id: 2, code: 'SH-02', name: 'Sea Harvest', capacity_kg: 2400, active: true },
  { id: 3, code: 'RM-07', name: 'River Mouth', capacity_kg: 900, active: true },
  { id: 4, code: 'SL-03', name: 'Shoreline Team A', capacity_kg: 400, active: true },
]

export const MATERIAL_OPTIONS = [
  ['PET_BOTTLES', 'PET bottles'],
  ['HDPE_RIGID', 'HDPE rigid'],
  ['FISHING_NET_ROPE', 'Fishing net / rope'],
  ['LDPE_FILM', 'LDPE film'],
  ['MIXED', 'Mixed'],
]

export const MATERIAL_LABELS = Object.fromEntries(
  MATERIAL_OPTIONS.map(([value, label]) => [value, label]),
)
