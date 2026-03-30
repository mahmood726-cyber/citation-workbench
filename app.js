(function () {
  const data = window.CITATION_WORKBENCH_DATA;
  if (!data) {
    return;
  }

  const state = {
    search: "",
    band: "",
    type: "",
    sort: "score",
  };

  const metricGrid = document.getElementById("metric-grid");
  const gapGrid = document.getElementById("gap-grid");
  const typeTable = document.getElementById("type-table");
  const projectGrid = document.getElementById("project-grid");
  const resultsCopy = document.getElementById("results-copy");
  const exportLinks = document.getElementById("export-links");

  function pct(value) {
    return `${Number(value).toFixed(1)}%`;
  }

  function renderMetrics() {
    const cards = [
      [data.metrics.trackedProjects, "Indexed projects", `${data.metrics.cffPackets} CFF packets generated`],
      [pct(data.metrics.highCitationReadinessPercent), "High citation readiness", `${data.metrics.highCitationReadinessCount} packet sets`],
      [pct(data.metrics.dataciteCoreReadyPercent), "DataCite core ready", `${data.metrics.dataciteCoreReadyCount} draft records`],
      [pct(data.metrics.paperBackedPercent), "Paper-backed records", `${data.metrics.paperBackedCount} projects with manuscript evidence`],
    ];
    metricGrid.innerHTML = cards.map(([value, label, note]) => `
      <article class="metric-card">
        <span class="metric-value">${value}</span>
        <span>${label}</span>
        <span class="metric-note">${note}</span>
      </article>
    `).join("");
  }

  function renderExports() {
    const links = [
      ["CFF Index", data.project.links.packetIndex, "Lookup table for generated packet files"],
      ["DataCite Drafts", data.project.links.dataciteDrafts, "Aggregated DOI-facing metadata drafts"],
      ["CiteProc Items", data.project.links.cslItems, "Aggregated CSL JSON export"],
      ["E156 Submission", data.project.links.e156, "Paper, protocol, metadata, and reader"],
      ["GitHub Repo", data.project.links.repo, "Full code and bundled snapshots"],
    ];
    exportLinks.innerHTML = links.map(([title, href, text]) => `
      <a class="export-link" href="${href}">
        <strong>${title}</strong>
        <span>${text}</span>
      </a>
    `).join("");
  }

  function renderGaps() {
    gapGrid.innerHTML = data.gapBreakdown.map((item) => `
      <article class="chip">
        <strong>${item.label}</strong>
        <p>${item.count} projects</p>
      </article>
    `).join("");
  }

  function renderTypes() {
    typeTable.innerHTML = data.resourceTypes.map((item) => `
      <tr>
        <td>${item.resourceTypeGeneral}</td>
        <td>${item.count}</td>
        <td>${item.highReadiness}</td>
      </tr>
    `).join("");
  }

  function fillTypeOptions() {
    const select = document.getElementById("type-select");
    data.resourceTypes.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.resourceTypeGeneral;
      option.textContent = item.resourceTypeGeneral;
      select.appendChild(option);
    });
  }

  function filteredProjects() {
    const q = state.search.trim().toLowerCase();
    const projects = data.projects.filter((project) => {
      if (state.band && project.readinessBand !== state.band) {
        return false;
      }
      if (state.type && project.resourceTypeGeneral !== state.type) {
        return false;
      }
      if (!q) {
        return true;
      }
      return [
        project.name,
        project.tier,
        project.recordType,
        project.resolvedStatus,
        project.targetJournal,
        project.primaryGap,
        project.resourceTypeGeneral,
      ].join(" ").toLowerCase().includes(q);
    });

    const sorters = {
      score: (a, b) => b.citationReadinessScore - a.citationReadinessScore || a.name.localeCompare(b.name),
      name: (a, b) => a.name.localeCompare(b.name),
      year: (a, b) => b.publicationYear - a.publicationYear || a.name.localeCompare(b.name),
    };
    return projects.sort(sorters[state.sort]);
  }

  function renderProjects() {
    const projects = filteredProjects();
    resultsCopy.textContent = `${projects.length} packet pages shown`;
    projectGrid.innerHTML = projects.map((project) => `
      <a class="project-card" href="packets/${project.slug}.html">
        <div class="pill-row">
          <span class="pill ${project.readinessBand}">${project.readinessBand} readiness</span>
          <span class="pill">${project.resourceTypeGeneral}</span>
          <span class="pill">${project.tier}</span>
        </div>
        <div>
          <h3>${project.name}</h3>
          <p class="hero-text">${project.plainCitation}</p>
        </div>
        <div class="score">${project.citationReadinessScore}</div>
        <div class="project-meta">
          <span>Status: ${project.resolvedStatus}</span>
          <span>Journal: ${project.targetJournal || "Not preserved"}</span>
          <span>Primary gap: ${project.primaryGap}</span>
        </div>
      </a>
    `).join("");
  }

  function bindEvents() {
    document.getElementById("search-input").addEventListener("input", (event) => {
      state.search = event.target.value;
      renderProjects();
    });
    document.getElementById("band-select").addEventListener("change", (event) => {
      state.band = event.target.value;
      renderProjects();
    });
    document.getElementById("type-select").addEventListener("change", (event) => {
      state.type = event.target.value;
      renderProjects();
    });
    document.getElementById("sort-select").addEventListener("change", (event) => {
      state.sort = event.target.value;
      renderProjects();
    });
  }

  fillTypeOptions();
  renderMetrics();
  renderExports();
  renderGaps();
  renderTypes();
  bindEvents();
  renderProjects();
}());
