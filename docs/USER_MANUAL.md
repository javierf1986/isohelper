# ISOHelper User Manual

This user manual describes all features of ISOHelper. The manual is organized by feature; we'll document one feature at a time. This document contains the "Document Generator" section first. Subsequent sections will be added on request.

## 1. Document Generator

Overview
--------
The Document Generator creates ISO-standard documentation (for example, an ISO 9001 manual) tailored to your organization using templates, company data, and optional AI enhancements. It supports clause-level generation, multi-clause documents, language selection, and outputs in Markdown, DOCX, PDF, and HTML.

Who uses it
-----------
- Quality Managers preparing or maintaining manuals
- Consultants generating client manuals
- Compliance Officers who need quick drafts to review

Key capabilities
----------------
- Generate a complete ISO manual from selected clauses and company profile
- Generate single clauses or sets of clauses
- Language selection for the generated content (EN/ES/FR/DE/ZH)
- AI enhancement mode: expand or refine generated text using the AI engine (configurable)
- Output formats: Markdown, DOCX, PDF, HTML
- Save generated document to workspace storage and create version entries
- Automatic SHA-256 hashing and versioning when saved

How to use (Frontend)
---------------------
1. Navigate to Dashboard → Generate or click 'Generate Document' from the Documents page.
2. Choose the target Workspace (top-left workspace selector).
3. Select ISO standard (e.g., ISO 9001) and then select clauses you want included.
4. Enter company details or select an existing company profile.
5. (Optional) Toggle 'AI Enhancement' to expand results using the AI engine. Configure the enhancement level in Settings.
6. Choose language from the language dropdown.
7. Choose output format(s) (Markdown, DOCX, PDF, HTML).
8. Click 'Generate'.
9. When generation finishes, click 'View' to preview or 'Download' to save locally.

How to use (API)

-----------------

Endpoint: `POST /api/v1/documents/generate`
Request body (example):



  "clauses": ["4.1", "4.2", "5.1"],




{
  "id": "doc_123456",
  "workspace_id": "ws_abc",
  "status": "completed",

  "download_urls": {

    "md": "/api/v1/documents/doc_123456/download?format=md",
    "docx": "/api/v1/documents/doc_123456/download?format=docx"
  },

  "version_id": "v_2025_001",

  "sha256": "..."
}


Permissions

-----------
- You must be a member of the workspace and have the 'create_documents' permission (default for roles: admin, editor).
- Guests have read-only access and cannot generate documents.


-------------------

- Generated documents stored within the selected workspace.
- The system automatically creates a `DocumentVersion` entry with the generated output.
- Each save generates a SHA-256 content hash for integrity.

- You can view previous versions in the Document → Versions page.


AI Enhancement
--------------
- Uses the integrated AI provider (OpenAI/mistralai) to expand or refine generated copy.

- You can set the enhancement level in 'Settings' (Low/Medium/High).

- If generation fails, check:

  - For large clause sets, try smaller batches or increase server timeouts

- Frontend page: `frontend/app/generate/page.tsx`
- Service: `backend/services/document_generator.py`
- Models: `backend/models/version_models.py`, `backend/models/document_models.py`

Tips

----
- Save frequently if editing generated content to preserve version history.
- Use workspace templates for company-specific reusable content.


---



--------

- Admins and Template Authors who build standard-compliant templates

- Consultants who package templates for clients
- Editors who customize templates per workspace

Key capabilities
----------------
- Create, edit, and delete templates
- Template variables (placeholders) with validation and default values
- Template metadata (title, description, standard, clause number, tags)
- Versioning of templates with history and rollback
- Workspace-local templates and global templates (marketplace)
- Import/export templates as JSON or ZIP bundles
- Preview templates rendered with sample company data

How to use (Frontend)
---------------------
1. Navigate to Admin → Templates (or Dashboard → Templates if you have permissions).
2. Click 'New Template' to create a template from scratch or 'Import' to upload an existing bundle.
3. Fill template metadata (title, standard, clause number, tags, language).
4. Define template content using markdown with placeholders: `{{company_name}}`, `{{process_owner}}`, `{{clause_text}}`.
5. Add variable definitions in the variables panel: name, type (string, date, number, enum), default value, validation (regex or list), and helpful description.
6. Use the 'Preview' button to render the template with sample or real company data.
7. Click 'Save' to persist. Each save creates a new template version.
8. To publish: choose 'Publish to Workspace' (makes it available to workspace users) or 'Submit to Marketplace' (requires admin approval).

How to use (API)
-----------------
Endpoints
- `GET /api/v1/templates/` — List templates (supports query params: workspace_id, standard, tag, language)
- `GET /api/v1/templates/{template_id}` — Get template details and variable schema
- `POST /api/v1/templates/` — Create a new template (body: metadata + content + variables)
- `PUT /api/v1/templates/{template_id}` — Update template (creates new version)
- `DELETE /api/v1/templates/{template_id}` — Delete template (soft delete, requires permissions)
- `POST /api/v1/templates/{template_id}/preview` — Render template with provided context
- `POST /api/v1/templates/import` — Import template bundle (JSON/ZIP)
- `GET /api/v1/templates/{template_id}/export` — Export template bundle

Example: Create template (simplified)

Request POST `/api/v1/templates/`

{
  "title": "ISO9001 Clause 4.1 - Organization Context",
  "standard": "ISO9001",
  "clause": "4.1",
  "language": "en",
  "content": "# Understanding the Organization\n\n{{company_name}} operates in the {{industry}} sector...",
  "variables": [
    {"name":"company_name","type":"string","default":"Your Company"},
    {"name":"industry","type":"string","default":"industry"}
  ]
}

Response (201): `{ "template_id": "tpl_12345", "version": "1.0" }`

Permissions
-----------
- Creating, editing, deleting, and publishing templates require the 'manage_templates' permission (default for Admin role).
- Editors may create and save workspace-local templates but require publish approval for the marketplace.
- Viewers may only preview and use published templates.

Versioning & Rollback
---------------------
- Every update to a template creates a new `TemplateVersion` with a unique version identifier.
- You can view version history and restore any previous version if needed.

Marketplace
----------
- Templates can be submitted to the Template Marketplace where they are reviewed and published as global templates.
- Marketplace templates include licensing metadata, author info, pricing (if applicable), and demo previews.
- When a workspace installs a marketplace template, it becomes a workspace-local copy; updates by the author do not automatically overwrite local copies unless the workspace opts into auto-updates.

Import/Export
-------------
- Templates can be exported as JSON bundles (metadata, variables, content) or ZIP packages including sample data and preview images.
- Use the API `POST /api/v1/templates/import` to bulk import template bundles.

Related pages & files
---------------------
- Frontend: `frontend/app/templates/` directory
- API route: `backend/api/routes/templates.py`
- Service: `backend/services/template_service.py`
- Models: `backend/models/template_models.py`

Tips
----
- Standardize variable names across templates for easier automation (e.g., `company_name`, `process_owner`).
- Use enum variables for fields with limited choices (e.g., `company_size` to be small/medium/large).
- Keep guidance notes within templates to help editors understand mandatory vs optional sections.

Troubleshooting
---------------
- If preview rendering fails, check variable schema and required variables.
- If import fails, confirm the bundle structure and that the JSON is valid.
- If templates are missing from the workspace, ensure they are published to the workspace (not only to marketplace) and that your role has `view_templates`.

---

(End of Template Repository section)

## 3. API Infrastructure (User-facing)

Overview
--------
The API provides a simple way to perform the same actions as the web UI but programmatically — useful for automation, integrations, or using tools like Postman. You do not need to be a developer to use the API; this section explains the most common actions in plain language and shows how to try them with Postman or a single command.

Who uses it
-----------
- Power users who automate document generation or exports
- IT teams integrating ISOHelper with other systems (HR, ERP)
- Consultants who want programmatic access to multiple client workspaces

How authentication works (simple)
-------------------------------
- The API uses tokens to identify you. Think of a token like a key you include with each request.
- To get a token: log in through the web UI or the `POST /api/v1/auth/login` endpoint with your email and password.
- The response contains an `access_token`. Add this token to each request in an `Authorization: Bearer <token>` header.
- Tokens expire after a configured time. Use the refresh token (if available) to get a new access token.

Common actions (and where to find them)
-------------------------------------
- Generate a document: `POST /api/v1/documents/generate` — same as the "Generate" UI.
- Check document status or download: `GET /api/v1/documents/{document_id}` and `/download?format=...`.
- Manage templates: `GET /api/v1/templates/`, `POST /api/v1/templates/`, `PUT /api/v1/templates/{id}`.
- Artifacts (NC, CA, Audit, Reviews): Use endpoints under `/api/v1/artifacts/*` to create, list, update, and close items.
- Gap analysis: Upload a file via `POST /api/v1/gap-analysis/upload` and run analysis with `/api/v1/gap-analysis/{id}/analyze`.
- Versioning actions: `/api/v1/versions/` endpoints let you create, compare, approve, and rollback document versions.
- Export management: `/api/v1/export/` endpoints let you trigger exports and list exported files.

Quick try-it examples (user-friendly)
-----------------------------------
Prerequisite: get an access token by logging in or ask your admin for one.

1) Generate a document (simple example)

PowerShell (copy into a PowerShell window / Postman body = JSON):

```powershell
$headers = @{ "Authorization" = "Bearer YOUR_ACCESS_TOKEN" ; "Content-Type" = "application/json" }
$body = @{
  company_name = "ABC Manufacturing Ltd"
  industry = "automotive"
  company_size = "medium"
  clauses = @("4.1","4.2","5.1")
  language = "en"
  ai_enhance = $true
  output_formats = @("md","docx")
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/generate" -Method Post -Headers $headers -Body $body
```

Explanation for users: replace `YOUR_ACCESS_TOKEN` with the token you obtained. The command asks the server to create a document and returns a response that includes an ID and download links when finished.

2) Check document status and download URL

PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/doc_123456" -Method Get -Headers @{ "Authorization" = "Bearer YOUR_ACCESS_TOKEN" }
```

If the document is ready the response contains `download_urls` for the formats you requested.

Postman tips (non-developer)
---------------------------
- Create a new request and paste the URL (e.g., `http://localhost:8000/api/v1/documents/generate`).
- Under the "Authorization" tab choose "Bearer Token" and paste your access token.
- Under "Body" choose raw → JSON and paste a request body like the example above.
- Click Send and view the response in Postman. Use the "Save" button to keep requests you use often.

Permissions notes
-----------------
- API calls follow the same permissions as the UI: if you cannot create a document in the UI, the API will also be blocked.
- Admin roles can perform all actions (manage templates, publish to marketplace, manage workspace settings).

Security and best practices (user-focused)
----------------------------------------
- Keep your access token secret. Do not paste it into public places.
- Use the UI to initially obtain tokens if you are not comfortable using the login endpoint.
- If you share API requests with colleagues, remove the token placeholder and show `YOUR_ACCESS_TOKEN` instead.

Related pages & files
---------------------
- API reference (developer docs): `backend/api/routes/` (if you need specific endpoint names) — ask your admin for an exported Postman collection.
- Useful endpoints:
  - `POST /api/v1/auth/login` — get tokens
  - `POST /api/v1/documents/generate` — generate documents
  - `GET /api/v1/documents/{id}` — document status and download links
  - `GET /api/v1/templates/` — list templates
  - `POST /api/v1/gap-analysis/upload` — upload files for gap analysis

---

(End of API Infrastructure section)

## 4. Document Processing & Export

Overview
--------
This feature explains how ISOHelper processes generated content and the options available to export documents. The platform converts generated Markdown into DOCX, PDF, and HTML, and offers export settings for branding and layout.

Who uses it
-----------
- Users who need printable manuals (DOCX/PDF)
- Teams that publish web-based policies (HTML)
- Auditors who want versioned exports for records

Core concepts
-------------
- Input format: Generated content is produced as Markdown (fast, portable) internally.
- Conversion: The platform converts Markdown to DOCX, PDF, and HTML using server-side converters.
- Export bundle: An export can include multiple formats and attachments (e.g., referenced diagrams, annexes).
- Branding: Export templates allow adding logos, headers, footers, and company metadata.

How to export (Frontend)
------------------------
1. After generating a document, open the Document detail page.
2. Click 'Export' and choose formats (DOCX, PDF, HTML). You can select multiple formats at once.
3. (Optional) Choose an export template for branding (logo, header/footer) or use default workspace branding.
4. Click 'Export' to begin conversion. Large documents may take a minute or two.
5. When ready, download links will appear in the Export panel or in the Notifications area.

Export options explained
-----------------------
- DOCX: Best for editable manuals. Preserves headings, lists, tables, and images.
- PDF: Best for official distribution and archival. Uses the DOCX render as a source for consistent layout.
- HTML: Lightweight web view for internal publishing. Useful for intranets.
- Include attachments: Check this to include referenced files in a ZIP alongside the exported documents.
- Page size & margins: Choose A4/Letter and margins from the dropdown.
- Include version metadata: Adds a version block with version number, author, and SHA-256.

How to export (API)
-------------------
- Trigger export: `POST /api/v1/export/` with `document_id` and `formats`.
- Download exported files: `GET /api/v1/export/download/{file_name}`.

Example (PowerShell)

```powershell
$headers = @{ "Authorization" = "Bearer YOUR_ACCESS_TOKEN" ; "Content-Type" = "application/json" }
$body = @{ document_id = "doc_123456" ; formats = @("pdf","docx") } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/export/" -Method Post -Headers $headers -Body $body
```

Export processing details (user-friendly)
----------------------------------------
- Conversion pipeline: Markdown -> intermediate DOCX -> (PDF/HTML) to guarantee consistent visual output.
- Images/attachments: Images embedded in the Markdown are packaged and linked in DOCX/HTML. PDFs embed the images directly.
- Large exports: For extremely large documents, exports are processed in background jobs — you'll get a notification when ready.

Branding & Templates
--------------------
- Admins can create Export Templates (logo, header/footer, legal footer text). These are selectable at export time.
- Workspace-level branding overrides the global default when selected.

Troubleshooting & tips
----------------------
- Missing images in exported DOCX/PDF: Ensure images are uploaded to the workspace and referenced using the document editor image tool.
- Broken layout in DOCX: Check for unclosed Markdown elements (lists or code fences). Use the preview to validate before exporting.
- Export fails or times out: Try exporting a single format (e.g., DOCX only) or split the document into smaller sections.
- Export stuck in queue: Contact your admin to check background worker status and server resources.

Related pages & files
---------------------
- Export API: `backend/api/routes/export.py`
- Export Service: `backend/services/export_service.py`
- Conversion utilities: `backend/utils/converters.py`
- Frontend export pages: `frontend/app/documents/[id]/export/page.tsx`

Tips
----
- Prefer DOCX for final editable copies and PDF for official distribution.
- Keep images under 2MB where possible to speed up conversion.
- Use the 'Include version metadata' option when sharing externally to provide audit traceability.

---

(End of Document Processing & Export section)

## 5. Multi-language (i18n)

Overview
--------
ISOHelper supports multiple languages so teams can work in the language they prefer and produce documents in the target language for publication. The platform uses a combination of frontend message files and backend translation support to present UI strings, templates, and generated documents in different locales.

Who uses it
-----------
- International teams with localized documentation needs
- Consultants creating manuals for clients in other countries
- Admins who manage workspace language defaults and translation quality

Key capabilities
----------------
- UI language switching for individual users
- Workspace-level default language
- Document generation in supported target languages (when templates/translations exist)
- Translation management for UI strings and template content
- Fallback behavior when a translation is missing (falls back to English/default locale)

How to change language (Frontend, user-facing)
--------------------------------------------
1. Look for the language selector in the top navigation or user profile menu.
2. Select the desired language (for example: English, Español, Français, Deutsch, 中文).
3. The UI updates immediately. Some pages may require a refresh to load full locale resources.
4. Generated documents: when starting a new generation, pick the language in the Generate dialog — the generator will attempt to use templates/translations for that language.

Workspace defaults & user preferences
------------------------------------
- Workspace Default: Admins can set a workspace default language in Admin → Settings → Workspace. New users in the workspace will see the default language unless they override it in their profile.
- User Preference: Each user can override the workspace default in their profile preferences. This is stored per-user and persists across sessions.

Managing translations (Admin / Translator guide)
-----------------------------------------------
- Frontend message files: Translations are stored as JSON files under `frontend/messages/` (for example `en.json`, `de.json`, `zh.json`). Each file maps translation keys to localized strings. Use the existing keys; keep keys stable to avoid missing text.
- Template translations: Templates may include language-specific versions. When creating or editing templates, choose the template language or add a translated variant of the same template (same template id but language-specific content).
- Backend translations: The backend has APIs and models to store workspace-specific translations and language metadata. Check `backend/api/routes/languages.py` and `backend/services/translation_service.py` (if present) for endpoints to list and update translations.
- Add a new language (high-level steps):
  1. Create a new frontend messages file, e.g. `frontend/messages/fr.json`, and add translations for all keys used in the UI and templates.
 2. Add or register the locale in the frontend's locale configuration (check `next.config.js` / `next-intl` setup).
 3. Add any server-side locale metadata (language code, display name, direction) via Admin → Settings or the backend API.
 4. Provide translated template content or mark which templates require translation work.
 5. Test the UI and generate a document in the new language to verify both UI strings and document output.

Best practices for translations
-------------------------------
- Keep translation keys stable — changing keys requires updating every locale file.
- Prefer complete translations for templates before publishing workspace-wide defaults.
- Use native speakers to review translations, especially for legal or compliance text.
- Keep placeholders (e.g., `{{company_name}}`) intact in translations; translators should not modify interpolation tokens.
- Shorter keys and messages are easier to fit UI layouts (menu labels, buttons).

Fallbacks and missing translations
---------------------------------
- If a translation key is missing for the selected language, ISOHelper falls back to the workspace default language (commonly English). You will see the fallback text in that case.
- For generated documents, if a template or clause text is not available in the requested language, the generator falls back to the default template language and adds a note indicating the fallback.

Special cases: RTL languages and formatting
-----------------------------------------
- Right-to-left (RTL) languages such as Arabic require layout adjustments. Confirm that the frontend supports RTL by testing the full UI (menus, form inputs, and document previews).
- Date, time, and number formatting depend on locale. When generating documents, the system formats dates according to the selected locale where support exists.

Troubleshooting (common user issues)
-----------------------------------
- Missing strings after switching languages: refresh the page to force locale resources to load. If problems persist, check with your admin that the locale file exists and is properly registered.
- Placeholders showing in generated text (e.g., `{{company_name}}`): this indicates variable substitution failed. Verify that you supplied the required template variables when generating the document.
- Document content appears in mixed languages: check that the selected templates have translations for all included clauses; the generator will mix fallback content if a clause translation is missing.

Tips
----
- Test new languages with a sample workspace before rolling out to all users.
- Keep a checklist for translators: UI strings, template headings, clause bodies, and export templates.
- Use the 'Preview' feature in Templates to check translated templates with sample company data.

Related files & pages
---------------------
- Frontend messages: `frontend/messages/` (per-locale JSON files)
- Frontend locale config: `next.config.js`, `frontend/middleware.ts` or `middleware.ts` (locale detection)
- API route: `backend/api/routes/languages.py` (language metadata & management endpoints)
- Services: `backend/services/translation_service.py` (translation management, if present)

---

(End of Multi-language section)

## 5. Configuration & Setup

Overview
--------
This section helps non-developer users run a local copy for testing, understand the key environment variables, and perform basic troubleshooting. It is written for Windows PowerShell users but the concepts apply to macOS/Linux with equivalent commands.

When should you run locally?
- Testing features, trying new templates, or demonstrating the app to a client without deploying to a server.
- Note: Production deployments should be handled by your IT/DevOps team.

Prerequisites (user-friendly)
- Python 3.11+ installed and available in your PATH.
- Node.js (if you want to run the frontend locally) — LTS recommended.
- Git to checkout the repository.

Key environment variables (what they mean)
- `DATABASE_URL`: Database connection string. For local testing it's usually `sqlite:///./dev.db` or `sqlite:///:memory:`.
- `SECRET_KEY`: A random string used to sign tokens. Keep it secret.
- `OPENAI_API_KEY` (optional): If using AI features, set this to your provider key.
- `ENVIRONMENT`: `development`, `staging`, or `production` — controls logging and debugging.
- `ALLOWED_ORIGINS`: Comma-separated domains for CORS. Use `http://localhost:3000` when running frontend locally.

Run backend locally (PowerShell)
-------------------------------
1. Open PowerShell and navigate to the repository folder:

```powershell
cd C:\dev\isohelper\backend
```

2. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies (from the repository):

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in `backend/` by copying the provided example (ask your admin if an example is present) and set minimal values:

```powershell
# Example .env (backend/.env)
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=change-me-to-a-secure-value
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
# Optional for AI:
OPENAI_API_KEY=
```

5. Start the backend server:

```powershell
cd ..\backend
python -m uvicorn backend.main:app --reload --port 8000
```

You should see logs indicating the server started and available at `http://localhost:8000`.

Run frontend locally (PowerShell)
-------------------------------
1. Open a new PowerShell window and go to the frontend folder:

```powershell
cd C:\dev\isohelper\frontend
```

2. Install Node dependencies (one-time):

```powershell
npm install
```

3. Start the Next.js dev server:

```powershell
npm run dev
```

4. Open `http://localhost:3000` in your browser. The frontend talks to `http://localhost:8000` (backend). If CORS errors appear, ensure `ALLOWED_ORIGINS` includes `http://localhost:3000`.

Basic troubleshooting
---------------------
- Backend fails to start: check `.env` variables and that dependencies installed correctly. Look for traceback messages in the console.
- Database errors: If using SQLite, verify the file exists and is writable. If using Postgres, ensure the connection string is correct and the server is running.
- CORS errors: Add `http://localhost:3000` to `ALLOWED_ORIGINS` in `.env` and restart backend.
- Ports already in use: If 8000 or 3000 are taken, use `--port` to change them.

Security notes for users
------------------------
- Never commit the `.env` file with secrets to Git. Add it to `.gitignore` if needed.
- Use a strong `SECRET_KEY` in staging/production. Your admin should manage production secrets.

Help & support
--------------
- If you are stuck, capture the console logs and share them with the devops or admin team.
- For AI issues, ensure `OPENAI_API_KEY` (or provider key) is set and valid.

Related pages & files
---------------------
- Settings: `config/settings.py`
- Startup entry: `backend/main.py`
- Requirements: `backend/requirements.txt`

---

(End of Configuration & Setup section)

## 6. Document Versioning

Overview
--------
Document Versioning tracks changes made to generated or edited documents so teams can review history, compare versions, approve releases, and roll back when necessary. Versioning helps maintain an audit trail for compliance and lets multiple contributors collaborate safely.

Who uses it
-----------
- Document owners and Quality Managers who need an audit trail
- Editors and contributors who create and refine content
- Approvers who review and approve documents for publication
- Auditors who need to verify change history

Key capabilities
----------------
- Automatic version creation when saving or exporting documents
- Manual 'Save as Version' from the editor for explicit checkpoints
- SHA-256 integrity hashes to verify content
- Side-by-side and inline diff viewer to compare versions
- Approval workflow with roles: Draft → Review → Approved → Published
- Rollback to a previous version (creates a new version representing the rollback)
- Version metadata: author, timestamp, notes, and change summary
- Locking or branch draft support to avoid edit conflicts (workspace setting)

How versioning works (user-facing)
---------------------------------
1. Every time a document is saved, ISOHelper creates a `DocumentVersion` entry. You can also use 'Save as Version' from the editor to force a version checkpoint with a custom note.
2. Version entries include who saved them, when, and a short note if provided.
3. The Versions view on a Document shows a chronological list of versions with quick actions: Preview, Compare, Restore, and Download.

Viewing versions (Frontend)
---------------------------
1. Open the Document you want to inspect.
2. Click the 'Versions' tab or 'History' button.
3. Click a version to preview it. Use the 'Compare' button on two selected versions to open the diff viewer.

Comparing versions (user-friendly)
---------------------------------
- Use the side-by-side diff viewer to see changes in headings, paragraphs, lists, and placeholders. The viewer highlights additions, deletions, and modified lines.
- Use the inline diff mode for quick scanning when comparing small edits.
- For large documents, comparisons may take a few seconds — the server computes a diff of the stored Markdown bodies.

Approval workflow (simple guide)
--------------------------------
1. Draft: Editors create or edit a document and save versions as drafts.
2. Review: When ready, request a Review. The system notifies Approvers in the workspace (based on role/permission settings).
3. Approve/Request Changes: Approvers can approve the version or request changes with comments. Requesting changes returns the document to Draft state.
4. Publish: After approval, mark the version as Approved and optionally Published. Published versions are the canonical public copies used for exports and audits.

Rollback and restore
--------------------
- If a mistake is discovered, choose a previous version and click 'Restore' or 'Rollback'. The system creates a new version that is a copy of the restored content and marks the action in the audit trail (who restored, when, and a required comment).
- Rollbacks do not delete history — they add to it so the entire timeline remains auditable.

Permissions & roles
-------------------
- Only users with `view_versions` can see version history.
- `create_versions` and `restore_versions` control save/restore actions (usually Editor and Admin roles).
- `approve_versions` is reserved for Approver roles; only they can mark a version as Approved/Published.

API endpoints (non-developer examples)
------------------------------------
- `GET /api/v1/documents/{id}/versions/` — list versions for a document
- `GET /api/v1/documents/{id}/versions/{version_id}` — get version details and download links
- `POST /api/v1/documents/{id}/versions/{version_id}/approve` — approve a version (requires permission)
- `POST /api/v1/documents/{id}/versions/{version_id}/restore` — restore a version (creates a new version)

Troubleshooting (common user issues)
-----------------------------------
- Missing version entries: confirm you saved the document (automatic versioning may be disabled in some workspaces). Check your workspace settings or contact an admin.
- Compare shows no differences: some editors auto-reformat Markdown; use 'Show raw' in the compare view to inspect exact changes.
- Cannot restore: confirm you have `restore_versions` permission; if the restore fails, check server logs or ask your admin to retry.

Tips
----
- Add short, descriptive notes when using 'Save as Version' so collaborators understand the intent of the checkpoint.
- Use the approval comments to give reviewers context — these are stored in the audit trail.
- Regularly publish approved versions to create stable exportable records.

Related files & pages
---------------------
- Frontend versions UI: `frontend/app/documents/[id]/versions/` (versions list and compare pages)
- API routes: `backend/api/routes/versions.py`
- Models: `backend/models/version_models.py` (`DocumentVersion` and related metadata)
- Services: `backend/services/versioning_service.py`

---

(End of Document Versioning section)

## 7. Artifact Management

Overview
--------
Artifacts capture discrete compliance actions and records such as Non-Conformities (NC), Corrective Actions (CA), Audit findings, Management Reviews, Training records, and Complaints. ISOHelper provides a central place to create, track, assign, and report on these items so that corrective workflows are visible and auditable.

Who uses it
-----------
- Quality Managers who track NCs and CAs
- Auditors who record findings and evidence
- HR and Training Coordinators who manage training records
- Process owners who receive assigned actions and close items
- Customer support or compliance teams who log complaints

Key concepts & artifact types
-----------------------------
- Non-Conformity (NC): Records a deviation from a requirement. Includes severity, discovery date, reporter, and linked evidence.
- Corrective Action (CA): An action that addresses the root cause of an NC. CAs can be linked to NCs and have assignees, due dates, and status (Open, In Progress, Verified, Closed).
- Audit finding: Items raised during internal or external audits. Often mapped to clauses and linked to NCs/CAs.
- Management Review: High-level meetings where managers review performance, NC trends, and resource needs. Records actions and decisions.
- Training record: Evidence of completed training sessions, assigned courses, attendees, and expiry/recertification dates.
- Complaint: Customer or stakeholder complaints that may trigger investigations, NCs, or CAs.

How to create and manage artifacts (user-facing)
-----------------------------------------------
1. Navigate to the Artifacts or Quality menu and choose the artifact type (NC, CA, Audit, Review, Training, Complaint).
2. Click 'New' and fill in the required fields: title, description, related clause/template (optional), date, priority/severity, and attach evidence files if available.
3. Assign the artifact to a user or team and set due dates for actions.
4. Save the artifact. The assigned users receive a notification (in-app and optionally email) depending on workspace notification settings.

Statuses and lifecycle
----------------------
- NCs: New → Assigned → Investigating → Root Cause Identified → CA Created → Verified → Closed
- CAs: Open → In Progress → Verified → Closed
- Audit findings: Open → Responded → Closed
- Training: Assigned → Completed → Expired (if recertification required)
- Complaints: New → Investigating → Resolved → Closed

Linking artifacts
-----------------
- Link NCs to the related Document, Template, Clause, or Audit finding for traceability.
- Create a CA from an NC quickly via the 'Create Corrective Action' action; the CA will reference the originating NC.
- Attach evidence files (photos, logs, emails) to artifacts to support investigations and audits.

Notifications & assignments
---------------------------
- When assigned, users receive an in-app notification. Optionally, email notifications can be enabled in Admin → Notifications.
- Assignment reassignment is recorded in the audit trail with previous assignee, new assignee, and timestamp.

Management Review workflows
---------------------------
- Schedule Management Review meetings in the Reviews area. Add agenda items, link artifacts (NCs, CA summaries, audit findings), and record decisions and actions.
- After the meeting, convert decisions into action items (CAs) or assign follow-ups to process owners and set due dates.

Training records & compliance
----------------------------
- Assign courses or training sessions to users or teams. Track attendance and completion evidence (certificates, uploaded files).
- Set recertification intervals; ISOHelper notifies users and admins when training is near expiry.

Analytics & reporting
---------------------
- Artifact dashboards show counts by type, status, severity, owner, and time. Use filters to focus on a workspace, standard clause, or date range.
- Trend charts highlight recurring NCs by clause or process owner to guide root-cause projects.
- Export artifact reports (CSV/PDF) for meetings or audits.

Permissions & audit trail
-------------------------
- Artifact creation and editing require `create_artifacts` / `manage_artifacts` permissions depending on the workspace policy.
- All artifact changes are recorded in the audit trail: who changed what and when. Audit entries include file attachments download records.

Best practices (user-facing)
----------------------------
- Capture evidence as early as possible — photos, timestamps, and initial findings help investigations.
- Link artifacts to clauses and documents for clear traceability during audits.
- Use templates for recurring audit findings or standard CA workflows to speed recording.
- Keep CA descriptions focused on root cause and corrective measures; use comments to record investigation notes.

Troubleshooting (common user issues)
-----------------------------------
- Missing notifications: check your profile notification preferences and Admin → Notifications settings.
- Unable to attach files: confirm file size limits in Admin → Settings (large files may be blocked) and try smaller attachments.
- Artifact counts don't match expectations: apply date and workspace filters to ensure you are viewing the correct scope.

Related files & pages
---------------------
- Frontend artifacts UI: `frontend/app/artifacts/` (create, list, edit pages)
- API routes: `backend/api/routes/artifacts.py`
- Models: `backend/models/artifact_models.py` (artifact types and relationships)
- Services: `backend/services/artifact_service.py` (creation, workflow, analytics)

---

(End of Artifact Management section)

## 8. Gap Analysis Engine

Overview
--------
The Gap Analysis Engine helps you compare your existing processes, documents, or audit evidence against a chosen ISO standard and generates a list of gaps, recommended actions, and mapped clauses. It's designed to speed up readiness assessments and create an actionable roadmap for compliance work.

Who uses it
-----------
- Quality Managers preparing for certification
- Consultants performing readiness assessments for clients
- Internal audit teams conducting baseline gap analysis

Key capabilities
----------------
- Upload evidence: Excel, CSV, Word, PDF, or structured checklists
- Automatic mapping to standard clauses where possible
- Generate a prioritized gap list with recommended actions and suggested owners
- Export gap reports (CSV/PDF) and create linked artifacts (NC/CA) from findings
- Track remediation progress and see time-to-close metrics

How to run a gap analysis (user-facing)
-------------------------------------
1. Navigate to Gap Analysis → New Analysis.
2. Choose the ISO standard (for example ISO 9001) and the target scope (site, department, or full organization).
3. Upload your evidence files or use a sample checklist template provided by ISOHelper.
4. Configure analysis options: auto-map clauses (on/off), sensitivity (Lenient/Strict), and whether to create artifacts automatically for high-severity gaps.
5. Click 'Run Analysis'. The engine will parse files, map evidence to clauses, and create a gap summary. This usually completes in seconds to minutes depending on file size.

Understanding the results
-------------------------
- Gap Summary: a high-level table showing the number of gaps by clause and severity.
- Findings list: each finding includes a description, suggested remedial action, suggested owner, and a confidence score if auto-mapped.
- Mapped evidence: links to uploaded files and the exact location (page/section) where evidence was found when available.

Creating remediation plans
-------------------------
- Convert findings into Corrective Actions (CAs) directly from the results with one click. The CA will reference the originating finding and include suggested due dates and owners.
- Export a remediation roadmap (CSV/PDF) for management review or to assign in bulk to teams.

Integrations and automation
---------------------------
- Auto-create artifacts: enable this during analysis to automatically create NCs/CAs for high-severity findings.
- Template mapping: use workspace templates to standardize how findings are recorded and which fields are required when converting to artifacts.
- Notifications: assigned owners receive notifications for created CAs or NCs and see them in their task list.

Reports & exports
-----------------
- Export full analysis as a PDF report (summary + findings + evidence links) or download the raw findings as CSV for further processing.
- Use the API to export results programmatically: `GET /api/v1/gap-analysis/{id}/export`.

Accuracy & tips
---------------
- Auto-mapping uses heuristics and text-matching — review low-confidence matches before converting them to actions.
- Use the sensitivity setting to control false positives: Lenient finds fewer items (higher precision); Strict finds more (higher recall).
- Large collections of documents increase analysis time; consider uploading smaller batches and merging results.

Troubleshooting (common user issues)
-----------------------------------
- Analysis fails or times out: try smaller file batches and check server status; contact admin if the service is down.
- Missing evidence links: some file formats (scanned PDFs) may not include extractable text. Use OCR'd PDFs or upload source documents when possible.
- Auto-mapping confidence low: review the mapping, adjust sensitivity, or add manual mappings for templates you use often.

Related files & pages
---------------------
- Frontend gap analysis pages: `frontend/app/gap-analysis/`
- API routes: `backend/api/routes/gap_analysis.py`
- Services: `backend/services/gap_analysis_service.py` (parsing, mapping, reporting)
- Models: `backend/models/gap_analysis_models.py`

---

(End of Gap Analysis Engine section)

## 9. Advanced Analytics

Overview
--------
Advanced Analytics provides dashboards, trend analysis, and customizable reports that help organizations monitor compliance performance, spot trends, and prioritize improvement efforts. The analytics layer aggregates data from documents, artifacts, gap analyses, and exports to produce actionable insights.

Who uses it
-----------
- Quality Managers tracking NC/CA trends and time-to-close metrics
- Leadership teams reviewing compliance health across workspaces or sites
- Data analysts extracting metrics for quarterly reports

Key capabilities
----------------
- Pre-built dashboards: Artifact summary, CA aging, Audit findings, Training coverage, Gap Analysis trends
- Custom reports: Create and save custom charts and tables using filters and date ranges
- Time-series trend analysis: visualize trends over time for NCs, CAs, training compliance, and audit findings
- Cost tracking: attribute estimated costs to NCs/CAs and report on cumulative cost of non-conformities
- Predictive insights (optional): forecast likely hotspots using historical trend data (requires enabled predictive module)
- Alerts & thresholds: configure alerts for KPI breaches (e.g., overdue CAs > 10%)

Using dashboards (user-friendly)
-------------------------------
1. Open Analytics → Dashboards.
2. Choose a pre-built dashboard (for example, 'Artifact Summary' or 'CA Aging') or open a saved custom report.
3. Use filters to select workspace, date range, standard clauses, or owners. Charts update live.
4. Click individual data points in charts to drill into the underlying artifacts or documents.

Creating custom reports
-----------------------
- Click 'New Report', select the data source (Artifacts, Documents, Gap Analysis), and choose dimensions (e.g., status, owner) and metrics (e.g., count, average time-to-close, total estimated cost).
- Save reports to your personal library or share with workspace admins.

Cost tracking & attribution
---------------------------
- When creating CAs or NCs, users can optionally add an estimated cost (labor, remediation, fines). The analytics engine aggregates these values to show cumulative cost by period, owner, or clause.
- Use cost reports in Management Review meetings to prioritize investments.

Predictive insights (optional module)
------------------------------------
- If your workspace has the predictive module enabled, ISOHelper can use historical trends to highlight where NCs are likely to occur and suggest preventive actions.
- Predictive insights are best-effort suggestions — always validate with process owners before taking action.

Alerts & scheduled reports
-------------------------
- Configure KPI alerts in Admin → Analytics to receive notifications when thresholds are crossed (email or in-app).
- Schedule recurring reports (daily/weekly/monthly) to be sent to stakeholders via email or to export locations (SFTP/email attachments).

Exporting analytics data
------------------------
- Download charts and tables as PNG/CSV/PDF for inclusion in board packs or audits.
- Use the API for programmatic exports: `GET /api/v1/analytics/export?report_id=...&format=csv`.

Best practices & tips
---------------------
- Start with the pre-built dashboards to get immediate value; customize reports as you become familiar with filters and dimensions.
- Use consistent tagging (clauses, process owner, cost centers) to make cross-workspace comparisons meaningful.
- Regularly review CA aging and escalate overdue items in Management Review meetings.

Troubleshooting (common user issues)
-----------------------------------
- Dashboard shows stale data: confirm background jobs are running and that caching is not delaying updates (ask admin if unsure).
- Charts are empty: check date filters and workspace selection — some dashboards default to the current month.
- Predictive module missing: confirm your workspace subscription includes the predictive analytics module and that the module is enabled in Admin settings.

Related files & pages
---------------------
- Frontend analytics UI: `frontend/app/analytics/` (dashboards and report builder)
- API routes: `backend/api/routes/analytics.py`
- Services: `backend/services/analytics_service.py` (aggregation, caching, export)
- Models: `backend/models/analytics_models.py` (report definitions, saved queries)

---

(End of Advanced Analytics section)

## 10. Workspaces & Multi-Tenancy

Overview
--------
Workspaces let you separate work by client, department, or site. Multi-tenancy support enables multiple isolated workspaces running within the same ISOHelper instance while sharing the same application codebase. Workspaces contain their own templates, documents, artifacts, and settings.

Who uses it
-----------
- Administrators who manage multiple clients or departments
- Consultants working across several client workspaces
- Team members who need to switch context between different organizations or projects

Key concepts
------------
- Workspace: an isolated container that holds templates, documents, artifacts, users, and settings.
- Membership & roles: users are invited into workspaces with specific roles (Admin, Editor, Viewer, Approver) that control permissions.
- Isolation: data and templates are workspace-scoped by default; cross-workspace sharing requires explicit actions (publish to marketplace or export/import).

Creating a workspace (user-friendly)
----------------------------------
1. Navigate to the Workspace selector (top-left) and choose 'Create Workspace' or go to Admin → Workspaces.
2. Fill in workspace name, description, default language, and optionally upload a logo.
3. Set privacy: Public (visible to organization) or Private (invite-only).
4. Click 'Create'. You will be the first Admin of the workspace and can then invite members.

Inviting users and membership
-----------------------------
1. Open Workspace → Members → Invite.
2. Enter email addresses, choose a role for each invitee, and optionally add a welcome note.
3. Invited users receive an email with a sign-up or accept link. Once accepted, they appear in the Members list.

Roles & permissions (simple guide)
----------------------------------
- Admin: Full permissions — manage workspace settings, invite users, publish templates, and manage billing (if applicable).
- Editor: Create and edit documents and templates, create artifacts, and save versions.
- Approver: Review and approve versions or artifacts as part of the approval workflow.
- Viewer: Read-only access to workspace content.

Switching workspaces
--------------------
- Use the workspace selector (top-left) to switch context. The UI reloads to show workspace-specific templates, documents, and artifacts.
- Bookmarks, saved reports, and personal preferences can persist across workspaces depending on the setting; check Admin → Settings if you expect cross-workspace persistence.

Workspace settings & defaults
-----------------------------
- Language: workspace default language for generated documents and UI fallback.
- Notification defaults: in-app/email preferences, who receives escalation emails for overdue CAs.
- Automation: workspace-level toggles for auto-creating CAs from gap analysis or enabling predictive analytics.

Cross-workspace sharing
-----------------------
- Publish templates to the Template Marketplace to share them across workspaces.
- Export/import templates and documents as bundles to move content between workspaces.

Billing & subscription notes (if applicable)
------------------------------------------
- Some deployments may associate a billing account with a workspace. Admins can view usage and billing under Admin → Billing.

Monitoring workspace activity
----------------------------
- Workspace activity logs show recent actions: who created documents, who ran analyses, and artifact changes.
- Use workspace statistics to see document counts, artifact counts, and active users over time.

Troubleshooting (common user issues)
-----------------------------------
- Invitations not received: check spam/junk folders and ensure your admin email templates are configured.
- Missing workspace content: confirm you have switched to the correct workspace and have the necessary permissions.
- Unable to create workspace: contact your system admin if the Create action is restricted by global policy.

Related files & pages
---------------------
- Frontend workspaces UI: `frontend/app/workspaces/` (selector, settings, members)
- API routes: `backend/api/routes/workspaces.py`
- Models: `backend/models/workspace_models.py`
- Services: `backend/services/workspace_service.py`

---

(End of Workspaces & Multi-Tenancy section)

## 11. Template Marketplace

Overview
--------
The Template Marketplace is a central place to discover, publish, and install templates. It enables template authors to share templates across workspaces and provides a simple licensing and versioning model so workspaces can adopt high-quality templates quickly.

Who uses it
-----------
- Template authors who want to publish reusable templates
- Workspace admins who install templates into their workspace
- Consultants who package and sell templates for clients

Key capabilities
----------------
- Publish templates to the Marketplace with metadata, preview, and licensing terms
- Browse, search, and install marketplace templates into a workspace
- Template licensing: free, paid, or custom license types (depends on deployment)
- Versioning: marketplace templates are versioned and updates can be pushed by authors
- Install as workspace-local copy: installations create a workspace-scoped copy that can be edited locally

Publishing a template (author guide)
-----------------------------------
1. Prepare your template: ensure metadata (title, description, standard, clause), sample data, and preview images are included.
2. In Templates → My Templates select the template and choose 'Publish to Marketplace'.
3. Fill in marketplace details: pricing (if applicable), license type, author info, and optional tags.
4. Submit for review: depending on your deployment, Marketplace submissions may require admin approval before going live.

Installing templates (workspace admin)
--------------------------------------
1. Open Marketplace → Browse and search for templates by standard, clause, tags, or author.
2. Click a template to view details and preview rendered output with sample data.
3. Click 'Install' to add it to your workspace. You will get a workspace-local copy that your editors can modify.
4. If the template is paid, follow the billing/checkout flow (deployment-dependent).

Updating & versioning marketplace templates
-----------------------------------------
- When authors publish a new version, workspaces that installed the template receive a notification that an update is available.
- Workspace admins can review updates and choose to apply them (which creates a new version in the workspace) or ignore if they maintain local customizations.

Licensing & billing notes
-------------------------
- Marketplace licensing and billing workflows depend on your deployment. Some installations use a free-only marketplace; others support paid templates with per-install or subscription licensing.
- Admins can view purchased templates and licensing details under Admin → Marketplace Purchases.

Security & quality checks
-------------------------
- Marketplace submissions are scanned and reviewed by admins for quality and compliance. Avoid including secrets in template files.
- Preview templates with sample data before installing to ensure they meet your workspace standards.

Troubleshooting (common user issues)
-----------------------------------
- Cannot install a template: confirm you have `manage_templates` permission in the workspace and that billing (if required) is completed.
- Marketplace search returns no results: try broader search terms or check filters (standard, language, tags).
- Updates conflict with local edits: decide whether to accept the update (overwriting local changes) or keep the local version. Consider exporting local edits before applying updates.

Related files & pages
---------------------
- Frontend marketplace UI: `frontend/app/marketplace/`
- API routes: `backend/api/routes/marketplace.py`
- Services: `backend/services/marketplace_service.py`
- Models: `backend/models/marketplace_models.py` (listings, purchases, licenses)

---

(End of Template Marketplace section)

## 12. Export & Sharing

Overview
--------
Export & Sharing covers how to create branded exports, share documents with stakeholders, and manage retention policies for exported artifacts. ISOHelper provides flexible export formats and secure sharing links for internal and external distribution.

Who uses it
-----------
- Editors and document owners preparing distribution packages
- Marketing or communications teams that handle external sharing
- Auditors and regulators who need authenticated access to exported records

Key capabilities
----------------
- Export formats: DOCX, PDF, HTML, and ZIP bundles (documents + attachments)
- Branded exports: choose workspace branding, custom headers/footers, and cover pages
- Secure sharing: time-limited, tokenized download links and optional password protection
- Retention & policies: configure how long exported files are kept on the server and automatic purge rules
- Bulk exports: export multiple documents at once into a single ZIP

How to export a document (user-facing)
-------------------------------------
1. Open the Document detail page and click 'Export'.
2. Choose formats (DOCX, PDF, HTML) and select an Export Template for branding if desired.
3. Toggle 'Include attachments' to bundle images and supporting files.
4. Click 'Start Export'. When the export completes you will see download links and notifications.

Branded exports & templates
---------------------------
- Export Templates contain layout options (cover page, header/footer, logo placement), default page size, and optional legal footers.
- Admins can create and upload Export Templates in Admin → Exports. Workspace-level templates override global defaults.

Sharing exports securely
------------------------
- Generate a secure share link from the Export panel. Choose link expiry (hours/days) and whether to require a password.
- Copy the link or send it via email from the app. Recipients can download without signing in if the link allows public access.
- For internal sharing, prefer 'Require Sign-in' so that downloads track the user in the audit trail.

Retention & cleanup policies
----------------------------
- Admins can configure retention policies for exported files (e.g., keep exports for 30 days). Older exports are automatically purged to save storage.
- Exports referenced in an audit or compliance package can be archived to prevent automated deletion.

Bulk exports and scheduling
---------------------------
- Use Bulk Export to select multiple documents and export them into a single ZIP for distribution.
- Schedule recurring exports (e.g., monthly reports) in Admin → Exports → Scheduled Jobs and send them to email or an SFTP target.

Troubleshooting (common user issues)
-----------------------------------
- Export fails or times out: try exporting a single format (DOCX only) or reduce included attachments. If recurring, check background worker status.
- Missing images in export: confirm images are attached to the document and are available in workspace storage.
- Share link not working: verify link expiry and password protection settings. For 'Require Sign-in' links, confirm recipient has workspace access.

Related files & pages
---------------------
- Frontend export UI: `frontend/app/documents/[id]/export/`
- API routes: `backend/api/routes/export.py`
- Services: `backend/services/export_service.py`
- Models: `backend/models/export_models.py`

---

(End of Export & Sharing section)




## 13. Authentication & RBAC

Overview
--------
Authentication and Role-Based Access Control (RBAC) protect your workspace data and ensure people only see and do what they're allowed to. This section explains how to register, sign in, manage roles, and secure API endpoints — all written for non-developers.

Who uses it
-----------
- End users who sign in to view and work on documents and artifacts
- Workspace admins who invite members and assign roles
- IT/Security who configure system-wide authentication settings

Key concepts (user-facing)
--------------------------
- Authentication: proving who you are (email + password, SSO).
- Authorization: what you are allowed to do (roles and permissions).
- Roles: named collections of permissions such as Admin, Editor, Approver, Viewer.
- Permissions: fine-grained actions like `create_documents`, `manage_templates`, `approve_versions`.
- Tokens: short-lived access tokens let the frontend call the API on your behalf; refresh tokens renew access without re-entering credentials.

How to sign up and sign in (user-friendly)
-----------------------------------------
1. Sign up: If self-registration is enabled for your deployment, click 'Sign up' on the login page, enter your name, email and a password, then confirm your email if required.
2. Invite: Workspace Admins can invite users via Admin → Workspaces → Members → Invite. Invited users receive an email with an accept link.
3. Sign in: Enter your email and password on the login page, or use a configured Single Sign-On (SSO) provider if your organization has one (for example, Google or Microsoft).
4. Forgot password: use the 'Forgot password' link to request a password reset email.

Roles & common defaults
-----------------------
- Admin: full control — manage workspace settings, invite users, publish templates, and manage billing (if available).
- Editor: create and edit documents and templates, run gap analyses, and create artifacts.
- Approver: review and approve document versions and artifact closures.
- Viewer: read-only access.

Permissions (how they map to user tasks)
---------------------------------------
- `create_documents`: ability to generate new documents.
- `edit_templates`: create or modify templates in the workspace.
- `create_artifacts`: open NCs, CAs, or audit findings.
- `approve_versions`: approve or publish a document version.
- `manage_users`: invite or change roles for workspace members.

How admins manage users and roles (user-facing)
---------------------------------------------
1. Open Admin → Workspaces → Members for the workspace you manage.
2. Invite a new member by entering their email and choosing a role.
3. To change a role, find the member in the list, click the role dropdown and select the new role. Changes are recorded in the audit trail.
4. To revoke access, remove the member from the workspace; this action is recorded with timestamp and actor.

Single Sign-On (SSO) and enterprise login
-----------------------------------------
- Many deployments support SSO (SAML, OIDC) so users sign in with corporate credentials. If your organization has SSO enabled, use the 'Sign in with <Your Provider>' button on the login page.
- SSO reduces password management overhead and can enforce organization-wide policies like MFA (multi-factor authentication).

Token behavior (simple explanation)
----------------------------------
- Access tokens are short-lived (for example, 15 minutes) and are used for every API request.
- Refresh tokens are longer-lived and allow the client to request a new access token without prompting the user to log in again.
- If you sign out, the client removes tokens; some deployments also revoke tokens server-side for immediate logout.

Securing endpoints (what users should know)
------------------------------------------
- When you use the API (Postman or automation), include your `Authorization: Bearer <access_token>` header.
- Keep tokens private — do not paste them into public chat or code samples with real tokens.
- For shared automated integrations, use service accounts or API keys issued by your admin and store them securely.

Multi-factor authentication (MFA)
--------------------------------
- If enabled, MFA requires an extra verification step (SMS, authenticator app, or hardware key) when signing in. Follow the prompts in your Profile → Security to enroll.

Common issues & user troubleshooting
-----------------------------------
- Can't sign in: check email/password, confirm your registration email, or ask an Admin to resend an invite.
- Missing permissions: contact your Workspace Admin to request a role change or specific permission.
- Token expired errors: sign out and sign back in, or use the refresh flow in the UI (usually automatic).
- SSO problems: contact your IT team — SSO configuration is managed by administrators.

Audit trail and accountability (user-facing)
------------------------------------------
- Role changes, invites, and removals appear in the workspace audit log with actor and timestamp.
- Approved versions, exported files, and artifact closures are also logged so you can trace who performed important actions.

Related files & pages
---------------------
- Frontend auth pages: `frontend/app/auth/` (login, signup, password reset) and `frontend/app/profile/` (MFA & tokens).
- API routes: `backend/api/routes/auth.py` (login, refresh, revoke), `backend/api/routes/users.py` (invite, list, roles).
- Services: `backend/services/auth_service.py`, `backend/services/user_service.py`.
- Config: `config/settings.py` for token lifetime, SSO settings, and security toggles.

Tips
----
- Use SSO where available to reduce password issues and centralize access control.
- Use Approver roles sparingly — limit to users who need to sign off on official documents.
- Regularly review workspace members and remove inactive users to reduce exposure.

(End of Authentication & RBAC section)

## 14. Deployment & CI/CD

Overview
--------
This section helps non-developer users and site administrators understand the deployment and CI/CD story for ISOHelper. It covers development vs production, Docker basics, database migrations, and a recommended GitHub Actions pipeline that runs tests and builds for each PR.

Who uses it
-----------
- DevOps teams responsible for deploying the app
- Administrators who manage staging and production environments
- Developers preparing a release or contributing changes

Deployment types (simple)
-------------------------
- Development: run locally using the instructions in Configuration & Setup.
- Staging: an environment that mirrors production where final QA runs occur.
- Production: the public-facing environment, typically behind load balancers and with high-availability considerations.

Docker basics (user-friendly)
----------------------------
- ISOHelper can be packaged into Docker images for easy deployment. A typical deployment includes two services: the backend (FastAPI) and the frontend (Next.js). Optional extras are a worker (for background jobs) and a database service (Postgres) if not using managed DBs.
- A simple `docker-compose.yml` brings these services up together for staging or small deployments.

Database migrations
-------------------
- Use Alembic (or the project's migration tooling) to manage schema changes. Before deploying a new release, run migrations against the staging DB and verify the application starts normally.
- Typical commands (admin):

```powershell
cd C:\dev\isohelper\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

CI/CD recommended workflow (GitHub Actions - user-facing)
-----------------------------------------------------
1. Developers open a Pull Request (PR) to the `dev` branch.
2. GitHub Actions runs the pipeline:
  - Install Python & Node deps
  - Run the test suite (`pytest`) and upload coverage
  - Linting and type checks (optional)
  - Build frontend artifacts and run a lightweight frontend test
3. If all checks pass, a reviewer approves and the PR is merged to `dev`.
4. Periodic releases are cut from `dev` to `main` and a deploy job runs that builds Docker images and pushes them to the registry.

Security & secrets (user-facing)
--------------------------------
- Store secrets (database credentials, SSO secrets, API keys) in your cloud provider's secret store or GitHub Actions Secrets — never in the repository.
- Use role-based service accounts for CI that only have the minimum rights needed to deploy.

Monitoring & rollback (user-facing)
----------------------------------
- Monitor health endpoints (`/health`), logs, and key metrics (error rate, request latency, background job queue length).
- For production incidents, roll back to the previous working release image while you diagnose the issue.

Simple example: GitHub Actions job summary (non-technical)
------------------------------------------------------
- On PR: install deps → run tests → report results. If tests fail, the PR shows failing checks.
- On release: build Docker images → push to registry → trigger deployment (or create a release artifact for Ops to deploy).

Troubleshooting common issues (user-facing)
-----------------------------------------
- Failed migrations: restore a pre-release DB snapshot and re-run migrations in a test/staging environment until they succeed.
- Deployment failing due to secrets: verify the environment has the expected secrets (DB URL, secret key) and that they have correct formatting.
- Frontend/backend CORS issues: ensure `ALLOWED_ORIGINS` includes the frontend origin and that the deployed frontend points to the correct backend URL.

Related files & pages
---------------------
- Example Docker files: `docker/` or root-level `Dockerfile` (check the repo for exact paths)
- Example `docker-compose.yml` for staging (if present)
- CI workflows: `.github/workflows/` (look for `ci.yml` or similar)
- Migrations: `backend/migrations/` or Alembic config in `backend/alembic.ini`

Tips
----
- Run a smoke test after each deployment: a simple API call to the health endpoint and a quick sample generation to verify services are working.
- Keep staging as close to production as possible to reduce surprises during releases.

(End of Deployment & CI/CD section)




