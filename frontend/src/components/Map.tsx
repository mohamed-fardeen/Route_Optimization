import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-arrowheads'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function MapClickHandler({ setStops, stops, setStartLocation }: any) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng
      // If user holds Shift while clicking, set the starting location
      const isShift = (e as any).originalEvent?.shiftKey
      if (isShift && setStartLocation) {
        setStartLocation({ lat, lng, address: `${lat.toFixed(5)}, ${lng.toFixed(5)}` })
        return
      }
      // Otherwise add a stop using coordinates as the address label
      setStops([...stops, { lat, lng, address: `${lat.toFixed(5)}, ${lng.toFixed(5)}` }])
    }
  })
  return null
}

function FitBounds({ positions }: { positions: [number, number][] }){
  const map = useMap()
  useEffect(()=>{
    if(!positions || positions.length === 0) {
      map.setView([20.5937, 78.9629], 5)
      return
    }
    const bounds = L.latLngBounds(positions as any)
    map.fitBounds(bounds, { padding: [50, 50] })
  }, [map, positions])
  return null
}

function RouteWithArrows({ positions }: any) {
  const polylineRef = useRef<any>(null)
  
  useEffect(() => {
    if (!polylineRef.current || positions.length < 2) return
    try {
      (polylineRef.current as any).arrowheads({
        size: '25%',
        frequency: '60px',
        npl: 500
      })
    } catch(e) {
      console.log('Arrow setup:', e)
    }
  }, [positions])

  return (
    <Polyline
      ref={polylineRef}
      positions={positions as any}
      color="#06b6d4"
      weight={4}
      opacity={0.9}
      lineCap="round"
      lineJoin="round"
    />
  )
}

function ZoomToLocation({ startLocation }: { startLocation: { lat: number, lng: number } | null }) {
  const map = useMap()

  useEffect(() => {
    if (startLocation) {
      map.setView([startLocation.lat, startLocation.lng], 13)
    }
  }, [startLocation, map])

  return null
}

export default function Map({ route, stops, startLocation, setStops, setStartLocation }: any){
  const routePositions: [number, number][] = (route?.path && route.path.length > 0)
    ? route.path
    : (route?.stops || []).map((s:any)=>[s.latitude || s.lat || 0, s.longitude || s.lng || 0]).filter((p:any) => p[0] !== 0 && p[1] !== 0)
  const stopPositions: [number, number][] = (stops || []).map((s:any)=>[s.lat, s.lng])
  const hasRoute = (route && ((route.path && route.path.length > 0) || (route.stops && route.stops.length > 0)))

  return (
    <div className="map-wrap" style={{height:'100%', position:'relative'}}>
      <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{height:'100%', width:'100%'}}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />
        
        {startLocation && (
          <Marker position={[startLocation.lat, startLocation.lng]} icon={L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
          })}>
            <Popup>
              <div style={{minWidth:150, fontSize:'12px'}}>
                <strong>🟢 Start: {startLocation.address}</strong>
              </div>
            </Popup>
          </Marker>
        )}
        
        {hasRoute ? (
          <>
            {route.stops.slice(1).map((s:any, i:number)=> (
              <Marker key={i} position={[s.latitude || s.lat, s.longitude || s.lng]}>
                <Popup>
                  <div style={{minWidth:180, fontSize:'12px'}}>
                    <strong>Stop {(s.sequence || i) + 1}</strong>
                    <div>{s.address_name || s.street || s.address || `${(s.latitude||s.lat).toFixed ? (s.latitude||s.lat).toFixed(5) : s.latitude||s.lat}, ${(s.longitude||s.lng).toFixed ? (s.longitude||s.lng).toFixed(5) : s.longitude||s.lng}`}</div>
                    <div>Distance: {(s.distance_from_previous_km || 0).toFixed(2)} km</div>
                  </div>
                </Popup>
              </Marker>
            ))}
            <RouteWithArrows positions={routePositions} />
            <FitBounds positions={routePositions} />
          </>
        ) : (
          <>
            {stops && stops.map((s:any, i:number)=> (
              <Marker key={i} position={[s.lat, s.lng]}>
                <Popup>
                  <div style={{minWidth:140, fontSize:'12px'}}>
                    <strong>{i + 1}. {s.address || `${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}`}</strong>
                    <div style={{marginTop:6, fontSize:11, color:'#9aa4b2'}}>Coords: {s.lat.toFixed(5)}, {s.lng.toFixed(5)}</div>
                    <button 
                      onClick={() => setStops(stops.filter((_:any, idx:number) => idx !== i))}
                      style={{marginTop:'8px', padding:'4px 8px', background:'#ff6b6b', color:'white', border:'none', borderRadius:'4px', cursor:'pointer', fontSize:'11px'}}
                    >
                      Remove
                    </button>
                  </div>
                </Popup>
              </Marker>
            ))}
            <MapClickHandler setStops={setStops} stops={stops} setStartLocation={setStartLocation} />
            <FitBounds positions={stopPositions} />
          </>
        )}
        <ZoomToLocation startLocation={startLocation} />
      </MapContainer>
      <div style={{position:'absolute', top:'10px', left:'10px', background:'rgba(15,23,36,0.9)', color:'#e6eef6', padding:'8px 12px', borderRadius:'6px', fontSize:'12px', zIndex:1000, maxWidth:'280px'}}>
        <p style={{margin:'0 0 4px 0', fontWeight:600}}>🚀 Route Optimizer</p>
        <p style={{margin:'0 0 4px 0', fontSize:'11px', color:'#9aa4b2'}}>🟢 Green = Start | 📍 Red = Stops | 🔵 Blue = Route</p>
        <p style={{margin:'0 0 4px 0', fontSize:'11px', color:'#9aa4b2'}}>➜ Arrows show direction</p>
        <p style={{margin:'0 0 4px 0', fontSize:'11px', color:'#9aa4b2'}}>Shift+Click on map to set start; Click to add stops</p>
      </div>
    </div>
  )
}
