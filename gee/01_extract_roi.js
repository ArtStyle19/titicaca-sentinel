// ==========================
// TITICACA SENTINEL - ROI EXTRACTION
// Extract Lake Titicaca geometry using JRC Global Surface Water
// ==========================

// ==========================
// 1) Define bounding box
// ==========================
var bbox = ee.Geometry.Rectangle([-70.3, -17.3, -68.4, -15.4]);

// ==========================
// 2) Load JRC Global Surface Water
// ==========================
var gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater");
var occurrence = gsw.select("occurrence");

// ==========================
// 3) Water mask (permanent water > 50%)
// ==========================
var waterMask = occurrence.gt(50).selfMask();

// ==========================
// 4) Convert mask to polygons
// ==========================
var vectors = waterMask.reduceToVectors({
  geometry: bbox,
  scale: 30,
  geometryType: "polygon",
  maxPixels: 1e13,
});

// ==========================
// 5) Add area with maxError to avoid geometry errors
// ==========================
var vectorsWithArea = vectors.map(function (f) {
  var area = f.geometry({ maxError: 10 }).area({ maxError: 10 });
  return f.set("area", area);
});

// ==========================
// 6) Select the largest polygon (the complete lake)
// ==========================
var lake = vectorsWithArea.sort("area", false).first();
var roi = ee.Feature(lake).geometry({ maxError: 10 });

// ==========================
// 7) Display on map
// ==========================
Map.centerObject(roi, 8);
Map.addLayer(roi, { color: "blue" }, "Lago Titicaca (ROI EXTRACTED)");

// ==========================
// 8) Print ROI information
// ==========================
print("Área del Lago Titicaca (m²):", roi.area({ maxError: 10 }));
print("ROI exacto del Lago Titicaca:", roi);
print("Export to GeoJSON:");
print(roi.coordinates());

// ==========================
// 9) Export ROI as GeoJSON (optional)
// ==========================
// To export, uncomment the following lines:
/*
Export.table.toDrive({
  collection: ee.FeatureCollection([ee.Feature(roi)]),
  description: 'titicaca_roi',
  fileFormat: 'GeoJSON'
});
*/
