// F2 · Collection saved | FR-2.3 visual preview
import { Link, useLocation, useNavigate } from 'react-router'

import { F2Button, F2Card, F2Notice, F2Page } from '../components/F2Page.jsx'
import { MATERIAL_LABELS } from '../mockData.js'

export default function CollectionSavedPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { record, previewOnly } = location.state || {}

  return (
    <F2Page title="Collection saved" description="Review the collection details." width="max-w-3xl">
      <F2Card className="mx-auto max-w-2xl p-6 sm:p-8">
        <div className="mb-6 text-center">
          <span className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-2xl font-bold text-emerald-700" aria-hidden="true">✓</span>
          <h2 className="text-xl font-semibold text-slate-900">Saved</h2>
          <p className="mt-1 text-sm text-slate-600">Collection details are ready for review.</p>
        </div>

        {previewOnly && (
          <F2Notice tone="calm" className="mb-5">
            UI preview only. This record has not been saved to the database.
          </F2Notice>
        )}

        {record ? (
          <dl className="divide-y divide-slate-100 rounded-lg border border-slate-200">
            <SummaryRow label="Record number" value={record.record_number} />
            <SummaryRow label="Boat" value={`${record.boat_code} · ${record.boat_name}`} />
            <SummaryRow label="Weight" value={`${Number(record.weight_kg).toLocaleString()} kg`} />
            <SummaryRow label="Material" value={MATERIAL_LABELS[record.material] || record.material} />
            <SummaryRow label="Status" value={record.status} />
          </dl>
        ) : (
          <F2Notice tone="warning" className="mb-5">
            No preview record is open. Start a new collection to see this screen.
          </F2Notice>
        )}

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
          <F2Button type="button" variant="secondary" onClick={() => navigate('/home')}>Back to home</F2Button>
          <F2Button type="button" onClick={() => navigate('/record')}>Add another</F2Button>
        </div>
      </F2Card>
    </F2Page>
  )
}

function SummaryRow({ label, value }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-semibold text-slate-900">{value}</dd>
    </div>
  )
}
