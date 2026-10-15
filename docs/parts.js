"use strict";
const en = new URLSearchParams(location.search).get("lang") === "en";
document.documentElement.lang = en ? "en" : "ko";
if (en) document.querySelectorAll("[data-en]").forEach(n => { n.textContent = n.dataset.en; });
let parts = [];
const search = document.getElementById("search");
const status = document.getElementById("status");
function render() {
  const term = search.value.trim().toLowerCase();
  const selected = parts.filter(p => [p.part_no, p.svc_number, p.description].join(" ").toLowerCase().includes(term));
  const rows = document.getElementById("rows");
  rows.replaceChildren();
  for (const part of selected) {
    const tr = document.createElement("tr");
    for (const value of [part.part_no, part.svc_number, part.description]) {
      const td = document.createElement("td"); td.textContent = value; tr.append(td);
    }
    rows.append(tr);
  }
  status.textContent = selected.length + (en ? " parts" : "개 부품");
}
search.addEventListener("input", render);
fetch("./catalogue.json?v=parts-only").then(r => {
  if (!r.ok) throw new Error(en ? "Unable to load catalogue" : "목록을 불러올 수 없습니다");
  return r.json();
}).then(data => { parts = data.parts; render(); }).catch(e => { status.textContent = e.message; });
