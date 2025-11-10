/**
 * Object Utilities for Emergency Department 3D Visualization
 * 
 * This module contains factory functions for loading and creating:
 * - Hospital bed models (from simple_bed.glb)
 * - Patient figures (from patient.glb)
 * - Staff figures (from medical_staff.glb)
 * 
 * Uses GLTFLoader to load 3D models from Sketchfab
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { COLORS } from './environmentUtils';

// ============================================
// MODEL LOADER INITIALIZATION
// ============================================
const loader = new GLTFLoader();

// Cache for loaded models to avoid reloading
const modelCache: {
  bed?: THREE.Group;
  patient?: THREE.Group;
  staff?: THREE.Group;
} = {};

/**
 * Load a model from glb file
 * Caches the model for reuse
 * 
 * @param modelPath - Path to the .glb file
 * @param cacheName - Name to cache the model under
 * @returns Promise with THREE.Group model
 */
async function loadModel(modelPath: string, cacheName: keyof typeof modelCache): Promise<THREE.Group> {
  // Return cached model if available
  if (modelCache[cacheName]) {
    return modelCache[cacheName]!.clone();
  }

  return new Promise((resolve, reject) => {
    loader.load(
      modelPath,
      (gltf) => {
        const model = gltf.scene;
        
        console.log(`Model loaded: ${modelPath}`);
        console.log(`Model children count: ${model.children.length}`);
        console.log(`Model structure:`, model);
        
        // Enable shadows on all meshes
        model.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        // Cache the model
        modelCache[cacheName] = model.clone();
        
        resolve(model);
      },
      // Optional: track loading progress
      () => {
        // const percentComplete = (progress.loaded / progress.total * 100).toFixed(0);
        // console.log(`Loading ${cacheName}: ${percentComplete}%`);
      },
      (_error) => {
        console.error(`Error loading ${cacheName} model:`, _error);
        reject(_error);
      }
    );
  });
}

// ============================================
// BED MODELS
// ============================================

/**
 * Creates a hospital bed model from 3D glb file
 * 
 * @param position - Position to place the bed
 * @returns Promise<THREE.Group> - Group containing bed model
 */
export async function createBed(position: THREE.Vector3): Promise<THREE.Group> {
  try {
    const bedModel = await loadModel('/models/simple_bed.glb', 'bed');
    
    // Clone the model for this instance
    const bed = bedModel.clone();
    
    // Position the bed
    bed.position.copy(position);
    
    // Scale adjustment - reduce to smallest size (0.6 scale)
    bed.scale.set(0.002, 0.002, 0.002);
    
    bed.name = 'Bed';
    
    // Enable shadows on cloned model
    bed.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    
    return bed;
  } catch (error) {
    console.error('Failed to create bed:', error);
    // Fallback to simple geometry if model fails to load
    return createBedFallback(position);
  }
}

/**
 * Fallback bed creation using simple geometry
 * Used if model fails to load
 * 
 * @param position - Position to place the bed
 * @returns THREE.Group - Group containing bed components
 */
function createBedFallback(position: THREE.Vector3): THREE.Group {
  const bedGroup = new THREE.Group();
  bedGroup.name = 'Bed_Fallback';

  const bedGeometry = new THREE.BoxGeometry(0.0018, 0.0003, 0.0009);
  const bedMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.BEDS, // Green #88C999
  });
  const bedFrame = new THREE.Mesh(bedGeometry, bedMaterial);
  bedFrame.castShadow = true;
  bedFrame.receiveShadow = true;

  bedGroup.add(bedFrame);
  bedGroup.position.copy(position);

  return bedGroup;
}

/**
 * Creates multiple beds and positions them in a zone
 * 
 * @param positions - Array of positions for beds
 * @returns Promise<THREE.Group> - Group containing all beds
 */
export async function createBeds(positions: THREE.Vector3[]): Promise<THREE.Group> {
  const bedsGroup = new THREE.Group();
  bedsGroup.name = 'Beds';

  // Create all beds in parallel for performance
  const bedPromises = positions.map((position, index) =>
    createBed(position).then((bed) => {
      bed.name = `Bed_${index}`;
      return bed;
    })
  );

  const beds = await Promise.all(bedPromises);
  beds.forEach((bed) => bedsGroup.add(bed));

  return bedsGroup;
}

// ============================================
// PATIENT FIGURES
// ============================================

/**
 * Creates a humanoid patient figure from 3D glb file
 * 
 * @param position - Position to place the figure
 * @returns Promise<THREE.Group> - Group containing patient model
 */
export async function createPatientFigure(position: THREE.Vector3): Promise<THREE.Group> {
  try {
    const patientModel = await loadModel('/models/patient.glb', 'patient');
    
    // Clone the model for this instance
    const patient = patientModel.clone();
    
    // Position the patient
    patient.position.copy(position);
    
    // Scale adjustment - reduce to smallest size (0.001 scale)
    patient.scale.set(0.005, 0.005, 0.005);
    
    patient.name = 'Patient';
    
    // Enable shadows on cloned model
    patient.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    
    return patient;
  } catch (error) {
    console.error('Failed to create patient:', error);
    // Fallback to simple geometry if model fails to load
    return createPatientFigureFallback(position);
  }
}

/**
 * Fallback patient creation using simple geometry
 * Used if model fails to load
 * 
 * @param position - Position to place the figure
 * @returns THREE.Group - Group containing patient components
 */
function createPatientFigureFallback(position: THREE.Vector3): THREE.Group {
  const patientGroup = new THREE.Group();
  patientGroup.name = 'Patient_Fallback';

  const bodyHeight = 0.0014; // Scaled to match 0.001 scale factor
  const bodyRadius = 0.0002; // Scaled to match 0.001 scale factor

  const bodyGeometry = new THREE.CylinderGeometry(bodyRadius, bodyRadius, bodyHeight, 16);
  const patientMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.PATIENTS, // White #FFFFFF
  });
  const body = new THREE.Mesh(bodyGeometry, patientMaterial);
  body.castShadow = true;
  body.receiveShadow = true;

  patientGroup.add(body);
  patientGroup.position.copy(position);

  return patientGroup;
}

/**
 * Creates multiple patient figures
 * 
 * @param positions - Array of positions for patients
 * @returns Promise<THREE.Group> - Group containing all patients
 */
export async function createPatients(positions: THREE.Vector3[]): Promise<THREE.Group> {
  const patientsGroup = new THREE.Group();
  patientsGroup.name = 'Patients';

  // Create all patients in parallel for performance
  const patientPromises = positions.map((position, index) =>
    createPatientFigure(position).then((patient) => {
      patient.name = `Patient_${index}`;
      return patient;
    })
  );

  const patients = await Promise.all(patientPromises);
  patients.forEach((patient) => patientsGroup.add(patient));

  return patientsGroup;
}

// ============================================
// STAFF FIGURES
// ============================================

/**
 * Creates a humanoid staff figure from 3D glb file
 * 
 * @param position - Position to place the figure
 * @returns Promise<THREE.Group> - Group containing staff model
 */
export async function createStaffFigure(position: THREE.Vector3): Promise<THREE.Group> {
  try {
    const staffModel = await loadModel('/models/patient.glb', 'staff');
    
    // Clone the model for this instance
    const staff = staffModel.clone();
    
    // Position the staff member
    staff.position.copy(position);
    
    staff.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        // Ensure the material supports color
        child.material = (child.material as THREE.Material).clone(); 
        if (child.material instanceof THREE.MeshLambertMaterial || child.material instanceof THREE.MeshStandardMaterial) {
          child.material.color.set(0x3399ff); // Blue color
        }
      }
    });
    
    // Scale adjustment - try larger scale to see if staff are visible
    // Original was 0.0005, trying 0.01 to test visibility
    staff.scale.set(0.005, 0.005, 0.005);
    
    staff.name = 'Staff';
    
    
    // Enable shadows on cloned model
    staff.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    
    return staff;
  } catch (error) {
    console.error('Failed to create staff:', error);
    // Fallback to simple geometry if model fails to load
    return createStaffFigureFallback(position);
  }
}

/**
 * Fallback staff creation using simple geometry
 * Used if model fails to load
 * 
 * @param position - Position to place the figure
 * @returns THREE.Group - Group containing staff components
 */
function createStaffFigureFallback(position: THREE.Vector3): THREE.Group {
  const staffGroup = new THREE.Group();
  staffGroup.name = 'Staff_Fallback';

  const bodyHeight = 0.0015; // Scaled to match 0.001 scale factor
  const bodyRadius = 0.00018; // Scaled to match 0.001 scale factor

  const bodyGeometry = new THREE.CylinderGeometry(bodyRadius, bodyRadius, bodyHeight, 16);
  const staffMaterial = new THREE.MeshLambertMaterial({
    color: COLORS.STAFF, // Blue #3399FF
  });
  const body = new THREE.Mesh(bodyGeometry, staffMaterial);
  body.castShadow = true;
  body.receiveShadow = true;

  staffGroup.add(body);
  staffGroup.position.copy(position);

  return staffGroup;
}

/**
 * Creates multiple staff figures
 * 
 * @param positions - Array of positions for staff
 * @returns Promise<THREE.Group> - Group containing all staff
 */
export async function createStaff(positions: THREE.Vector3[]): Promise<THREE.Group> {
  const staffGroup = new THREE.Group();
  staffGroup.name = 'StaffMembers';


  // Create all staff in parallel for performance
  const staffPromises = positions.map((position, index) =>
    createStaffFigure(position).then((staff) => {
      staff.name = `Staff_${index}`;
      console.log(`Staff ${index} created successfully - name: ${staff.name}`);
      return staff;
    })
  );

  const staffMembers = await Promise.all(staffPromises);
  
  staffMembers.forEach((staff) => {
    staffGroup.add(staff);
  });

  return staffGroup;
}

// ============================================
// SCENE POPULATION
// ============================================

/**
 * Generates bed positions in Treatment and Boarding zones
 * @param treatmentCount - Number of beds in treatment zone
 * @param boardingCount - Number of beds in boarding zone
 * @returns Array of bed positions
 */
export function generateBedPositions(
  treatmentCount: number,
  boardingCount: number
): THREE.Vector3[] {
  const positions: THREE.Vector3[] = [];

  // Treatment zone beds (x: -2 to 2)
  // Arrange in rows
  const treatmentStartX = -1.5;
  const treatmentSpacingX = 3 / Math.max(1, Math.ceil(treatmentCount / 2) - 1) || 1.5;
  const treatmentZPositions = [-2.5, 2.5]; // Two rows

  for (let i = 0; i < treatmentCount; i++) {
    const row = i % 2;
    const col = Math.floor(i / 2);
    const x = treatmentStartX + col * treatmentSpacingX;
    const z = treatmentZPositions[row];
    const y = 0.15; // Bed height (half of bed height)
    
    positions.push(new THREE.Vector3(x, y, z));
  }

  // Boarding zone beds (x: 2 to 6)
  const boardingStartX = 2.5;
  const boardingSpacingX = 3 / Math.max(1, Math.ceil(boardingCount / 2) - 1) || 1.5;
  const boardingZPositions = [-2.5, 2.5]; // Two rows

  for (let i = 0; i < boardingCount; i++) {
    const row = i % 2;
    const col = Math.floor(i / 2);
    const x = boardingStartX + col * boardingSpacingX;
    const z = boardingZPositions[row];
    const y = 0.15;
    
    positions.push(new THREE.Vector3(x, y, z));
  }

  return positions;
}

/**
 * Generates patient positions (one patient per bed)
 * @param bedPositions - Positions of beds
 * @returns Array of patient positions and states
 */
export function generatePatientPositions(
  bedPositions: THREE.Vector3[]
): Array<{ position: THREE.Vector3; inBed: boolean }> {
  const positions: Array<{ position: THREE.Vector3; inBed: boolean }> = [];

  // One patient per bed (lying down)
  // Patient body height is 1.4, so when lying down (rotated 90°), 
  // we need to position them at the bed height + radius (0.2)
  
  for (let i = 0; i < bedPositions.length; i++) {
    const bedPos = bedPositions[i];
    // Position patient on bed - when rotated 90°, position Y should be at bed surface + patient radius
    positions.push({
      position: new THREE.Vector3(bedPos.x, 0 , bedPos.z),
      inBed: true,
    });
  }

  return positions;
}

/**
 * Generates staff positions throughout the department
 * @param count - Number of staff members
 * @returns Array of staff positions
 */
export function generateStaffPositions(count: number): THREE.Vector3[] {
  const positions: THREE.Vector3[] = [];

  console.log('Generating staff positions for count:', count);

  // Distribute staff across zones with better spacing
  const zones = [
    { x: -4, z: -2, name: 'Triage_1' },
    { x: -4, z: 2, name: 'Triage_2' },
    { x: 0, z: -2, name: 'Treatment' },
    { x: 4, z: 2, name: 'Boarding' },
  ];

  for (let i = 0; i < count; i++) {
    const zone = zones[i % zones.length];
    const x = zone.x + (Math.random() - 0.5) * 1; // Reduced random variance
    const z = zone.z + (Math.random() - 0.5) * 1; // Reduced random variance
    const y = 0; // Half of body height for standing
    
    const pos = new THREE.Vector3(x, y, z);
    console.log(`Staff ${i} position: x=${pos.x.toFixed(2)}, z=${pos.z.toFixed(2)}`);
    positions.push(pos);
  }

  console.log('Generated staff positions:', positions.length);
  return positions;
}

/**
 * Creates and positions all 3D objects in the scene
 * Now uses async model loading - all models load in parallel for performance
 * 
 * @param bedCount - Total number of beds (default: 10)
 * @param patientCount - Total number of patients (default: 10)
 * @param staffCount - Total number of staff (default: 4)
 * @returns Promise<THREE.Group> - Group containing all objects
 */
export async function createAllSceneObjects(
  bedCount: number = 10,
  patientCount: number = 10,
  staffCount: number = 4
): Promise<THREE.Group> {
  const objectsGroup = new THREE.Group();
  objectsGroup.name = 'SceneObjects';

  console.log('Creating all scene objects - beds:', bedCount, 'patients:', patientCount, 'staff:', staffCount);

  // Calculate bed distribution (60% treatment, 40% boarding)
  const treatmentBeds = Math.ceil(bedCount * 0.6);
  const boardingBeds = bedCount - treatmentBeds;

  // Generate positions
  const bedPositions = generateBedPositions(treatmentBeds, boardingBeds);
  const patientData = generatePatientPositions(bedPositions);
  const staffPositions = generateStaffPositions(staffCount);

  // Load all model types in parallel
  const [beds, patients, staff] = await Promise.all([
    createBeds(bedPositions),
    createPatients(patientData.map(d => d.position)),
    createStaff(staffPositions),
  ]);

  console.log('Scene objects loaded - beds children:', beds.children.length, 'patients:', patients.children.length, 'staff:', staff.children.length);

  objectsGroup.add(beds);

  // Add patients - no rotation, standing upright on beds
  const patientsArray = patients.children;
  patientData.forEach((data, index) => {
    if (index < patientsArray.length) {
      const patient = patientsArray[index];
      if (patient instanceof THREE.Group || patient instanceof THREE.Object3D) {
        patient.rotation.z = 0; // No rotation - standing upright
      }
    }
  });

  objectsGroup.add(patients);
  objectsGroup.add(staff);

  return objectsGroup;
}
