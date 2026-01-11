// routes.ts
import { 
  PATH_CAPE_OF_GOOD_HOPE, 
  PATH_SUEZ_CANAL, 
  PATH_PANAMA, 
  PATH_ARCTIC_NSR 
} from './routeData';

export interface Route {
  id: string;
  name: string;
  riskLevel: "high" | "medium" | "low";
  color: string;
  strokeWidth: number;
  waypoints: [number, number][];
  waypointNames: string[];
  distance: number;
  estimatedTime: number;
  description: string;
}

export interface GlobalPort {
  name: string;
  country: string;
  coordinates: [number, number]; 
  region: string;
}

// --- 1. THE FULL OLD PORT LIST (Restored) ---
const MAJOR_PORTS: GlobalPort[] = [
  // Europe
  { name: "Rotterdam", country: "Netherlands", coordinates: [4.47, 51.92], region: "Europe" },
  { name: "Hamburg", country: "Germany", coordinates: [9.99, 53.55], region: "Europe" },
  { name: "Antwerp", country: "Belgium", coordinates: [4.4, 51.22], region: "Europe" },
  { name: "Le Havre", country: "France", coordinates: [0.11, 49.49], region: "Europe" },
  { name: "Barcelona", country: "Spain", coordinates: [2.17, 41.38], region: "Europe" },
  { name: "Piraeus", country: "Greece", coordinates: [23.65, 37.94], region: "Europe" },
  { name: "Istanbul", country: "Turkey", coordinates: [28.97, 41.01], region: "Europe" },
  { name: "Gdansk", country: "Poland", coordinates: [18.65, 54.35], region: "Europe" },

  // Middle East
  { name: "Dubai", country: "UAE", coordinates: [55.27, 25.2], region: "Middle East" },
  { name: "Jeddah", country: "Saudi Arabia", coordinates: [39.19, 21.54], region: "Middle East" },
  { name: "Port Said", country: "Egypt", coordinates: [32.28, 31.26], region: "Middle East" },
  { name: "Haifa", country: "Israel", coordinates: [34.99, 32.82], region: "Middle East" },

  // Asia
  { name: "Singapore", country: "Singapore", coordinates: [103.85, 1.29], region: "Asia" },
  { name: "Hong Kong", country: "China", coordinates: [114.17, 22.32], region: "Asia" }, 
  { name: "Shanghai", country: "China", coordinates: [121.47, 31.23], region: "Asia" },
  { name: "Busan", country: "South Korea", coordinates: [129.04, 35.18], region: "Asia" },
  { name: "Tokyo", country: "Japan", coordinates: [139.77, 35.68], region: "Asia" },
  { name: "Mumbai", country: "India", coordinates: [72.88, 19.08], region: "Asia" },
  { name: "Colombo", country: "Sri Lanka", coordinates: [79.85, 6.93], region: "Asia" },
  { name: "Jakarta", country: "Indonesia", coordinates: [106.85, -6.21], region: "Asia" },

  // Africa
  { name: "Cape Town", country: "South Africa", coordinates: [18.42, -33.92], region: "Africa" },
  { name: "Durban", country: "South Africa", coordinates: [31.03, -29.86], region: "Africa" },
  { name: "Lagos", country: "Nigeria", coordinates: [3.39, 6.45], region: "Africa" },
  { name: "Djibouti", country: "Djibouti", coordinates: [43.15, 11.59], region: "Africa" },
  { name: "Mombasa", country: "Kenya", coordinates: [39.66, -4.05], region: "Africa" },

  // Americas
  { name: "New York", country: "USA", coordinates: [-74.01, 40.71], region: "Americas" },
  { name: "Los Angeles", country: "USA", coordinates: [-118.24, 34.05], region: "Americas" },
  { name: "Miami", country: "USA", coordinates: [-80.19, 25.76], region: "Americas" },
  { name: "Houston", country: "USA", coordinates: [-95.36, 29.76], region: "Americas" },
  { name: "Santos", country: "Brazil", coordinates: [-46.33, -23.96], region: "Americas" },
  { name: "Buenos Aires", country: "Argentina", coordinates: [-58.38, -34.6], region: "Americas" },
  { name: "Panama City", country: "Panama", coordinates: [-79.53, 8.98], region: "Americas" },
  { name: "Vancouver", country: "Canada", coordinates: [-123.12, 49.28], region: "Americas" },

  // Oceania
  { name: "Sydney", country: "Australia", coordinates: [151.21, -33.87], region: "Oceania" },
  { name: "Melbourne", country: "Australia", coordinates: [144.96, -37.81], region: "Oceania" },
  { name: "Auckland", country: "New Zealand", coordinates: [174.76, -36.85], region: "Oceania" },

  // Strategic passages
  { name: "Suez Canal", country: "Egypt", coordinates: [32.35, 30.44], region: "Middle East" },
  { name: "Strait of Malacca", country: "Malaysia", coordinates: [100.35, 2.5], region: "Asia" },
  { name: "Strait of Gibraltar", country: "Spain", coordinates: [-5.36, 36.14], region: "Europe" },
];


// --- 2. MAIN CALCULATION LOGIC ---

export function calculateRoutes(origin: [number, number], destination: [number, number]): Route[] {
  const originPort = findNearestPort(origin);
  const destPort = findNearestPort(destination, new Set([originPort.name]));

  // CHECK: Is this the specific Shanghai <-> Hamburg route?
  // We check both directions.
  const isShanghaiHamburg = 
    (originPort.name === "Shanghai" && destPort.name === "Hamburg") ||
    (originPort.name === "Hamburg" && destPort.name === "Shanghai");

  if (isShanghaiHamburg) {
    // Return the HIGH PRECISION manual paths
    return getDetailedShanghaiHamburgRoutes();
  }

  // OTHERWISE: Return the GENERIC dynamic paths (Old Logic)
  return calculateDynamicRoutes(originPort, destPort);
}


// --- 3. SPECIFIC ROUTE BUILDER (Uses routeData.ts) ---

function getDetailedShanghaiHamburgRoutes(): Route[] {
  const distCape = calculateTotalDistance(PATH_CAPE_OF_GOOD_HOPE);
  const distSuez = calculateTotalDistance(PATH_SUEZ_CANAL);
  const distPanama = calculateTotalDistance(PATH_PANAMA);
  const distArctic = calculateTotalDistance(PATH_ARCTIC_NSR);

  return [
    {
      id: "fixed-cape",
      name: "Cape of Good Hope (Standard)",
      riskLevel: "low",
      color: "#2ecc71",
      strokeWidth: 3,
      waypoints: PATH_CAPE_OF_GOOD_HOPE,
      waypointNames: ["Shanghai", "Singapore", "Cape Town", "Rotterdam", "Hamburg"],
      distance: distCape,
      estimatedTime: Math.round(distCape / 35),
      description: "Primary safe route via Africa. Avoids Red Sea conflict.",
    },
    {
      id: "fixed-suez",
      name: "Suez Canal (Red Sea)",
      riskLevel: "high",
      color: "#e74c3c",
      strokeWidth: 3,
      waypoints: PATH_SUEZ_CANAL,
      waypointNames: ["Shanghai", "Singapore", "Suez Canal", "Hamburg"],
      distance: distSuez,
      estimatedTime: Math.round(distSuez / 32),
      description: "Shortest but High Risk due to regional conflict.",
    },
    {
      id: "fixed-panama",
      name: "Panama Canal (Westbound)",
      riskLevel: "medium",
      color: "#f1c40f",
      strokeWidth: 2.5,
      waypoints: PATH_PANAMA,
      waypointNames: ["Shanghai", "Panama Canal", "Hamburg"],
      distance: distPanama,
      estimatedTime: Math.round(distPanama / 38),
      description: "All-water alternative avoiding Middle East.",
    },
    {
      id: "fixed-arctic",
      name: "Northern Sea Route (Arctic)",
      riskLevel: "high",
      color: "#3498db",
      strokeWidth: 2,
      waypoints: PATH_ARCTIC_NSR,
      waypointNames: ["Shanghai", "Bering Strait", "Arctic", "Hamburg"],
      distance: distArctic,
      estimatedTime: Math.round(distArctic / 25),
      description: "Seasonal shortcut. Impassable in Winter.",
    }
  ];
}


// --- 4. GENERIC DYNAMIC LOGIC (Restored from Original) ---

function calculateDynamicRoutes(originPort: GlobalPort, destPort: GlobalPort): Route[] {
  const routes: Route[] = [];

  // Route 1: Safe (3 intermediates)
  const safeIntermediates = findIntermediatePorts(
    originPort.coordinates, destPort.coordinates, 3, ["Africa", "Middle East", "Asia"]
  );
  const safeWaypoints = [originPort.coordinates, ...safeIntermediates.map(p => p.coordinates), destPort.coordinates];
  const safeDist = calculateTotalDistance(safeWaypoints);

  routes.push({
    id: "dyn-safe-1",
    name: "Standard Corridor",
    riskLevel: "low",
    color: "#5a9a7a",
    strokeWidth: 2,
    waypoints: safeWaypoints as [number, number][],
    waypointNames: [originPort.name, ...safeIntermediates.map(p => p.name), destPort.name],
    distance: safeDist,
    estimatedTime: Math.round(safeDist / 35),
    description: "Calculated secure route via major hubs",
  });

  // Route 2: Alternative (Via different regions)
  const altIntermediates = findIntermediatePorts(
    originPort.coordinates, destPort.coordinates, 2, ["Europe", "Asia"], safeIntermediates
  );
  const altWaypoints = [originPort.coordinates, ...altIntermediates.map(p => p.coordinates), destPort.coordinates];
  const altDist = calculateTotalDistance(altWaypoints);

  routes.push({
    id: "dyn-safe-2",
    name: "Alternative Corridor",
    riskLevel: "low",
    color: "#6ba889",
    strokeWidth: 2,
    waypoints: altWaypoints as [number, number][],
    waypointNames: [originPort.name, ...altIntermediates.map(p => p.name), destPort.name],
    distance: altDist,
    estimatedTime: Math.round(altDist / 35),
    description: "Secondary secure routing option",
  });

  // Route 3: Express (Fewer stops)
  const expressIntermediates = findIntermediatePorts(
    originPort.coordinates, destPort.coordinates, 1, undefined, [...safeIntermediates, ...altIntermediates]
  );
  const expressWaypoints = [originPort.coordinates, ...expressIntermediates.map(p => p.coordinates), destPort.coordinates];
  const expressDist = calculateTotalDistance(expressWaypoints);

  routes.push({
    id: "dyn-express",
    name: "Express Route",
    riskLevel: "medium",
    color: "#e8a547",
    strokeWidth: 2.5,
    waypoints: expressWaypoints as [number, number][],
    waypointNames: [originPort.name, ...expressIntermediates.map(p => p.name), destPort.name],
    distance: expressDist,
    estimatedTime: Math.round(expressDist / 38),
    description: "Direct routing with moderate risk profile",
  });

  return routes;
}


// --- 5. HELPERS (Restored) ---

function findNearestPort(coord: [number, number], excludeNames: Set<string> = new Set()): GlobalPort {
  let nearest = MAJOR_PORTS[0];
  let minDistance = Infinity;
  for (const port of MAJOR_PORTS) {
    if (excludeNames.has(port.name)) continue;
    const dist = calculateDistance(coord[1], coord[0], port.coordinates[1], port.coordinates[0]);
    if (dist < minDistance) {
      minDistance = dist;
      nearest = port;
    }
  }
  return nearest;
}

function findIntermediatePorts(
  origin: [number, number], 
  destination: [number, number], 
  count: number, 
  regions?: string[], 
  avoid?: GlobalPort[]
): GlobalPort[] {
  const result: GlobalPort[] = [];
  const used = new Set((avoid || []).map(p => p.name));

  for (let i = 1; i <= count; i++) {
    const ratio = i / (count + 1);
    const lat = origin[1] + (destination[1] - origin[1]) * ratio;
    const lng = origin[0] + (destination[0] - origin[0]) * ratio;

    let candidates = MAJOR_PORTS.filter(p => !used.has(p.name));
    if (regions) {
      const regFilter = candidates.filter(p => regions.includes(p.region));
      if (regFilter.length) candidates = regFilter;
    }

    let best = candidates[0];
    let minD = Infinity;
    for (const p of candidates) {
      const d = calculateDistance(lat, lng, p.coordinates[1], p.coordinates[0]);
      if (d < minD) {
        minD = d;
        best = p;
      }
    }
    result.push(best);
    used.add(best.name);
  }
  return result;
}

function calculateTotalDistance(waypoints: [number, number][]): number {
  let total = 0;
  for (let i = 0; i < waypoints.length - 1; i++) {
    const [lng1, lat1] = waypoints[i];
    const [lng2, lat2] = waypoints[i + 1];
    total += calculateDistance(lat1, lng1, lat2, lng2);
  }
  return Math.round(total);
}

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function toRad(d: number): number {
  return d * Math.PI / 180;
}