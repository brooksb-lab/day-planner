# Day planner: handoff

Read this whole file before changing anything.

## What it is

A personal daily planner for Brooks (single user). It sits on top of Google Calendar and protects open time for studio work on his apparel line. Live at https://brooksb-lab.github.io/day-planner/ and installed on his iPhone as a Home Screen web app. He tests every change on the iPhone, so iPhone layout matters as much as desktop.

## How to work with Brooks

- Direct and terse. No em dashes. No corporate language. No over-explaining.
- He expects changes right the first time. Test before you report done.
- Every change: edit `index.html`, bump the version (below), test, commit, push to `main`. GitHub Pages deploys in about a minute. Tell him the version number to refresh to.
- Short replies: what changed, what to check, version number.

## Files

```
index.html             the whole app: HTML, CSS and JS in one file (~3,700 lines)
sw.js                  service worker, network-first, no stale cache
manifest.webmanifest   Home Screen app manifest
icons/                 app icons, sun/moon, Claude mark
tests/smoke.py         headless smoke test (desktop + iPhone sizes)
```

No build step, no framework, no server. Plain JS inside one IIFE at the bottom of `index.html`.

## Versioning (every push)

- `APP_VERSION` in `index.html`, format `YYYY.MM.DD-N` (current `2026.10.25-78`).
- `CACHE` in `sw.js`, `day-vN` with the same N.
- He sees the version at the very bottom of the sidebar (desktop) and of More (iPhone).

## Back end (all in the browser)

- **Google Calendar**: REST API with Google Identity Services sign-in. `gcall(tool, args)` wraps it with tool names `list_calendars`, `list_events`, `create_event`, `update_event`, `delete_event`, `move_event` (shaped like the claude.ai calendar connector this started on; `S.mcp.callTool` returns `{payload}`). Edits never email guests.
- **To-dos and settings**: one JSON file in the Google Drive appData folder, cached in localStorage (`plannerStore`). `S.db.collection(name).doc(id)` / `.add()` / `.update()` / `.delete()` / `onSnapshot`. Collections: `todos`, `settings` (doc `main`), `aliases`.
- **Claude bar**: Anthropic Messages API with his own key in localStorage (`anthropicKey`). Tools are in `TOOLS` (add/update/complete to-dos, schedule, settings).
- **Weather**: Open-Meteo, no key. **Geocoding**: Nominatim, cached in localStorage `geoCache`.
- Setup needs `gClientId` (OAuth web client ID, authorized origin `https://brooksb-lab.github.io`) in localStorage; the setup screen asks for it.

## Code map (section comments in index.html)

state, calendars, settings (`CFG_DEFAULTS`, `cfg()`, `saveCfg()`), events (`parseEvent`, `allEvents`), todos (db), undo/redo (`pushUndo(label, undoFn, redoFn)`), calendar writes, tabs (`TABS`), render (`render()`, `schedule()`), to-do lists, app shell + iOS layout, weather, pane sizing, leave-by travel, morning brief, free time, recurring to-dos, quick add, interactions, drag engines, swipe on to-dos, tap-to-create, aliases for read-only events, check-off, event sheet (change calendar), Claude bar, Google/Drive/Anthropic adapters, boot.

Key state: `S` (tab, calendars, events, todos, paneMode, split, aliases, doneOpt, swiping, lstDrag). `render()` rebuilds `#main` and skips while a drag, swipe or animation is running (guard at the top of `render`).

## Data model

- **Calendars**: `calKind()` maps by name: personal (primary), work (his own "CLO" calendar; free/busy subscriptions and @clo3d.com are filtered out), fun, meal, between, studio, body, admin, social, bday (Birthdays), tasks→admin, hol (holidays). Color comes from Google's calendar color (`backgroundColor`), else `--c-<kind>`, else a per-name override in `cfg().calColors`.
- **Routing**: `guessCal(text)` picks a calendar for new items by keywords.
- **To-do**: `{title, notes, pri, cal, est, status: open|scheduled|done, order, list, star, eventId, calId, start, doneAt, repeat, repeatTime, seriesId, showFrom}`. Scheduled to-dos link to their event (`eventId`, plus `planner:todo/<id>` in the event description).
- **Lists**: `cfg().lists = [{id, name, color}]`. First list id `inbox`. Items without `list` belong to `inbox`. Starred items get a tint in their list color.
- **Aliases**: local names and "show as another calendar" for read-only events (work Busy blocks). Never written to Google. Keys: `ev|id`, `base|cal|recurringId`, slot.
- **Done for plain events**: a `✓ ` prefix on the Google title. Check-offs show instantly via `S.doneOpt` and save after.
- **Samples**: events with description `planner:sample` and titles `Sample · …`. "Clear samples" in the sidebar deletes them.

## Layout

- Desktop: a macOS-style window (BrooksOS look) with menubar, title bar tabs (Day, 2 Day, Week) and a hideable sidebar. The old "Day" look is retired; keep `theme-day` CSS untouched or delete it.
- iPhone (`IOS_MQ`, max-width 560px → `body.ios`):
  - glass header `#iosHead` (`#iosNav` title + icons) floating over content;
  - bottom `#iosTabs` segmented control: Day, 2 Day, Week (pill is draggable);
  - page swiping between tabs is off; sideways swipes on the calendar move through days;
  - More ("…" icon) slides in as a full-height panel (the desktop sidebar);
  - timelines run edge to edge, everything else has a 16px inset.
- Panes: every tab is timeline + lists with a draggable divider and three layout modes. Morning/Evening/Tomorrow/To-do views were removed as tabs (functions still in the file, unused).
- Day / 2 Day / Week are one strip of days (`viewStrip`): `S.dayOff` = first visible day relative to today, `visCols()` = 1 / 2 / 7 (3 on iPhone week). The strip renders `STRIP_R` (7) days either side and snaps per day (`.pane-strip`, column width from container query `100cqw`). Scrolling updates `S.dayOff` and the headers (`stripScroll`, `stripHeadPaint`); near the strip ends it re-renders centered. ‹ Today › buttons use `stripStep`. The event window (`windowRange`) follows `S.dayOff` in 14-day blocks.
- Lists fold with the chevron (`collapsed` on the list in `cfg().lists`).
- Known limit: the iOS Home Screen web app stops short of the bottom edge (a status-bar-height band). Content can't render there. Don't try to stretch past `innerHeight`; it pushes the tab bar off screen (tried twice).

## Interactions to keep working

- Drag to-dos between lists, onto the timeline (schedules), and events off the timeline into a list (unschedules; plain events become to-dos).
- Drag events to move/resize (on touch: press and hold first; holding the bottom edge resizes); in Week, across days.
- Tap an editable event or a to-do's text: bottom sheet (`openSheet`) to edit title, time, calendar, list, color, location, notes; mark done, star, delete. Tap a read-only block: rename / show as another calendar (local).
- Item colors are Google event colors (`EV_COLORS`, `colorId`); to-dos keep `color`, and it carries across scheduling and unscheduling.
- Check off calendar blocks: quick swipe right on iPhone, hover circle on desktop, or the sheet.
- Swipe to-dos: right = done, left = tomorrow, far left = delete.
- Scheduled to-dos not checked off carry over to today at the same time (`carryOver`, moves the Google event). Checked-off items drop out of lists the day after.
- Press and hold empty timeline space, drag to place, let go to name a new event.
- Overlapping events fan out (Google Calendar style), later ones on top. Overlap is decided by real times; short blocks never grow into the next event.
- Pinch the timeline (ctrl/⌘ + scroll on desktop) to change hour height; saved as `hourHeight`. Re-renders during the pinch re-attach the touch targets hidden so the gesture keeps reporting.
- To-dos have title, notes, location, list, estimate, calendar, color; all of it goes onto the event when scheduled. Priority badges (P1–P3) are hidden; stars replace them.
- Split screen: one value, `--tlF` (timeline share, 0 = list only, 1 = timeline only), set inline on `.pane`. Mode buttons, the handle and flings all go through `animatePane` (critically damped spring in JS). No CSS transitions on the layout. Drag follows the finger and stays where released; a fling (>0.7px/ms, still moving) or a drag near an edge opens fully. `applyCfg` won't overwrite the mode mid-drag or mid-animation.
- Dragging an event or to-do to the left/right edge of the calendar steps a day (every 650ms while held), on desktop and iPhone; drop lands on that date.
- Event taps on touch open from `pointerup` (iOS drops delegated clicks on plain divs); the following click is swallowed for 700ms.
- Short events show the time after the title with a `|`.
- Swipe a notice up or sideways to dismiss it.
- Undo/redo for every write.

## Testing

```
pip install playwright && python -m playwright install chromium
python tests/smoke.py        # desktop + iPhone, prints page errors (should be [])
```

For deeper checks, copy `index.html` to a scratch folder, insert `window.__T={S,schedule};` before the last `})();`, inject fake calendars/events into `S.calendars`, `S.calMap`, `S.events`, and stub `S.mcp = {callTool, invalidate, watchTool}` to record calls. Use CDP touch events for swipe tests. Screenshot at 390x844 and 1280x860, light and dark.

## Open threads

- iPhone polish is ongoing; he sends screenshots. Match iOS proportions.
- A native Xcode shell (WKWebView, `~/Projects/DayWeb` on his Mac) exists but is parked. It has his credentials baked in and must stay private.
- An older native SwiftUI/EventKit project lives at `~/Projects/Day` on his Mac. Not in use.
- The CLO work subscription (brooks@clo3d.com) is filtered out. Office time comes from his own "CLO" calendar on his personal account (kind `work`, writable).

## Updates reaching the phone

- `sw.js` always fetches the page with a unique `?fresh=` query and `no-store`, so the GitHub Pages CDN cache (10 min) never serves an old page.
- The refresh button fetches the newest `index.html` directly, compares `APP_VERSION`, drops the service worker and caches if they are behind, then reloads with `?r=`.
- The day always fills the timeline box: `fitTimeline()` sets a minimum hour height (`S.pxFloor`); `S.pxUser` is the zoom he chose.
- Travel: events with a location get a leave-by time (next 8 days). Origin = the previous event with a place within 90 min, else "Start from", else device location. Drawn as a hatched `.travel` block from leave-by to start. Addresses geocode via Nominatim, trying the full location, then the street lines only (cache key `geoCache2`).
- Time zones: primary is always the device zone (shown in More/sidebar as "automatic"). Second zone `cfg().tz2`: "auto" (default, also when unset) shows NYC only when the device is on a different clock; "off" hides it; or a fixed IANA zone.
- Repeat: the event sheet shows the series rule (fetched with `get_event` on `recurringEventId`). Plain choices map to RRULEs (`repeatRule`/`ruleKind`); other rules show as text and are left alone. "Change: This event / All events"; changing the repeat always edits the series master (EXDATEs kept).
- Every list has an "Add to <list>" row at the bottom; it goes through `quickAdd(text, listId)` so times like "thu 2pm" still schedule.
- Timeline background: `wxLayer` darkens each column with real outside darkness (sunrise/sunset from Open-Meteo, 45 min twilight ramp; fallback 7:00/18:15), hourly temps on the right of each column, sunrise/sunset lines, rain hatching with %.
- Desktop background: `#skybg` canvas (live sky): gradient by time of day from sunrise/sunset, clouds by cover, rain/snow/lightning from the current weather code, stars and moon at night. ~30fps at 0.6 scale, pauses when hidden. `?sky=rain|snow|storm|cloudy|fog|clear` forces a look for testing. Toggle "Live weather background" in the sidebar (localStorage `liveSky`). Hidden on iPhone.
- Location fields (sheet, Travel "Start from") suggest places as you type via Photon (OpenStreetMap, no key). Picking one saves "Name\naddress" and caches its coordinates for travel times.
