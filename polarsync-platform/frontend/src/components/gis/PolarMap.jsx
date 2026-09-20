import React, { useEffect, useState, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Layers, Maximize2, ShieldAlert, Truck, Users, MapPin, Route as RouteIcon, AlertTriangle } from 'lucide-react';

// Map auto-fit bounds helper component
function MapBoundsUpdater({ locations, assets, personnel, emergency, triggerFit }) {
  const map = useMap();

  useEffect(() => {
    const points = [];
    if (locations && locations.length > 0) {
      locations.forEach(loc => points.push([loc.latitude, loc.longitude]));
    }
    if (assets && assets.length > 0) {
      assets.forEach(a => points.push([a.latitude, a.longitude]));
    }
    if (emergency) {
      points.push([emergency.latitude, emergency.longitude]);
    }

    if (points.length > 0) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 9 });
    }
  }, [locations, assets, emergency, triggerFit, map]);

  return null;
}

// Custom DivIcons
const createStationIcon = (name, type) => {
  const isBase = type === 'BASE_STATION' || name.includes('Maitri');
  const bg = isBase ? '#0284c7' : '#0369a1';
  const border = isBase ? '#38bdf8' : '#7dd3fc';
  const label = name.replace('Camp ', 'C-').substring(0, 9);

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="
        background: ${bg};
        border: 2px solid ${border};
        color: #ffffff;
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 10px;
        font-weight: 700;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 4px;
      ">
        <span style="display:inline-block; width:6px; height:6px; background:#38bdf8; border-radius:50%;"></span>
        ${label}
      </div>
    `,
    iconSize: [64, 24],
    iconAnchor: [32, 12]
  });
};

const createVehicleIcon = (asset) => {
  const isMoving = asset.speed_kmh > 0 || asset.status === 'IN_TRANSIT';
  const isSAR = asset.status === 'DISPATCHED_EMERGENCY';
  const isLowFuel = asset.fuel_pct < 25;
  const bg = isSAR ? '#d97706' : (isLowFuel ? '#991b1b' : '#0f172a');
  const border = isSAR ? '#fbbf24' : (isLowFuel ? '#ef4444' : (isMoving ? '#38bdf8' : '#64748b'));

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="
        background: ${bg};
        border: 2px solid ${border};
        color: #f1f5f9;
        border-radius: 4px;
        padding: 2px 5px;
        font-size: 10px;
        font-weight: 700;
        font-family: monospace;
        box-shadow: 0 0 8px ${border}88;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 4px;
      ">
        <span style="color:${isSAR ? '#fbbf24' : (isLowFuel ? '#f87171' : '#38bdf8')}">⯈</span>
        ${asset.name || asset.id}
      </div>
    `,
    iconSize: [68, 22],
    iconAnchor: [34, 11]
  });
};

const createPersonnelIcon = (person) => {
  const isAffected = person.status === 'AFFECTED_EMERGENCY' || person.status === 'UNCONFIRMED_DUE';
  const bg = isAffected ? '#e11d48' : '#065f46';
  const border = isAffected ? '#fda4af' : '#34d399';

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
        box-shadow: 0 0 6px ${border};
      ">
        👤
      </div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

const createEmergencyIcon = (emergency) => {
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="emergency-pin" style="
        width: 34px;
        height: 34px;
        background: #e11d48;
        border: 2px solid #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 15px;
      ">
        ⚠
      </div>
    `,
    iconSize: [34, 34],
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
  height = '520px'
}) => {
  const defaultCenter = [-70.3, 40.0];

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

  return (
    <div className="relative rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950" style={{ height }}>
      {/* Top HUD Bar */}
      <div className="absolute top-3 left-3 z-[1000] polar-glass px-3.5 py-1.5 rounded-lg text-xs font-mono flex items-center gap-3 border border-sky-500/30">
        <span className="flex items-center gap-1.5 text-sky-400 font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          GIS COMMAND CENTER
        </span>
        <span className="text-slate-500">|</span>
        <span className="text-slate-300">QUEEN MAUD LAND (ANTARCTICA)</span>
      </div>

      {/* Layer Controls Bar (Top Right) */}
      <div className="absolute top-3 right-3 z-[1000] flex items-center gap-1.5 polar-glass p-1 rounded-lg border border-slate-700/80 backdrop-blur-md">
        <button
          onClick={() => toggleLayer('bases')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.bases
              ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Stations & Bases"
        >
          Bases
        </button>

        <button
          onClick={() => toggleLayer('assets')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.assets
              ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Vehicle Assets"
        >
          Assets
        </button>

        <button
          onClick={() => toggleLayer('personnel')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.personnel
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Personnel Locations"
        >
          Personnel
        </button>

        <button
          onClick={() => toggleLayer('routes')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.routes
              ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Traverse Routes"
        >
          Routes
        </button>

        <button
          onClick={() => toggleLayer('dangerZones')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.dangerZones
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Danger Zones"
        >
          Danger Zones
        </button>

        <button
          onClick={() => toggleLayer('emergencies')}
          className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition ${
            layers.emergencies
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
              : 'text-slate-500 hover:text-slate-300'
          }`}
          title="Toggle Emergencies"
        >
          Emergency
        </button>

        <div className="w-[1px] h-4 bg-slate-700 mx-0.5" />

        <button
          onClick={() => setFitTrigger((prev) => prev + 1)}
          className="px-2.5 py-1 rounded text-[11px] font-mono font-semibold bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 flex items-center gap-1"
          title="Fit bounds to active operations"
        >
          <Maximize2 className="w-3 h-3" />
          <span>FIT TO OPERATION</span>
        </button>
      </div>

      {/* Map Legend (Bottom Right) */}
      <div className="absolute bottom-3 right-3 z-[1000] polar-glass p-2.5 rounded-lg text-[11px] font-mono border border-slate-700/60 flex flex-col gap-1.5 backdrop-blur-md">
        <div className="font-semibold text-slate-300 text-xs border-b border-slate-700 pb-1 mb-0.5">MAP LAYERS</div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded bg-sky-600 border border-sky-400"></span> Station / Base
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded bg-slate-900 border border-sky-400"></span> Vehicle Fleet
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-rose-600/40 border border-rose-500"></span> Danger Zone
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-0.5 bg-sky-400 inline-block"></span> Transit Corridor
        </div>
        {emergency && layers.emergencies && (
          <div className="flex items-center gap-2 text-rose-400 font-bold animate-pulse">
            <span className="w-3 h-3 rounded-full bg-rose-600 border border-white"></span> SAR Incident
          </div>
        )}
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={7}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <MapBoundsUpdater
          locations={locations}
          assets={assets}
          personnel={personnel}
          emergency={emergency}
          triggerFit={fitTrigger}
        />

        {/* Base Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="filter brightness-[0.75] contrast-[1.2] invert-[0.9] hue-rotate-[190deg]"
        />

        {/* Danger Zones */}
        {layers.dangerZones && dangerZones.map((zone) => (
          <Circle
            key={zone.id}
            center={[zone.center_lat, zone.center_lon]}
            radius={zone.radius_km * 1000}
            pathOptions={{
              color: zone.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b',
              fillColor: zone.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b',
              fillOpacity: 0.25,
              weight: 1.5,
              dashArray: '4, 6'
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={0.9} sticky>
              <div className="font-mono text-xs">
                <div className="font-bold text-rose-400">⚠ {zone.name}</div>
                <div>Type: {zone.type}</div>
                <div>Radius: {zone.radius_km} km ({zone.severity})</div>
                {zone.passable_by_air_only && <div className="text-amber-300">Air passage only</div>}
              </div>
            </Tooltip>
          </Circle>
        ))}

        {/* Route Lines */}
        {layers.routes && routes.map((route) => (
          <Polyline
            key={route.id}
            positions={route.waypoints}
            pathOptions={{
              color: '#38bdf8',
              weight: 3,
              opacity: 0.7,
              dashArray: '6, 8'
            }}
          >
            <Tooltip sticky>
              <div className="font-mono text-xs text-sky-300">
                <div className="font-bold">{route.name}</div>
                <div>Distance: {route.distance_km} km</div>
              </div>
            </Tooltip>
          </Polyline>
        ))}

        {/* Location / Base Stations */}
        {layers.bases && locations.map((loc) => (
          <Marker
            key={loc.id}
            position={[loc.latitude, loc.longitude]}
            icon={createStationIcon(loc.name, loc.type)}
          >
            <Popup>
              <div className="font-mono text-xs">
                <div className="font-bold text-sky-400 text-sm mb-1">{loc.name}</div>
                <div className="text-slate-300">Station ID: {loc.id}</div>
                <div className="text-slate-300">Type: {loc.type}</div>
                <div className="text-slate-300">Coordinates: {loc.latitude.toFixed(4)}°, {loc.longitude.toFixed(4)}°</div>
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

        {/* Vehicle Fleet */}
        {layers.assets && assets.map((asset) => (
          <Marker
            key={asset.id}
            position={[asset.latitude, asset.longitude]}
            icon={createVehicleIcon(asset)}
          >
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
                <div className="text-slate-300">Speed: {asset.speed_kmh} km/h | Heading: {asset.heading}°</div>
                <div className="text-slate-300">Fuel Level: {asset.fuel_pct}% ({asset.fuel_liters} L)</div>
                <div className="text-slate-300">Battery: {asset.battery_pct}%</div>
                <div className="text-slate-300">Connectivity: {asset.connectivity}</div>
                <div className="text-slate-300">Route Progress: {asset.route_progress_pct}%</div>
                <div className="mt-1 text-slate-400 text-[10px]">
                  Coords: {asset.latitude.toFixed(4)}°, {asset.longitude.toFixed(4)}°
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Personnel Markers (when coordinates exist) */}
        {layers.personnel && personnel.map((person) => {
          if (!person.latitude || !person.longitude) return null;
          return (
            <Marker
              key={person.id}
              position={[person.latitude, person.longitude]}
              icon={createPersonnelIcon(person)}
            >
              <Popup>
                <div className="font-mono text-xs">
                  <div className="font-bold text-emerald-400 text-sm mb-1">{person.name}</div>
                  <div className="text-slate-300">ID: {person.id} | Role: {person.role}</div>
                  <div className="text-slate-300">Location: {person.assigned_location_id}</div>
                  <div className="text-slate-300">Movement: {person.movement_status}</div>
                  <div className="text-slate-300">Muster: {person.status}</div>
                  <div className="text-slate-300">Heartbeat: {person.heartbeat_active ? 'ACTIVE' : 'LOST'}</div>
                  <div className="text-slate-400 text-[10px] mt-1">
                    Coords: {person.latitude.toFixed(4)}°, {person.longitude.toFixed(4)}°
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Emergency Incident Marker */}
        {layers.emergencies && emergency && (
          <Marker
            position={[emergency.latitude, emergency.longitude]}
            icon={createEmergencyIcon(emergency)}
          >
            <Popup>
              <div className="font-mono text-xs">
                <div className="font-bold text-rose-500 text-sm flex items-center gap-1 mb-1">
                  <span>⚠ INCIDENT: {emergency.id}</span>
                </div>
                <div className="text-slate-200 font-semibold">{emergency.incident_type}</div>
                <div className="text-rose-300">Status: {emergency.status} ({emergency.severity})</div>
                <div className="text-slate-300">Landmark: {emergency.nearest_landmark}</div>
                <div className="text-slate-300">Affected Personnel: {emergency.affected_count} ({emergency.affected_personnel_ids?.join(', ')})</div>
                <div className="text-slate-300">Required: {emergency.required_capabilities?.join(', ')}</div>
                <div className="text-slate-400 text-[10px] mt-1">
                  Coords: {emergency.latitude.toFixed(4)}°, {emergency.longitude.toFixed(4)}°
                </div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default PolarMap;
