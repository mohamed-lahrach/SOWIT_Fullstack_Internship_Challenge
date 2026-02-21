import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "./App.css";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || "";
const SAVED_PLOTS_SOURCE_ID = "saved-plots";
const SAVED_PLOTS_FILL_LAYER_ID = "saved-plots-fill";
const SAVED_PLOTS_OUTLINE_LAYER_ID = "saved-plots-outline";

const toFeatureCollection = (features) => ({
  type: "FeatureCollection",
  features,
});

function App() {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const drawRef = useRef(null);

  const [plotName, setPlotName] = useState("");
  const [draftPolygon, setDraftPolygon] = useState(null);
  const [plots, setPlots] = useState([]);
  const [selectedPlotId, setSelectedPlotId] = useState("");

  const fetchPlots = async () => {
    const res = await fetch(`${API_BASE}/api/plots/`);
    if (!res.ok) throw new Error("Failed to fetch plots");
    const data = await res.json();
    setPlots(data.features || []);
  };

  useEffect(() => {
    if (!mapboxgl.accessToken) {
      console.error("Missing VITE_MAPBOX_TOKEN");
      return;
    }

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/streets-v12",
      center: [-6.84, 34.02], // Morocco-ish default
      zoom: 5,
    });
    mapRef.current = map;

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: { polygon: true, trash: true },
      defaultMode: "draw_polygon",
    });
    drawRef.current = draw;
    map.addControl(draw, "top-left");
    map.addControl(new mapboxgl.NavigationControl(), "top-left");

    const syncPolygon = () => {
      const data = draw.getAll();
      const first = data.features?.[0] || null;
      setDraftPolygon(first ? first.geometry : null);
    };

    map.on("draw.create", syncPolygon);
    map.on("draw.update", syncPolygon);
    map.on("draw.delete", () => setDraftPolygon(null));

    map.on("load", () => {
      if (!map.getSource(SAVED_PLOTS_SOURCE_ID)) {
        map.addSource(SAVED_PLOTS_SOURCE_ID, {
          type: "geojson",
          data: toFeatureCollection([]),
        });
      }

      if (!map.getLayer(SAVED_PLOTS_FILL_LAYER_ID)) {
        map.addLayer({
          id: SAVED_PLOTS_FILL_LAYER_ID,
          type: "fill",
          source: SAVED_PLOTS_SOURCE_ID,
          paint: {
            "fill-color": "#16a34a",
            "fill-opacity": 0.22,
          },
        });
      }

      if (!map.getLayer(SAVED_PLOTS_OUTLINE_LAYER_ID)) {
        map.addLayer({
          id: SAVED_PLOTS_OUTLINE_LAYER_ID,
          type: "line",
          source: SAVED_PLOTS_SOURCE_ID,
          paint: {
            "line-color": "#14532d",
            "line-width": 2.5,
            "line-opacity": 1,
          },
        });
      }
    });

    fetchPlots().catch(console.error);

    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const source = map.getSource(SAVED_PLOTS_SOURCE_ID);
    if (source) {
      source.setData(toFeatureCollection(plots));
      return;
    }

    const syncAfterLoad = () => {
      const loadedSource = map.getSource(SAVED_PLOTS_SOURCE_ID);
      if (!loadedSource) return;
      loadedSource.setData(toFeatureCollection(plots));
    };
    map.once("load", syncAfterLoad);
  }, [plots]);

  const handleSave = async () => {
    if (!draftPolygon) {
      alert("Draw a polygon first.");
      return;
    }
    if (!plotName.trim()) {
      alert("Enter a plot name.");
      return;
    }

    const payload = {
      type: "Feature",
      geometry: draftPolygon,
      properties: {
        name: plotName.trim(),
      },
    };

    const res = await fetch(`${API_BASE}/api/plots/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(JSON.stringify(err));
      return;
    }

    setPlotName("");
    drawRef.current?.deleteAll();
    setDraftPolygon(null);
    await fetchPlots();
  };

  const flyToPlot = (plotId) => {
    const feature = plots.find((p) => String(p.id) === String(plotId));
    if (!feature || !mapRef.current) return;

    const coords = feature.geometry?.coordinates?.[0];
    if (!coords?.length) return;

    const bounds = new mapboxgl.LngLatBounds();
    coords.forEach(([lng, lat]) => bounds.extend([lng, lat]));

    mapRef.current.fitBounds(bounds, {
      padding: 60,
      duration: 1500, // animation zoom/pan
    });
  };

  const handleSelect = (e) => {
    const value = e.target.value;
    setSelectedPlotId(value);
    if (value) flyToPlot(value);
  };

  return (
    <div className="app">
      <aside className="panel">
        <h2>Plots</h2>

        <label>Plot Name</label>
        <input
          value={plotName}
          onChange={(e) => setPlotName(e.target.value)}
          placeholder="e.g. Farm A"
        />

        <button onClick={handleSave}>Save Drawn Polygon</button>

        <label>Saved Plots</label>
        <select value={selectedPlotId} onChange={handleSelect}>
          <option value="">Select a plot...</option>
          {plots.map((f) => (
            <option key={f.id} value={f.id}>
              {f.properties?.name || `Plot ${f.id}`}
            </option>
          ))}
        </select>
      </aside>

      <main className="map-wrap">
        <div ref={mapContainerRef} className="map" />
      </main>
    </div>
  );
}

export default App;
