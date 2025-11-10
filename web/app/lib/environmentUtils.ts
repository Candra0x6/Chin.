/**
 * Environment Utilities for Emergency Department 3D Visualization
 * 
 * This module contains factory functions for creating:
 * - Floor planes with different colors
 * - Walls using BoxGeometry
 * - Zone definitions and layouts
 */

import * as THREE from 'three';

// Zone dimensions and positions based on specifications
export const ZONES = {
  ENTRANCE: { start: -8, end: -6, name: 'ENTRANCE' },
  TRIAGE: { start: -6, end: -2, name: 'TRIAGE' },
  TREATMENT: { start: -2, end: 2, name: 'TREATMENT' },
  BOARDING: { start: 2, end: 6, name: 'BOARDING' },
  EXIT: { start: 6, end: 8, name: 'EXIT' },
} as const;

// Color palette from specifications
export const COLORS = {
  FLOOR: 0x303030,        // Dark gray (48, 48, 48)
  WALLS: 0xB0B0B0,        // Light gray (176, 176, 176)
  BEDS: 0x88C999,         // Green (136, 201, 153)
  PATIENTS: 0xFFFFFF,     // White (255, 255, 255)
  STAFF: 0x3399FF,        // Blue (51, 153, 255)
  TRIAGE_ZONE: 0x882222,  // Red (136, 34, 34)
  LABELS: 0xFFFFFF,       // White (255, 255, 255)
} as const;

// Constants for environment
const FLOOR_WIDTH = 20;
const FLOOR_DEPTH = 12;
const WALL_HEIGHT = 2; // 2 meters high
const WALL_THICKNESS = 0.2;

/**
 * Creates the main floor plane
 * @returns THREE.Mesh - The floor plane mesh
 */
export function createMainFloor(): THREE.Mesh {
  // Create plane geometry for the floor
  const floorGeometry = new THREE.PlaneGeometry(FLOOR_WIDTH, FLOOR_DEPTH);
  
  // Use MeshLambertMaterial for simple, performant rendering
  const floorMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.FLOOR,
    side: THREE.DoubleSide,
  });

  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  
  // Rotate to be horizontal (planes are vertical by default)
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = 0;
  
  // Enable shadow receiving (optional for Phase 6)
  floor.receiveShadow = true;

  return floor;
}

/**
 * Creates a wall segment
 * @param width - Width of the wall
 * @param position - Position {x, y, z} for the wall
 * @param rotation - Optional rotation around Y axis
 * @returns THREE.Mesh - The wall mesh
 */
export function createWall(
  width: number,
  position: { x: number; y: number; z: number },
  rotation: number = 0
): THREE.Mesh {
  // Create box geometry for wall (width x height x thickness)
  const wallGeometry = new THREE.BoxGeometry(width, WALL_HEIGHT, WALL_THICKNESS);
  
  const wallMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.WALLS,
  });

  const wall = new THREE.Mesh(wallGeometry, wallMaterial);
  wall.position.set(position.x, position.y, position.z);
  wall.rotation.y = rotation;
  
  // Enable shadow casting (optional for Phase 6)
  wall.castShadow = true;
  wall.receiveShadow = true;

  return wall;
}

/**
 * Creates all walls for the emergency department
 * @returns THREE.Group - Group containing all wall meshes
 */
export function createWalls(): THREE.Group {
  const wallsGroup = new THREE.Group();
  wallsGroup.name = 'Walls';

  // Wall height is centered at y = WALL_HEIGHT / 2 to sit on floor
  const wallY = WALL_HEIGHT / 2;

  // Back wall (along Z axis, negative side)
  const backWall = createWall(
    FLOOR_WIDTH,
    { x: 0, y: wallY, z: -FLOOR_DEPTH / 2 }
  );
  backWall.name = 'BackWall';
  wallsGroup.add(backWall);

  // Left wall (along X axis, negative side)
  const leftWall = createWall(
    FLOOR_DEPTH,
    { x: -FLOOR_WIDTH / 2, y: wallY, z: 0 },
    Math.PI / 2 // Rotate 90 degrees
  );
  leftWall.name = 'LeftWall';
  wallsGroup.add(leftWall);

  // Right wall (along X axis, positive side)
  const rightWall = createWall(
    FLOOR_DEPTH,
    { x: FLOOR_WIDTH / 2, y: wallY, z: 0 },
    Math.PI / 2 // Rotate 90 degrees
  );
  rightWall.name = 'RightWall';
  wallsGroup.add(rightWall);

  // Front wall (along Z axis, positive side)
  // This could be partial or have openings for entrance/exit
  const frontWall = createWall(
    FLOOR_WIDTH,
    { x: 0, y: wallY, z: FLOOR_DEPTH / 2 }
  );
  frontWall.name = 'FrontWall';
  wallsGroup.add(frontWall);

  return wallsGroup;
}

/**
 * Creates the Triage zone with red floor
 * @returns THREE.Mesh - The triage zone floor mesh
 */
export function createTriageZone(): THREE.Mesh {
  // Calculate triage zone dimensions
  const triageWidth = ZONES.TRIAGE.end - ZONES.TRIAGE.start;
  const triageDepth = FLOOR_DEPTH;

  // Create plane for triage zone
  const triageGeometry = new THREE.PlaneGeometry(triageWidth, triageDepth);
  
  const triageMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.TRIAGE_ZONE,
    side: THREE.DoubleSide,
  });

  const triageZone = new THREE.Mesh(triageGeometry, triageMaterial);
  
  // Rotate to be horizontal
  triageZone.rotation.x = -Math.PI / 2;
  
  // Position at triage zone center, slightly above main floor to avoid z-fighting
  const triageCenterX = (ZONES.TRIAGE.start + ZONES.TRIAGE.end) / 2;
  triageZone.position.set(triageCenterX, 0.01, 0);
  
  triageZone.receiveShadow = true;
  triageZone.name = 'TriageZone';

  return triageZone;
}

/**
 * Creates visual zone markers (optional floor planes for each zone)
 * @returns THREE.Group - Group containing zone marker meshes
 */
export function createZoneMarkers(): THREE.Group {
  const markersGroup = new THREE.Group();
  markersGroup.name = 'ZoneMarkers';

  // Create subtle zone boundaries using line geometry
  Object.values(ZONES).forEach((zone) => {
    if (zone.name === 'ENTRANCE') return; // Skip entrance for now

    // Create a line at zone boundary
    const points = [
      new THREE.Vector3(zone.start, 0.02, -FLOOR_DEPTH / 2),
      new THREE.Vector3(zone.start, 0.02, FLOOR_DEPTH / 2),
    ];

    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x505050,
      linewidth: 1,
    });

    const line = new THREE.Line(lineGeometry, lineMaterial);
    line.name = `${zone.name}Boundary`;
    markersGroup.add(line);
  });

  return markersGroup;
}

/**
 * Creates the complete environment (floor, walls, zones)
 * @returns THREE.Group - Group containing all environment elements
 */
export function createEnvironment(): THREE.Group {
  const environmentGroup = new THREE.Group();
  environmentGroup.name = 'Environment';

  // Add main floor
  const floor = createMainFloor();
  floor.name = 'MainFloor';
  environmentGroup.add(floor);

  // Add walls
  const walls = createWalls();
  environmentGroup.add(walls);

  // Add triage zone (red floor area)
  const triageZone = createTriageZone();
  environmentGroup.add(triageZone);

  // Add zone markers
  const zoneMarkers = createZoneMarkers();
  environmentGroup.add(zoneMarkers);

  return environmentGroup;
}

/**
 * Helper function to get zone center position
 * @param zoneName - Name of the zone
 * @returns THREE.Vector3 - Center position of the zone
 */
export function getZoneCenter(zoneName: keyof typeof ZONES): THREE.Vector3 {
  const zone = ZONES[zoneName];
  const centerX = (zone.start + zone.end) / 2;
  return new THREE.Vector3(centerX, 0, 0);
}

/**
 * Helper function to get random position within a zone
 * @param zoneName - Name of the zone
 * @param yPosition - Y position (height)
 * @returns THREE.Vector3 - Random position within the zone
 */
export function getRandomPositionInZone(
  zoneName: keyof typeof ZONES,
  yPosition: number = 0
): THREE.Vector3 {
  const zone = ZONES[zoneName];
  const randomX = zone.start + Math.random() * (zone.end - zone.start);
  const randomZ = -FLOOR_DEPTH / 4 + Math.random() * (FLOOR_DEPTH / 2);
  
  return new THREE.Vector3(randomX, yPosition, randomZ);
}
