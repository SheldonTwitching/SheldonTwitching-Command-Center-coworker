/* SheldonTwitching Labels editor: no build tools or CDN dependencies required. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const icons = ["⭐", "🔥", "🏆", "💜", "💎", "🎮", "🎵", "⚡", "👑", "💰"];
  const numeric = new Set(["x", "y", "w", "h", "fontSize", "labelSize", "iconSize", "gap", "pad", "radius", "border", "shadow", "fontWeight", "transitionMs", "dwell", "part"]);
  let project, live = {}, files = [], selectedId = null, stage, scale = 1;
  let saveTimer = null, saving = false, savePromise = null, saveNeeded = false, rotationTimer = null, playing = false, previewIndex = 0, showAll = false;
  let toastTimer;
  let roster = [];
  const history = [];
  let historyIndex = -1, historyTimer = null, restoring = false;

  function toast(message) {
    $("toast").textContent = message;
    $("toast").classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $("toast").classList.remove("visible"), 3200);
  }
  function selected() { return project?.items.find(item => item.id === selectedId) || project?.items[0]; }
  function esc(text) { return String(text ?? "").replace(/[&<>"']/g, x => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[x]); }
  function color6(value) { return /^#[0-9a-f]{6}/i.test(value || "") ? value.slice(0, 7) : "#230934"; }
  const hexAlpha = n => Math.round(Math.min(100, Math.max(0, Number(n))) * 255 / 100).toString(16).padStart(2, "0");
  const percentAlpha = color => /^[#][a-f0-9]{8}$/i.test(color || "") ? Math.round(parseInt(color.slice(7, 9), 16) / 255 * 100) : 100;
  function recordHistory() {
    clearTimeout(historyTimer); historyTimer = null;
    if (!project || restoring) return;
    const state = JSON.stringify(project);
    if (history[historyIndex] === state) return;
    history.splice(historyIndex + 1);
    history.push(state);
    if (history.length > 60) history.shift();
    historyIndex = history.length - 1;
    updateHistoryButtons();
  }
  function updateHistoryButtons() {
    $("undo").disabled = historyIndex <= 0;
    $("redo").disabled = historyIndex >= history.length - 1;
  }
  function historyChanged() {
    clearTimeout(historyTimer);
    historyTimer = setTimeout(recordHistory, 350);
  }
  function travelHistory(direction) {
    recordHistory();
    const next = historyIndex + direction;
    if (next < 0 || next >= history.length) return;
    historyIndex = next;
    restoring = true;
    project = JSON.parse(history[historyIndex]);
    selectedId = project.items.find(i => i.id === selectedId)?.id || project.items[0]?.id || null;
    stopPreview(); rerender(true);
    restoring = false;
    updateHistoryButtons();
    markDirty(); toast(direction < 0 ? "Undid change" : "Redid change");
  }
  function markDirty() { if (!restoring) historyChanged(); $("saveStatus").textContent = "● Unsaved"; $("saveStatus").style.color = "#ffb86a"; saveNeeded = true; clearTimeout(saveTimer); saveTimer = setTimeout(saveNow, 450); }
  async function saveNow() {
    // A single write queue prevents folder/project import and autosave racing.
    if (saving) { saveNeeded = true; return savePromise; }
    saving = true; saveNeeded = true;
    savePromise = (async () => {
      try {
        do {
          saveNeeded = false;
          const body = JSON.stringify(project);
          const res = await fetch("/api/project", {method:"POST", headers:{"Content-Type":"application/json"}, body});
          if (!res.ok) throw new Error((await res.json()).error || "Save failed");
        } while (saveNeeded);
        $("saveStatus").textContent = "● Saved";
        $("saveStatus").style.color = "#8fdfb4";
        return true;
      } catch (e) {
        saveNeeded = true;
        $("saveStatus").textContent = "● Save error";
        $("saveStatus").style.color = "#ff7070";
        toast(e.message);
        return false;
      } finally { saving = false; savePromise = null; }
    })();
    return savePromise;
  }
  function rerender(controls = false) {
    if (!project) return;
    $("canvasW").value = project.width;
    $("canvasH").value = project.height;
    $("rotationToggle").checked = Boolean(project.rotation);
    $("selectedTag").textContent = (selected()?.name || "NO LABEL").toUpperCase();
    $("folderPath").value = project.folder || "";
    renderItemList();
    renderSources();
    renderCanvas();
    renderParsing();
    renderTimeline();
    if (controls) { renderControls(); renderTipControls(); }
  }
  function renderItemList() {
    $("itemList").innerHTML = (project.items || []).map(item => `<button class="item-row ${item.id === selectedId ? "selected" : ""}" data-select="${esc(item.id)}"><span class="item-symbol">${/^data:image/.test(item.icon || "") ? "🖼️" : esc(item.icon || "⭐")}</span><span class="item-detail"><strong>${esc(item.name || item.label)}</strong><small>${esc(item.file || "No source selected")}</small></span><span class="item-on ${item.enabled === false ? "off" : ""}"></span></button>`).join("");
  }
  function renderSources() {
    $("folderState").textContent = project.folder ? `${files.length} text file(s) found` : "Using example data until a folder is connected.";
    $("fileCount").textContent = String(files.length);
    $("filesList").innerHTML = files.length ? files.map(name => `<button class="file-entry" data-source="${esc(name)}">▤ ${esc(name)}</button>`).join("") : `<span class="hint">${project.folder ? "No .txt files in this folder." : "Select a Streamlabels folder."}</span>`;
    $("availableFiles").innerHTML = files.map(name => `<option value="${esc(name)}"></option>`).join("");
  }
  function renderTimeline() {
    $("timelineItems").innerHTML = project.items.filter(i => i.enabled !== false).map((i, idx) => `<div class="timeline-pill ${i.id === selectedId ? "active" : ""}"><b>${idx + 1}</b> ${esc(i.name)} · ${Number(i.dwell || 5)}s</div>`).join("") || `<span class="hint">No enabled items.</span>`;
  }
  function renderParsing() {
    const i = selected();
    if (!i) return;
    const text = live[i.file];
    $("rawPreview").textContent = typeof text === "string" && text.trim() ? text : "[No file data — showing fallback]";
    $("parsedPreview").textContent = SL.parseValue(i, text);
  }
  function renderCanvas() {
    if (!stage) return;
    const host = $("previewHost");
    const box = $("canvasViewport");
    scale = Math.min(1.3, (box.clientWidth - 46) / project.width, (box.clientHeight - 48) / project.height);
    scale = Math.max(.1, scale);
    $("stageScaler").style.width = (project.width * scale) + "px";
    $("stageScaler").style.height = (project.height * scale) + "px";
    host.style.width = project.width + "px";
    host.style.height = project.height + "px";
    host.style.transform = `scale(${scale})`;
    host.style.transformOrigin = "top left";
    $("canvasScale").textContent = `${project.width} × ${project.height} · ${Math.round(scale * 100)}%`;
    stage.update(project, live, selectedId, showAll);
    if (playing) showPreviewCard();
    else for (const card of stage.cards.values()) { card.style.display = "flex"; card.classList.remove(...Array.from(card.classList).filter(x => x.startsWith("enter-") || x.startsWith("exit-"))); }
  }
  function renderTipControls() {
    const tip = project.tipBar || {};
    document.querySelectorAll('[data-tip]').forEach(element => {
      const value = tip[element.dataset.tip];
      element.value = value ?? '';
    });
  }
  async function readSpotifyStatus() {
    try {
      const res = await fetch('/api/spotify/status');
      const d = await res.json();
      $('spotifyClientId').value = d.client_id || '';
      $('spotifyStatus').textContent = d.connected ? '● Spotify connected' : d.configured ? '● Client ID saved · click Connect' : '● Spotify not configured';
    } catch (_) { $('spotifyStatus').textContent = 'Bridge offline'; }
  }
  function renderRoster() {
    const list = $('rosterChoices');if(!list)return;
    const q=($('rosterSearch').value||'').toLowerCase();
    list.innerHTML=roster.filter(c=>c.name.toLowerCase().includes(q)).map(c=> c.asset
      ? `<button type="button" class="roster-pick" data-character="${esc(c.id)}" title="Select ${esc(c.name)}"><img src="${esc(c.asset)}" alt=""><span>${esc(c.name)}</span></button>`
      : `<span class="roster-pending" title="Art not drawn yet">${esc(c.name)} · pending</span>`).join('');
  }
  function renderControls() {
    const i = selected();
    if (!i) return;
    for (const element of document.querySelectorAll("[data-field]")) {
      const key = element.dataset.field;
      if (element.type === "checkbox") element.checked = Boolean(i[key]);
      else if (element.type === "color") element.value = color6(i[key]);
      else if (element.id === "customIconText") element.value = /^data:image/.test(i.icon || "") ? "[Embedded image]" : (i.icon || "");
      else element.value = i[key] ?? "";
      if (element.type === "range") updateOutput(key, element.value);
    }
    $("panelColor").value = color6(i.bg);
    $("panelOpacity").value = percentAlpha(i.bg);
    $("opacityValue").textContent = $("panelOpacity").value + "%";
    $("customCSS").value = project.customCSS || "";
    $("iconChoices").innerHTML = icons.map(icon => `<button class="icon-pick ${i.icon === icon ? "active" : ""}" data-icon="${icon}" title="Use ${icon}">${icon}</button>`).join("");
  }
  function updateOutput(key, value) {
    const target = $(key + "Value");
    if (target) target.textContent = value + (key === "dwell" ? "s" : key === "transitionMs" ? "ms" : key === "fontWeight" || key === "part" ? "" : "px");
  }
  function selectItem(id) {
    if (!project.items.some(i => i.id === id)) return;
    selectedId = id;
    rerender(true);
  }
  function randomId() { return "item-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 6); }
  function addItem(copy = false) {
    const src = selected() || project.items[0];
    const item = src ? structuredClone(src) : {name:"New label", label:"NEW LABEL", icon:"⭐", x:80,y:25,w:350,h:110,enabled:true,fontSize:30,labelSize:15,iconSize:39,gap:15,pad:18,radius:13,border:2,bg:"#230934e8",accent:"#e600d9",textColor:"#ffffff",labelColor:"#e5b7ff",font:"Impact,sans-serif",fontWeight:800,shadow:13,enter:"fade",exit:"fade",dwell:5,transitionMs:550,parseMode:"raw",fallback:"New supporter"};
    item.id = randomId();
    item.name = copy ? item.name + " Copy" : "New Label";
    item.label = copy ? item.label : "NEW LABEL";
    item.x = Math.max(0, Math.min(project.width - Number(item.w || 350), (Number(item.x) || 0) + 18));
    item.y = Math.max(0, Math.min(project.height - Number(item.h || 100), (Number(item.y) || 0) + 8));
    project.items.push(item); selectedId = item.id; rerender(true); markDirty();
    toast(copy ? "Label duplicated" : "Label added");
  }
  function deleteItem() {
    if (project.items.length <= 1) return toast("Keep at least one label in your project");
    project.items = project.items.filter(i => i.id !== selectedId);
    selectedId = project.items[0]?.id;
    rerender(true); markDirty(); toast("Label deleted");
  }
  function moveItem(delta) {
    const index = project.items.findIndex(i => i.id === selectedId);
    const dest = index + delta;
    if (index < 0 || dest < 0 || dest >= project.items.length) return;
    [project.items[index], project.items[dest]] = [project.items[dest], project.items[index]];
    rerender(false); markDirty();
  }
  function showPreviewCard() {
    const enabled = project.items.filter(i => i.enabled !== false);
    if (!enabled.length) return;
    previewIndex = previewIndex % enabled.length;
    const active = enabled[previewIndex];
    for (const card of stage.cards.values()) {
      card.style.display = card.dataset.id === active.id ? "flex" : "none";
      card.classList.remove(...Array.from(card.classList).filter(x => x.startsWith("enter-") || x.startsWith("exit-")));
      card.classList.remove("selected");
    }
    const card = stage.cards.get(active.id);
    if (card) { void card.offsetWidth; card.classList.add("enter-" + (active.enter || "fade")); }
  }
  function stopPreview() {
    clearTimeout(rotationTimer); rotationTimer = null; playing = false;
    $("previewPlay").textContent = "▶ Preview rotation";
    renderCanvas();
  }
  function startPreview() {
    if (playing) return stopPreview();
    playing = true; previewIndex = 0;
    $("previewPlay").textContent = "■ Stop preview";
    const tick = () => {
      if (!playing) return;
      const enabled = project.items.filter(i => i.enabled !== false);
      if (!enabled.length) return stopPreview();
      previewIndex %= enabled.length;
      showPreviewCard();
      const item = enabled[previewIndex];
      rotationTimer = setTimeout(() => {
        if (!playing) return;
        const card = stage.cards.get(item.id);
        if (card) { card.classList.remove("enter-" + (item.enter || "fade")); card.classList.add("exit-" + (item.exit || "fade")); }
        rotationTimer = setTimeout(() => { previewIndex++; tick(); }, Number(item.transitionMs || 550));
      }, Number(item.dwell || 5) * 1000);
    };
    tick();
  }
  function beginDrag(itemId, event) {
    if (playing || event.button !== 0) return;
    if (selectedId !== itemId) selectItem(itemId);
    const i = selected();
    const grip = event.target.closest?.(".resize-grip");
    const resizing = Boolean(grip);
    const originX = event.clientX, originY = event.clientY;
    const startX = Number(i.x) || 0, startY = Number(i.y) || 0;
    const startW = Number(i.w) || 350, startH = Number(i.h) || 110;
    const move = e => {
      if (!project.items.some(a => a.id === itemId)) return;
      const dx = (e.clientX - originX) / scale, dy = (e.clientY - originY) / scale;
      if (resizing) {
        i.w = Math.round(Math.max(70, Math.min(project.width - startX, startW + dx)));
        i.h = Math.round(Math.max(30, Math.min(project.height - startY, startH + dy)));
      } else {
        i.x = Math.round(Math.max(0, Math.min(project.width - startW, startX + dx)));
        i.y = Math.round(Math.max(0, Math.min(project.height - startH, startY + dy)));
      }
      renderCanvas();
      for (const prop of ["x", "y", "w", "h"]) document.querySelector(`[data-field="${prop}"]`).value = i[prop];
    };
    const finish = () => {
      document.removeEventListener("pointermove", move);
      document.removeEventListener("pointerup", finish);
      document.removeEventListener("pointercancel", finish);
      markDirty();
    };
    document.addEventListener("pointermove", move);
    document.addEventListener("pointerup", finish);
    document.addEventListener("pointercancel", finish);
    event.preventDefault();
  }
  async function chooseFolder() {
    if (window.pywebview?.api?.choose_folder) {
      try { const folder = await window.pywebview.api.choose_folder(); if (folder) { $("folderPath").value = folder; await connectFolder(); } }
      catch(e) { toast("Folder picker unavailable: " + e.message); }
    } else { $("folderPath").focus(); toast("Enter or paste the Streamlabels folder path above"); }
  }
  async function connectFolder() {
    const folder = $("folderPath").value.trim();
    if (!folder) return toast("Enter your Streamlabels folder path");
    try {
      if (!await saveNow()) throw new Error("Save failed. Connect folder aborted.");
      const res = await fetch("/api/folder", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({folder})});
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Cannot open folder");
      project.folder = folder;
      files = data.files || [];
      rerender(false);
      toast(`Connected: ${files.length} .txt file(s) found`);
    } catch(e) { toast(e.message); }
  }
  async function poll() {
    try {
      const res = await fetch("/api/snapshot", {cache:"no-store"});
      if (!res.ok) return;
      const data = await res.json();
      live = data.live || {};
      if (JSON.stringify(files) !== JSON.stringify(data.files)) { files = data.files || []; renderSources(); }
      $("connection").textContent = "● Bridge running"; $("connection").style.color = "#8fdfb4";
      if (project) {
        if (playing) {
          for (const item of project.items) {
            const card = stage.cards.get(item.id);
            if (card) card.querySelector(".overlay-value").textContent = SL.parseValue(item, live[item.file]);
          }
        } else stage.update(project, live, selectedId, showAll);
        renderParsing();
      }
    } catch (_) { $("connection").textContent = "● Bridge offline"; $("connection").style.color = "#ff7878"; }
  }
  function bind() {
    document.querySelectorAll('[data-tip]').forEach(control => {
      const handler = e => {
        project.tipBar ||= {};
        const key = control.dataset.tip;
        project.tipBar[key] = ['amountFallback','goalFallback'].includes(key) ? Math.max(0, Number(control.value)||0) : control.value;
        markDirty();
      };
      control.addEventListener(control.tagName === 'SELECT' || control.type === 'number' ? 'change' : 'input', handler);
    });
    $('spotifySave').onclick = async () => {
      try {
        const res = await fetch('/api/spotify/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client_id:$('spotifyClientId').value.trim()})});
        const d = await res.json();if(!res.ok)throw Error(d.error||'Spotify configuration failed');
        await readSpotifyStatus();toast('Spotify Client ID saved locally');
      }catch(e){toast(e.message)}
    };
    $('spotifyConnect').onclick = () => {window.open('/spotify/connect','_blank','noopener');toast('Authorize Spotify in the new browser tab');};
    $('spotifyDisconnect').onclick = async () => {
      if(!confirm('Disconnect Spotify on this computer?'))return;
      await fetch('/api/spotify/disconnect',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
      await readSpotifyStatus();toast('Spotify disconnected');
    };
    $("itemList").addEventListener("click", e => { const b = e.target.closest("[data-select]"); if (b) { if (playing) stopPreview(); selectItem(b.dataset.select); } });
    $("filesList").addEventListener("click", e => { const b = e.target.closest("[data-source]"); if (b && selected()) { selected().file = b.dataset.source; rerender(true); markDirty(); toast("Data source changed without changing the design"); } });
    $('rosterSearch').oninput=renderRoster;
    $('rosterChoices').addEventListener('click',async e=>{
      const button=e.target.closest('[data-character]');if(!button||!selected())return;
      const entry=roster.find(c=>c.id===button.dataset.character);if(!entry||!entry.asset)return;
      try {
        const response=await fetch(entry.asset);if(!response.ok)throw Error('Icon not available');
        const blob=await response.blob();if(blob.size>400000)throw Error('Icon exceeds widget limit');
        const reader=new FileReader();reader.onload=()=>{selected().icon=reader.result;rerender(true);markDirty();toast(entry.name+' icon selected')};reader.readAsDataURL(blob);
      }catch(e){toast(e.message)}
    });
    $("iconChoices").addEventListener("click", e => { const b = e.target.closest("[data-icon]"); if (b && selected()) { selected().icon = b.dataset.icon; rerender(true); markDirty(); } });
    $("undo").onclick = () => travelHistory(-1);
    $("redo").onclick = () => travelHistory(1);
    $("downloadProject").onclick = async () => { if (await saveNow()) { location.href = "/api/project/download"; toast("Project backup requested"); } };
    $("importProject").onclick = () => $("projectFile").click();
    $("projectFile").onchange = async e => {
      const file = e.target.files[0]; if (!file) return;
      if (file.size > 2_000_000) return toast("Project is too large (2 MB maximum)");
      try {
        const incoming = JSON.parse(await file.text());
        if (!incoming || !Array.isArray(incoming.items) || incoming.items.length > 100 || !Number.isFinite(Number(incoming.width)) || !Number.isFinite(Number(incoming.height))) throw Error("Not a valid project");
        if (!confirm(`Replace your current layout with ${incoming.items.length} label(s) from ${file.name}? Your current project is backed up automatically.`)) return;
        if (!await saveNow()) throw Error("Save your current project before importing");
        const res = await fetch("/api/project", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(incoming)});
        const reply = await res.json(); if (!res.ok) throw Error(reply.error || "Project import failed");
        stopPreview(); project = incoming; selectedId = project.items[0]?.id || null;
        history.length = 0; historyIndex = -1; recordHistory(); rerender(true);
        toast("Project imported successfully");
      } catch (err) { toast("Import failed: " + err.message); }
      finally { e.target.value = ""; }
    };
    const stylePresets = {
      arcade: {accent:"#e600d9",bg:"#230934e8",textColor:"#ffffff",labelColor:"#e5b7ff",radius:13,border:2,shadow:14,font:"'Arial Narrow', Impact, sans-serif",fontWeight:800},
      flame: {accent:"#ff8b19",bg:"#230b16f0",textColor:"#fff3e5",labelColor:"#ffbb9c",radius:4,border:3,shadow:24,font:"Impact, sans-serif",fontWeight:900},
      minimal: {accent:"#ffffff",bg:"#180f2299",textColor:"#ffffff",labelColor:"#e5b7ff",radius:2,border:0,shadow:0,font:"'Segoe UI', sans-serif",fontWeight:600},
      glass: {accent:"#b961ff",bg:"#3b2269a0",textColor:"#ffffff",labelColor:"#f2c4ff",radius:22,border:1,shadow:7,font:"'Trebuchet MS', sans-serif",fontWeight:700}
    };
    document.querySelectorAll("[data-preset]").forEach(button => button.onclick = () => {
      if (!selected()) return;
      Object.assign(selected(), stylePresets[button.dataset.preset]);
      rerender(true); markDirty(); toast("Applied " + button.dataset.preset + " style");
    });
    document.querySelectorAll("[data-layout]").forEach(button => button.onclick = () => {
      const i = selected(); if (!i) return;
      const x = button.dataset.layout === "left" ? 0 : button.dataset.layout === "right" ? project.width - i.w : (project.width - i.w) / 2;
      i.x = Math.max(0, Math.round(x)); rerender(true); markDirty();
    });
    $("addItem").onclick = () => addItem(false);
    $("duplicateItem").onclick = () => addItem(true);
    $("deleteItem").onclick = deleteItem;
    $("moveUp").onclick = () => moveItem(-1);
    $("moveDown").onclick = () => moveItem(1);
    $("browseFolder").onclick = chooseFolder;
    $("connectFolder").onclick = connectFolder;
    $("refreshSources").onclick = poll;
    $("previewPlay").onclick = startPreview;
    $("replayAnimation").onclick = () => { stopPreview(); playing = true; previewIndex = Math.max(0, project.items.filter(i => i.enabled !== false).findIndex(i => i.id === selectedId)); showPreviewCard(); playing = false; };
    $("showAll").onchange = e => { showAll = e.target.checked; renderCanvas(); };
    $("rotationToggle").onchange = e => { project.rotation = e.target.checked; markDirty(); };
    $("startupToggle").onchange = async e => {
      const enabled = e.target.checked;
      try {
        const res = await fetch("/api/startup", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({enabled})});
        const data = await res.json();
        if (!res.ok) throw Error(data.error || "Could not update Windows startup");
        e.target.checked = data.enabled; toast(data.enabled ? "OBS bridge will start with Windows" : "Windows auto-start disabled");
      } catch(err) { e.target.checked = !enabled; toast(err.message); }
    };
    for (const [input, key, min, max] of [["canvasW","width",160,3840],["canvasH","height",80,2160]]) {
      $(input).addEventListener("change", e => { project[key] = Math.min(max, Math.max(min, Number(e.target.value)||min)); renderCanvas(); markDirty(); });
    }
    document.querySelectorAll("[data-field]").forEach(input => {
      const handle = e => {
        const item = selected();
        if (!item) return;
        const key = e.target.dataset.field;
        let value = input.type === "checkbox" ? input.checked : input.value;
        if (numeric.has(key)) value = Number(value);
        if (input.type === "color") value = color6(value);
        if (input.id === "customIconText" && /^data:image/.test(item.icon || "") && value === "[Embedded image]") return;
        item[key] = value;
        if (input.type === "range") updateOutput(key, value);
        rerender(false); markDirty();
      };
      input.addEventListener(input.type === "checkbox" || input.type === "number" || input.tagName === "SELECT" ? "change" : "input", handle);
    });
    $("panelColor").oninput = e => { const item = selected(); if (item) { item.bg = e.target.value + hexAlpha(percentAlpha(item.bg)); renderCanvas(); markDirty(); } };
    $("panelOpacity").oninput = e => { const item = selected(); if (item) { item.bg = color6(item.bg) + hexAlpha(e.target.value); $("opacityValue").textContent = e.target.value + "%"; renderCanvas(); markDirty(); } };
    $("customCSS").oninput = e => { project.customCSS = e.target.value; renderCanvas(); markDirty(); };
    document.querySelectorAll("[data-tab]").forEach(tab => tab.onclick = () => {
      document.querySelectorAll("[data-tab]").forEach(x => x.classList.toggle("active", x === tab));
      document.querySelectorAll("[data-panel]").forEach(x => x.classList.toggle("active", x.dataset.panel === tab.dataset.tab));
    });
    $("copyUrl").onclick = async () => {
      const url = `${location.origin}/overlay`;
      try { await navigator.clipboard.writeText(url); toast("OBS URL copied: " + url); }
      catch (_) { prompt("Copy this Browser Source URL", url); }
    };
    $("openObs").onclick = () => window.open("/overlay", "_blank");
    $("exportZip").onclick = async () => { if (await saveNow()) { location.href = "/api/export"; toast("Overlay ZIP export requested"); } };
    $("copyGeneratedCSS").onclick = async () => {
      const i = selected(); if (!i) return;
      const css = `.overlay-card[data-id="${i.id}"] {
  --accent: ${i.accent};
  --bg: ${i.bg};
  --value-color: ${i.textColor};
  --label-color: ${i.labelColor};
  --font-size: ${i.fontSize}px;
  --label-size: ${i.labelSize || 15}px;
  --icon-size: ${i.iconSize}px;
  --gap: ${i.gap}px;
  --pad: ${i.pad}px;
  --radius: ${i.radius}px;
  --border: ${i.border || 0}px;
  --shadow: ${i.shadow}px;
}`;
      try { await navigator.clipboard.writeText(css); toast("Visual CSS copied"); }
      catch (_) { prompt("Copy generated CSS", css); }
    };
    $("copyCSS").onclick = async () => { try { await navigator.clipboard.writeText(project.customCSS || "/* Add your custom CSS here */"); toast("Custom CSS copied"); } catch (_) { toast("Clipboard unavailable"); } };
    $("loadCSS").onclick = () => $("loadCSSFile").click();
    $("loadCSSFile").onchange = async e => { const file = e.target.files[0]; if (!file) return; if (file.size > 150000) return toast("CSS must be under 150 KB"); project.customCSS = await file.text(); $("customCSS").value = project.customCSS; renderCanvas(); markDirty(); toast("CSS imported"); };
    $("insertCSS").onclick = () => { const css = `\n/* SheldonTwitching neon pulse */\n@keyframes neonPulse { 0%,100%{filter:drop-shadow(0 0 0px #e600d9)} 50%{filter:drop-shadow(0 0 14px #e600d9)} }\n.overlay-icon { animation:neonPulse 2s ease-in-out infinite; }\n`; project.customCSS += css; $("customCSS").value = project.customCSS; renderCanvas(); markDirty(); toast("Neon pulse CSS added"); };
    $("iconUpload").onchange = async e => {
      const file = e.target.files[0];
      if (!file || !selected()) return;
      if (!/^image\/(png|jpeg|webp|svg\+xml)$/.test(file.type)) return toast("Use PNG, JPEG, WebP, or SVG images");
      if (file.size > 400_000) return toast("Icon too large (400 KB maximum)");
      const reader = new FileReader();
      reader.onload = () => { selected().icon = reader.result; rerender(true); markDirty(); toast("Custom icon embedded in project"); };
      reader.readAsDataURL(file);
    };
    window.addEventListener("resize", renderCanvas);
    document.addEventListener("keydown", e => {
      if (!(e.ctrlKey || e.metaKey)) return;
      const key = e.key.toLowerCase();
      if (key === "s") { e.preventDefault(); clearTimeout(saveTimer); saveNeeded = true; saveNow(); toast("Project saved"); return; }
      if (e.target.closest("input, textarea, [contenteditable]")) return;
      if (key === "z" && !e.shiftKey) { e.preventDefault(); travelHistory(-1); }
      if (key === "y" || (key === "z" && e.shiftKey)) { e.preventDefault(); travelHistory(1); }
    });
  }
  async function init() {
    try {
      const res = await fetch("/api/snapshot");
      if (!res.ok) throw new Error("Cannot connect to local bridge");
      const data = await res.json();
      project = data.project; live = data.live || {}; files = data.files || [];
      selectedId = project.items[0]?.id || null;
      stage = new SL.Stage($("previewHost"), {editor:true, select:beginDrag});
      try{const catalog=await (await fetch('/roster.json')).json();roster=catalog.characters||[]}catch(_){roster=[]}
      bind(); rerender(true); renderRoster(); recordHistory(); readSpotifyStatus();
      try {
        const status = await (await fetch("/api/startup")).json();
        $("startupToggle").checked = Boolean(status.enabled);
        $("startupToggle").disabled = !status.supported;
        if (!status.supported) $("startupToggle").title = "Available on Windows only";
      } catch (_) { $("startupToggle").disabled = true; }
      setInterval(poll, 1250);
    } catch (e) { toast("Unable to start editor: " + e.message); }
  }
  window.addEventListener("DOMContentLoaded", init);
})();
