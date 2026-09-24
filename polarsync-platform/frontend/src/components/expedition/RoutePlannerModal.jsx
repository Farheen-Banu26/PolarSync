import React, { useState } from 'react';
import { Compass, Fuel, Clock, AlertTriangle, ShieldCheck, Plus, Trash2, X, CheckCircle2, ChevronRight } from 'lucide-react';
import { planRoute, saveRoute } from '../../services/api';
import StatusBadge from '../common/StatusBadge';

export const RoutePlannerModal = ({ isOpen, onClose, locations = [], assets = [], onRouteSaved, scenarioId = 1 }) => {
  if (!isOpen) return null;

  const [originId, setOriginId] = useState(locations[0]?.id || 'MAITRI_II');
  const [destId, setDestId] = useState(locations[1]?.id || 'CAMP_ALPHA');
  const [vehicleId, setVehicleId] = useState(assets[0]?.id || 'TV-01');
  const [waypoints, setWaypoints] = useState([]);
  const [newLat, setNewLat] = useState('');
  const [newLon, setNewLon] = useState('');
  const [planningResult, setPlanningResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const originLoc = locations.find(l => l.id === originId) || locations[0] || { latitude: -70.7667, longitude: 11.7333 };
  const destLoc = locations.find(l => l.id === destId) || locations[1] || { latitude: -70.8333, longitude: 11.7500 };
  const selectedVehicle = assets.find(a => a.id === vehicleId) || assets[0] || { name: 'PistenBully 300 Polar', fuel_pct: 95 };

  const handleAddWaypoint = () => {
    const lat = parseFloat(newLat);
    const lon = parseFloat(newLon);
    if (!isNaN(lat) && !isNaN(lon)) {
      setWaypoints([...waypoints, [lat, lon]]);
      setNewLat('');
      setNewLon('');
      setPlanningResult(null);
    }
  };

  const handleRemoveWaypoint = (index) => {
    setWaypoints(waypoints.filter((_, i) => i !== index));
    setPlanningResult(null);
  };

  const handleEvaluate = async () => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const payload = {
        origin_id: originId,
        origin_coords: [originLoc.latitude, originLoc.longitude],
        destination_id: destId,
        destination_coords: [destLoc.latitude, destLoc.longitude],
        waypoints: waypoints,
        vehicle_id: vehicleId,
        vehicle_name: selectedVehicle.name,
        avg_speed_kmh: 18.0,
        fuel_consumption_l_per_km: 1.4,
        vehicle_fuel_capacity_l: 450.0,
        current_fuel_pct: selectedVehicle.fuel_pct || 90.0
      };

      const res = await planRoute(payload, scenarioId);
      setPlanningResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Route feasibility calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRoute = async () => {
    if (!planningResult) return;
    setSaving(true);
    setError(null);
    try {
      const savePayload = {
        name: `${originLoc.name || originId} to ${destLoc.name || destId} Traverse`,
        origin_id: originId,
        destination_id: destId,
        vehicle_id: vehicleId,
        total_distance_km: planningResult.total_distance_km,
        estimated_travel_time_hours: planningResult.estimated_travel_time_hours,
        waypoints: planningResult.waypoints,
        notes: `Validated traverse corridor with ${planningResult.fuel_remaining_pct}% remaining fuel.`
      };

      await saveRoute(savePayload);
      setSuccessMsg('Traverse route successfully approved and recorded in audit log!');
      if (onRouteSaved) onRouteSaved();
      setTimeout(() => {
        onClose();
      }, 1400);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to save route');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in font-mono text-xs">
      <div className="polar-glass w-full max-w-2xl rounded-2xl border border-sky-500/30 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg bg-slate-900/80 text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2 mb-4 text-sky-400 font-bold uppercase text-sm border-b border-slate-800 pb-3">
          <Compass className="w-5 h-5" /> Interactive Antarctic Traverse Route Planner
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-lg bg-rose-950/50 border border-rose-500/40 text-rose-200">
            {error}
          </div>
        )}

        {successMsg && (
          <div className="p-3 mb-4 rounded-lg bg-emerald-950/50 border border-emerald-500/40 text-emerald-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            {successMsg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          {/* Origin */}
          <div>
            <label className="block text-slate-400 mb-1 text-[11px] font-bold">ORIGIN FACILITY / BASE:</label>
            <select
              value={originId}
              onChange={(e) => { setOriginId(e.target.value); setPlanningResult(null); }}
              className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>{loc.name} ({loc.type})</option>
              ))}
            </select>
          </div>

          {/* Destination */}
          <div>
            <label className="block text-slate-400 mb-1 text-[11px] font-bold">DESTINATION LOCATION:</label>
            <select
              value={destId}
              onChange={(e) => { setDestId(e.target.value); setPlanningResult(null); }}
              className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>{loc.name} ({loc.type})</option>
              ))}
            </select>
          </div>

          {/* Assigned Asset */}
          <div className="sm:col-span-2">
            <label className="block text-slate-400 mb-1 text-[11px] font-bold">ASSIGNED FLEET ASSET:</label>
            <select
              value={vehicleId}
              onChange={(e) => { setVehicleId(e.target.value); setPlanningResult(null); }}
              className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.type}) • Fuel: {a.fuel_pct}%
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Custom Waypoints Editor */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-300 font-bold">INTERMEDIATE GPS WAYPOINTS ({waypoints.length})</span>
            <span className="text-[10px] text-slate-500">Add waypoints to bypass crevasse fields</span>
          </div>

          {waypoints.length > 0 && (
            <div className="space-y-1.5 mb-3">
              {waypoints.map((wp, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 rounded bg-slate-950 border border-slate-800 text-[11px]">
                  <span>WP #{idx + 1}: Lat {wp[0].toFixed(4)}°, Lon {wp[1].toFixed(4)}°</span>
                  <button onClick={() => handleRemoveWaypoint(idx)} className="text-rose-400 hover:text-rose-300">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <input
              type="number"
              step="0.0001"
              placeholder="Lat (e.g. -70.80)"
              value={newLat}
              onChange={(e) => setNewLat(e.target.value)}
              className="w-1/2 p-2 rounded bg-slate-950 border border-slate-700 text-slate-200"
            />
            <input
              type="number"
              step="0.0001"
              placeholder="Lon (e.g. 11.74)"
              value={newLon}
              onChange={(e) => setNewLon(e.target.value)}
              className="w-1/2 p-2 rounded bg-slate-950 border border-slate-700 text-slate-200"
            />
            <button
              onClick={handleAddWaypoint}
              className="px-3 py-2 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add
            </button>
          </div>
        </div>

        {/* Feasibility Result Card */}
        {planningResult && (
          <div className="p-4 rounded-xl bg-slate-900 border border-sky-500/40 mb-4 space-y-3 animate-fade-in">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <span className="font-bold text-slate-200 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-sky-400" /> Route Autonomy Feasibility Report
              </span>
              <StatusBadge
                status={planningResult.validation_status === 'APPROVED' ? 'nominal' : 'warning'}
                label={planningResult.validation_status}
                size="xs"
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500">Traverse Distance:</span>
                <div className="font-bold text-slate-100 text-sm mt-0.5">{planningResult.total_distance_km} km</div>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500">Estimated ETA:</span>
                <div className="font-bold text-sky-400 text-sm mt-0.5">{planningResult.estimated_travel_time_hours} hrs</div>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500">Fuel Required:</span>
                <div className="font-bold text-amber-300 text-sm mt-0.5">{planningResult.fuel_required_liters} L</div>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500">Fuel Post-Traverse:</span>
                <div className={`font-bold text-sm mt-0.5 ${planningResult.fuel_remaining_pct >= 15 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {planningResult.fuel_remaining_pct}%
                </div>
              </div>
            </div>

            {planningResult.hazard_warnings?.length > 0 && (
              <div className="p-2.5 rounded bg-rose-950/40 border border-rose-500/30 text-rose-300 text-[11px]">
                <div className="font-bold flex items-center gap-1 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> Hazard Proximity Warnings Detected:
                </div>
                {planningResult.hazard_warnings.map((h, i) => (
                  <div key={i} className="text-[10px] text-slate-300">
                    • {h.name} ({h.type}) within {h.distance_to_corridor_km} km of traverse path.
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold transition-colors"
          >
            Cancel
          </button>
          {!planningResult ? (
            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <Compass className="w-4 h-4" /> {loading ? 'Evaluating...' : 'Evaluate Route Feasibility'}
            </button>
          ) : (
            <button
              onClick={handleSaveRoute}
              disabled={saving}
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" /> {saving ? 'Saving...' : 'Approve & Save Route'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoutePlannerModal;
