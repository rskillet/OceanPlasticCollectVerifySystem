// F2 · Choose the boat (step 1 of 2) | FR-2.1 visual preview
import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { F2Button, F2Card, F2Notice, F2Page, inputClassName } from '../components/F2Page.jsx'
import { PREVIEW_BOATS } from '../mockData.js'

export default function ChooseBoatPage() {
  const navigate = useNavigate()
  const [selectedId, setSelectedId] = useState(null)
  const [search, setSearch] = useState('')
  const [mode, setMode] = useState('choose')

  const filteredBoats = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    if (!query) return PREVIEW_BOATS
    return PREVIEW_BOATS.filter((boat) => `${boat.code} ${boat.name}`.toLocaleLowerCase().includes(query))
  }, [search])

  const selectedBoat = PREVIEW_BOATS.find((boat) => String(boat.id) === String(selectedId))

  return (
    <F2Page
      title="Which boat?"
      description="Choose the boat used for this collection. You can change it on the next screen."
      actions={<span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">UI preview</span>}
    >
      <F2Card className="mx-auto max-w-3xl">
        <div className="mb-5 flex gap-2 border-b border-slate-200 pb-4" role="tablist" aria-label="Boat selection method">
          {[
            ['choose', 'Choose'],
            ['name', 'Type name'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={mode === value}
              onClick={() => setMode(value)}
              className={`min-h-11 rounded-lg px-4 text-sm font-semibold ${
                mode === value ? 'bg-[#0c6e80] text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <label htmlFor="boat-search" className="mb-2 block text-sm font-semibold text-slate-800">
          {mode === 'choose' ? 'Search by code or boat name' : 'Type the boat name'}
        </label>
        <input
          id="boat-search"
          className={inputClassName}
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={mode === 'choose' ? 'For example, HC-14 or Harbor Cleaner' : 'Enter a boat name'}
          autoComplete="off"
        />
        {mode === 'name' && (
          <p className="mt-2 text-xs text-slate-500">Search for one of the active registered boats below.</p>
        )}

        <F2Notice tone="calm" className="mt-4">Preview data is being used while the F5 boat API is built.</F2Notice>

        <div className="mt-4 space-y-2" aria-live="polite">
          {filteredBoats.length ? filteredBoats.map((boat) => {
            const selected = String(selectedId) === String(boat.id)
            return (
              <button
                key={boat.id}
                type="button"
                onClick={() => setSelectedId(boat.id)}
                aria-pressed={selected}
                className={`flex min-h-16 w-full items-center justify-between gap-4 rounded-lg border px-4 py-3 text-left transition ${
                  selected
                    ? 'border-[#0c6e80] bg-[#eff8f9] ring-1 ring-[#0c6e80]'
                    : 'border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50'
                }`}
              >
                <span className="flex min-w-0 items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#e4f1f3] text-xs font-bold text-[#0c6e80]">
                    {boat.code.slice(0, 2)}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-slate-900">{boat.code} · {boat.name}</span>
                    <span className="mt-0.5 block text-xs text-slate-500">Capacity {boat.capacity_kg.toLocaleString()} kg</span>
                  </span>
                </span>
                <span className={`shrink-0 text-sm font-semibold ${selected ? 'text-[#0c6e80]' : 'text-slate-400'}`}>
                  {selected ? 'Selected' : 'Choose'}
                </span>
              </button>
            )
          }) : (
            <p className="rounded-lg bg-slate-50 p-4 text-sm text-slate-600">No boat matches that search.</p>
          )}
        </div>

        <div className="mt-6 flex flex-col-reverse justify-between gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:items-center">
          <p className="text-xs text-slate-500">Choose an active boat to continue.</p>
          <div className="flex gap-2">
            <Link to="/home" className="inline-flex min-h-12 items-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">Cancel</Link>
            <F2Button
              type="button"
              disabled={!selectedBoat}
              onClick={() => selectedBoat && navigate('/record/details', { state: { boat: selectedBoat } })}
            >
              Continue
            </F2Button>
          </div>
        </div>
      </F2Card>
    </F2Page>
  )
}
