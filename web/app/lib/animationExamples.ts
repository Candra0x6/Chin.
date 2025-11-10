/**
 * Animation System Usage Examples
 * Demonstrates how to use the patient flow animation system
 */

import * as THREE from 'three';
import {
  PatientState,
  STATE_TO_ZONE,
  WAIT_PERIODS,
  MOVEMENT_SPEED,
  createPatientAnimation,
  createPatientAnimations,
  updatePatientAnimation,
  updateAllPatientAnimations,
  getAnimationStats,
  type PatientAnimation
} from './animationUtils';

// ============================================
// Example 1: Basic Single Patient Animation
// ============================================
export function example1_SinglePatient() {
  // Create a patient mesh (group with body and head)
  const patientMesh = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, 0.15, 0.8, 8),
    new THREE.MeshLambertMaterial({ color: 0xffffff })
  );
  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 8, 8),
    new THREE.MeshLambertMaterial({ color: 0xffffff })
  );
  head.position.y = 0.55;
  patientMesh.add(body, head);

  // Initialize animation (no start delay)
  const animation = createPatientAnimation(patientMesh, 0);

  // In your animation loop
  const clock = new THREE.Clock();
  function animate() {
    const deltaTime = clock.getDelta();
    updatePatientAnimation(animation, deltaTime);
    
    // Check current state
    console.log('Patient state:', animation.state);
    console.log('Position:', animation.mesh.position);
    
    requestAnimationFrame(animate);
  }
  animate();
}

// ============================================
// Example 2: Multiple Patients with Stagger
// ============================================
export function example2_MultiplePatients(scene: THREE.Scene) {
  // Assume you have created multiple patient meshes
  const patientMeshes: THREE.Group[] = [];
  
  // Create 5 patient figures
  for (let i = 0; i < 5; i++) {
    const patient = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.CylinderGeometry(0.15, 0.15, 0.8, 8),
      new THREE.MeshLambertMaterial({ color: 0xffffff })
    );
    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 8, 8),
      new THREE.MeshLambertMaterial({ color: 0xffffff })
    );
    head.position.y = 0.55;
    patient.add(body, head);
    scene.add(patient);
    patientMeshes.push(patient);
  }

  // Initialize all animations with 1.5 second stagger
  const animations = createPatientAnimations(patientMeshes, 1.5);

  // In your animation loop
  const clock = new THREE.Clock();
  function animate() {
    const deltaTime = clock.getDelta();
    updateAllPatientAnimations(animations, deltaTime);
    
    requestAnimationFrame(animate);
  }
  animate();
}

// ============================================
// Example 3: Extract Patients from Scene
// ============================================
export function example3_ExtractFromScene(scene: THREE.Scene): THREE.Group[] {
  const patientMeshes: THREE.Group[] = [];
  
  scene.traverse((child) => {
    // Check if it's a group with children
    if (child instanceof THREE.Group && child.children.length >= 2) {
      const firstChild = child.children[0];
      
      // Check if first child is a mesh
      if (firstChild instanceof THREE.Mesh) {
        const material = firstChild.material as THREE.MeshLambertMaterial;
        
        // Patient figures use white color (#FFFFFF)
        // Staff figures use blue (#3399FF)
        // Beds use green (#88C999)
        if (material.color.getHex() === 0xffffff) {
          patientMeshes.push(child);
        }
      }
    }
  });
  
  return patientMeshes;
}

// ============================================
// Example 4: Custom Animation Configuration
// ============================================
export function example4_CustomConfiguration() {
  // You can modify constants in animationUtils.ts:
  
  // Change movement speed (units per second)
  // export const MOVEMENT_SPEED = 3; // Faster
  
  // Change waiting periods (seconds)
  // export const WAIT_PERIODS = {
  //   TRIAGING: 5,   // Longer triage
  //   TREATING: 10,  // Longer treatment
  //   BOARDING: 3,   // Longer boarding
  //   // ...
  // };
  
  // Then use normally
  console.log('Custom config example - modify source constants');
}

// ============================================
// Example 5: Animation Statistics & Debugging
// ============================================
export function example5_AnimationStats(animations: PatientAnimation[]) {
  // Get current distribution of patients across zones
  const stats = getAnimationStats(animations);
  
  console.log('=== Patient Distribution ===');
  console.log(`Entering: ${stats.entering} patients`);
  console.log(`Triaging: ${stats.triaging} patients`);
  console.log(`Treating: ${stats.treating} patients`);
  console.log(`Boarding: ${stats.boarding} patients`);
  console.log(`Exiting: ${stats.exiting} patients`);
  
  // You can use this for:
  // - Dashboard displays
  // - Performance monitoring
  // - Debugging animation flow
  // - Real-time statistics
}

// ============================================
// Example 6: State-Based Event Handling
// ============================================
export class PatientEventHandler {
  private lastStates: Map<PatientAnimation, PatientState> = new Map();

  /**
   * Check for state changes and trigger events
   */
  checkStateChanges(animations: PatientAnimation[]): void {
    animations.forEach(patient => {
      const lastState = this.lastStates.get(patient);
      const currentState = patient.state;

      // State changed
      if (lastState !== currentState) {
        this.onStateChange(patient, lastState, currentState);
        this.lastStates.set(patient, currentState);
      }
    });
  }

  /**
   * Handle state change events
   */
  private onStateChange(
    patient: PatientAnimation,
    oldState: PatientState | undefined,
    newState: PatientState
  ): void {
    console.log(`Patient state changed: ${oldState} → ${newState}`);

    // Trigger specific events
    switch (newState) {
      case PatientState.TRIAGING:
        this.onArrivedAtTriage(patient);
        break;
      case PatientState.TREATING:
        this.onStartedTreatment(patient);
        break;
      case PatientState.BOARDING:
        this.onStartedBoarding(patient);
        break;
      case PatientState.EXITING:
        this.onExiting(patient);
        break;
    }
  }

  private onArrivedAtTriage(patient: PatientAnimation): void {
    console.log('Patient arrived at triage');
    // Could trigger: visual indicator, sound effect, UI update
  }

  private onStartedTreatment(patient: PatientAnimation): void {
    console.log('Patient started treatment');
    // Could trigger: assign to bed, update capacity
  }

  private onStartedBoarding(patient: PatientAnimation): void {
    console.log('Patient boarding (waiting for discharge)');
    // Could trigger: boarding alert, capacity warning
  }

  private onExiting(patient: PatientAnimation): void {
    console.log('Patient exiting ED');
    // Could trigger: completion animation, statistics update
  }
}

// ============================================
// Example 7: Integration with React Component
// ============================================
export function example7_ReactIntegration() {
  /*
  import { useEffect, useRef } from 'react';
  
  function MyScene() {
    const animationsRef = useRef<PatientAnimation[]>([]);
    const clockRef = useRef<THREE.Clock>(new THREE.Clock());
    
    useEffect(() => {
      // Setup scene, camera, renderer...
      const scene = new THREE.Scene();
      
      // Create and extract patient meshes
      const patientMeshes = example3_ExtractFromScene(scene);
      
      // Initialize animations
      animationsRef.current = createPatientAnimations(patientMeshes, 1.0);
      clockRef.current.start();
      
      // Animation loop
      function animate() {
        const deltaTime = clockRef.current.getDelta();
        updateAllPatientAnimations(animationsRef.current, deltaTime);
        
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
      }
      animate();
      
      return () => {
        // Cleanup
        clockRef.current.stop();
      };
    }, []);
    
    return <div ref={containerRef} />;
  }
  */
  console.log('See source code for React integration example');
}

// ============================================
// Example 8: Advanced - Custom Easing
// ============================================
export function example8_CustomEasing() {
  // The default easing is ease-in-out cubic
  // If you want different easing, modify the easeInOutCubic function:
  
  // Linear (no easing)
  const linear = (t: number) => t;
  
  // Ease-in quadratic
  const easeInQuad = (t: number) => t * t;
  
  // Ease-out quadratic
  const easeOutQuad = (t: number) => t * (2 - t);
  
  // Ease-in-out sine
  const easeInOutSine = (t: number) => -(Math.cos(Math.PI * t) - 1) / 2;
  
  // Bounce
  const bounce = (t: number) => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) {
      return n1 * t * t;
    } else if (t < 2 / d1) {
      return n1 * (t -= 1.5 / d1) * t + 0.75;
    } else if (t < 2.5 / d1) {
      return n1 * (t -= 2.25 / d1) * t + 0.9375;
    } else {
      return n1 * (t -= 2.625 / d1) * t + 0.984375;
    }
  };
  
  console.log('Custom easing functions:', {
    linear,
    easeInQuad,
    easeOutQuad,
    easeInOutSine,
    bounce
  });
}

// ============================================
// Example 9: Performance Monitoring
// ============================================
export class AnimationPerformanceMonitor {
  private frameCount = 0;
  private lastTime = performance.now();
  private fps = 0;

  update(animations: PatientAnimation[]): void {
    this.frameCount++;
    const currentTime = performance.now();
    const elapsed = currentTime - this.lastTime;

    // Update FPS every second
    if (elapsed >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / elapsed);
      this.frameCount = 0;
      this.lastTime = currentTime;

      // Log performance metrics
      console.log('=== Performance ===');
      console.log(`FPS: ${this.fps}`);
      console.log(`Active animations: ${animations.length}`);
      console.log(`Moving: ${animations.filter(a => a.isMoving).length}`);
      console.log(`Waiting: ${animations.filter(a => !a.isMoving).length}`);
    }
  }
}

// ============================================
// Example 10: Complete Setup Helper
// ============================================
export class PatientFlowAnimationSystem {
  private animations: PatientAnimation[] = [];
  private clock: THREE.Clock = new THREE.Clock();
  private eventHandler: PatientEventHandler = new PatientEventHandler();
  private perfMonitor: AnimationPerformanceMonitor = new AnimationPerformanceMonitor();

  /**
   * Initialize the animation system
   */
  initialize(scene: THREE.Scene, staggerDelay: number = 1.0): void {
    // Extract patient meshes from scene
    const patientMeshes = example3_ExtractFromScene(scene);
    
    console.log(`Found ${patientMeshes.length} patients in scene`);

    // Create animations
    this.animations = createPatientAnimations(patientMeshes, staggerDelay);
    
    // Start clock
    this.clock.start();
  }

  /**
   * Update all animations (call in animation loop)
   */
  update(): void {
    const deltaTime = this.clock.getDelta();
    
    // Update animations
    updateAllPatientAnimations(this.animations, deltaTime);
    
    // Check for state changes
    this.eventHandler.checkStateChanges(this.animations);
    
    // Monitor performance
    this.perfMonitor.update(this.animations);
  }

  /**
   * Get current statistics
   */
  getStats() {
    return getAnimationStats(this.animations);
  }

  /**
   * Cleanup
   */
  dispose(): void {
    this.clock.stop();
    this.animations = [];
  }
}

// ============================================
// Usage:
// ============================================
/*
const animSystem = new PatientFlowAnimationSystem();
animSystem.initialize(scene, 1.0);

function animate() {
  animSystem.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
*/
