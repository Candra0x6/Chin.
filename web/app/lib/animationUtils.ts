/**
 * Animation utilities for patient flow visualization
 * Handles patient movement through zones with waiting periods
 */

import * as THREE from 'three';
import { getZoneCenter } from './environmentUtils';

/**
 * Patient flow states following the ED workflow
 */
export enum PatientState {
  ENTERING = 'ENTERING',
  TRIAGING = 'TRIAGING',
  TREATING = 'TREATING',
  BOARDING = 'BOARDING',
  EXITING = 'EXITING',
  EXITED = 'EXITED'
}

/**
 * Zone names corresponding to patient states
 */
export const STATE_TO_ZONE: Record<PatientState, 'ENTRANCE' | 'TRIAGE' | 'TREATMENT' | 'BOARDING' | 'EXIT'> = {
  [PatientState.ENTERING]: 'ENTRANCE',
  [PatientState.TRIAGING]: 'TRIAGE',
  [PatientState.TREATING]: 'TREATMENT',
  [PatientState.BOARDING]: 'BOARDING',
  [PatientState.EXITING]: 'EXIT',
  [PatientState.EXITED]: 'EXIT'
};

/**
 * Waiting periods for each state (in seconds)
 */
export const WAIT_PERIODS: Record<PatientState, number> = {
  [PatientState.ENTERING]: 0,
  [PatientState.TRIAGING]: 3,
  [PatientState.TREATING]: 5,
  [PatientState.BOARDING]: 2,
  [PatientState.EXITING]: 0,
  [PatientState.EXITED]: 0
};

/**
 * Movement speed (units per second)
 */
export const MOVEMENT_SPEED = 2;

/**
 * Patient animation data structure
 */
export interface PatientAnimation {
  mesh: THREE.Group;
  state: PatientState;
  targetPosition: THREE.Vector3;
  startPosition: THREE.Vector3;
  moveProgress: number;
  waitTimer: number;
  isMoving: boolean;
  totalCycleTime: number;
}

/**
 * Create animation data for a patient mesh
 */
export function createPatientAnimation(
  mesh: THREE.Group,
  startDelay: number = 0
): PatientAnimation {
  const entranceCenter = getZoneCenter('ENTRANCE');
  
  // Start at entrance
  mesh.position.set(entranceCenter.x, 0.9, entranceCenter.z);
  
  return {
    mesh,
    state: PatientState.ENTERING,
    targetPosition: entranceCenter.clone(),
    startPosition: entranceCenter.clone(),
    moveProgress: 0,
    waitTimer: startDelay,
    isMoving: false,
    totalCycleTime: 0
  };
}

/**
 * Get next state in the patient flow
 */
function getNextState(currentState: PatientState): PatientState {
  const stateOrder = [
    PatientState.ENTERING,
    PatientState.TRIAGING,
    PatientState.TREATING,
    PatientState.BOARDING,
    PatientState.EXITING,
    PatientState.EXITED
  ];
  
  const currentIndex = stateOrder.indexOf(currentState);
  if (currentIndex < stateOrder.length - 1) {
    return stateOrder[currentIndex + 1];
  }
  
  // Loop back to start
  return PatientState.ENTERING;
}

/**
 * Transition patient to next state
 */
function transitionToNextState(patient: PatientAnimation): void {
  const nextState = getNextState(patient.state);
  patient.state = nextState;
  
  // If exited, reset to entrance
  if (nextState === PatientState.EXITED) {
    patient.state = PatientState.ENTERING;
  }
  
  // Get target position for new state
  const zoneName = STATE_TO_ZONE[patient.state];
  const targetCenter = getZoneCenter(zoneName);
  
  // Add slight randomization to avoid overlap
  const randomOffsetX = (Math.random() - 0.5) * 1.5;
  const randomOffsetZ = (Math.random() - 0.5) * 1.5;
  
  patient.targetPosition.set(
    targetCenter.x + randomOffsetX,
    0.9,
    targetCenter.z + randomOffsetZ
  );
  
  patient.startPosition.copy(patient.mesh.position);
  patient.moveProgress = 0;
  patient.isMoving = true;
  patient.waitTimer = 0;
}

/**
 * Easing function for smooth movement (ease-in-out)
 */
function easeInOutCubic(t: number): number {
  return t < 0.5
    ? 4 * t * t * t
    : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Update patient animation (called each frame)
 * @param patient Patient animation data
 * @param deltaTime Time since last frame (in seconds)
 */
export function updatePatientAnimation(
  patient: PatientAnimation,
  deltaTime: number
): void {
  patient.totalCycleTime += deltaTime;
  
  if (patient.isMoving) {
    // Calculate movement distance this frame
    const distance = patient.startPosition.distanceTo(patient.targetPosition);
    const moveDuration = distance / MOVEMENT_SPEED;
    
    patient.moveProgress += deltaTime / moveDuration;
    
    if (patient.moveProgress >= 1) {
      // Movement complete
      patient.mesh.position.copy(patient.targetPosition);
      patient.moveProgress = 1;
      patient.isMoving = false;
      patient.waitTimer = 0;
    } else {
      // Interpolate position with easing
      const easedProgress = easeInOutCubic(patient.moveProgress);
      patient.mesh.position.lerpVectors(
        patient.startPosition,
        patient.targetPosition,
        easedProgress
      );
    }
  } else {
    // Waiting period
    const waitDuration = WAIT_PERIODS[patient.state];
    patient.waitTimer += deltaTime;
    
    if (patient.waitTimer >= waitDuration) {
      // Wait complete, move to next state
      transitionToNextState(patient);
    }
  }
}

/**
 * Create multiple patient animations with staggered start times
 */
export function createPatientAnimations(
  patientMeshes: THREE.Group[],
  staggerDelay: number = 1
): PatientAnimation[] {
  return patientMeshes.map((mesh, index) => 
    createPatientAnimation(mesh, index * staggerDelay)
  );
}

/**
 * Update all patient animations
 */
export function updateAllPatientAnimations(
  patients: PatientAnimation[],
  deltaTime: number
): void {
  patients.forEach(patient => updatePatientAnimation(patient, deltaTime));
}

/**
 * Get animation statistics for debugging
 */
export function getAnimationStats(patients: PatientAnimation[]): {
  entering: number;
  triaging: number;
  treating: number;
  boarding: number;
  exiting: number;
} {
  const stats = {
    entering: 0,
    triaging: 0,
    treating: 0,
    boarding: 0,
    exiting: 0
  };
  
  patients.forEach(patient => {
    switch (patient.state) {
      case PatientState.ENTERING:
        stats.entering++;
        break;
      case PatientState.TRIAGING:
        stats.triaging++;
        break;
      case PatientState.TREATING:
        stats.treating++;
        break;
      case PatientState.BOARDING:
        stats.boarding++;
        break;
      case PatientState.EXITING:
        stats.exiting++;
        break;
    }
  });
  
  return stats;
}
