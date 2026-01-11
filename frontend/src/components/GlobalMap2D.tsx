import React, { useEffect, useState, useMemo, memo } from 'react';
import { motion } from 'motion/react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Line,
  Marker,
  ZoomableGroup,
} from 'react-simple-maps';
import { RouteLegend } from './RouteLegend';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { calculateRoutes, Route } from '../utils/routeCalculator';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
const MAP_SCALE = 147;
const MAP_WIDTH = 923.628; // Exact width for scale 147 (2 * PI * 147)

// --- 1. Optimized Line Component (Memoized) ---
const WrapAwareLine = memo(({
  from,
  to,
  route,
  isSelected,
  pulseOpacity,
  onClick
}: {
  from: [number, number];
  to: [number, number];
  route: Route;
  isSelected: boolean;
  pulseOpacity: number;
  onClick: () => void;
}) => {
  const [fromLon, fromLat] = from;
  const [toLon, toLat] = to;
  const deltaLon = toLon - fromLon;

  const opacity = isSelected ? pulseOpacity : 0.3;
  const strokeWidth = isSelected ? route.strokeWidth : route.strokeWidth * 0.6;
  
  const commonProps = {
    stroke: route.color,
    strokeWidth,
    strokeLinecap: "round" as const,
    opacity,
    style: {
      filter: isSelected ? `drop-shadow(0 0 8px ${route.color})` : 'none',
      cursor: 'pointer',
      transition: 'opacity 0.2s ease-in-out' // Smooth hover transition
    },
    onClick,
  };

  // CROSSING THE DATELINE (Pacific Ocean)
  if (Math.abs(deltaLon) > 180) {
    const isGoingEast = deltaLon < 0;
    const totalDist = 360 - Math.abs(deltaLon);
    const distToEdge = isGoingEast ? (180 - fromLon) : (fromLon + 180);
    const ratio = distToEdge / totalDist;
    const midLat = fromLat + (toLat - fromLat) * ratio;

    // We purposely overshoot 180 slightly (180.1) to prevent 1px gaps at seams
    const edgeLon1 = isGoingEast ? 180.1 : -180.1;
    const edgeLon2 = isGoingEast ? -180.1 : 180.1;

    return (
      <g>
        <Line from={from} to={[edgeLon1, midLat]} {...commonProps} />
        <Line from={[edgeLon2, midLat]} to={to} {...commonProps} />
      </g>
    );
  }

  // STANDARD LINE
  return <Line from={from} to={to} {...commonProps} />;
});

// --- 2. Optimized World Instance (Memoized) ---
// This component renders ONE copy of the world. It is memoized so it 
// DOES NOT re-render when the parent's zoom/center changes, only when props change.
const WorldInstance = memo(({ 
  offset, 
  geoData, 
  routes, 
  selectedRouteId, 
  pulseOpacity,
  origin, 
  destination,
  onRouteClick 
}: any) => {
  return (
    <g transform={`translate(${offset}, 0)`}>
      {/* Landmass */}
      {geoData && (
        <Geographies geography={geoData}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#1e3a5f"
                stroke="#0a0e1a"
                strokeWidth={0.5}
                style={{
                  default: { outline: 'none' },
                  hover: { outline: 'none', fill: '#2a4a6f' },
                  pressed: { outline: 'none' },
                }}
              />
            ))
          }
        </Geographies>
      )}

      {/* Routes */}
      {routes.map((route: Route) => (
        <g key={route.id}>
          {route.waypoints.map((waypoint, index) => {
            if (index === route.waypoints.length - 1) return null;
            return (
              <WrapAwareLine
                key={`${route.id}-${index}`}
                from={waypoint}
                to={route.waypoints[index + 1]}
                route={route}
                isSelected={route.id === selectedRouteId}
                pulseOpacity={pulseOpacity}
                onClick={() => onRouteClick(route)}
              />
            );
          })}
        </g>
      ))}

      {/* Markers (Only render on the main instance to avoid clutter, or all if needed) */}
      {/* We render on all instances so they appear when you pan infinitely */}
      {origin && (
        <Marker coordinates={origin.coordinates}>
          <g>
            <motion.circle r="12" fill="none" stroke="#4a90e2" strokeWidth="2" opacity={0.5} animate={{ r: [8, 16, 8], opacity: [0.5, 0.1, 0.5] }} transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }} />
            <circle r="6" fill="#4a90e2" />
            <text textAnchor="middle" y={-15} style={{ fontFamily: 'system-ui', fontSize: '10px', fill: '#8ab4e5', fontWeight: 500 }}>{origin.name}</text>
          </g>
        </Marker>
      )}
      {destination && (
        <Marker coordinates={destination.coordinates}>
           <g>
            <motion.circle r="12" fill="none" stroke="#c94444" strokeWidth="2" opacity={0.5} animate={{ r: [8, 16, 8], opacity: [0.5, 0.1, 0.5] }} transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }} />
            <circle r="6" fill="#c94444" />
            <text textAnchor="middle" y={-15} style={{ fontFamily: 'system-ui', fontSize: '10px', fill: '#e85555', fontWeight: 500 }}>{destination.name}</text>
          </g>
        </Marker>
      )}
    </g>
  );
});


interface Port {
  name: string;
  coordinates: [number, number];
}

interface GlobalMap2DProps {
  origin?: Port;
  destination?: Port;
  onRouteSelect?: (route: Route) => void;
  onRoutesCalculated?: (routes: Route[]) => void;
  selectedRouteFromParent?: Route | null;
}

export function GlobalMap2D({
  origin,
  destination,
  onRouteSelect,
  onRoutesCalculated,
  selectedRouteFromParent,
}: GlobalMap2DProps) {
  const [geoData, setGeoData] = useState<any>(null);
  const [pulseOpacity, setPulseOpacity] = useState(0.6);
  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState<[number, number]>([0, 20]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);

  // 1. Fetch Geometry Once
  useEffect(() => {
    fetch(GEO_URL)
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch(err => console.error("Failed to load map data", err));
  }, []);

  // 2. Optimized Animation Loop
  // Using requestAnimationFrame directly with state setter
  useEffect(() => {
    let animationFrameId: number;
    let start = performance.now();

    const animate = (time: number) => {
      // Sine wave pulse for smoother opacity change (0.4 to 1.0)
      const elapsed = time - start;
      const newOpacity = 0.7 + 0.3 * Math.sin(elapsed / 500); // Faster, smoother pulse
      setPulseOpacity(newOpacity);
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // 3. Route Calculation & Logic
  useEffect(() => {
    if (origin && destination) {
      try {
        const calculatedRoutes = calculateRoutes(origin.coordinates, destination.coordinates);
        setRoutes(calculatedRoutes);

        const bestRoute = calculatedRoutes.find((r) => r.riskLevel === 'low') || calculatedRoutes[0];
        setSelectedRouteId(bestRoute.id);

        if (onRoutesCalculated) onRoutesCalculated(calculatedRoutes);
        if (onRouteSelect) onRouteSelect(bestRoute);

        // Smart Centering (Pacific vs Atlantic)
        const isPacificRoute = Math.abs(origin.coordinates[0] - destination.coordinates[0]) > 180;
        if (isPacificRoute) {
          setCenter([180, 20]);
        } else {
          const midLng = (origin.coordinates[0] + destination.coordinates[0]) / 2;
          const midLat = (origin.coordinates[1] + destination.coordinates[1]) / 2;
          setCenter([midLng, midLat]);
        }
        setZoom(1.2);
      } catch (e) {
        console.error("Error calculating routes", e);
      }
    } else {
      setRoutes([]);
      setSelectedRouteId(null);
    }
  }, [origin, destination]);

  useEffect(() => {
    if (selectedRouteFromParent) {
      setSelectedRouteId(selectedRouteFromParent.id);
    }
  }, [selectedRouteFromParent]);

  const handleRouteClick = (route: Route) => {
    setSelectedRouteId(route.id);
    if (onRouteSelect) onRouteSelect(route);
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev * 1.5, 8));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev / 1.5, 1));
  const handleReset = () => { setZoom(1); setCenter([0, 20]); };

  return (
    <div className="relative w-full h-full bg-[#0a0e1a] overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="grid-2d" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#4a90e2" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-2d)" />
        </svg>
      </div>

      {/* Controls */}
      <div className="absolute top-6 right-6 flex flex-col gap-2 z-10">
        <button onClick={handleZoomIn} className="p-2 bg-[#0f1621]/95 border border-[#1a2332] rounded-sm text-white/60 hover:text-white/90 hover:border-[#4a90e2]/50 backdrop-blur-sm transition-all"><ZoomIn className="w-4 h-4" /></button>
        <button onClick={handleZoomOut} className="p-2 bg-[#0f1621]/95 border border-[#1a2332] rounded-sm text-white/60 hover:text-white/90 hover:border-[#4a90e2]/50 backdrop-blur-sm transition-all"><ZoomOut className="w-4 h-4" /></button>
        <button onClick={handleReset} className="p-2 bg-[#0f1621]/95 border border-[#1a2332] rounded-sm text-white/60 hover:text-white/90 hover:border-[#4a90e2]/50 backdrop-blur-sm transition-all"><Maximize2 className="w-4 h-4" /></button>
      </div>

      {/* Main Map Area */}
      {geoData ? (
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{ scale: MAP_SCALE }}
          style={{ width: '100%', height: '100%' }}
        >
          <ZoomableGroup
            zoom={zoom}
            center={center}
            onMoveEnd={(position) => {
              setCenter(position.coordinates);
              setZoom(position.zoom);
            }}
            translateExtent={[
              [-Infinity, -Infinity],
              [Infinity, Infinity]
            ]}
          >
            {/* 1. Left Clone */}
            <WorldInstance 
              offset={-MAP_WIDTH}
              geoData={geoData}
              routes={routes}
              selectedRouteId={selectedRouteId}
              pulseOpacity={pulseOpacity}
              origin={origin}
              destination={destination}
              onRouteClick={handleRouteClick}
            />
            
            {/* 2. Main World */}
            <WorldInstance 
              offset={0}
              geoData={geoData}
              routes={routes}
              selectedRouteId={selectedRouteId}
              pulseOpacity={pulseOpacity}
              origin={origin}
              destination={destination}
              onRouteClick={handleRouteClick}
            />
            
            {/* 3. Right Clone */}
            <WorldInstance 
              offset={MAP_WIDTH}
              geoData={geoData}
              routes={routes}
              selectedRouteId={selectedRouteId}
              pulseOpacity={pulseOpacity}
              origin={origin}
              destination={destination}
              onRouteClick={handleRouteClick}
            />

          </ZoomableGroup>
        </ComposableMap>
      ) : (
        <div className="flex items-center justify-center w-full h-full text-white/30">
          Loading Map Data...
        </div>
      )}

      {/* HUD Info */}
      <div className="absolute top-6 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-[#0f1621]/95 border border-[#1a2332] rounded-sm backdrop-blur-sm pointer-events-none">
        <span className="text-[10px] text-white/40 font-mono tracking-wider uppercase">
          Zoom: {zoom.toFixed(1)}x
        </span>
      </div>

      <RouteLegend />
    </div>
  );
}