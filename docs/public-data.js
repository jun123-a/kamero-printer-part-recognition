"use strict";
// The public viewer uses an approved static snapshot; it never calls localhost.
const publicSnapshot = fetch("./catalogue.json").then(response => {
  if (!response.ok) throw new Error("Could not load catalogue: " + response.status);
  return response.json();
});
window.publicCatalogueGet = async function(path) {
  const data = await publicSnapshot;
  const url = new URL(path, location.origin);
  if (url.pathname === "/api/datasets") return {datasets: data.datasets};
  const match = url.pathname.match(/^\/api\/datasets\/(\d+)\/(summary|parts|assets)$/);
  if (!match || !data.details[match[1]]) throw new Error("Dataset not found");
  const detail = data.details[match[1]];
  if (match[2] === "summary") return detail.summary;
  if (match[2] === "parts") return {parts: detail.parts};
  const part = url.searchParams.get("part_no");
  const rows = part ? detail.assets.filter(a => a.parts.some(p => p.part_no === Number(part))) : detail.assets;
  const offset = Number(url.searchParams.get("offset") || 0);
  const limit = Number(url.searchParams.get("limit") || 50);
  return {total: rows.length, assets: rows.slice(offset, offset + limit)};
};
