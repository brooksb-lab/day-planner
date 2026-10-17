# Day Planner

A daily planner on top of Google Calendar, styled after the Day app.

- Unscheduled to-dos live in the app. Anything with a time lives in Google Calendar.
- Drag to-dos onto the timeline to schedule them, drag events to move or resize, drag a to-do event back off the timeline to unschedule it.
- Morning, Day, Evening and Tomorrow views switch with the time of day.
- A Claude command bar edits the planner in plain language.

## How it runs

Everything runs in the browser. There is no server.

- **Google Calendar**: read and written directly with Google sign-in. Edits never email guests.
- **To-dos and settings**: one JSON file in your Google Drive's hidden app folder, cached on the device so it opens instantly and works offline.
- **Claude bar**: calls the Anthropic API with your own key, stored only on the device.

## Setup

1. In Google Cloud, create a project, enable the Google Calendar API and Google Drive API, configure the OAuth consent screen and add yourself as a test user.
2. Create an OAuth client ID of type Web application with this site's origin as an authorized JavaScript origin.
3. Open the site and paste the client ID.
4. Optional: add an Anthropic API key under Connections for the Claude bar.

On iPhone, open the site in Safari and use Share → Add to Home Screen for a fullscreen app.
