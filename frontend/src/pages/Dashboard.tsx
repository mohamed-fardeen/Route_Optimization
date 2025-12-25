import React, {useState} from 'react'
import api from '../services/api'
import Map from '../components/Map'

type Stop = { lat: number; lng: number; address?: string }

// Simple haversine distance calculator
const haversine = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
  const R = 6371 // Earth radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng/2) * Math.sin(dLng/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

// Helper: fetch road distance matrix from OSRM (meters)
const getOSRMMatrix = async (stops: Stop[]) => {
  if(stops.length < 2) return { distances: [], durations: [] }
  const coords = stops.map(s => `${s.lng},${s.lat}`).join(';')
  const url = `https://router.project-osrm.org/table/v1/driving/${coords}?annotations=distance,duration`
  const res = await fetch(url)
  const data = await res.json()
  if(!data || data.code !== 'Ok') throw new Error('OSRM matrix error')
  return { distances: data.distances, durations: data.durations }
}

// Async greedy nearest neighbor using road distances (fallbacks to haversine)
const optimizeRouteUsingRoads = async (stops: Stop[]): Promise<{stops: any[], distance: number, path: [number, number][] | null}> => {
  if(stops.length < 2) return {stops: [], distance: 0, path: null}
  try {
    const { distances } = await getOSRMMatrix(stops)
    const n = stops.length
    const unvisited = Array.from({length: n}, (_, i) => i)
    const routeIdx: number[] = []
    let current = unvisited.shift()!
    routeIdx.push(current)
    
    while(unvisited.length > 0) {
      let nearest = unvisited[0]
      let minDist = (distances[current]?.[nearest]) ?? haversine(stops[current].lat, stops[current].lng, stops[nearest].lat, stops[nearest].lng) * 1000
      for(let i = 1; i < unvisited.length; i++) {
        const idx = unvisited[i]
        const d = (distances[current]?.[idx]) ?? haversine(stops[current].lat, stops[current].lng, stops[idx].lat, stops[idx].lng) * 1000
        if(d < minDist) { minDist = d; nearest = idx }
      }
      unvisited.splice(unvisited.indexOf(nearest), 1)
      routeIdx.push(nearest)
      current = nearest
    }

    try {
      const orderedCoords = routeIdx.map(i => `${stops[i].lng},${stops[i].lat}`).join(';')
      const routeUrl = `https://router.project-osrm.org/route/v1/driving/${orderedCoords}?overview=full&geometries=geojson`
      const rRes = await fetch(routeUrl)
      const rData = await rRes.json()
      if(rData?.code === 'Ok' && rData.routes?.length > 0) {
        const routeGeo = rData.routes[0].geometry.coordinates
        const legs = rData.routes[0].legs || []
        const path: [number, number][] = routeGeo.map((c:any) => [c[1], c[0]])

        const routeStops: any[] = []
        let cumul = 0
        for(let i = 0; i < routeIdx.length; i++){
          const idx = routeIdx[i]
          const distMeters = i === 0 ? 0 : legs[i-1]?.distance ?? (distances?.[routeIdx[i-1]]?.[idx]) ?? 0
          const distKm = distMeters / 1000
          cumul += distKm
          routeStops.push({ ...stops[idx], sequence: i, distance_from_previous_km: distKm, cumulative_distance_km: cumul })
        }
        return { stops: routeStops, distance: Math.round((cumul + Number.EPSILON) * 100) / 100, path }
      }
    } catch(routeErr) {
      console.warn('OSRM route fetch failed, falling back to matrix distances', routeErr)
    }

    const route: any[] = []
    let cumul = 0
    for(let i = 0; i < routeIdx.length; i++){
      const idx = routeIdx[i]
      const prevIdx = i === 0 ? null : routeIdx[i-1]
      const distMeters = prevIdx == null ? 0 : (distances?.[prevIdx]?.[idx]) ?? haversine(stops[prevIdx].lat, stops[prevIdx].lng, stops[idx].lat, stops[idx].lng) * 1000
      const distKm = distMeters / 1000
      cumul += distKm
      route.push({ ...stops[idx], sequence: i, distance_from_previous_km: distKm, cumulative_distance_km: cumul })
    }
    return { stops: route, distance: Math.round((cumul + Number.EPSILON) * 100) / 100, path: null }
  } catch(e) {
    console.warn('OSRM failed, falling back to haversine optimizer', e)
    if(stops.length < 2) return {stops: [], distance:0, path: null}
    const unvisited = stops.map((s, i) => ({...s, idx: i}))
    const route: any[] = []
    let current = unvisited.shift()!
    route.push({...current, sequence: 0, distance_from_previous_km: 0, cumulative_distance_km: 0})
    let totalDistance = 0
    while(unvisited.length > 0) {
      let nearest = unvisited[0]
      let minDist = haversine(current.lat, current.lng, nearest.lat, nearest.lng)
      for(let i = 1; i < unvisited.length; i++) {
        const d = haversine(current.lat, current.lng, unvisited[i].lat, unvisited[i].lng)
        if(d < minDist) { minDist = d; nearest = unvisited[i] }
      }
      totalDistance += minDist
      unvisited.splice(unvisited.indexOf(nearest), 1)
      route.push({ ...nearest, sequence: route.length, distance_from_previous_km: minDist, cumulative_distance_km: totalDistance })
      current = nearest
    }
    return {stops: route, distance: totalDistance, path: null}
  }
}

const geocodeAddress = async (address: string): Promise<Stop | null> => {
  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1`)
    const results = await response.json()
    if(results.length > 0) {
      return {
        lat: parseFloat(results[0].lat),
        lng: parseFloat(results[0].lon),
        address: results[0].display_name
      }
    }
    return null
  } catch(e) {
    console.error('Geocoding error:', e)
    return null
  }
}

export default function Dashboard(){
  const [startLocation, setStartLocation] = useState<Stop | null>(null)
  const [stops, setStops] = useState<Stop[]>([])
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [route, setRoute] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [searchInput, setSearchInput] = useState('')
  const [startSearchInput, setStartSearchInput] = useState('')
  const [searchingStart, setSearchingStart] = useState(false)

  const handleGeocode = async (address: string, setter: (result: Stop) => void, searchSetter: (isSearching: boolean) => void) => {
    if (!address.trim()) {
      setError('Please enter an address.');
      return;
    }
    searchSetter(true);
    setError(null);
    try {
      const result = await geocodeAddress(address);
      if (result) {
        setter({ ...result, address: result.address || address });
      } else {
        setError('Location not found. Please try a more specific address.');
      }
    } catch (e) {
      setError('Geocoding search failed. Please try again.');
    } finally {
      searchSetter(false);
    }
  };

  const searchStartLocation = () => handleGeocode(startSearchInput, (res) => {
    setStartLocation(res);
    setStartSearchInput('');
  }, setSearchingStart);

  const searchLocation = () => handleGeocode(searchInput, (res) => {
    setStops([...stops, res]);
    setSearchInput('');
  }, setSearching);

  const optimize = async () => {
    if (!startLocation) return setError('Please set a starting location.');
    if (stops.length === 0) return setError('Please add at least one stop.');
    
    setLoading(true);
    setError(null);
    try {
      const allStops = [startLocation, ...stops];
      const { stops: optimizedStops, distance, path } = await optimizeRouteUsingRoads(allStops);
      setRoute({
        stops: optimizedStops,
        path: path,
        total_distance_km: distance,
        total_cost_inr: distance * 12, // Assuming a fixed rate
        total_time_min: distance / 30 * 60 // Assuming average speed of 30 km/h
      });
    } catch (e: any) {
      setError('Failed to optimize route.');
      console.error('❌ Optimize error:', e);
    } finally {
      setLoading(false);
    }
  };

  const onTextFile = async (file: File | null) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const { data } = await api.post('/upload/csv', form, { headers: { 'Content-Type': 'multipart/form-data' } });
      
      if (data?.addresses) {
        const parsed = data.addresses.map((a: any) => ({
          lat: a.latitude || a.lat,
          lng: a.longitude || a.lng,
          address: a.name || a.street,
        })).filter((a: any) => a.lat && a.lng);
        
        if (parsed.length < 1) return setError('File must contain at least one valid address.');
        
        setStops(parsed);
        setRoute(null);
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'File upload failed.');
      console.error('❌ Upload error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <section className="left">
        <div className="card">
          <h3>📍 Starting Location</h3>
          <div className="input-group">
            <input
              type="text"
              className="input"
              placeholder="e.g. Delhi Headquarters..."
              value={startSearchInput}
              onChange={(e) => setStartSearchInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchStartLocation()}
            />
            <button className="btn primary" onClick={searchStartLocation} disabled={searchingStart || !startSearchInput.trim()}>
              {searchingStart ? '🔄' : 'Set'}
            </button>
          </div>
          {startLocation && (
            <div className="p-2 rounded-md bg-green-500/10 text-sm">
              <p className="font-semibold text-green-400">✅ {startLocation.address}</p>
              <button
                onClick={() => setStartLocation(null)}
                className="btn btn-sm btn-danger mt-2"
              >
                Change
              </button>
            </div>
          )}
        </div>

        <div className="card">
          <h3>🔍 Add Stops</h3>
          <div className="input-group">
            <input
              type="text"
              className="input"
              placeholder="Enter address to add..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchLocation()}
            />
            <button className="btn primary" onClick={searchLocation} disabled={searching || !searchInput.trim()}>
              {searching ? '🔄' : 'Add'}
            </button>
          </div>
          <label className="btn primary block text-center cursor-pointer mb-3">
            📤 Upload from File
            <input type="file" accept=".txt,.csv" onChange={(e) => onTextFile(e.target.files?.[0] || null)} className="hidden" />
          </label>
          
          {error && <div className="error">❌ {error}</div>}

          <div>
            <p><strong>Stops Added: {stops.length}</strong></p>
            {stops.length > 0 && (
              <ul className="stops-list">
                {stops.map((s, i) => (
                  <li key={i}>
                    <span className="stop-address">{s.address}</span>
                    <button
                      onClick={() => setStops(stops.filter((_, idx) => idx !== i))}
                      className="btn btn-sm btn-danger"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        
        <div className="card">
            <button className="btn primary w-full text-lg" onClick={optimize} disabled={loading || !startLocation || stops.length === 0}>
                {loading ? '⏳ Optimizing...' : '🚀 Optimize Route'}
            </button>
        </div>

        {route && (
            <div className="card info">
                <h3>📊 Route Info</h3>
                <p>📏 Distance: <strong>{(route.total_distance_km || 0).toFixed(2)} km</strong></p>
                <p>💰 Cost: <strong>₹{(route.total_cost_inr || 0).toFixed(0)}</strong></p>
                <p>⏱️ Time: <strong>{(route.total_time_min || 0).toFixed(0)} min</strong></p>
                <p>🛑 Stops: <strong>{route.stops?.length || 0}</strong></p>
            </div>
        )}
      </section>
      
      <section className="right">
        <Map route={route} stops={stops} startLocation={startLocation} setStops={setStops} setStartLocation={setStartLocation} />
      </section>
    </div>
  )
}
