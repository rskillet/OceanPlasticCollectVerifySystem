// F2 · Send page | UI-first version placeholder; offline sync comes later.
import { Link } from 'react-router'

import { F2Card, F2Notice, F2Page } from '../components/F2Page.jsx'

export default function SendPage() {
  return (
    <F2Page title="Send saved records" description="This screen is outside the current Figma flow.">
      <F2Card className="mx-auto max-w-2xl">
        <F2Notice tone="calm">
          Offline queue and resend behavior will be connected after the first UI review.
        </F2Notice>
        <div className="mt-5">
          <Link to="/record" className="inline-flex min-h-12 items-center justify-center rounded-lg bg-[#0c6e80] px-4 py-2 text-sm font-semibold text-white hover:bg-[#095d6c]">
            Back to recording
          </Link>
        </div>
      </F2Card>
    </F2Page>
  )
}
