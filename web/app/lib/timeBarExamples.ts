/**
 * Time Bar Usage Examples
 * Demonstrates various ways to use and customize the time bar system
 */

import * as THREE from 'three';
import {
  createTimeBar,
  updateTimeBar,
  updateTimeBarProgress,
  syncTimeBarWithAnimations,
  resetTimeBar,
  getTimeBarStats,
  disposeTimeBar,
  DEFAULT_TIME_BAR_CONFIG,
  type TimeBarConfig,
  type TimeBarState
} from './timeBarUtils';
import type { PatientAnimation } from './animationUtils';

// ============================================
// Example 1: Basic Time Bar Setup
// ============================================
export async function example1_BasicSetup(scene: THREE.Scene) {
  // Create time bar with default configuration
  const timeBar = await createTimeBar();
  
  // Add to scene
  scene.add(timeBar.container);
  
  // In animation loop
  const clock = new THREE.Clock();
  function animate() {
    const deltaTime = clock.getDelta();
    updateTimeBar(timeBar, deltaTime);
    
    // Your rendering code...
    requestAnimationFrame(animate);
  }
  animate();
  
  return timeBar;
}

// ============================================
// Example 2: Custom Configuration
// ============================================
export async function example2_CustomConfig(scene: THREE.Scene) {
  // Create custom configuration
  const customConfig: TimeBarConfig = {
    width: 20,              // Wider bar
    height: 0.6,            // Taller bar
    depth: 0.15,            // Thicker bar
    position: {
      x: 0,
      y: 0.1,               // Higher above floor
      z: 8                  // Further back
    },
    colors: {
      background: 0x1a1a1a, // Darker gray
      progress: 0x00FF00,   // Green instead of blue
      label: 0xFFFF00       // Yellow label
    },
    cycleDuration: 30       // 30 second cycle
  };
  
  // Create time bar with custom config
  const timeBar = await createTimeBar(customConfig);
  scene.add(timeBar.container);
  
  return timeBar;
}

// ============================================
// Example 3: Syncing with Patient Animations
// ============================================
export async function example3_SyncWithPatients(
  scene: THREE.Scene,
  patientAnimations: PatientAnimation[]
) {
  const timeBar = await createTimeBar();
  scene.add(timeBar.container);
  
  const clock = new THREE.Clock();
  function animate() {
    const deltaTime = clock.getDelta();
    
    // Calculate average patient cycle time
    if (patientAnimations.length > 0) {
      const totalCycleTime = patientAnimations.reduce(
        (sum, patient) => sum + patient.totalCycleTime,
        0
      );
      const avgCycleTime = totalCycleTime / patientAnimations.length;
      
      // Sync time bar with patient animations
      syncTimeBarWithAnimations(timeBar, avgCycleTime);
    } else {
      // Fallback to default update
      updateTimeBar(timeBar, deltaTime);
    }
    
    requestAnimationFrame(animate);
  }
  animate();
}

// ============================================
// Example 4: Manual Progress Control
// ============================================
export async function example4_ManualControl(scene: THREE.Scene) {
  const timeBar = await createTimeBar();
  scene.add(timeBar.container);
  
  // Set progress manually (0.0 to 1.0)
  updateTimeBarProgress(timeBar, 0.5);  // 50%
  
  // You can control this with:
  // - User input (slider)
  // - Custom animation logic
  // - External data source
  
  // Example: Animate to 100% over 5 seconds
  let elapsed = 0;
  const duration = 5;
  
  function animate() {
    const delta = 0.016; // ~60 FPS
    elapsed += delta;
    
    const progress = Math.min(1, elapsed / duration);
    updateTimeBarProgress(timeBar, progress);
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }
  animate();
}

// ============================================
// Example 5: Statistics and Monitoring
// ============================================
export async function example5_Statistics(scene: THREE.Scene) {
  const timeBar = await createTimeBar();
  scene.add(timeBar.container);
  
  const clock = new THREE.Clock();
  let lastLogTime = 0;
  
  function animate() {
    const deltaTime = clock.getDelta();
    updateTimeBar(timeBar, deltaTime);
    
    // Log statistics every second
    if (timeBar.elapsedTime - lastLogTime >= 1) {
      const stats = getTimeBarStats(timeBar);
      
      console.log('=== Time Bar Stats ===');
      console.log(`Progress: ${(stats.progress * 100).toFixed(1)}%`);
      console.log(`Elapsed: ${stats.formattedTime}`);
      console.log(`Cycle: ${stats.cycleCount + 1}`);
      console.log(`Raw Time: ${stats.elapsedTime.toFixed(2)}s`);
      
      lastLogTime = timeBar.elapsedTime;
    }
    
    requestAnimationFrame(animate);
  }
  animate();
}

// ============================================
// Example 6: Reset Functionality
// ============================================
export async function example6_Reset(scene: THREE.Scene) {
  const timeBar = await createTimeBar();
  scene.add(timeBar.container);
  
  // Reset button handler
  function handleReset() {
    resetTimeBar(timeBar);
    console.log('Time bar reset to 0%');
  }
  
  // You can trigger this with:
  // - User button click
  // - Keyboard shortcut
  // - Scene reset event
  
  // Example: Reset every 10 seconds
  setInterval(() => {
    handleReset();
  }, 10000);
}

// ============================================
// Example 7: Multiple Color Schemes
// ============================================
export async function example7_ColorSchemes(scene: THREE.Scene) {
  // Theme presets
  const themes = {
    blue: {
      background: 0x404040,
      progress: 0x3399FF,
      label: 0xFFFFFF
    },
    green: {
      background: 0x2a2a2a,
      progress: 0x00FF00,
      label: 0xFFFFFF
    },
    orange: {
      background: 0x3a3a3a,
      progress: 0xFF9900,
      label: 0xFFFFFF
    },
    purple: {
      background: 0x2d2d2d,
      progress: 0x9966FF,
      label: 0xFFFFFF
    },
    red: {
      background: 0x3d3d3d,
      progress: 0xFF3333,
      label: 0xFFFFFF
    }
  };
  
  // Create with selected theme
  const selectedTheme = 'green';
  const timeBar = await createTimeBar({
    ...DEFAULT_TIME_BAR_CONFIG,
    colors: themes[selectedTheme]
  });
  
  scene.add(timeBar.container);
  return timeBar;
}

// ============================================
// Example 8: React Integration
// ============================================
export function example8_ReactIntegration() {
  /*
  import { useEffect, useRef } from 'react';
  
  function MyScene() {
    const timeBarRef = useRef<TimeBarState | null>(null);
    const clockRef = useRef<THREE.Clock>(new THREE.Clock());
    
    useEffect(() => {
      const scene = new THREE.Scene();
      
      // Create time bar
      createTimeBar().then((timeBar) => {
        timeBarRef.current = timeBar;
        scene.add(timeBar.container);
      });
      
      // Animation loop
      function animate() {
        const deltaTime = clockRef.current.getDelta();
        
        if (timeBarRef.current) {
          updateTimeBar(timeBarRef.current, deltaTime);
        }
        
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
      }
      animate();
      
      return () => {
        // Cleanup
        if (timeBarRef.current) {
          disposeTimeBar(timeBarRef.current);
        }
      };
    }, []);
    
    return <div ref={containerRef} />;
  }
  */
  console.log('See source code for React integration example');
}

// ============================================
// Example 9: Responsive Sizing
// ============================================
export async function example9_ResponsiveSizing(
  scene: THREE.Scene,
  sceneWidth: number
) {
  // Create time bar that matches scene width
  const timeBar = await createTimeBar({
    ...DEFAULT_TIME_BAR_CONFIG,
    width: sceneWidth * 0.8,  // 80% of scene width
    position: {
      x: 0,
      y: 0.05,
      z: sceneWidth / 2 - 1  // Position relative to scene
    }
  });
  
  scene.add(timeBar.container);
  return timeBar;
}

// ============================================
// Example 10: Complete Setup Helper Class
// ============================================
export class TimeBarManager {
  private timeBar: TimeBarState | null = null;
  private clock: THREE.Clock = new THREE.Clock();
  private isPaused: boolean = false;

  /**
   * Initialize the time bar
   */
  async initialize(
    scene: THREE.Scene,
    config?: Partial<TimeBarConfig>
  ): Promise<void> {
    const finalConfig = config
      ? { ...DEFAULT_TIME_BAR_CONFIG, ...config }
      : DEFAULT_TIME_BAR_CONFIG;
    
    this.timeBar = await createTimeBar(finalConfig);
    scene.add(this.timeBar.container);
    this.clock.start();
    
    console.log('Time bar initialized');
  }

  /**
   * Update time bar (call in animation loop)
   */
  update(): void {
    if (!this.timeBar || this.isPaused) return;
    
    const deltaTime = this.clock.getDelta();
    updateTimeBar(this.timeBar, deltaTime);
  }

  /**
   * Pause animation
   */
  pause(): void {
    this.isPaused = true;
    console.log('Time bar paused');
  }

  /**
   * Resume animation
   */
  resume(): void {
    this.isPaused = false;
    this.clock.getDelta(); // Reset delta to avoid jump
    console.log('Time bar resumed');
  }

  /**
   * Toggle pause/resume
   */
  togglePause(): void {
    if (this.isPaused) {
      this.resume();
    } else {
      this.pause();
    }
  }

  /**
   * Reset to start
   */
  reset(): void {
    if (!this.timeBar) return;
    resetTimeBar(this.timeBar);
    console.log('Time bar reset');
  }

  /**
   * Set progress manually
   */
  setProgress(progress: number): void {
    if (!this.timeBar) return;
    updateTimeBarProgress(this.timeBar, progress);
  }

  /**
   * Get current statistics
   */
  getStats() {
    if (!this.timeBar) return null;
    return getTimeBarStats(this.timeBar);
  }

  /**
   * Get progress percentage (0-100)
   */
  getProgressPercent(): number {
    if (!this.timeBar) return 0;
    return this.timeBar.currentProgress * 100;
  }

  /**
   * Get elapsed time
   */
  getElapsedTime(): number {
    if (!this.timeBar) return 0;
    return this.timeBar.elapsedTime;
  }

  /**
   * Cleanup
   */
  dispose(): void {
    if (this.timeBar) {
      disposeTimeBar(this.timeBar);
      this.timeBar = null;
    }
    this.clock.stop();
  }
}

// ============================================
// Example 11: Event-Based Updates
// ============================================
export class TimeBarEventSystem {
  private timeBar: TimeBarState | null = null;
  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  private listeners: Map<string, Set<Function>> = new Map();

  async initialize(scene: THREE.Scene): Promise<void> {
    this.timeBar = await createTimeBar();
    scene.add(this.timeBar.container);
  }

  update(deltaTime: number): void {
    if (!this.timeBar) return;
    
    const oldProgress = this.timeBar.currentProgress;
    updateTimeBar(this.timeBar, deltaTime);
    const newProgress = this.timeBar.currentProgress;
    
    // Trigger events at specific milestones
    if (oldProgress < 0.25 && newProgress >= 0.25) {
      this.trigger('quarter');
    }
    if (oldProgress < 0.5 && newProgress >= 0.5) {
      this.trigger('half');
    }
    if (oldProgress < 0.75 && newProgress >= 0.75) {
      this.trigger('threequarter');
    }
    if (oldProgress > newProgress) {
      this.trigger('cycle');
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  off(event: string, callback: Function): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  private trigger(event: string): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback());
    }
    console.log(`Time bar event: ${event}`);
  }
}

// ============================================
// Example 12: UI Dashboard Integration
// ============================================
export class TimeBarDashboard {
  private timeBar: TimeBarState | null = null;
  private dashboardElement: HTMLElement | null = null;

  async initialize(scene: THREE.Scene, dashboardId: string): Promise<void> {
    this.timeBar = await createTimeBar();
    scene.add(this.timeBar.container);
    
    this.dashboardElement = document.getElementById(dashboardId);
  }

  update(deltaTime: number): void {
    if (!this.timeBar || !this.dashboardElement) return;
    
    updateTimeBar(this.timeBar, deltaTime);
    this.updateDashboard();
  }

  private updateDashboard(): void {
    if (!this.timeBar || !this.dashboardElement) return;
    
    const stats = getTimeBarStats(this.timeBar);
    
    this.dashboardElement.innerHTML = `
      <div class="time-bar-stats">
        <div class="stat">
          <label>Progress:</label>
          <span>${(stats.progress * 100).toFixed(1)}%</span>
        </div>
        <div class="stat">
          <label>Elapsed:</label>
          <span>${stats.formattedTime}</span>
        </div>
        <div class="stat">
          <label>Cycle:</label>
          <span>${stats.cycleCount + 1}</span>
        </div>
      </div>
    `;
  }
}

// ============================================
// Usage Examples:
// ============================================

/*
// Basic usage
const timeBar = await example1_BasicSetup(scene);

// Custom colors and size
const customTimeBar = await example2_CustomConfig(scene);

// Synced with animations
await example3_SyncWithPatients(scene, patientAnimations);

// Using manager class
const manager = new TimeBarManager();
await manager.initialize(scene);
function animate() {
  manager.update();
  requestAnimationFrame(animate);
}

// With events
const eventSystem = new TimeBarEventSystem();
await eventSystem.initialize(scene);
eventSystem.on('half', () => console.log('Halfway through!'));
eventSystem.on('cycle', () => console.log('Cycle complete!'));
*/
