/**
 * jira-config.js
 * ─────────────────────────────────────────────────────────────
 * All Jira field mappings, custom fields, and status definitions.
 * Edit this file to match YOUR Jira project setup.
 *
 * How to find custom field IDs:
 *   1. Go to Jira → Project Settings → Fields
 *   2. Or call: GET /rest/api/3/field  (add /rest/api/3/field to your Jira URL in browser)
 *   3. Custom fields have IDs like "customfield_10001"
 * ─────────────────────────────────────────────────────────────
 */

const JIRA_CONFIG = {

  // ── Issue Type ──────────────────────────────────────────────
  // Change to "Task" if your project uses Tasks instead of Subtasks
  issueType: 'Subtask',

  // ── Summary prefix format ───────────────────────────────────
  // Use {date} and {summary} as placeholders
  // Example results: "[10-Mar-2026] Fix login bug"
  summaryFormat: '[{date}] {summary}',

  // ── Status Definitions ──────────────────────────────────────
  // These are the statuses shown in the dropdown.
  // 'jiraName'  → must match EXACTLY what Jira calls the transition (check your workflow)
  // 'label'     → display name shown in the UI
  // 'color'     → CSS color for the pill
  // 'cssClass'  → maps to .status-pill.{cssClass} in style.css
  statuses: [
    {
      jiraName: 'To Do',
      label:    'To Do',
      color:    '#aaaaaa',
      cssClass: 'todo',
    },
    {
      jiraName: 'In Progress',
      label:    'In Progress',
      color:    'var(--accent)',
      cssClass: 'inprogress',
    },
    {
      jiraName: 'Done',
      label:    'Done',
      color:    'var(--green)',
      cssClass: 'done',
    },

    // ── Add more statuses here as needed ──────────────────────
    // {
    //   jiraName: 'In Review',
    //   label:    'In Review',
    //   color:    '#ffd96d',
    //   cssClass: 'inreview',   // also add .status-pill.inreview to style.css
    // },
    // {
    //   jiraName: 'Blocked',
    //   label:    'Blocked',
    //   color:    '#fa6d8a',
    //   cssClass: 'blocked',
    // },
  ],

  // ── Status → CSS class mapping ──────────────────────────────
  // Maps a Jira status name to a task-item border class (st-*)
  // Extend this if you add custom statuses above
  statusClassMap(jiraStatusName) {
    if (!jiraStatusName) return 'todo';
    const n = jiraStatusName.toLowerCase();
    if (n.includes('progress'))                         return 'inprogress';
    if (n.includes('review'))                           return 'inprogress'; // treat review as in-progress visually
    if (n.includes('done') || n.includes('closed') || n.includes('resolv')) return 'done';
    if (n.includes('block'))                            return 'error';
    return 'todo';
  },

  // ── Custom Fields ───────────────────────────────────────────
  // Add any custom fields your project requires on every subtask.
  // These are merged into the Jira issue body on creation.
  //
  // Format:
  //   fieldId: value
  //
  // Common value shapes:
  //   Plain text:       "some text"
  //   Number:           42
  //   Select option:    { value: "Option Name" }
  //   Multi-select:     [{ value: "Option A" }, { value: "Option B" }]
  //   User picker:      { accountId: "user-account-id" }
  //   Date:             "2026-03-10"   (YYYY-MM-DD)
  //   URL field:        "https://example.com"
  //
  customFields: {
    // ── Examples — uncomment and fill in your real field IDs ──

    // Sprint (next-gen projects use "customfield_10020"):
    // customfield_10020: { id: 1234 },   // sprint ID (integer)

    // Story Points:
    // customfield_10016: 1,

    // Team / Squad picker:
    // customfield_10100: { value: 'Backend Team' },

    // Epic Link (classic projects):
    // customfield_10014: 'PROJ-456',

    // Priority (built-in, not custom — but can override here):
    // priority: { name: 'Medium' },

    // Environment label:
    // customfield_10200: { value: 'Production' },

    // Reporter override (defaults to token owner):
    // reporter: { accountId: 'your-account-id' },
  },

  // ── Fields to fetch on Sync ─────────────────────────────────
  // When syncing from Jira, these fields are fetched per subtask.
  // Add any custom field IDs you want pulled back into the app.
  syncFields: [
    'summary',
    'status',
    'assignee',
    // 'customfield_10016',   // story points
    // 'customfield_10020',   // sprint
  ],

};