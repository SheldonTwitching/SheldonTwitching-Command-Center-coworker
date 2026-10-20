# SheldonTwitching Stream Costs — Streamlabs Tip Goal

**This is NOT a Streamlabels .txt-based goal.** The real Stream Costs bar is the existing [Streamlabs Tip Goal widget](https://support.streamlabs.com/hc/en-us/articles/360052472373-How-to-Set-up-the-Streamlabs-Tip-Goal-Widget). Streamlabs itself updates the current amount and goal.

## Keep your existing goal and OBS source

1. In OBS, keep the existing Streamlabs Tip Goal Browser Source and its existing private URL. **Do not publish or commit the URL.** Leave the active goal in place.
2. Launch SheldonTwitching Labels and open **Stream Costs · Streamlabs Tip Goal** in the left panel.
3. Use the color pickers, title-size slider, animation selector and raw-CSS editor to create the visual style.
4. Open **Preview arcade theme**; this preview shows **sample $35 / $100**, not real tips.
5. Click **Export Streamlabs HTML / CSS / JS**. Extract the ZIP and read `INSTALL.txt`.
6. Go to **[Streamlabs Dashboard](https://streamlabs.com/dashboard) → All Widgets → Tip Goal → Settings**. **Back up any current custom code** first. Enable custom HTML/CSS and paste the contents of `HTML.txt`, `CSS.txt`, and `JS.txt` into their corresponding editing tabs, then Save Settings.
7. In OBS, keep using the **same** Streamlabs browser source, positioned over the Stream Costs slot in the gameplay cabinet (approx. x=576, y=205 on a 1920×1080 canvas; displayed 760×108).
8. If you change the theme in SheldonTwitching Labels, export again and replace the CSS/JS in Streamlabs. The app does not have access to your private Streamlabs settings and cannot push edits there automatically.

The `goalLoad` and `goalEvent` browser events read amount.current, amount.target and goal title from the Streamlabs goal widget. This integration has automated mock-event tests, but you should verify the latest Streamlabs widget implementation with its dashboard preview, including during a test tip if available. Tip settings/active goal changes are handled at Streamlabs.com. You do **not** need to enter a separate amount/goal file in SheldonTwitching Labels.

The old `http://127.0.0.1:47831/tip-bar` route remains available only as a **legacy text-file/demo widget** for backward compatibility. **Do not add it** alongside your Streamlabs Tip Goal, or you'll see duplicate bars and potentially incorrect dollar amounts.

The Gameplay scene now reserves an empty Stream Costs placement; it intentionally does **not** embed any Streamlabs URL, because that URL is private and has to be managed inside OBS.

## Current source layers in OBS

1. SheldonTwitching gameplay browser scene (main cabinet art, 1920×1080)
2. Existing Streamlabs Tip Goal browser source ABOVE that gameplay scene at the target Stream Costs location
3. Game Capture BELOW the gameplay cabinet scene (the cabinet artwork has a transparent gameplay window)
4. Any separately-managed webcam layers placed according to your existing layout

## Why the code is separate

The HTML, CSS and JS are pasted into Streamlabs' own custom widget slots and therefore run within the Streamlabs widget's page. Pasting our local CSS into the OBS Browser Source's **Custom CSS** field without matching the Streamlabs DOM is not equivalent; the generated style expects the matching custom HTML structure.

Never put your personal Streamlabs widget URL, Spotify tokens or other account credentials into the GitHub repository.
