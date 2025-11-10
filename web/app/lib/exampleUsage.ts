/**
 * Example Usage of Environment Utilities
 * 
 * This file demonstrates how to use the environment utilities
 * for placing objects in specific zones.
 */

import * as THREE from 'three';
import {
  ZONES,
  COLORS,
  getZoneCenter,
  getRandomPositionInZone,
} from './environmentUtils';

// ============================================
// Example 1: Get Zone Centers
// ============================================

export function getAllZoneCenters() {
  const centers = {
    entrance: getZoneCenter('ENTRANCE'),
    triage: getZoneCenter('TRIAGE'),
    treatment: getZoneCenter('TREATMENT'),
    boarding: getZoneCenter('BOARDING'),
    exit: getZoneCenter('EXIT'),
  };

  console.log('Zone Centers:', centers);
  // ENTRANCE: (-7, 0, 0)
  // TRIAGE: (-4, 0, 0)
  // TREATMENT: (0, 0, 0)
  // BOARDING: (4, 0, 0)
  // EXIT: (7, 0, 0)

  return centers;
}

// ============================================
// Example 2: Place Object at Zone Center
// ============================================

export function placeObjectAtZoneCenter(
  object: THREE.Object3D,
  zoneName: keyof typeof ZONES
) {
  const center = getZoneCenter(zoneName);
  object.position.copy(center);
  return object;
}

// ============================================
// Example 3: Place Multiple Objects in Zone
// ============================================

export function placeBedsinZone(zoneName: keyof typeof ZONES, count: number) {
  const beds: THREE.Mesh[] = [];

  for (let i = 0; i < count; i++) {
    // Create a simple bed (placeholder)
    const bedGeometry = new THREE.BoxGeometry(1.8, 0.3, 0.9);
    const bedMaterial = new THREE.MeshLambertMaterial({
      color: COLORS.BEDS,
    });
    const bed = new THREE.Mesh(bedGeometry, bedMaterial);

    // Get random position in zone
    const position = getRandomPositionInZone(zoneName, 0.15); // 0.15m height
    bed.position.copy(position);

    beds.push(bed);
  }

  return beds;
}

// ============================================
// Example 4: Create Path Between Zones
// ============================================

export function createPathBetweenZones(
  startZone: keyof typeof ZONES,
  endZone: keyof typeof ZONES
): THREE.Vector3[] {
  const start = getZoneCenter(startZone);
  const end = getZoneCenter(endZone);

  // Create waypoints for smooth path
  const waypoints: THREE.Vector3[] = [];
  const steps = 10;

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const point = new THREE.Vector3().lerpVectors(start, end, t);
    waypoints.push(point);
  }

  return waypoints;
}

// ============================================
// Example 5: Check if Position is in Zone
// ============================================

export function isPositionInZone(
  position: THREE.Vector3,
  zoneName: keyof typeof ZONES
): boolean {
  const zone = ZONES[zoneName];
  return position.x >= zone.start && position.x <= zone.end;
}

// ============================================
// Example 6: Get Closest Zone to Position
// ============================================

export function getClosestZone(position: THREE.Vector3): keyof typeof ZONES {
  let closestZone: keyof typeof ZONES = 'ENTRANCE';
  let minDistance = Infinity;

  for (const zoneName of Object.keys(ZONES) as Array<keyof typeof ZONES>) {
    const center = getZoneCenter(zoneName);
    const distance = position.distanceTo(center);

    if (distance < minDistance) {
      minDistance = distance;
      closestZone = zoneName;
    }
  }

  return closestZone;
}

// ============================================
// Example 7: Grid Placement in Zone
// ============================================

export function createGridInZone(
  zoneName: keyof typeof ZONES,
  rows: number,
  cols: number,
  yPosition: number = 0
): THREE.Vector3[] {
  const zone = ZONES[zoneName];
  const positions: THREE.Vector3[] = [];

  const zoneWidth = zone.end - zone.start;
  const zoneDepth = 10; // Approximate depth (can be imported from constants)

  const spacingX = zoneWidth / (cols + 1);
  const spacingZ = zoneDepth / (rows + 1);

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = zone.start + spacingX * (col + 1);
      const z = -zoneDepth / 2 + spacingZ * (row + 1);
      positions.push(new THREE.Vector3(x, yPosition, z));
    }
  }

  return positions;
}

// ============================================
// Example 8: Animate Object Through Zones
// ============================================

export class ZonePathAnimator {
  private object: THREE.Object3D;
  private currentZoneIndex: number = 0;
  private zonePath: Array<keyof typeof ZONES>;
  private speed: number;

  constructor(
    object: THREE.Object3D,
    zonePath: Array<keyof typeof ZONES>,
    speed: number = 1
  ) {
    this.object = object;
    this.zonePath = zonePath;
    this.speed = speed;

    // Start at first zone
    const startPos = getZoneCenter(zonePath[0]);
    object.position.copy(startPos);
  }

  update(deltaTime: number): boolean {
    if (this.currentZoneIndex >= this.zonePath.length - 1) {
      return false; // Animation complete
    }

    const currentZone = this.zonePath[this.currentZoneIndex];
    const nextZone = this.zonePath[this.currentZoneIndex + 1];

    const currentPos = getZoneCenter(currentZone);
    const targetPos = getZoneCenter(nextZone);

    // Move towards target
    const direction = new THREE.Vector3()
      .subVectors(targetPos, this.object.position)
      .normalize();

    const moveDistance = this.speed * deltaTime;
    this.object.position.add(direction.multiplyScalar(moveDistance));

    // Check if reached target
    const distanceToTarget = this.object.position.distanceTo(targetPos);
    if (distanceToTarget < 0.1) {
      this.currentZoneIndex++;
    }

    return true; // Animation continues
  }

  getCurrentZone(): keyof typeof ZONES {
    return this.zonePath[this.currentZoneIndex];
  }

  reset() {
    this.currentZoneIndex = 0;
    const startPos = getZoneCenter(this.zonePath[0]);
    this.object.position.copy(startPos);
  }
}

// ============================================
// Usage Examples in Comments
// ============================================

/*

// Example: Place 5 beds in Treatment zone
const treatmentBeds = placeBedsinZone('TREATMENT', 5);
treatmentBeds.forEach(bed => scene.add(bed));

// Example: Create patient path from entrance to exit
const patientPath = createPathBetweenZones('ENTRANCE', 'EXIT');

// Example: Grid placement (3x2 beds in Treatment)
const bedPositions = createGridInZone('TREATMENT', 2, 3, 0.15);

// Example: Animate patient through zones
const patient = new THREE.Mesh(geometry, material);
const animator = new ZonePathAnimator(
  patient,
  ['ENTRANCE', 'TRIAGE', 'TREATMENT', 'BOARDING', 'EXIT'],
  2 // speed
);

// In animation loop:
function animate(time) {
  const deltaTime = clock.getDelta();
  const isAnimating = animator.update(deltaTime);
  
  if (!isAnimating) {
    animator.reset(); // Loop animation
  }
}

*/
