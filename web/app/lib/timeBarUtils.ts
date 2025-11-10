/**
 * Time Bar utilities for patient flow visualization
 * Creates and manages a visual time progress indicator
 */

import * as THREE from 'three';
import { Font } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';
import { loadFont } from './labelUtils';

/**
 * Time bar configuration
 */
export interface TimeBarConfig {
  width: number;          // Total width of the time bar
  height: number;         // Height of the time bar
  depth: number;          // Depth (thickness) of the time bar
  position: {
    x: number;
    y: number;
    z: number;
  };
  colors: {
    background: number;   // Background bar color
    progress: number;     // Progress bar color
    label: number;        // Label text color
  };
  cycleDuration: number;  // Total animation cycle duration (seconds)
}

/**
 * Default time bar configuration
 */
export const DEFAULT_TIME_BAR_CONFIG: TimeBarConfig = {
  width: 16,              // 16 units wide (matches scene width)
  height: 0.4,            // 0.4 units tall
  depth: 0.1,             // 0.1 units thick
  position: {
    x: 0,                 // Centered on X-axis
    y: 0.05,              // Just above floor
    z: 7,                 // At the back of the scene
  },
  colors: {
    background: 0x404040, // Dark gray background
    progress: 0x3399FF,   // Blue progress (matches staff color)
    label: 0xFFFFFF,      // White label text
  },
  cycleDuration: 20,      // 20 seconds total cycle (approximate)
};

/**
 * Time bar state
 */
export interface TimeBarState {
  backgroundBar: THREE.Mesh;
  progressBar: THREE.Mesh;
  label: THREE.Mesh | null;
  container: THREE.Group;
  currentProgress: number;  // 0.0 to 1.0
  elapsedTime: number;      // Total elapsed time in seconds
  config: TimeBarConfig;
}

/**
 * Create the time bar background
 */
function createBackgroundBar(config: TimeBarConfig): THREE.Mesh {
  const geometry = new THREE.BoxGeometry(
    config.width,
    config.height,
    config.depth
  );
  
  const material = new THREE.MeshLambertMaterial({
    color: config.colors.background,
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = false;
  mesh.receiveShadow = true;
  mesh.name = 'TimeBarBackground';
  
  return mesh;
}

/**
 * Create the time bar progress indicator
 */
function createProgressBar(config: TimeBarConfig): THREE.Mesh {
  // Start with minimal width (will be scaled)
  const geometry = new THREE.BoxGeometry(
    config.width,
    config.height * 0.8, // Slightly smaller than background
    config.depth * 1.5   // Slightly thicker to appear in front
  );
  
  const material = new THREE.MeshLambertMaterial({
    color: config.colors.progress,
    emissive: config.colors.progress,
    emissiveIntensity: 0.2, // Slight glow effect
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = false;
  mesh.receiveShadow = false;
  mesh.name = 'TimeBarProgress';
  
  // Start at 0% progress
  mesh.scale.x = 0;
  
  return mesh;
}

/**
 * Create the "TIME" label for the time bar
 */
async function createTimeLabel(config: TimeBarConfig): Promise<THREE.Mesh> {
  const font = await loadFont();
  
  const geometry = new TextGeometry('TIME', {
    font: font,
    size: 0.3,
    depth: 0.05,
  });
  
  // Center the text
  geometry.computeBoundingBox();
  const textWidth = geometry.boundingBox!.max.x - geometry.boundingBox!.min.x;
  geometry.translate(-textWidth / 2, 0, 0);
  
  const material = new THREE.MeshLambertMaterial({
    color: config.colors.label,
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = false;
  mesh.receiveShadow = false;
  mesh.name = 'TimeBarLabel';
  
  // Position label above the bar
  mesh.position.set(0, config.height + 0.3, 0);
  
  return mesh;
}

/**
 * Create elapsed time display (e.g., "0:15")
 */
async function createTimeDisplay(
  time: number,
  config: TimeBarConfig,
  font: Font
): Promise<THREE.Mesh> {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  
  const geometry = new TextGeometry(timeString, {
    font: font,
    size: 0.25,
    depth: 0.04,
  });
  
  // Center the text
  geometry.computeBoundingBox();
  const textWidth = geometry.boundingBox!.max.x - geometry.boundingBox!.min.x;
  geometry.translate(-textWidth / 2, 0, 0);
  
  const material = new THREE.MeshLambertMaterial({
    color: config.colors.label,
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = false;
  mesh.receiveShadow = false;
  mesh.name = 'TimeDisplay';
  
  // Position below the bar
  mesh.position.set(0, -config.height - 0.4, 0);
  
  return mesh;
}

/**
 * Create the complete time bar system
 */
export async function createTimeBar(
  config: TimeBarConfig = DEFAULT_TIME_BAR_CONFIG
): Promise<TimeBarState> {
  const container = new THREE.Group();
  container.name = 'TimeBarContainer';
  
  // Create background bar
  const backgroundBar = createBackgroundBar(config);
  container.add(backgroundBar);
  
  // Create progress bar
  const progressBar = createProgressBar(config);
  container.add(progressBar);
  
  // Create label
  let label: THREE.Mesh | null = null;
  try {
    label = await createTimeLabel(config);
    container.add(label);
  } catch (error) {
    console.error('Failed to create time bar label:', error);
  }
  
  // Position the container
  container.position.set(
    config.position.x,
    config.position.y,
    config.position.z
  );
  
  return {
    backgroundBar,
    progressBar,
    label,
    container,
    currentProgress: 0,
    elapsedTime: 0,
    config,
  };
}

/**
 * Update time bar progress
 * @param timeBar Time bar state
 * @param progress Progress value (0.0 to 1.0)
 */
export function updateTimeBarProgress(
  timeBar: TimeBarState,
  progress: number
): void {
  // Clamp progress between 0 and 1
  const clampedProgress = Math.max(0, Math.min(1, progress));
  
  // Update progress bar scale
  timeBar.progressBar.scale.x = clampedProgress;
  
  // Offset position to keep left-aligned
  // When scale is 0.5, we need to move it left by 0.25 of the total width
  const offset = (1 - clampedProgress) / 2;
  timeBar.progressBar.position.x = -offset * timeBar.config.width;
  
  timeBar.currentProgress = clampedProgress;
}

/**
 * Update time bar based on elapsed time
 * @param timeBar Time bar state
 * @param deltaTime Time since last frame (seconds)
 */
export function updateTimeBar(
  timeBar: TimeBarState,
  deltaTime: number
): void {
  timeBar.elapsedTime += deltaTime;
  
  // Calculate progress based on cycle duration
  const cycleDuration = timeBar.config.cycleDuration;
  const progress = (timeBar.elapsedTime % cycleDuration) / cycleDuration;
  
  updateTimeBarProgress(timeBar, progress);
}

/**
 * Sync time bar with patient animations
 * Uses the average total cycle time from all patients
 * @param timeBar Time bar state
 * @param averageCycleTime Average patient cycle time
 */
export function syncTimeBarWithAnimations(
  timeBar: TimeBarState,
  averageCycleTime: number
): void {
  if (averageCycleTime > 0) {
    const progress = (timeBar.elapsedTime % averageCycleTime) / averageCycleTime;
    updateTimeBarProgress(timeBar, progress);
  }
}

/**
 * Reset time bar to start
 */
export function resetTimeBar(timeBar: TimeBarState): void {
  timeBar.elapsedTime = 0;
  updateTimeBarProgress(timeBar, 0);
}

/**
 * Update time display text (optional feature)
 * Call this less frequently (e.g., once per second) to avoid performance impact
 */
export async function updateTimeDisplay(
  timeBar: TimeBarState,
  container: THREE.Group
): Promise<void> {
  // Remove old time display if exists
  const oldDisplay = container.getObjectByName('TimeDisplay');
  if (oldDisplay) {
    container.remove(oldDisplay);
    if (oldDisplay instanceof THREE.Mesh) {
      oldDisplay.geometry.dispose();
      (oldDisplay.material as THREE.Material).dispose();
    }
  }
  
  // Create new time display
  try {
    const font = await loadFont();
    const newDisplay = await createTimeDisplay(
      timeBar.elapsedTime,
      timeBar.config,
      font
    );
    container.add(newDisplay);
  } catch (error) {
    console.error('Failed to update time display:', error);
  }
}

/**
 * Get time bar statistics for debugging
 */
export function getTimeBarStats(timeBar: TimeBarState): {
  progress: number;
  elapsedTime: number;
  formattedTime: string;
  cycleCount: number;
} {
  const minutes = Math.floor(timeBar.elapsedTime / 60);
  const seconds = Math.floor(timeBar.elapsedTime % 60);
  const formattedTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  const cycleCount = Math.floor(timeBar.elapsedTime / timeBar.config.cycleDuration);
  
  return {
    progress: timeBar.currentProgress,
    elapsedTime: timeBar.elapsedTime,
    formattedTime,
    cycleCount,
  };
}

/**
 * Dispose time bar resources
 */
export function disposeTimeBar(timeBar: TimeBarState): void {
  // Dispose geometries and materials
  timeBar.backgroundBar.geometry.dispose();
  (timeBar.backgroundBar.material as THREE.Material).dispose();
  
  timeBar.progressBar.geometry.dispose();
  (timeBar.progressBar.material as THREE.Material).dispose();
  
  if (timeBar.label) {
    timeBar.label.geometry.dispose();
    (timeBar.label.material as THREE.Material).dispose();
  }
  
  // Clear container
  timeBar.container.clear();
}
