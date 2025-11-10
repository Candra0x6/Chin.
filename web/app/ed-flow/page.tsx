'use client';

import ThreeScene from '../components/ThreeScene';

/**
 * Emergency Department 3D Flow Visualization
 * 
 * Main page component that renders the Three.js scene
 */
export default function EDFlowVisualization() {
  return (
    <main style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
      <ThreeScene />
    </main>
  );
}
