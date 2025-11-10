/**
 * OrbitControls Usage Examples
 * 
 * This file contains practical examples and patterns for using OrbitControls
 * in the Emergency Department 3D Flow Visualization project.
 */

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import * as THREE from 'three';

// ============================================================================
// EXAMPLE 1: Basic Setup (As Used in ThreeScene.tsx)
// ============================================================================

export function example1_BasicSetup(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  // Initialize OrbitControls
  const controls = new OrbitControls(camera, renderer.domElement);
  
  // Set target to scene center
  controls.target.set(0, 0, 0);
  
  // Enable smooth damping
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  
  // Set zoom limits
  controls.minDistance = 5;
  controls.maxDistance = 50;
  
  // Set rotation limits
  controls.minPolarAngle = 0;
  controls.maxPolarAngle = Math.PI / 2 + 0.3;
  
  // Enable all controls
  controls.enablePan = true;
  controls.enableZoom = true;
  controls.enableRotate = true;
  
  // Standard speeds
  controls.panSpeed = 1.0;
  controls.zoomSpeed = 1.0;
  controls.rotateSpeed = 1.0;
  
  // World-space panning
  controls.screenSpacePanning = false;
  
  // No auto-rotation
  controls.autoRotate = false;
  
  // Apply settings
  controls.update();
  
  return controls;
}

// ============================================================================
// EXAMPLE 2: Auto-Rotating Showcase
// ============================================================================

export function example2_AutoRotate(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.target.set(0, 0, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  
  // Enable auto-rotation
  controls.autoRotate = true;
  controls.autoRotateSpeed = 2.0; // 2 degrees per second
  
  // User can still interact
  controls.enablePan = true;
  controls.enableZoom = true;
  controls.enableRotate = true;
  
  controls.update();
  return controls;
}

// Animation loop for auto-rotate
export function example2_AnimationLoop(controls: OrbitControls) {
  function animate() {
    requestAnimationFrame(animate);
    
    // Update controls to apply auto-rotation
    controls.update();
    
    // ... render scene
  }
  animate();
}

// ============================================================================
// EXAMPLE 3: Limited View (Restricted Controls)
// ============================================================================

export function example3_LimitedView(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.target.set(0, 0, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  
  // Tight zoom limits
  controls.minDistance = 10;
  controls.maxDistance = 20;
  
  // Restrict vertical rotation
  controls.minPolarAngle = Math.PI / 4;  // 45° minimum
  controls.maxPolarAngle = Math.PI / 3;  // 60° maximum
  
  // Restrict horizontal rotation
  controls.minAzimuthAngle = -Math.PI / 4;  // -45°
  controls.maxAzimuthAngle = Math.PI / 4;   // +45°
  
  controls.update();
  return controls;
}

// ============================================================================
// EXAMPLE 4: Precise Examination Mode (Slow Speed)
// ============================================================================

export function example4_PreciseMode(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.target.set(0, 0, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08; // More damping for smoother feel
  
  // Slow speeds for precision
  controls.panSpeed = 0.3;
  controls.zoomSpeed = 0.5;
  controls.rotateSpeed = 0.3;
  
  // Close zoom for details
  controls.minDistance = 2;
  controls.maxDistance = 15;
  
  controls.update();
  return controls;
}

// ============================================================================
// EXAMPLE 5: Fast Navigation Mode
// ============================================================================

export function example5_FastMode(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.target.set(0, 0, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.03; // Less damping for responsive feel
  
  // Fast speeds for quick navigation
  controls.panSpeed = 2.0;
  controls.zoomSpeed = 2.0;
  controls.rotateSpeed = 1.5;
  
  // Wide zoom range
  controls.minDistance = 5;
  controls.maxDistance = 100;
  
  controls.update();
  return controls;
}

// ============================================================================
// EXAMPLE 6: Camera Preset System
// ============================================================================

export interface CameraPreset {
  position: THREE.Vector3;
  target: THREE.Vector3;
  name: string;
}

export const cameraPresets: CameraPreset[] = [
  {
    name: 'Top-Down',
    position: new THREE.Vector3(0, 25, 0),
    target: new THREE.Vector3(0, 0, 0),
  },
  {
    name: 'Isometric',
    position: new THREE.Vector3(15, 10, 15),
    target: new THREE.Vector3(0, 0, 0),
  },
  {
    name: 'Side View',
    position: new THREE.Vector3(25, 5, 0),
    target: new THREE.Vector3(0, 0, 0),
  },
  {
    name: 'Entrance View',
    position: new THREE.Vector3(-12, 8, 8),
    target: new THREE.Vector3(-7, 0, 0),
  },
  {
    name: 'Treatment View',
    position: new THREE.Vector3(0, 6, 12),
    target: new THREE.Vector3(0, 0, 0),
  },
];

export function applyCameraPreset(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls,
  preset: CameraPreset,
  duration: number = 1000 // Animation duration in ms
) {
  // Simple version (instant)
  camera.position.copy(preset.position);
  controls.target.copy(preset.target);
  controls.update();
  
  // For animated transition, use GSAP or custom interpolation
  // (See Example 7 for animation)
}

// ============================================================================
// EXAMPLE 7: Animated Camera Transitions
// ============================================================================

export function animateCameraToPreset(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls,
  preset: CameraPreset,
  duration: number = 1000
): Promise<void> {
  return new Promise((resolve) => {
    const startPosition = camera.position.clone();
    const startTarget = controls.target.clone();
    const startTime = Date.now();
    
    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease-in-out interpolation
      const t = progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;
      
      // Interpolate position
      camera.position.lerpVectors(startPosition, preset.position, t);
      
      // Interpolate target
      controls.target.lerpVectors(startTarget, preset.target, t);
      
      controls.update();
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        resolve();
      }
    }
    
    animate();
  });
}

// Usage
export async function example7_Usage(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls
) {
  // Animate to top-down view
  await animateCameraToPreset(camera, controls, cameraPresets[0], 1500);
  
  // Wait 2 seconds
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Animate to isometric view
  await animateCameraToPreset(camera, controls, cameraPresets[1], 1500);
}

// ============================================================================
// EXAMPLE 8: Event-Driven Interactions
// ============================================================================

export function example8_EventHandlers(controls: OrbitControls) {
  // Track when user starts interacting
  controls.addEventListener('start', () => {
    console.log('User started interacting with camera');
    // Pause auto-rotation if enabled
    controls.autoRotate = false;
  });
  
  // Track camera changes
  let changeCount = 0;
  controls.addEventListener('change', () => {
    changeCount++;
    console.log(`Camera changed: ${changeCount} times`);
    
    // Get current state
    const distance = controls.getDistance();
    const polarAngle = controls.getPolarAngle();
    const azimuthAngle = controls.getAzimuthalAngle();
    
    console.log('Camera state:', {
      distance: distance.toFixed(2),
      polarAngle: (polarAngle * 180 / Math.PI).toFixed(1) + '°',
      azimuthAngle: (azimuthAngle * 180 / Math.PI).toFixed(1) + '°',
    });
  });
  
  // Track when user stops interacting
  controls.addEventListener('end', () => {
    console.log('User stopped interacting with camera');
    // Resume auto-rotation if desired
    // controls.autoRotate = true;
  });
}

// ============================================================================
// EXAMPLE 9: Save/Restore Camera State
// ============================================================================

export interface CameraState {
  position: { x: number; y: number; z: number };
  target: { x: number; y: number; z: number };
  zoom: number;
}

export function saveCameraState(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls
): CameraState {
  return {
    position: {
      x: camera.position.x,
      y: camera.position.y,
      z: camera.position.z,
    },
    target: {
      x: controls.target.x,
      y: controls.target.y,
      z: controls.target.z,
    },
    zoom: camera.zoom,
  };
}

export function restoreCameraState(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls,
  state: CameraState
) {
  camera.position.set(state.position.x, state.position.y, state.position.z);
  controls.target.set(state.target.x, state.target.y, state.target.z);
  camera.zoom = state.zoom;
  camera.updateProjectionMatrix();
  controls.update();
}

export function example9_SaveRestore(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls
) {
  // Save current state
  const savedState = saveCameraState(camera, controls);
  console.log('Camera state saved:', savedState);
  
  // Later, restore the state
  restoreCameraState(camera, controls, savedState);
  console.log('Camera state restored');
  
  // Save to localStorage
  localStorage.setItem('cameraState', JSON.stringify(savedState));
  
  // Load from localStorage
  const loadedState = localStorage.getItem('cameraState');
  if (loadedState) {
    restoreCameraState(camera, controls, JSON.parse(loadedState));
  }
}

// ============================================================================
// EXAMPLE 10: Dynamic Control Limits Based on Scene State
// ============================================================================

export function example10_DynamicLimits(
  controls: OrbitControls,
  focusZone: 'entrance' | 'triage' | 'treatment' | 'boarding' | 'exit'
) {
  // Adjust controls based on which zone is being examined
  switch (focusZone) {
    case 'entrance':
      controls.target.set(-7, 0, 0);
      controls.minDistance = 3;
      controls.maxDistance = 15;
      break;
    
    case 'triage':
      controls.target.set(-4, 0, 0);
      controls.minDistance = 2;
      controls.maxDistance = 12;
      break;
    
    case 'treatment':
      controls.target.set(0, 0, 0);
      controls.minDistance = 3;
      controls.maxDistance = 20;
      break;
    
    case 'boarding':
      controls.target.set(4, 0, 0);
      controls.minDistance = 3;
      controls.maxDistance = 15;
      break;
    
    case 'exit':
      controls.target.set(7, 0, 0);
      controls.minDistance = 3;
      controls.maxDistance = 15;
      break;
  }
  
  controls.update();
}

// ============================================================================
// EXAMPLE 11: Touch-Optimized Controls (Mobile)
// ============================================================================

export function example11_TouchOptimized(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.target.set(0, 0, 0);
  
  // Disable damping for more responsive touch
  controls.enableDamping = false;
  
  // Faster speeds for touch
  controls.rotateSpeed = 1.5;
  controls.panSpeed = 1.5;
  controls.zoomSpeed = 1.5;
  
  // Wider zoom range for pinch gesture
  controls.minDistance = 3;
  controls.maxDistance = 60;
  
  // Configure touch gestures
  controls.touches = {
    ONE: THREE.TOUCH.ROTATE,      // One finger: rotate
    TWO: THREE.TOUCH.DOLLY_PAN,   // Two fingers: zoom and pan
  };
  
  controls.update();
  return controls;
}

// ============================================================================
// EXAMPLE 12: Performance Monitoring
// ============================================================================

export class ControlsPerformanceMonitor {
  private controls: OrbitControls;
  private changeCount = 0;
  private lastTime = Date.now();
  private updateTimes: number[] = [];
  
  constructor(controls: OrbitControls) {
    this.controls = controls;
    this.setupMonitoring();
  }
  
  private setupMonitoring() {
    this.controls.addEventListener('change', () => {
      this.changeCount++;
      
      const currentTime = Date.now();
      const deltaTime = currentTime - this.lastTime;
      this.lastTime = currentTime;
      
      this.updateTimes.push(deltaTime);
      
      // Keep only last 100 updates
      if (this.updateTimes.length > 100) {
        this.updateTimes.shift();
      }
    });
  }
  
  public getStats() {
    const avgUpdateTime = this.updateTimes.length > 0
      ? this.updateTimes.reduce((a, b) => a + b, 0) / this.updateTimes.length
      : 0;
    
    return {
      totalChanges: this.changeCount,
      averageUpdateInterval: avgUpdateTime.toFixed(2) + 'ms',
      updatesPerSecond: (1000 / avgUpdateTime).toFixed(1),
    };
  }
  
  public reset() {
    this.changeCount = 0;
    this.updateTimes = [];
    this.lastTime = Date.now();
  }
}

// Usage
export function example12_Usage(controls: OrbitControls) {
  const monitor = new ControlsPerformanceMonitor(controls);
  
  // After some time
  setTimeout(() => {
    const stats = monitor.getStats();
    console.log('Controls Performance:', stats);
  }, 10000);
}

// ============================================================================
// EXAMPLE 13: Keyboard Shortcuts for Camera Control
// ============================================================================

export function example13_KeyboardShortcuts(
  camera: THREE.PerspectiveCamera,
  controls: OrbitControls
) {
  window.addEventListener('keydown', (event) => {
    const moveSpeed = 2;
    const rotateSpeed = 0.1;
    
    switch (event.key) {
      // Arrow keys: rotate
      case 'ArrowLeft':
        controls.target.x -= moveSpeed;
        camera.position.x -= moveSpeed;
        break;
      case 'ArrowRight':
        controls.target.x += moveSpeed;
        camera.position.x += moveSpeed;
        break;
      case 'ArrowUp':
        controls.target.z -= moveSpeed;
        camera.position.z -= moveSpeed;
        break;
      case 'ArrowDown':
        controls.target.z += moveSpeed;
        camera.position.z += moveSpeed;
        break;
      
      // +/- : zoom
      case '+':
      case '=':
        camera.position.multiplyScalar(0.9);
        break;
      case '-':
      case '_':
        camera.position.multiplyScalar(1.1);
        break;
      
      // Number keys: presets
      case '1':
        applyCameraPreset(camera, controls, cameraPresets[0]);
        break;
      case '2':
        applyCameraPreset(camera, controls, cameraPresets[1]);
        break;
      case '3':
        applyCameraPreset(camera, controls, cameraPresets[2]);
        break;
      
      // R: reset
      case 'r':
      case 'R':
        controls.reset();
        break;
    }
    
    controls.update();
  });
}

// ============================================================================
// EXAMPLE 14: Follow Target Mode
// ============================================================================

export function example14_FollowTarget(
  controls: OrbitControls,
  targetObject: THREE.Object3D,
  offset: THREE.Vector3 = new THREE.Vector3(0, 5, 10)
) {
  // Update controls target to follow an object
  function updateFollowTarget() {
    controls.target.copy(targetObject.position);
    controls.update();
    
    requestAnimationFrame(updateFollowTarget);
  }
  
  updateFollowTarget();
}

// ============================================================================
// EXAMPLE 15: Screen-Space Panning Comparison
// ============================================================================

export function example15_PanningModes(
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer
) {
  // World-space panning (default for architectural views)
  const worldSpaceControls = new OrbitControls(camera, renderer.domElement);
  worldSpaceControls.screenSpacePanning = false;
  // Panning moves in the XZ plane (ground plane)
  
  // Screen-space panning (better for some 3D applications)
  const screenSpaceControls = new OrbitControls(camera, renderer.domElement);
  screenSpaceControls.screenSpacePanning = true;
  // Panning moves relative to screen orientation
  
  // For our ED visualization, world-space is better
  return worldSpaceControls;
}

// ============================================================================
// Type Exports
// ============================================================================

export type { OrbitControls };
