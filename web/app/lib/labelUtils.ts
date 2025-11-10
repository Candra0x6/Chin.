/**
 * Label Utilities for Emergency Department 3D Visualization
 * 
 * This module contains functions for creating 3D text labels:
 * - Load fonts using FontLoader
 * - Create 3D text labels using TextGeometry
 * - Position labels for each zone
 */

import * as THREE from 'three';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';
import { ZONES, COLORS, getZoneCenter } from './environmentUtils';
import type { Font } from 'three/examples/jsm/loaders/FontLoader.js';

// Cache the loaded font to avoid reloading
let cachedFont: Font | null = null;

/**
 * Loads the font file for TextGeometry
 * @returns Promise<Font> - The loaded font
 */
export async function loadFont(): Promise<Font> {
  // Return cached font if already loaded
  if (cachedFont) {
    return cachedFont;
  }

  return new Promise((resolve, reject) => {
    const loader = new FontLoader();
    
    loader.load(
      '/fonts/helvetiker_regular.typeface.json',
      (font) => {
        cachedFont = font;
        resolve(font);
      },
      undefined, // onProgress
      (error) => {
        console.error('Error loading font:', error);
        reject(error);
      }
    );
  });
}

/**
 * Creates a 3D text label
 * @param text - The text to display
 * @param font - The loaded font
 * @param options - Text configuration options
 * @returns THREE.Mesh - The text mesh
 */
export function createTextLabel(
  text: string,
  font: Font,
  options: {
    size?: number;
    height?: number;
    color?: number;
    position?: THREE.Vector3;
  } = {}
): THREE.Mesh {
  const {
    size = 0.5,
    height = 0.1,
    color = COLORS.LABELS,
    position = new THREE.Vector3(0, 0, 0),
  } = options;

  // Create text geometry
  const textGeometry = new TextGeometry(text, {
    font: font,
    size: size,
    depth: height, // Use 'depth' instead of 'height' for TextGeometry
    curveSegments: 12,
    bevelEnabled: true,
    bevelThickness: 0.02,
    bevelSize: 0.02,
    bevelOffset: 0,
    bevelSegments: 5,
  });

  // Center the geometry
  textGeometry.computeBoundingBox();
  if (textGeometry.boundingBox) {
    const centerX = -0.5 * (textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x);
    const centerY = -0.5 * (textGeometry.boundingBox.max.y - textGeometry.boundingBox.min.y);
    textGeometry.translate(centerX, centerY, 0);
  }

  // Create material
  const textMaterial = new THREE.MeshLambertMaterial({
    color: color,
  });

  // Create mesh
  const textMesh = new THREE.Mesh(textGeometry, textMaterial);
  textMesh.castShadow = true;
  textMesh.receiveShadow = true;

  // Position the text
  textMesh.position.copy(position);

  // Rotate to lie flat on the floor
  textMesh.rotation.x = -Math.PI / 2;

  return textMesh;
}

/**
 * Creates labels for all zones
 * @param font - The loaded font
 * @returns THREE.Group - Group containing all zone labels
 */
export function createZoneLabels(font: Font): THREE.Group {
  const labelsGroup = new THREE.Group();
  labelsGroup.name = 'ZoneLabels';

  const labelConfigs = [
    {
      text: 'ENTRANCE',
      zoneName: 'ENTRANCE' as keyof typeof ZONES,
      size: 0.4,
    },
    {
      text: 'TRIAGE',
      zoneName: 'TRIAGE' as keyof typeof ZONES,
      size: 0.5,
    },
    {
      text: 'TREATMENT',
      zoneName: 'TREATMENT' as keyof typeof ZONES,
      size: 0.5,
    },
    {
      text: 'BOARDING',
      zoneName: 'BOARDING' as keyof typeof ZONES,
      size: 0.5,
    },
    {
      text: 'EXIT',
      zoneName: 'EXIT' as keyof typeof ZONES,
      size: 0.4,
    },
  ];

  labelConfigs.forEach((config) => {
    const zoneCenter = getZoneCenter(config.zoneName);
    
    // Position label at front of zone (positive Z)
    const labelPosition = new THREE.Vector3(
      zoneCenter.x,
      0.02, // Slightly above floor to prevent z-fighting
      4.5   // Near the front wall
    );

    const label = createTextLabel(config.text, font, {
      size: config.size,
      height: 0.08,
      color: COLORS.LABELS,
      position: labelPosition,
    });

    label.name = `${config.text}Label`;
    labelsGroup.add(label);
  });

  return labelsGroup;
}

/**
 * Creates all labels for the scene (async)
 * This function loads the font and creates all zone labels
 * @returns Promise<THREE.Group> - Group containing all labels
 */
export async function createAllLabels(): Promise<THREE.Group> {
  try {
    // Load font
    const font = await loadFont();
    
    // Create zone labels
    const zoneLabels = createZoneLabels(font);
    
    return zoneLabels;
  } catch (error) {
    console.error('Error creating labels:', error);
    // Return empty group if font loading fails
    return new THREE.Group();
  }
}

/**
 * Creates a custom text label at a specific position
 * Useful for additional labels beyond zone labels
 * @param text - Text to display
 * @param position - Position for the label
 * @param options - Additional options
 * @returns Promise<THREE.Mesh | null> - The text mesh or null if font fails to load
 */
export async function createCustomLabel(
  text: string,
  position: THREE.Vector3,
  options: {
    size?: number;
    height?: number;
    color?: number;
    rotateToFloor?: boolean;
  } = {}
): Promise<THREE.Mesh | null> {
  try {
    const font = await loadFont();
    const label = createTextLabel(text, font, {
      size: options.size,
      height: options.height,
      color: options.color,
      position: position,
    });

    // Optionally rotate to floor
    if (options.rotateToFloor !== false) {
      label.rotation.x = -Math.PI / 2;
    }

    return label;
  } catch (error) {
    console.error('Error creating custom label:', error);
    return null;
  }
}
