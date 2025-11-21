// ==========================
// TITICACA SENTINEL - SENTINEL-2 PROCESSING
// Process Sentinel-2 SR data and calculate water quality indices
// ==========================

// ==========================
// 1) CONFIGURATION
// ==========================
var config = {
  // Time range (last 6 months from today)
  startDate: "2024-05-21",
  endDate: "2024-11-21",

  // Cloud coverage threshold
  cloudCoverage: 20,

  // Lake Titicaca bounding box
  bbox: ee.Geometry.Rectangle([-70.3, -17.3, -68.4, -15.4]),
};

// ==========================
// 2) EXTRACT ROI (Lake Titicaca)
// ==========================
var gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater");
var occurrence = gsw.select("occurrence");
var waterMask = occurrence.gt(50).selfMask();

var vectors = waterMask.reduceToVectors({
  geometry: config.bbox,
  scale: 30,
  geometryType: "polygon",
  maxPixels: 1e13,
});

var vectorsWithArea = vectors.map(function (f) {
  var area = f.geometry({ maxError: 10 }).area({ maxError: 10 });
  return f.set("area", area);
});

var lake = vectorsWithArea.sort("area", false).first();
var roi = ee.Feature(lake).geometry({ maxError: 10 });

print("ROI Area (km²):", roi.area({ maxError: 10 }).divide(1e6));

// ==========================
// 3) LOAD SENTINEL-2 SR DATA
// ==========================
var s2 = ee
  .ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
  .filterBounds(roi)
  .filterDate(config.startDate, config.endDate)
  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", config.cloudCoverage));

print("Total images found:", s2.size());

// ==========================
// 4) CLOUD MASKING FUNCTION
// ==========================
function maskS2clouds(image) {
  var qa = image.select("QA60");

  // Bits 10 and 11 are clouds and cirrus
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  var mask = qa
    .bitwiseAnd(cloudBitMask)
    .eq(0)
    .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image
    .updateMask(mask)
    .divide(10000)
    .copyProperties(image, ["system:time_start"]);
}

// ==========================
// 5) CALCULATE WATER QUALITY INDICES
// ==========================
function calculateIndices(image) {
  // Extract bands
  var green = image.select("B3");
  var red = image.select("B4");
  var redEdge1 = image.select("B5");
  var nir = image.select("B8");
  var swir1 = image.select("B11");

  // NDWI - Normalized Difference Water Index
  var ndwi = nir.subtract(green).divide(nir.add(green)).rename("NDWI");

  // NDCI - Normalized Difference Chlorophyll Index
  var ndci = redEdge1.subtract(red).divide(redEdge1.add(red)).rename("NDCI");

  // CI-green - Chlorophyll Index Green
  var ciGreen = nir.divide(green).subtract(1).rename("CI_green");

  // Turbidity approximation (Red/Green ratio)
  var turbidity = red.divide(green).rename("Turbidity");

  // TSM approximation (NIR/Red ratio)
  var tsm = nir.divide(red).rename("TSM");

  // Chlorophyll-a approximation (simple baseline)
  // Based on NDCI correlation with Chl-a
  var chla = ndci.multiply(50).add(30).clamp(0, 150).rename("Chla_approx");

  return image.addBands([ndwi, ndci, ciGreen, turbidity, tsm, chla]);
}

// ==========================
// 6) PROCESS COLLECTION
// ==========================
var s2Processed = s2.map(maskS2clouds).map(calculateIndices);

// Get latest image
var latest = s2Processed.sort("system:time_start", false).first();
var latestDate = ee.Date(latest.get("system:time_start")).format("YYYY-MM-dd");
print("Latest image date:", latestDate);

// Create median composite for the period
var composite = s2Processed.median().clip(roi);

// ==========================
// 7) RISK CLASSIFICATION
// ==========================
function classifyRisk(image) {
  var ndci = image.select("NDCI");
  var turbidity = image.select("Turbidity");

  // Calculate percentiles for relative thresholds
  var ndciStats = ndci.reduceRegion({
    reducer: ee.Reducer.percentile([70, 90]),
    geometry: roi,
    scale: 30,
    maxPixels: 1e9,
  });

  var turbStats = turbidity.reduceRegion({
    reducer: ee.Reducer.percentile([70, 90]),
    geometry: roi,
    scale: 30,
    maxPixels: 1e9,
  });

  var ndci_p70 = ee.Number(ndciStats.get("NDCI_p70"));
  var ndci_p90 = ee.Number(ndciStats.get("NDCI_p90"));
  var turb_p70 = ee.Number(turbStats.get("Turbidity_p70"));
  var turb_p90 = ee.Number(turbStats.get("Turbidity_p90"));

  print("NDCI Thresholds - P70:", ndci_p70, "P90:", ndci_p90);
  print("Turbidity Thresholds - P70:", turb_p70, "P90:", turb_p90);

  // Risk classification
  // High risk: NDCI > p90 OR Turbidity > p90
  // Medium risk: NDCI > p70 OR Turbidity > p70
  // Low risk: below thresholds

  var highRisk = ndci.gt(ndci_p90).or(turbidity.gt(turb_p90));
  var mediumRisk = ndci
    .gt(ndci_p70)
    .or(turbidity.gt(turb_p70))
    .and(highRisk.not());
  var lowRisk = highRisk.not().and(mediumRisk.not());

  // Create risk map (1=low, 2=medium, 3=high)
  var riskMap = lowRisk
    .multiply(1)
    .add(mediumRisk.multiply(2))
    .add(highRisk.multiply(3))
    .rename("Risk_Level");

  return image.addBands(riskMap);
}

var compositeWithRisk = classifyRisk(composite);

// ==========================
// 8) VISUALIZATION
// ==========================
// RGB visualization
var rgbVis = {
  bands: ["B4", "B3", "B2"],
  min: 0.0,
  max: 0.3,
  gamma: 1.4,
};

// NDWI visualization
var ndwiVis = {
  min: -1,
  max: 1,
  palette: ["red", "yellow", "green", "cyan", "blue"],
};

// NDCI visualization (chlorophyll)
var ndciVis = {
  min: -0.5,
  max: 0.5,
  palette: ["blue", "cyan", "yellow", "orange", "red"],
};

// Risk visualization
var riskVis = {
  min: 1,
  max: 3,
  palette: ["green", "yellow", "red"],
};

// Turbidity visualization
var turbVis = {
  min: 0.5,
  max: 2.0,
  palette: ["blue", "cyan", "yellow", "orange", "brown"],
};

// ==========================
// 9) ADD LAYERS TO MAP
// ==========================
Map.centerObject(roi, 9);
Map.addLayer(roi, { color: "blue" }, "Lake Titicaca ROI", false);
Map.addLayer(composite, rgbVis, "RGB Composite");
Map.addLayer(composite.select("NDWI"), ndwiVis, "NDWI", false);
Map.addLayer(composite.select("NDCI"), ndciVis, "NDCI (Chlorophyll)", true);
Map.addLayer(composite.select("Turbidity"), turbVis, "Turbidity", false);
Map.addLayer(compositeWithRisk.select("Risk_Level"), riskVis, "Risk Map", true);

// ==========================
// 10) CALCULATE STATISTICS
// ==========================
var stats = composite
  .select(["NDWI", "NDCI", "CI_green", "Turbidity", "TSM", "Chla_approx"])
  .reduceRegion({
    reducer: ee.Reducer.mean()
      .combine({
        reducer2: ee.Reducer.stdDev(),
        sharedInputs: true,
      })
      .combine({
        reducer2: ee.Reducer.percentile([10, 50, 90]),
        sharedInputs: true,
      }),
    geometry: roi,
    scale: 100,
    maxPixels: 1e9,
  });

print("Lake Statistics:", stats);

// ==========================
// 11) EXPORT INSTRUCTIONS
// ==========================
print("\n=== EXPORT INSTRUCTIONS ===");
print("To export the processed data, uncomment the Export sections below:");
print("1. Risk map as GeoTIFF");
print("2. Statistics as JSON");
print("3. Time series data");

/*
// Export risk map
Export.image.toDrive({
  image: compositeWithRisk.select(['B4', 'B3', 'B2', 'NDWI', 'NDCI', 'CI_green', 'Turbidity', 'Risk_Level']),
  description: 'titicaca_risk_map',
  folder: 'TiticacaSentinel',
  region: roi,
  scale: 30,
  maxPixels: 1e9
});

// Export statistics
Export.table.toDrive({
  collection: ee.FeatureCollection([
    ee.Feature(null, stats).set('date', latestDate)
  ]),
  description: 'titicaca_stats',
  folder: 'TiticacaSentinel',
  fileFormat: 'JSON'
});
*/
