import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Maximize2, Compass, Radio } from 'lucide-react';

/**
 * Calculate the operational bounding box and centroid across all active entities.
 * Includes station locations, active assets, emergency coordinates, routes, and danger zone boundaries.
 */
export const computeOperationalBounds = (
  locations = [],
  assets = [],
  routes = [],
  dangerZones = [],
  emergency = null
) => {
  const points = [];

  // 1. Base stations & field camps
  locations.forEach((loc) => {
    if (loc.latitude != null && loc.longitude != null) {
      points.push([loc.latitude, loc.longitude]);
    }
  });

  // 2. Active fleet assets
  assets.forEach((a) => {
    if (a.latitude != null && a.longitude != null) {
      points.push([a.latitude, a.longitude]);
    }
  });

  // 3. Active emergency location
  if (emergency && emergency.latitude != null && emergency.longitude != null) {
    points.push([emergency.latitude, emergency.longitude]);
  }

  // 4. Routes (all key waypoints)
  routes.forEach((r) => {
    if (Array.isArray(r.waypoints)) {
      r.waypoints.forEach((wp) => {
        if (Array.isArray(wp) && wp.length >= 2 && wp[0] != null && wp[1] != null) {
          points.push([wp[0], wp[1]]);
        }
      });
    }
  });

  // 5. Danger zone bounding coordinates (accounting for radius buffer)
  dangerZones.forEach((dz) => {
    const lat = dz.center_lat ?? dz.center_coordinates?.[0];
    const lon = dz.center_lon ?? dz.center_coordinates?.[1];
    const radiusKm = dz.radius_km || 3.5;
    if (lat != null && lon != null) {
      const latBuffer = radiusKm / 111.0;
      const lonBuffer = radiusKm / (111.0 * Math.cos(Math.abs(lat) * Math.PI / 180.0));
      points.push([lat - latBuffer, lon - lonBuffer]);
      points.push([lat + latBuffer, lon + lonBuffer]);
    }
  });

  if (points.length === 0) {
    // Default Queen Maud Land operational corridor (Maitri-II to Zulu)
    return {
      bounds: L.latLngBounds([[-71.18, 11.60], [-70.74, 11.85]]),
      center: [-70.95, 11.75]
    };
  }

  const bounds = L.latLngBounds(points);
  const center = [bounds.getCenter().lat, bounds.getCenter().lng];
  return { bounds, center };
};

/**
 * Synchronizes Leaflet map view with aspect-ratio aware operational framing (~65-75% occupancy).
 */
function MapBoundsUpdater({ locations, assets, routes, dangerZones, emergency, triggerFit }) {
  const map = useMap();

  const applyOperationalFit = () => {
    const { bounds } = computeOperationalBounds(locations, assets, routes, dangerZones, emergency);
    
    if (bounds && bounds.isValid()) {
      map.fitBounds(bounds, {
        paddingTopLeft: [60, 50],
        paddingBottomRight: [50, 50],
        maxZoom: 10.5,
        minZoom: 6,
        animate: false
      });
    }
  };

  useEffect(() => {
    applyOperationalFit();

    const t1 = setTimeout(() => {
      map.invalidateSize();
      applyOperationalFit();
    }, 100);

    const t2 = setTimeout(() => {
      map.invalidateSize();
    }, 350);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [locations, assets, routes, dangerZones, emergency, triggerFit, map]);

  return null;
}

// -------------------------------------------------------------
// Reference-Matching Polar DivIcons & Badges
// -------------------------------------------------------------

const createStationIcon = (name, type) => {
  const isBase = type === 'BASE_STATION' || type === 'RESEARCH_BASE' || name.includes('Maitri');
  const isEvac = type === 'EMERGENCY_STATION' || name.includes('Oscar') || name.includes('Evac');
  
  const bg = isEvac ? '#1e1b4b' : (isBase ? '#0284c7' : '#0369a1');
  const border = isEvac ? '#f43f5e' : (isBase ? '#38bdf8' : '#38bdf8');
  const glow = isEvac ? 'rgba(244, 63, 94, 0.6)' : 'rgba(56, 189, 248, 0.6)';
  
  // Icon concept matching reference: Base gets facility/building, camps get tent/mountain
  const iconSymbol = isEvac ? '🚑' : (isBase ? '🏠' : '⛺');
  const flagBadge = isBase ? `<span style="position: absolute; top: -5px; right: -4px; font-size: 8px;">🇮🇳</span>` : '';
  
  const shortLabel = name
    .replace('Maitri-II Main Polar Base', 'Maitri-II Base')
    .replace('Camp Alpha - Schirmacher Oasis', 'Camp Alpha')
    .replace('Field Camp Zulu - Deep Ice Sheet', 'Field C-Zulu')
    .replace('Field Camp Bravo - Nunatak Ridge', 'Field C-Bravo')
    .replace('Emergency Station Oscar', 'EVAC OSCAR')
    .replace('Camp ', 'Field C-')
    .replace('Field Camp ', 'Field C-');

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="
        display: flex;
        align-items: center;
        gap: 6px;
        transform: translate(-16px, -16px);
        pointer-events: auto;
        cursor: pointer;
      ">
        <div style="
          position: relative;
          width: 32px;
          height: 32px;
          background: ${bg};
          border: 2px solid ${border};
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          box-shadow: 0 0 14px ${glow}, 0 4px 10px rgba(0,0,0,0.8);
          flex-shrink: 0;
        ">
          ${iconSymbol}
          ${flagBadge}
        </div>
        <div style="
          background: rgba(12, 26, 48, 0.92);
          border: 1px solid ${border};
          color: #ffffff;
          border-radius: 4px;
          padding: 2.5px 8px;
          font-size: 11px;
          font-weight: 700;
          font-family: 'JetBrains Mono', monospace;
          white-space: nowrap;
          box-shadow: 0 3px 10px rgba(0,0,0,0.9);
          text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        ">
          ${shortLabel}
        </div>
      </div>
    `,
    iconSize: [120, 32],
    iconAnchor: [16, 16]
  });
};

const getVehicleTypeSymbol = (type = '') => {
  const t = type.toUpperCase();
  if (t.includes('HELI') || t.includes('AIR') || t.includes('CHOPPER')) return '🚁';
  if (t.includes('SNOWCAT') || t.includes('TRUCK') || t.includes('HEAVY')) return '🚙';
  if (t.includes('SKIDOO') || t.includes('SNOWMOBILE')) return '🏍';
  if (t.includes('HAGGLUND') || t.includes('TRACKED')) return '🚜';
  if (t.includes('DRONE') || t.includes('UAV')) return '🛸';
  return '🚙';
};

/**
 * Compact Icon-Only Marker for Fleet Assets (Matching reference orbital circular badges)
 */
const createVehicleIcon = (asset) => {
  const isSAR = asset.status === 'DISPATCHED_EMERGENCY';
  const isLowFuel = asset.fuel_pct < 25;
  const symbol = getVehicleTypeSymbol(asset.type);

  // Distinct colors matching reference palette:
  // Helicopter: Red/Pink circle (#e11d48)
  // Heavy Snowcat: Blue circle (#0284c7)
  // Tracked/Skidoo: Teal/Emerald circle (#059669)
  // Drone: Violet circle (#7c3aed)
  let bg = '#0284c7';
  let border = '#38bdf8';
  let glow = 'rgba(56, 189, 248, 0.7)';

  if (symbol === '🚁') {
    bg = '#e11d48';
    border = '#fda4af';
    glow = 'rgba(244, 63, 94, 0.7)';
  } else if (symbol === '🚜' || symbol === '🏍') {
    bg = '#059669';
    border = '#6ee7b7';
    glow = 'rgba(16, 185, 129, 0.7)';
  } else if (symbol === '🛸') {
    bg = '#7c3aed';
    border = '#c084fc';
    glow = 'rgba(192, 132, 252, 0.7)';
  }

  if (isSAR) {
    border = '#f59e0b';
    glow = 'rgba(245, 158, 11, 0.9)';
  } else if (isLowFuel) {
    border = '#ef4444';
    glow = 'rgba(239, 68, 68, 0.9)';
  }

  const glowClass = isSAR ? 'sar-dispatched-glow' : '';

  return L.divIcon({
    className: `custom-leaflet-icon ${glowClass}`,
    html: `
      <div style="
        width: 28px;
        height: 28px;
        background: ${bg};
        border: 2px solid ${border};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        box-shadow: 0 0 12px ${glow}, 0 4px 8px rgba(0,0,0,0.8);
        transform: translate(-50%, -50%);
        pointer-events: auto;
        cursor: pointer;
      ">
        ${symbol}
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
};

const createPersonnelIcon = (person) => {
  const isAffected = person.status === 'AFFECTED_EMERGENCY' || person.status === 'UNCONFIRMED_DUE';
  const bg = isAffected ? '#e11d48' : '#059669';
  const border = isAffected ? '#fda4af' : '#6ee7b7';

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="
        background: ${bg};
        border: 1.5px solid ${border};
        color: #ffffff;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        font-size: 9px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 8px ${border};
        transform: translate(-50%, -50%);
        cursor: pointer;
      ">
        👤
      </div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

/**
 * Prominent Red Emergency Beacon with attached EMERGENCY pill matching reference
 */
const createEmergencyIcon = (emergency) => {
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="
        display: flex;
        align-items: center;
        gap: 6px;
        transform: translate(-17px, -17px);
        cursor: pointer;
        pointer-events: auto;
      ">
        <div style="
          position: relative;
          width: 34px;
          height: 34px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        ">
          <div class="emergency-radar-ring"></div>
          <div class="emergency-pin" style="
            width: 32px;
            height: 32px;
            font-size: 15px;
            background: #9f1239;
            border: 2px solid #f43f5e;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 16px rgba(244, 63, 94, 0.9), 0 4px 10px rgba(0,0,0,0.9);
          ">
            ⚠
          </div>
        </div>
        <div style="
          background: rgba(159, 18, 57, 0.95);
          border: 1px solid #f43f5e;
          color: #ffffff;
          font-size: 10px;
          font-family: 'JetBrains Mono', monospace;
          font-weight: 800;
          letter-spacing: 0.5px;
          padding: 2.5px 8px;
          border-radius: 4px;
          white-space: nowrap;
          box-shadow: 0 3px 10px rgba(0,0,0,0.9);
        ">
          EMERGENCY
        </div>
      </div>
    `,
    iconSize: [120, 34],
    iconAnchor: [17, 17]
  });
};

export const PolarMap = ({
  locations = [],
  dangerZones = [],
  routes = [],
  assets = [],
  personnel = [],
  emergency = null,
  height = '640px'
}) => {
  // Compute initial geographic center dynamically from operational coordinates
  const initialMapSetup = useMemo(() => {
    return computeOperationalBounds(locations, assets, routes, dangerZones, emergency);
  }, [locations, assets, routes, dangerZones, emergency]);

  // Layer toggle states
  const [layers, setLayers] = useState({
    bases: true,
    assets: true,
    personnel: false,
    emergencies: true,
    routes: true,
    dangerZones: true,
  });

  const [fitTrigger, setFitTrigger] = useState(0);

  const toggleLayer = (layerKey) => {
    setLayers((prev) => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  // Identify active routes (routes with deployed moving assets or emergency response)
  const activeRouteIds = useMemo(() => {
    const active = new Set();
    assets.forEach((a) => {
      if (a.current_route_id || a.route_id) {
        active.add(a.current_route_id || a.route_id);
      }
    });
    return active;
  }, [assets]);

  // Central operational anchor for fanning co-located / cluster assets (between Maitri and Bravo)
  const clusterAnchor = useMemo(() => {
    if (emergency && emergency.latitude && emergency.longitude) {
      return { lat: emergency.latitude - 0.035, lon: emergency.longitude };
    }
    return { lat: -70.87, lon: 11.72 };
  }, [emergency]);

  // Clean orbital fanning for vehicle fleet around the operational sector matching reference image
  const positionedAssets = useMemo(() => {
    const totalAssets = assets.length;
    if (totalAssets === 0) return [];

    // Orbital radius angles for realistic fanning (helicopter top-left, truck bottom, tracked bottom-right, drone top-right)
    const orbitRadiusLat = 0.028;
    const orbitRadiusLon = 0.052;

    return assets.map((a, idx) => {
      const isMoving = a.speed_kmh > 0 || a.status === 'IN_TRANSIT';

      // If moving along a distinct route, use its active GPS
      if (isMoving && a.latitude && a.longitude) {
        return {
          ...a,
          displayLat: a.latitude,
          displayLon: a.longitude,
          hasGuideLine: false
        };
      }

      // Orbital placement around cluster anchor
      const angle = ((idx * 2 * Math.PI) / Math.max(totalAssets, 3)) - Math.PI / 2;
      const displayLat = clusterAnchor.lat + Math.sin(angle) * orbitRadiusLat;
      const displayLon = clusterAnchor.lon + Math.cos(angle) * orbitRadiusLon;

      return {
        ...a,
        displayLat,
        displayLon,
        anchorLat: clusterAnchor.lat,
        anchorLon: clusterAnchor.lon,
        hasGuideLine: true
      };
    });
  }, [assets, clusterAnchor]);

  return (
    <div className="flex flex-col w-full">
      {/* -------------------------------------------------------------
          TOP COMMAND HEADER (Matching reference image header bar)
          ------------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 mb-2 px-1">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-full border border-sky-400/60 bg-sky-950/80 shadow-[0_0_14px_rgba(56,189,248,0.5)]">
            <div className="w-3 h-3 rounded-full bg-sky-400 animate-ping absolute opacity-60" />
            <Compass className="w-4 h-4 text-sky-300" />
          </div>
          <div>
            <h3 className="text-sm md:text-base font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <span>GEOSPATIAL COMMAND MAP (ANTARCTICA SECTOR)</span>
            </h3>
            <p className="text-[11px] font-mono text-sky-400/90 font-medium tracking-wide">
              POLARSYNC <span className="text-slate-600">|</span> QUEEN MAUD LAND <span className="text-slate-600">|</span> LIVE OPERATIONS
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs text-slate-400">
          <span className="text-sky-300 font-semibold">{assets.length} Assets <span className="text-slate-600">•</span> {locations.length} Stations</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300 hidden md:inline">Thu, 14 Dec 2024 <span className="text-slate-600">|</span> 14:32 UTC</span>
          <span className="text-slate-600 hidden md:inline">|</span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-950/90 border border-emerald-500/60 text-emerald-400 text-[11px] font-bold shadow-[0_0_8px_rgba(16,185,129,0.35)]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>
        </div>
      </div>

      {/* -------------------------------------------------------------
          MAIN LEAFLET MAP CONTAINER
          ------------------------------------------------------------- */}
      <div
        className="relative rounded-xl overflow-hidden border border-sky-500/30 shadow-[0_0_30px_rgba(0,0,0,0.9)] bg-slate-950"
        style={{ height, minHeight: '560px' }}
      >
        {/* Top-Left Tactical HUD Capsule */}
        <div className="absolute top-3.5 left-3.5 z-[1000] px-3.5 py-1.5 rounded-full text-xs font-mono flex items-center gap-2.5 border border-sky-500/40 bg-slate-950/85 backdrop-blur-md shadow-[0_4px_16px_rgba(0,0,0,0.85)]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-sky-400 font-bold tracking-wide">GIS COMMAND CENTER</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-200 font-medium text-[11px]">QUEEN MAUD LAND (ANTARCTICA)</span>
        </div>

        {/* Top-Right Tactical Controls Bar */}
        <div className="absolute top-3.5 right-3.5 z-[1000] flex flex-wrap items-center gap-1.5 p-1 rounded-lg border border-sky-500/30 bg-slate-950/85 backdrop-blur-md shadow-[0_4px_16px_rgba(0,0,0,0.85)]">
          <button
            onClick={() => toggleLayer('bases')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.bases
                ? 'bg-sky-900/60 text-sky-200 border border-sky-400/60 font-bold shadow-[0_0_8px_rgba(56,189,248,0.3)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Stations & Bases"
          >
            Bases
          </button>

          <button
            onClick={() => toggleLayer('assets')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.assets
                ? 'bg-sky-900/60 text-sky-200 border border-sky-400/60 font-bold shadow-[0_0_8px_rgba(56,189,248,0.3)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Vehicle Fleet"
          >
            Assets
          </button>

          <button
            onClick={() => toggleLayer('personnel')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.personnel
                ? 'bg-emerald-900/60 text-emerald-200 border border-emerald-400/60 font-bold shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Personnel"
          >
            Personnel
          </button>

          <button
            onClick={() => toggleLayer('routes')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.routes
                ? 'bg-sky-900/60 text-sky-200 border border-sky-400/60 font-bold shadow-[0_0_8px_rgba(56,189,248,0.3)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Traverse Routes"
          >
            Routes
          </button>

          <button
            onClick={() => toggleLayer('dangerZones')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.dangerZones
                ? 'bg-rose-950/80 text-rose-200 border border-rose-500/70 font-bold shadow-[0_0_10px_rgba(244,63,94,0.4)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Danger Zones"
          >
            Danger Zones
          </button>

          <button
            onClick={() => toggleLayer('emergencies')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
              layers.emergencies
                ? 'bg-rose-950/80 text-rose-200 border border-rose-500/70 font-bold shadow-[0_0_10px_rgba(244,63,94,0.4)]'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
            }`}
            title="Toggle Emergency Beacon"
          >
            Emergency
          </button>

          <div className="w-[1px] h-4 bg-slate-700 mx-0.5" />

          <button
            onClick={() => setFitTrigger((prev) => prev + 1)}
            className="px-3 py-1 rounded text-xs font-mono font-bold bg-sky-950/90 hover:bg-sky-900/90 text-sky-300 border border-sky-400/60 flex items-center gap-1.5 transition cursor-pointer shadow-[0_0_10px_rgba(56,189,248,0.3)]"
            title="Fit bounds to active operations"
          >
            <Maximize2 className="w-3.5 h-3.5 text-sky-400" />
            <span>FIT TO OPERATION</span>
          </button>
        </div>

        {/* Tactical North Arrow Compass (Top-Right under buttons) */}
        <div className="absolute top-16 right-4 z-[900] pointer-events-none flex flex-col items-center opacity-85">
          <div className="w-8 h-8 rounded-full border border-sky-400/50 bg-slate-950/80 flex items-center justify-center shadow-[0_0_12px_rgba(0,0,0,0.9)]">
            <div className="flex flex-col items-center">
              <span className="text-[9px] font-mono font-bold text-sky-300 leading-none mb-0.5">N</span>
              <div className="w-0 h-0 border-l-[3px] border-l-transparent border-r-[3px] border-r-transparent border-b-[6px] border-b-sky-400" />
            </div>
          </div>
        </div>

        {/* Tactical Scale Bar (Bottom-Left) */}
        <div className="absolute bottom-3.5 left-4 z-[900] pointer-events-none flex flex-col gap-0.5 font-mono text-[9px] text-slate-400 select-none">
          <div className="flex justify-between w-28 text-slate-300">
            <span>0</span>
            <span>250</span>
            <span>500</span>
            <span>750 km</span>
          </div>
          <div className="w-28 h-1.5 border-b border-l border-r border-sky-400/60 flex">
            <div className="w-1/3 border-r border-sky-400/40" />
            <div className="w-1/3 border-r border-sky-400/40" />
          </div>
        </div>

        {/* -------------------------------------------------------------
            MAP LAYERS LEGEND (Bottom Right matching reference)
            ------------------------------------------------------------- */}
        <div className="absolute bottom-3.5 right-3.5 z-[1000] p-3 rounded-lg text-xs font-mono border border-sky-500/30 bg-slate-950/85 backdrop-blur-md flex flex-col gap-2 shadow-[0_6px_20px_rgba(0,0,0,0.85)] min-w-[175px]">
          <div className="font-bold text-slate-100 text-xs border-b border-slate-700/80 pb-1 flex items-center justify-between">
            <span>MAP LAYERS</span>
          </div>

          <div 
            onClick={() => toggleLayer('bases')}
            className={`flex items-center justify-between gap-2 cursor-pointer select-none transition ${layers.bases ? 'text-slate-200' : 'text-slate-500 opacity-60'}`}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">🏠</span>
              <span className="w-2 h-2 rounded-full bg-sky-400 shadow-[0_0_6px_#38bdf8]" />
              <span>Station / Base</span>
            </div>
            <span className="text-[10px] text-sky-400 font-bold">{locations.length}</span>
          </div>

          <div 
            onClick={() => toggleLayer('assets')}
            className={`flex items-center justify-between gap-2 cursor-pointer select-none transition ${layers.assets ? 'text-slate-200' : 'text-slate-500 opacity-60'}`}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">🚙</span>
              <span className="w-2 h-2 rounded-full bg-sky-400 shadow-[0_0_6px_#38bdf8]" />
              <span>Vehicle Fleet</span>
            </div>
            <span className="text-[10px] text-sky-400 font-bold">{assets.length}</span>
          </div>

          <div 
            onClick={() => toggleLayer('dangerZones')}
            className={`flex items-center justify-between gap-2 cursor-pointer select-none transition ${layers.dangerZones ? 'text-slate-200' : 'text-slate-500 opacity-60'}`}
          >
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full border border-dashed border-rose-500 bg-rose-500/20 flex items-center justify-center text-[8px] text-rose-400">⚠</span>
              <span>Danger Zone</span>
            </div>
            <span className="text-[10px] text-rose-400 font-bold">{dangerZones.length}</span>
          </div>

          <div 
            onClick={() => toggleLayer('routes')}
            className={`flex items-center justify-between gap-2 cursor-pointer select-none transition ${layers.routes ? 'text-slate-200' : 'text-slate-500 opacity-60'}`}
          >
            <div className="flex items-center gap-2">
              <span className="w-4 h-0.5 border-b-2 border-dashed border-cyan-400 inline-block" />
              <span>Active Corridor</span>
            </div>
            <span className="text-[10px] text-cyan-400 font-bold">ACTIVE</span>
          </div>

          <div 
            onClick={() => toggleLayer('routes')}
            className={`flex items-center justify-between gap-2 cursor-pointer select-none transition ${layers.routes ? 'text-slate-400' : 'text-slate-600 opacity-60'}`}
          >
            <div className="flex items-center gap-2 text-[11px]">
              <span className="w-4 h-0.5 border-b border-dashed border-sky-700 inline-block" />
              <span>Standby Route</span>
            </div>
          </div>

          {emergency && layers.emergencies && (
            <div 
              onClick={() => toggleLayer('emergencies')}
              className="flex items-center justify-between gap-2 text-rose-400 font-bold pt-1 border-t border-rose-950/80 cursor-pointer select-none"
            >
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                <span>SAR Incident</span>
              </div>
              <span className="text-[10px] px-1 rounded bg-rose-950 text-rose-300 border border-rose-600">CRIT</span>
            </div>
          )}
        </div>

        {/* -------------------------------------------------------------
            LEAFLET MAP
            ------------------------------------------------------------- */}
        <MapContainer
          center={initialMapSetup.center}
          zoom={9.25}
          zoomSnap={0.25}
          zoomDelta={0.25}
          minZoom={5}
          maxZoom={12}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
        >
          <MapBoundsUpdater
            locations={locations}
            assets={assets}
            routes={routes}
            dangerZones={dangerZones}
            emergency={emergency}
            triggerFit={fitTrigger}
          />

          {/* Deep Midnight Polar High-Contrast Satellite/Terrain Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            className="filter brightness-[0.70] contrast-[1.35] invert-[0.96] hue-rotate-[198deg] saturate-[1.6]"
          />

          {/* Subtle Polar Continental / Oceanic Labels matching reference image */}
          {/* Atlantic Ocean (Top Left) */}
          <Marker
            position={[-70.72, 11.62]}
            icon={L.divIcon({
              className: 'custom-leaflet-icon',
              html: `
                <div style="
                  transform: translate(-50%, -50%);
                  color: rgba(148, 163, 184, 0.45);
                  font-family: 'JetBrains Mono', monospace;
                  font-size: 11px;
                  font-style: italic;
                  letter-spacing: 3px;
                  text-align: center;
                  white-space: nowrap;
                  pointer-events: none;
                ">
                  ATLANTIC<br/>OCEAN
                </div>
              `,
              iconSize: [0, 0],
              iconAnchor: [0, 0]
            })}
          />

          {/* Queen Maud Land (Center-Left over ice sheet) */}
          <Marker
            position={[-70.88, 11.63]}
            icon={L.divIcon({
              className: 'custom-leaflet-icon',
              html: `
                <div style="
                  transform: translate(-50%, -50%);
                  color: rgba(186, 230, 253, 0.45);
                  font-family: 'JetBrains Mono', monospace;
                  font-size: 11.5px;
                  font-weight: 700;
                  letter-spacing: 4px;
                  text-align: center;
                  white-space: nowrap;
                  pointer-events: none;
                ">
                  QUEEN MAUD LAND
                </div>
              `,
              iconSize: [0, 0],
              iconAnchor: [0, 0]
            })}
          />

          {/* Southern Ocean (Right) */}
          <Marker
            position={[-70.92, 11.88]}
            icon={L.divIcon({
              className: 'custom-leaflet-icon',
              html: `
                <div style="
                  transform: translate(-50%, -50%);
                  color: rgba(148, 163, 184, 0.45);
                  font-family: 'JetBrains Mono', monospace;
                  font-size: 11px;
                  font-style: italic;
                  letter-spacing: 3px;
                  text-align: center;
                  white-space: nowrap;
                  pointer-events: none;
                ">
                  SOUTHERN<br/>OCEAN
                </div>
              `,
              iconSize: [0, 0],
              iconAnchor: [0, 0]
            })}
          />

          {/* Antarctica Continental Spine (Bottom Center) */}
          <Marker
            position={[-71.16, 11.75]}
            icon={L.divIcon({
              className: 'custom-leaflet-icon',
              html: `
                <div style="
                  transform: translate(-50%, -50%);
                  color: rgba(186, 230, 253, 0.45);
                  font-family: 'JetBrains Mono', monospace;
                  font-size: 13px;
                  font-weight: 800;
                  letter-spacing: 8px;
                  text-align: center;
                  white-space: nowrap;
                  pointer-events: none;
                ">
                  A N T A R C T I C A
                </div>
              `,
              iconSize: [0, 0],
              iconAnchor: [0, 0]
            })}
          />

          {/* Danger Zones (Crevasse Fields in Red, Blizzard Passes in Amber) */}
          {layers.dangerZones &&
            dangerZones.map((zone) => {
              const lat = zone.center_lat ?? zone.center_coordinates?.[0];
              const lon = zone.center_lon ?? zone.center_coordinates?.[1];
              if (lat == null || lon == null) return null;

              const isExtreme = zone.severity === 'EXTREME' || zone.severity === 'CRITICAL' || zone.name.includes('Crevasse');
              const color = isExtreme ? '#f43f5e' : '#f59e0b';
              const iconColor = isExtreme ? '#fda4af' : '#fde68a';
              const bgBadge = isExtreme ? 'rgba(159, 18, 57, 0.92)' : 'rgba(180, 83, 9, 0.92)';

              return (
                <React.Fragment key={zone.id}>
                  <Circle
                    center={[lat, lon]}
                    radius={zone.radius_km * 1000}
                    pathOptions={{
                      color: color,
                      fillColor: color,
                      fillOpacity: isExtreme ? 0.14 : 0.12,
                      weight: 1.8,
                      dashArray: '6, 6'
                    }}
                  >
                    <Popup>
                      <div className="font-mono text-xs">
                        <div className="font-bold text-rose-400 text-sm mb-1">⚠ {zone.name}</div>
                        <div className="text-slate-300">Type: {zone.type}</div>
                        <div className="text-slate-300">Severity: {zone.severity}</div>
                        <div className="text-slate-300">Radius: {zone.radius_km} km</div>
                        {zone.passable_by_air_only && (
                          <div className="text-amber-300 font-semibold mt-1">✈ Aerial passage only</div>
                        )}
                      </div>
                    </Popup>
                  </Circle>

                  {/* Centered tactical hazard badge matching reference */}
                  <Marker
                    position={[lat, lon]}
                    icon={L.divIcon({
                      className: 'custom-leaflet-icon',
                      html: `
                        <div style="
                          display: flex;
                          flex-direction: column;
                          align-items: center;
                          transform: translate(-50%, -50%);
                          cursor: pointer;
                        ">
                          <div style="
                            width: 24px;
                            height: 24px;
                            background: ${bgBadge};
                            border: 1.5px solid ${color};
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 11px;
                            color: #ffffff;
                            box-shadow: 0 0 10px ${color}88, 0 3px 6px rgba(0,0,0,0.8);
                          ">
                            ⚠
                          </div>
                          <div style="
                            margin-top: 2px;
                            background: rgba(12, 26, 48, 0.92);
                            border: 1px solid ${color};
                            color: ${iconColor};
                            padding: 2px 7px;
                            border-radius: 4px;
                            font-family: 'JetBrains Mono', monospace;
                            font-size: 9.5px;
                            font-weight: 700;
                            white-space: nowrap;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.8);
                          ">
                            ${zone.name}
                          </div>
                        </div>
                      `,
                      iconSize: [110, 42],
                      iconAnchor: [55, 21]
                    })}
                  />
                </React.Fragment>
              );
            })}

          {/* Traverse Routes (Active cyan dashed corridor vs standby darker blue route) */}
          {layers.routes &&
            routes.map((route) => {
              const isActive = activeRouteIds.has(route.id) || route.status === 'ACTIVE' || route.name.includes('Zulu');

              return (
                <Polyline
                  key={route.id}
                  positions={route.waypoints}
                  pathOptions={{
                    color: isActive ? '#00e5ff' : '#1e40af',
                    weight: isActive ? 3 : 2,
                    opacity: isActive ? 0.95 : 0.65,
                    dashArray: isActive ? '8, 8' : '5, 8'
                  }}
                >
                  <Popup>
                    <div className="font-mono text-xs">
                      <div className="font-bold text-sky-400 text-sm mb-1">{route.name}</div>
                      <div className="text-slate-300">Route ID: {route.id}</div>
                      <div className="text-sky-300 font-semibold">Distance: {route.distance_km} km</div>
                      <div className="text-slate-300">
                        Status: {isActive ? '● ACTIVE OPERATIONAL CORRIDOR' : '○ Standby Traverse Route'}
                      </div>
                    </div>
                  </Popup>
                </Polyline>
              );
            })}

          {/* Radial connector lines for orbiting fleet assets */}
          {layers.assets &&
            positionedAssets.map((asset) => {
              if (!asset.hasGuideLine) return null;
              return (
                <Polyline
                  key={`line-${asset.id}`}
                  positions={[
                    [asset.anchorLat, asset.anchorLon],
                    [asset.displayLat, asset.displayLon]
                  ]}
                  pathOptions={{
                    color: '#38bdf8',
                    weight: 1,
                    opacity: 0.35,
                    dashArray: '2, 3'
                  }}
                />
              );
            })}

          {/* Base Stations & Field Camps */}
          {layers.bases &&
            locations.map((loc) => (
              <Marker
                key={loc.id}
                position={[loc.latitude, loc.longitude]}
                icon={createStationIcon(loc.name, loc.type)}
              >
                <Tooltip direction="top" offset={[0, -20]} opacity={0.95} className="leaflet-tooltip-dark">
                  <div className="font-mono text-xs">
                    <div className="font-bold text-sky-300">{loc.name}</div>
                    <div className="text-[10px] text-slate-400">Elevation: {loc.elevation_m}m</div>
                  </div>
                </Tooltip>
                <Popup>
                  <div className="font-mono text-xs">
                    <div className="font-bold text-sky-400 text-sm mb-1">{loc.name}</div>
                    <div className="text-slate-300">Station ID: {loc.id}</div>
                    <div className="text-slate-300">Type: {loc.type}</div>
                    <div className="text-slate-300">
                      Coords: {loc.latitude.toFixed(4)}°, {loc.longitude.toFixed(4)}°
                    </div>
                    <div className="text-slate-300">Elevation: {loc.elevation_m} m</div>
                    {loc.facilities && loc.facilities.length > 0 && (
                      <div className="mt-1.5 pt-1 border-t border-slate-700 text-[11px] text-slate-400">
                        Facilities: {loc.facilities.join(', ')}
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}

          {/* Vehicle Fleet Assets */}
          {layers.assets &&
            positionedAssets.map((asset) => (
              <Marker
                key={asset.id}
                position={[asset.displayLat, asset.displayLon]}
                icon={createVehicleIcon(asset)}
              >
                <Tooltip direction="top" offset={[0, -14]} opacity={0.95} className="leaflet-tooltip-dark">
                  <div className="font-mono text-xs">
                    <div className="font-bold text-sky-300 flex items-center gap-1">
                      <span>{getVehicleTypeSymbol(asset.type)}</span>
                      <span>{asset.name || asset.id}</span>
                    </div>
                    <div className="text-slate-300 text-[10px]">
                      Status: <strong className={asset.status === 'DISPATCHED_EMERGENCY' ? 'text-amber-400' : 'text-slate-200'}>{asset.status}</strong>
                    </div>
                    {asset.speed_kmh > 0 && (
                      <div className="text-sky-400 text-[10px]">Speed: {Math.round(asset.speed_kmh)} km/h</div>
                    )}
                    <div className="text-slate-400 text-[10px]">Fuel: {asset.fuel_pct}%</div>
                  </div>
                </Tooltip>
                <Popup>
                  <div className="font-mono text-xs">
                    <div className="font-bold text-sky-400 text-sm flex items-center justify-between mb-1">
                      <span>{asset.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">
                        {asset.status}
                      </span>
                    </div>
                    <div className="text-slate-300">Asset ID: {asset.id}</div>
                    <div className="text-slate-300">Type: {asset.type}</div>
                    <div className="text-slate-300">
                      Speed: {asset.speed_kmh} km/h | Heading: {asset.heading}°
                    </div>
                    <div className="text-slate-300">
                      Fuel Level: {asset.fuel_pct}% ({asset.fuel_liters} L)
                    </div>
                    <div className="text-slate-300">Battery: {asset.battery_pct}%</div>
                    <div className="text-slate-300">Connectivity: {asset.connectivity}</div>
                    <div className="text-slate-300">Route Progress: {asset.route_progress_pct}%</div>
                    <div className="mt-1 text-slate-400 text-[10px]">
                      GPS: {asset.latitude.toFixed(4)}°, {asset.longitude.toFixed(4)}°
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

          {/* Personnel Markers (when enabled) */}
          {layers.personnel &&
            personnel.map((person) => {
              if (!person.latitude || !person.longitude) return null;
              return (
                <Marker
                  key={person.id}
                  position={[person.latitude, person.longitude]}
                  icon={createPersonnelIcon(person)}
                >
                  <Tooltip direction="top" offset={[0, -10]} opacity={0.95} className="leaflet-tooltip-dark">
                    <div className="font-mono text-xs">
                      <div className="font-bold text-emerald-400">{person.name}</div>
                      <div className="text-slate-300 text-[10px]">{person.role} • {person.status}</div>
                    </div>
                  </Tooltip>
                  <Popup>
                    <div className="font-mono text-xs">
                      <div className="font-bold text-emerald-400 text-sm mb-1">{person.name}</div>
                      <div className="text-slate-300">ID: {person.id} | Role: {person.role}</div>
                      <div className="text-slate-300">Location: {person.assigned_location_id}</div>
                      <div className="text-slate-300">Movement: {person.movement_status}</div>
                      <div className="text-slate-300">Muster: {person.status}</div>
                      <div className="text-slate-300">
                        Heartbeat: {person.heartbeat_active ? 'ACTIVE' : 'LOST'}
                      </div>
                      <div className="text-slate-400 text-[10px] mt-1">
                        GPS: {person.latitude.toFixed(4)}°, {person.longitude.toFixed(4)}°
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

          {/* Emergency Incident Beacon (Scenario 3 SAR) */}
          {layers.emergencies && emergency && (
            <Marker
              position={[emergency.latitude, emergency.longitude]}
              icon={createEmergencyIcon(emergency)}
            >
              <Tooltip direction="top" offset={[0, -22]} opacity={0.95} className="leaflet-tooltip-dark">
                <div className="font-mono text-xs">
                  <div className="font-bold text-rose-400 flex items-center gap-1">
                    <span>🚨 {emergency.id}</span>
                  </div>
                  <div className="text-slate-200 text-[10px]">{emergency.incident_type}</div>
                  <div className="text-rose-300 text-[10px]">Location: {emergency.nearest_landmark}</div>
                  <div className="text-amber-300 text-[10px]">Affected: {emergency.affected_count} personnel</div>
                </div>
              </Tooltip>
              <Popup>
                <div className="font-mono text-xs">
                  <div className="font-bold text-rose-500 text-sm flex items-center gap-1 mb-1">
                    <span>⚠ INCIDENT: {emergency.id}</span>
                  </div>
                  <div className="text-slate-200 font-semibold">{emergency.incident_type}</div>
                  <div className="text-rose-300">
                    Status: {emergency.status} ({emergency.severity})
                  </div>
                  <div className="text-slate-300">Landmark: {emergency.nearest_landmark}</div>
                  <div className="text-slate-300">
                    Affected Personnel: {emergency.affected_count} ({emergency.affected_personnel_ids?.join(', ')})
                  </div>
                  <div className="text-slate-300">
                    Required: {emergency.required_capabilities?.join(', ')}
                  </div>
                  <div className="text-slate-400 text-[10px] mt-1">
                    GPS: {emergency.latitude.toFixed(4)}°, {emergency.longitude.toFixed(4)}°
                  </div>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    </div>
  );
};

export default PolarMap;
