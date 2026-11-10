# F2 · Record a collection (frontend)

**Owner:** Masaaki Kato · **Backend:** `server/app/features/f2_record_collection/`

The current frontend pass is a visual prototype for the three Figma screens. It uses local preview boat data and route state to demonstrate the flow.

| Screen | Route | Current preview behavior |
|---|---|---|
| Choose the boat | `/record` | Search and select a sample active boat |
| Enter collection & evidence | `/record/details` | Enter weight, material and optional note; preview a scale photo |
| Collection saved | `/record/saved` | Show a sample record summary and PENDING status |
| Send saved records | `/send` | Deferred placeholder; this screen is not in the current Figma flow |

This pass does not call the API or persist the record. GPS, offline storage and sync are deferred while the team reviews the screens. Before feature delivery, connect the form to F2 endpoints and implement the remaining system requirements.
