const sampleData = {
  cas: [
    { name: "LAB-ROOT-CA", role: "Root", children: ["LAB-SUB-CA"] },
    { name: "LAB-SUB-CA", role: "Subordinate", children: [] },
  ],
  templates: [
    { name: "UserAuthentication", eku: ["Client Authentication"], risk: "medium" },
    { name: "ESC1-Template", eku: ["Client Authentication", "Smart Card Logon"], risk: "high" },
  ],
  detections: [
    { template: "ESC1-Template", severity: "high", message: "Subject editable without approval" },
  ],
};

function renderPKIGraph() {
  const container = document.getElementById("pki-graph");
  container.innerHTML = "";
  sampleData.cas.forEach((ca) => {
    const element = document.createElement("div");
    element.className = "badge";
    element.innerText = `${ca.role}: ${ca.name}`;
    container.appendChild(element);
  });
}

function renderTemplates() {
  const list = document.getElementById("template-list");
  list.innerHTML = "";
  sampleData.templates.forEach((template) => {
    const item = document.createElement("li");
    item.innerText = `${template.name} – EKU: ${template.eku.join(", ")} (risk: ${template.risk})`;
    list.appendChild(item);
  });
}

function renderDetections() {
  const feed = document.getElementById("detection-feed");
  feed.innerHTML = "";
  sampleData.detections.forEach((finding) => {
    const card = document.createElement("div");
    card.className = "badge";
    card.innerText = `${finding.severity.toUpperCase()} – ${finding.template}: ${finding.message}`;
    feed.appendChild(card);
  });
}

function renderScore() {
  const score = document.getElementById("score");
  const hardenedTemplates = sampleData.templates.filter((t) => t.risk !== "high").length;
  const percentage = Math.round((hardenedTemplates / sampleData.templates.length) * 100);
  score.innerText = `Hardening completeness: ${percentage}%`;
}

renderPKIGraph();
renderTemplates();
renderDetections();
renderScore();
