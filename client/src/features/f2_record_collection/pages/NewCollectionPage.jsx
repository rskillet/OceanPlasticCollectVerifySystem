// F2 · Enter collection & evidence (step 2 of 2) | FR-2.2 visual preview
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { F2Button, F2Card, F2Notice, F2Page, inputClassName } from '../components/F2Page.jsx'
import { MATERIAL_OPTIONS, PREVIEW_BOATS } from '../mockData.js'

export default function NewCollectionPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const initialBoat = location.state?.boat || null
  const [boatId, setBoatId] = useState(initialBoat?.id || '')
  const [weight, setWeight] = useState('')
  const [material, setMaterial] = useState('')
  const [note, setNote] = useState('')
  const [photo, setPhoto] = useState(null)
  const [photoPreview, setPhotoPreview] = useState('')
  const [photoError, setPhotoError] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!initialBoat) navigate('/record', { replace: true })
  }, [initialBoat, navigate])

  useEffect(() => {
    if (!photo) {
      setPhotoPreview('')
      return undefined
    }
    const url = URL.createObjectURL(photo)
    setPhotoPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [photo])

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    const numericWeight = Number(weight)
    const selectedBoat = PREVIEW_BOATS.find((boat) => String(boat.id) === String(boatId))
    if (!selectedBoat) {
      setError('Choose a boat from the list.')
      return
    }
    if (!Number.isFinite(numericWeight) || numericWeight <= 0) {
      setError('Enter a weight greater than 0 kg.')
      return
    }
    if (!material) {
      setError('Choose one material type.')
      return
    }
    if (!photo) {
      setError('Take a photo of the scale before saving.')
      return
    }

    setSaving(true)
    const record = {
      record_number: `REC-${String(Date.now()).slice(-6)}`,
      boat_id: selectedBoat.id,
      boat_code: selectedBoat.code,
      boat_name: selectedBoat.name,
      weight_kg: numericWeight,
      material,
      note: note.trim(),
      status: 'PENDING',
      recorded_at: new Date().toISOString(),
    }
    navigate('/record/saved', { state: { record, previewOnly: true } })
  }

  if (!initialBoat) return null

  return (
    <F2Page
      title="New collection"
      description="Record the load and attach a clear photo of the scale."
      actions={<Link to="/record" className="inline-flex min-h-12 items-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">Cancel</Link>}
      width="max-w-6xl"
    >
      <form onSubmit={onSubmit}>
        <F2Card>
          <div className="mb-5 grid gap-3 border-b border-slate-200 pb-4 sm:grid-cols-[1fr_auto] sm:items-end">
            <div>
              <label htmlFor="collection-boat" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-[#0c6e80]">
                Step 2 of 2 · Boat
              </label>
              <select
                id="collection-boat"
                className="min-h-12 w-full max-w-sm rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-800 focus:border-[#0c6e80] focus:outline-none focus:ring-2 focus:ring-[#0c6e80]/20"
                value={boatId}
                onChange={(event) => setBoatId(event.target.value)}
              >
                {PREVIEW_BOATS.map((boat) => (
                  <option key={boat.id} value={boat.id}>{boat.code} · {boat.name}</option>
                ))}
              </select>
            </div>
            <span className="justify-self-start rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 sm:justify-self-end">UI preview</span>
          </div>

          <F2Notice tone="calm" className="mb-5">GPS, offline saving, and server upload are deferred in this first UI pass.</F2Notice>
          {error && <F2Notice tone="error" className="mb-5" role="alert">{error}</F2Notice>}

          <div className="grid gap-7 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.85fr)]">
            <div className="space-y-5">
              <div>
                <label htmlFor="weight-kg" className="mb-2 block text-sm font-semibold text-slate-800">
                  Weight (kg) <span className="text-red-700">*</span>
                </label>
                <input
                  id="weight-kg"
                  className={`${inputClassName} text-lg font-semibold`}
                  type="number"
                  min="0.001"
                  step="any"
                  inputMode="decimal"
                  placeholder="Read it from the scale"
                  value={weight}
                  onChange={(event) => setWeight(event.target.value)}
                  required
                />
              </div>

              <fieldset>
                <legend className="mb-2 text-sm font-semibold text-slate-800">
                  Material <span className="text-red-700">*</span>
                </legend>
                <div className="flex flex-wrap gap-2">
                  {MATERIAL_OPTIONS.map(([value, label]) => (
                    <button
                      key={value}
                      type="button"
                      aria-pressed={material === value}
                      onClick={() => setMaterial(value)}
                      className={`min-h-12 rounded-full border px-4 py-2 text-sm font-semibold transition ${
                        material === value
                          ? 'border-[#0c6e80] bg-[#0c6e80] text-white'
                          : 'border-slate-300 bg-white text-slate-700 hover:border-[#0c6e80] hover:text-[#0c6e80]'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </fieldset>

              <div>
                <label htmlFor="collection-note" className="mb-2 block text-sm font-semibold text-slate-800">
                  Note <span className="font-normal text-slate-500">(optional)</span>
                </label>
                <textarea
                  id="collection-note"
                  className={`${inputClassName} min-h-24 resize-y`}
                  rows="3"
                  maxLength="2000"
                  placeholder="Add a short note if needed"
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                />
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-semibold text-slate-800">
                Photo of the scale <span className="text-red-700">*</span>
              </p>
              <div className="flex min-h-72 flex-col items-center justify-center overflow-hidden rounded-xl border border-dashed border-slate-300 bg-[#f5f8f9] p-4 text-center">
                {photoPreview ? (
                  <img src={photoPreview} alt="Preview of the scale photo" className="max-h-64 w-full rounded-lg object-contain" />
                ) : (
                  <div className="max-w-xs">
                    <span className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#e1f0f2] text-xl text-[#0c6e80]" aria-hidden="true">＋</span>
                    <p className="text-sm font-semibold text-slate-800">Show the scale reading clearly</p>
                    <p className="mt-1 text-xs text-slate-500">One photo is required. You can retake it before saving.</p>
                  </div>
                )}
                <label className="mt-4 inline-flex min-h-12 cursor-pointer items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  {photo ? 'Retake photo' : 'Take photo'}
                  <input
                    className="sr-only"
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={(event) => {
                      const nextPhoto = event.target.files?.[0] || null
                      event.target.value = ''
                      if (nextPhoto && !nextPhoto.type.startsWith('image/')) {
                        setPhotoError('Choose an image file for the scale photo.')
                        setPhoto(null)
                      } else {
                        setPhotoError('')
                        setPhoto(nextPhoto)
                      }
                    }}
                  />
                </label>
                {photoError && <p className="mt-2 text-sm text-red-700">{photoError}</p>}
                {photo && <p className="mt-2 text-xs text-slate-500">{Math.max(1, Math.round(photo.size / 1024))} KB</p>}
              </div>
            </div>
          </div>

          <div className="mt-7 flex flex-col-reverse justify-between gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:items-center">
            <p className="text-xs text-slate-500">Preview only. The form is not connected to the API yet.</p>
            <F2Button type="submit" disabled={saving || !photo || !material}>
              {saving ? 'Saving preview…' : 'Save collection'}
            </F2Button>
          </div>
        </F2Card>
      </form>
    </F2Page>
  )
}
