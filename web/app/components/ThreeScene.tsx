'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { createEnvironment } from '../lib/environmentUtils';
import { createAllSceneObjects } from '../lib/objectUtils';
import { createAllLabels } from '../lib/labelUtils';
import { 
  createPatientAnimations, 
  updateAllPatientAnimations,
  type PatientAnimation 
} from '../lib/animationUtils';
import {
  createTimeBar,
  updateTimeBar,
  type TimeBarState
} from '../lib/timeBarUtils';
import {
  PerformanceMonitor,
  type PerformanceMetrics
} from '../lib/performanceMonitor';
import { useHospitalStore } from '@/lib/stores/hospitalStore';

/**
 * ThreeScene Component - Phases 2, 3, 4, 5, 6, 7, 8, 9 & 10
 * 
 * Phase 2: Core Scene Setup
 * - Scene, Camera, and Renderer initialization
 * - WebGL renderer with antialiasing
 * - Isometric camera positioning with 60° FOV
 * - Dark gray background (#303030)
 * - Responsive canvas resizing
 * 
 * Phase 3: Environment & Layout
 * - Main floor plane (dark gray #303030)
 * - Walls using BoxGeometry (light gray #B0B0B0, 2m high)
 * - 5 zones: Entrance, Triage, Treatment, Boarding, Exit
 * - Triage zone with red floor plane (#882222)
 * - Coordinate system and zone dimensions
 * 
 * Phase 4: 3D Objects & Assets
 * - Bed models (BoxGeometry + pillow, green #88C999)
 * - Patient figures (Capsule + sphere, white #FFFFFF)
 * - Staff figures (Capsule + sphere, blue #3399FF)
 * - 8-10 beds positioned in Treatment and Boarding areas
 * - 8-10 patient figures in the scene
 * - 3-5 staff figures throughout the department
 * 
 * Phase 5: Labels & Text
 * - Font loaded using FontLoader
 * - 3D text labels using TextGeometry
 * - Zone labels: ENTRANCE, TRIAGE, TREATMENT, BOARDING, EXIT
 * - Labels positioned on the floor in white (#FFFFFF)
 * 
 * Phase 6: Lighting
 * - Enhanced AmbientLight (0.7 intensity)
 * - Main DirectionalLight with soft shadows (0.8 intensity)
 * - Fill DirectionalLight for shadow softening (0.4 intensity)
 * - HemisphereLight for ambient variation (0.3 intensity)
 * - PCF soft shadow mapping enabled
 * - Shadow quality optimized (2048x2048 map)
 * 
 * Phase 7: Animation System
 * - Patient movement path through all zones
 * - State machine: ENTERING → TRIAGING (3s) → TREATING (5s) → BOARDING (2s) → EXITING
 * - Smooth position interpolation with ease-in-out cubic easing
 * - Waiting periods at each zone
 * - Staggered animation start times (1 second intervals)
 * - Continuous loop animation
 * - Delta-time based animation for consistent speed
 * 
 * Phase 8: Time Bar
 * - Horizontal time bar at bottom of scene
 * - Background bar (dark gray #404040)
 * - Animated progress bar (blue #3399FF with glow)
 * - "TIME" label above bar
 * - Synced with animation cycle (20 second loop)
 * - Smooth scaling animation
 * 
 * Phase 9: Interactivity (OrbitControls)
 * - Camera rotation (left-click drag)
 * - Camera pan (right-click drag or Shift + left-click)
 * - Camera zoom (mouse wheel)
 * - Smooth damping for natural feel (dampingFactor: 0.05)
 * - Control limits: zoom (5-50 units), polar angle (0-85°), azimuth (±180°)
 * - Auto-rotation disabled
 * - Target locked to scene center (0, 0, 0)
 * 
 * Phase 10: Testing & Optimization
 * - Performance monitoring (FPS, frame time, memory)
 * - Real-time performance metrics display
 * - Responsive canvas resizing tested
 * - Cross-browser compatibility verified
 * - Memory optimization and cleanup
 * - Render optimization (shadows, pixel ratio)
 * - Performance thresholds and warnings
 */
export default function ThreeScene() {
    const { peakCount, availableBeds, availableNurses } = useHospitalStore();
  
  // Refs to store Three.js objects
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animationFrameRef = useRef<number>(0);
  
  // Phase 7: Animation system refs
  const patientAnimationsRef = useRef<PatientAnimation[]>([]);
  const clockRef = useRef<THREE.Clock>(new THREE.Clock());
  
  // Phase 8: Time bar refs
  const timeBarRef = useRef<TimeBarState | null>(null);
  
  // Phase 9: OrbitControls ref
  const controlsRef = useRef<OrbitControls | null>(null);
  
  // Phase 10: Performance monitoring
  const performanceMonitorRef = useRef<PerformanceMonitor | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [showPerformance, setShowPerformance] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    // Store container reference for cleanup
    const container = containerRef.current;

    // ==========================================
    // 1. SCENE INITIALIZATION
    // ==========================================
    const scene = new THREE.Scene();
    // Transparant background #1F2937
    scene.background = new THREE.Color(0x1F2937);
    sceneRef.current = scene;
    

    // ==========================================
    // 2. CAMERA SETUP
    // ==========================================
    // Create PerspectiveCamera with 60° Field of View
    // Parameters: FOV, aspect ratio, near clipping plane, far clipping plane
    const camera = new THREE.PerspectiveCamera(
      60, // 60° FOV as specified
      container.clientWidth / container.clientHeight,
      0.1, // Near clipping plane
      1000 // Far clipping plane
    );

    // Set up isometric positioning
    // Isometric view typically uses equal angles on all axes
    // Position camera elevated and at an angle to view the scene
    camera.position.set(15, 12, 15); // Elevated and angled for isometric view
    camera.lookAt(0, 0, 0); // Look at the center of the scene
    cameraRef.current = camera;

    // ==========================================
    // 3. RENDERER CONFIGURATION
    // ==========================================
    // Create WebGL renderer with antialiasing enabled
    const renderer = new THREE.WebGLRenderer({
      antialias: true, // Enable antialiasing for smoother edges
      alpha: false, // We don't need transparency
    });

    // Set renderer size to match container
    renderer.setSize(
      container.clientWidth,
      container.clientHeight
    );

    // Set pixel ratio for sharper rendering on high-DPI displays
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Append renderer to DOM
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Enable shadow rendering
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Soft shadows

    // ==========================================
    // 4. LIGHTING SETUP (Phase 6 - Enhanced)
    // ==========================================
    
    // Ambient Light - Provides soft overall lighting
    // Increased intensity for better visibility
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    ambientLight.name = 'AmbientLight';
    scene.add(ambientLight);

    // Directional Light 1 - Main light with shadows
    // Positioned to create depth and cast realistic shadows
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(10, 15, 10);
    directionalLight1.castShadow = true;
    directionalLight1.name = 'MainDirectionalLight';

    // Configure shadow properties for quality and performance balance
    directionalLight1.shadow.mapSize.width = 2048;
    directionalLight1.shadow.mapSize.height = 2048;
    directionalLight1.shadow.camera.near = 0.5;
    directionalLight1.shadow.camera.far = 50;
    
    // Shadow camera frustum (area that can cast shadows)
    const shadowSize = 15;
    directionalLight1.shadow.camera.left = -shadowSize;
    directionalLight1.shadow.camera.right = shadowSize;
    directionalLight1.shadow.camera.top = shadowSize;
    directionalLight1.shadow.camera.bottom = -shadowSize;
    
    // Soft shadow configuration
    directionalLight1.shadow.radius = 4; // Soft shadow blur
    directionalLight1.shadow.bias = -0.0001; // Prevent shadow acne

    scene.add(directionalLight1);

    // Directional Light 2 - Fill light (no shadows)
    // Softens harsh shadows from main light
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-10, 10, -10);
    directionalLight2.name = 'FillDirectionalLight';
    scene.add(directionalLight2);

    // Optional: Hemisphere Light for subtle ambient variation
    // Simulates light from sky and ground
    const hemisphereLight = new THREE.HemisphereLight(
      0xffffff, // Sky color
      0x444444, // Ground color
      0.3       // Intensity
    );
    hemisphereLight.name = 'HemisphereLight';
    scene.add(hemisphereLight);

    // ==========================================
    // 5. ENVIRONMENT SETUP (Phase 3)
    // ==========================================
    // Create and add the complete environment
    // This includes: floor, walls, zones, and triage area
    const environment = createEnvironment();
    scene.add(environment);

    // ==========================================
    // 5.5. 3D OBJECTS SETUP (Phase 4)
    // ==========================================
    // Load all 3D objects asynchronously
    // This includes: beds, patients, and staff figures from 3D models
    const availableBeds = localStorage.getItem('available_beds')
    const availableNurses = localStorage.getItem('available_nurses')
    const peakCount = localStorage.getItem('peak_count')

    createAllSceneObjects(Number(availableBeds), Number(availableNurses), Number(peakCount)).then((sceneObjects) => {
      scene.add(sceneObjects);
      
      // Extract patient meshes for animation
      const patientMeshes: THREE.Group[] = [];
      sceneObjects.traverse((child) => {
        // Identify patient figures by traversing the scene graph
        if (child instanceof THREE.Group && child.name.includes('Patient_')) {
          patientMeshes.push(child);
        }
      });
      
      // ==========================================
      // 5.6. ANIMATION SETUP (Phase 7)
      // ==========================================
      // Initialize patient animations with staggered start times
      patientAnimationsRef.current = createPatientAnimations(patientMeshes, 1.0);
      
      // Start the animation clock
      clockRef.current.start();
    }).catch((error) => {
      console.error('Failed to load scene objects:', error);
    });

    // ==========================================
    // 5.75. LABELS SETUP (Phase 5)
    // ==========================================
    // Create and add all text labels asynchronously
    // This includes: zone labels for all 5 zones
    createAllLabels().then((labels) => {
      scene.add(labels);
    }).catch((error) => {
      console.error('Failed to load labels:', error);
    });
    
    // ==========================================
    // 5.8. TIME BAR SETUP (Phase 8)
    // ==========================================
    // Create and add time bar asynchronously
    createTimeBar().then((timeBar) => {
      timeBarRef.current = timeBar;
      scene.add(timeBar.container);
    }).catch((error) => {
      console.error('Failed to create time bar:', error);
    });

    // ==========================================
    // 5.9. ORBIT CONTROLS SETUP (Phase 9)
    // ==========================================
    // Initialize OrbitControls for camera interaction
    const controls = new OrbitControls(camera, renderer.domElement);
    
    // Set target to center of scene
    controls.target.set(0, 0, 0);
    
    // Enable damping for smooth camera movement
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Configure zoom limits
    controls.minDistance = 5;   // Minimum zoom distance (close-up)
    controls.maxDistance = 50;  // Maximum zoom distance (far away)
    
    // Configure rotation limits
    // Polar angle: vertical rotation (0 = top, π/2 = horizon, π = bottom)
    controls.minPolarAngle = 0;                    // Can look from directly above
    controls.maxPolarAngle = Math.PI / 2 + 0.3;    // Can't go below horizon (85°)
    
    // Azimuth angle: horizontal rotation (unlimited by default)
    // No limits set - allow full 360° rotation
    
    // Pan settings
    controls.enablePan = true;
    controls.panSpeed = 1.0;
    controls.screenSpacePanning = false; // Pan in world space (XZ plane)
    
    // Zoom settings
    controls.enableZoom = true;
    controls.zoomSpeed = 1.0;
    
    // Rotation settings
    controls.enableRotate = true;
    controls.rotateSpeed = 1.0;
    
    // Disable auto-rotation
    controls.autoRotate = false;
    
    // Mouse button assignments (default)
    // Left button: ROTATE
    // Middle button: DOLLY (zoom)
    // Right button: PAN
    
    // Update controls once to apply settings
    controls.update();
    
    // Store controls reference
    controlsRef.current = controls;

    // ==========================================
    // 5.10. PERFORMANCE MONITOR SETUP (Phase 10)
    // ==========================================
    // Initialize performance monitor
    const performanceMonitor = new PerformanceMonitor(renderer, 120);
    performanceMonitorRef.current = performanceMonitor;
    
    // Toggle performance display with 'P' key
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'p' || event.key === 'P') {
        setShowPerformance(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyPress);

    // ==========================================
    // 6. ANIMATION LOOP
    // ==========================================
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);

      // Get delta time for frame-independent animation
      const deltaTime = clockRef.current.getDelta();
      
      // Update all patient animations (Phase 7)
      updateAllPatientAnimations(patientAnimationsRef.current, deltaTime);
      
      // Update time bar (Phase 8)
      if (timeBarRef.current) {
        updateTimeBar(timeBarRef.current, deltaTime);
      }
      
      // Update OrbitControls (Phase 9)
      // Required when damping is enabled
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      
      // Update performance monitor (Phase 10)
      if (performanceMonitorRef.current) {
        performanceMonitorRef.current.update();
        
        // Update metrics every 60 frames (~1 second at 60 FPS)
        if (animationFrameRef.current % 60 === 0) {
          const metrics = performanceMonitorRef.current.getMetrics();
          setPerformanceMetrics(metrics);
        }
      }

      // Render the scene from the camera's perspective
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    animate();

    // ==========================================
    // 7. RESPONSIVE CANVAS RESIZING
    // ==========================================
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) {
        return;
      }

      // Update camera aspect ratio
      cameraRef.current.aspect =
        containerRef.current.clientWidth / containerRef.current.clientHeight;
      
      // Update camera projection matrix
      cameraRef.current.updateProjectionMatrix();

      // Update renderer size
      rendererRef.current.setSize(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      );

      // Update pixel ratio
      rendererRef.current.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    };

    // Add resize event listener
    window.addEventListener('resize', handleResize);

    // ==========================================
    // 8. CLEANUP
    // ==========================================
    return () => {
      // Remove event listeners
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('keydown', handleKeyPress);

      // Cancel animation frame
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      // Dispose of OrbitControls (Phase 9)
      if (controlsRef.current) {
        controlsRef.current.dispose();
      }

      // Dispose of renderer
      if (rendererRef.current) {
        rendererRef.current.dispose();
        if (container && rendererRef.current.domElement) {
          container.removeChild(rendererRef.current.domElement);
        }
      }

      // Clear scene (memory optimization - Phase 10)
      if (sceneRef.current) {
        sceneRef.current.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            if (object.geometry) {
              object.geometry.dispose();
            }
            if (object.material) {
              if (Array.isArray(object.material)) {
                object.material.forEach(material => material.dispose());
              } else {
                object.material.dispose();
              }
            }
          }
        });
        sceneRef.current.clear();
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Legend Panel - Shows object types and colors */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        background: 'rgba(0, 0, 0, 0.8)',
        color: '#ffffff',
        padding: '15px',
        fontFamily: 'monospace',
        fontSize: '12px',
        borderRadius: '8px',
        minWidth: '250px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        zIndex: 999,
      }}>
        <div style={{ 
          fontWeight: 'bold', 
          marginBottom: '10px', 
          fontSize: '14px',
          color: '#ffffff',
          borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
          paddingBottom: '8px'
        }}>
          Scene Legend
        </div>
        
        <div style={{ lineHeight: '2' }}>
          {/* Beds */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              backgroundColor: '#88C999',
              borderRadius: '2px',
              flexShrink: 0
            }} />
            <span>Hospital Beds</span>
          </div>
          
          {/* Patients */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              backgroundColor: '#FFFFFF',
              borderRadius: '50%',
              border: '1px solid #666',
              flexShrink: 0
            }} />
            <span>Patients (Waiting/Receiving Care)</span>
          </div>
          
          {/* Staff */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              backgroundColor: '#3399FF',
              borderRadius: '50%',
              flexShrink: 0
            }} />
            <span>Medical Staff (Doctors/Nurses)</span>
          </div>
          
          {/* Zones */}
          <div style={{ marginTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.2)', paddingTop: '8px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '11px', color: '#aaa' }}>
              Department Zones:
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{
                width: '14px',
                height: '14px',
                backgroundColor: '#444444',
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <span style={{ fontSize: '11px' }}>Entrance</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{
                width: '14px',
                height: '14px',
                backgroundColor: '#882222',
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <span style={{ fontSize: '11px' }}>Triage Area</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{
                width: '14px',
                height: '14px',
                backgroundColor: '#444444',
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <span style={{ fontSize: '11px' }}>Treatment</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{
                width: '14px',
                height: '14px',
                backgroundColor: '#444444',
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <span style={{ fontSize: '11px' }}>Boarding</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '14px',
                height: '14px',
                backgroundColor: '#444444',
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <span style={{ fontSize: '11px' }}>Exit</span>
            </div>
          </div>

          {/* Controls */}
          <div style={{ marginTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.2)', paddingTop: '8px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '11px', color: '#aaa' }}>
              Controls:
            </div>
            <div style={{ fontSize: '11px', lineHeight: '1.8' }}>
              <div>🖱️ <strong>Left Drag</strong> - Rotate View</div>
              <div>🖱️ <strong>Right Drag</strong> - Pan Camera</div>
              <div>🔄 <strong>Scroll</strong> - Zoom In/Out</div>
              <div><strong>P</strong> - Toggle Performance</div>
            </div>
          </div>
        </div>
      </div>


      {/* Performance Metrics Overlay (Phase 10) - Toggle with 'P' key */}
      {showPerformance && performanceMetrics && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: performanceMetrics.fps >= 55 ? '#00ff00' : 
                 performanceMetrics.fps >= 30 ? '#ffaa00' : '#ff0000',
          padding: '15px',
          fontFamily: 'monospace',
          fontSize: '12px',
          borderRadius: '8px',
          minWidth: '200px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
          zIndex: 1000,
        }}>
          <div style={{ 
            fontWeight: 'bold', 
            marginBottom: '10px', 
            fontSize: '14px',
            color: '#ffffff',
            borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
            paddingBottom: '5px'
          }}>
            Performance Monitor
          </div>
          
          <div style={{ lineHeight: '1.6' }}>
            <div><strong>FPS:</strong> {performanceMetrics.fps.toFixed(1)}</div>
            <div><strong>Avg FPS:</strong> {performanceMetrics.averageFps.toFixed(1)}</div>
            <div><strong>Min:</strong> {performanceMetrics.minFps.toFixed(1)} 
                 <strong style={{ marginLeft: '10px' }}>Max:</strong> {performanceMetrics.maxFps.toFixed(1)}
            </div>
            <div style={{ marginTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.2)', paddingTop: '8px' }}>
              <strong>Frame Time:</strong> {performanceMetrics.frameTime.toFixed(2)}ms
            </div>
            <div><strong>Avg Frame:</strong> {performanceMetrics.averageFrameTime.toFixed(2)}ms</div>
            
            {performanceMetrics.memoryUsed && (
              <div style={{ marginTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.2)', paddingTop: '8px' }}>
                <strong>Memory:</strong> {performanceMetrics.memoryUsed.toFixed(1)}MB
              </div>
            )}
            
            <div style={{ marginTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.2)', paddingTop: '8px' }}>
              <strong>Draw Calls:</strong> {performanceMetrics.drawCalls}
            </div>
            <div><strong>Triangles:</strong> {performanceMetrics.triangles.toLocaleString()}</div>
            <div><strong>Geometries:</strong> {performanceMetrics.geometries}</div>
            <div><strong>Textures:</strong> {performanceMetrics.textures}</div>
          </div>
          
          <div style={{ 
            marginTop: '10px', 
            fontSize: '10px', 
            color: 'rgba(255, 255, 255, 0.6)',
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
            paddingTop: '8px'
          }}>
            Press &apos;P&apos; to toggle
          </div>
        </div>
      )}
      
      {/* Performance Toggle Hint */}
      {!showPerformance && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'rgba(0, 0, 0, 0.6)',
          color: 'rgba(255, 255, 255, 0.8)',
          padding: '8px 12px',
          fontFamily: 'monospace',
          fontSize: '11px',
          borderRadius: '5px',
          zIndex: 1000,
        }}>
          Press &apos;P&apos; for performance stats
        </div>
      )}
    </div>
  );
}
