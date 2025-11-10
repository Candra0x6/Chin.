/**
 * Performance Monitor - Phase 10: Testing & Optimization
 * 
 * This module provides comprehensive performance monitoring utilities for the
 * Emergency Department 3D Flow Visualization, including FPS tracking, memory usage,
 * render time analysis, and performance metrics collection.
 */

import * as THREE from 'three';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface PerformanceMetrics {
  fps: number;
  averageFps: number;
  minFps: number;
  maxFps: number;
  frameTime: number;
  averageFrameTime: number;
  memoryUsed?: number;
  memoryTotal?: number;
  drawCalls: number;
  triangles: number;
  geometries: number;
  textures: number;
  programs: number;
}

export interface PerformanceStats {
  current: PerformanceMetrics;
  history: PerformanceMetrics[];
  startTime: number;
  duration: number;
}

export interface PerformanceThresholds {
  targetFps: number;
  minAcceptableFps: number;
  maxFrameTime: number;
  maxMemoryMB: number;
}

// ============================================================================
// PERFORMANCE MONITOR CLASS
// ============================================================================

export class PerformanceMonitor {
  private frames: number[] = [];
  private frameTimes: number[] = [];
  private lastTime: number = performance.now();
  private startTime: number = performance.now();
  private historySize: number = 60; // Keep last 60 samples
  
  private renderer?: THREE.WebGLRenderer;
  private thresholds: PerformanceThresholds = {
    targetFps: 60,
    minAcceptableFps: 30,
    maxFrameTime: 33.33, // 30 FPS = 33.33ms per frame
    maxMemoryMB: 500,
  };

  constructor(renderer?: THREE.WebGLRenderer, historySize: number = 60) {
    this.renderer = renderer;
    this.historySize = historySize;
  }

  /**
   * Update performance metrics (call this every frame)
   */
  public update(): void {
    const currentTime = performance.now();
    const deltaTime = currentTime - this.lastTime;
    const fps = 1000 / deltaTime;

    // Store frame time and FPS
    this.frameTimes.push(deltaTime);
    this.frames.push(fps);

    // Limit history size
    if (this.frameTimes.length > this.historySize) {
      this.frameTimes.shift();
      this.frames.shift();
    }

    this.lastTime = currentTime;
  }

  /**
   * Get current performance metrics
   */
  public getMetrics(): PerformanceMetrics {
    const currentFps = this.frames.length > 0 
      ? this.frames[this.frames.length - 1] 
      : 0;
    
    const averageFps = this.frames.length > 0
      ? this.frames.reduce((a, b) => a + b, 0) / this.frames.length
      : 0;

    const minFps = this.frames.length > 0
      ? Math.min(...this.frames)
      : 0;

    const maxFps = this.frames.length > 0
      ? Math.max(...this.frames)
      : 0;

    const currentFrameTime = this.frameTimes.length > 0
      ? this.frameTimes[this.frameTimes.length - 1]
      : 0;

    const averageFrameTime = this.frameTimes.length > 0
      ? this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length
      : 0;

    // Memory info (if available)
    let memoryUsed: number | undefined;
    let memoryTotal: number | undefined;
    
    if ('memory' in performance) {
      const memory = (performance as {memory?: {usedJSHeapSize: number; totalJSHeapSize: number}}).memory;
      if (memory) {
        memoryUsed = memory.usedJSHeapSize / (1024 * 1024); // Convert to MB
        memoryTotal = memory.totalJSHeapSize / (1024 * 1024);
      }
    }

    // Renderer info (if available)
    let drawCalls = 0;
    let triangles = 0;
    let geometries = 0;
    let textures = 0;
    let programs = 0;

    if (this.renderer) {
      const info = this.renderer.info;
      drawCalls = info.render.calls;
      triangles = info.render.triangles;
      geometries = info.memory.geometries;
      textures = info.memory.textures;
      programs = info.programs?.length || 0;
    }

    return {
      fps: currentFps,
      averageFps,
      minFps,
      maxFps,
      frameTime: currentFrameTime,
      averageFrameTime,
      memoryUsed,
      memoryTotal,
      drawCalls,
      triangles,
      geometries,
      textures,
      programs,
    };
  }

  /**
   * Get full performance stats including history
   */
  public getStats(): PerformanceStats {
    const currentTime = performance.now();
    
    return {
      current: this.getMetrics(),
      history: [], // Could store historical snapshots if needed
      startTime: this.startTime,
      duration: currentTime - this.startTime,
    };
  }

  /**
   * Check if performance meets thresholds
   */
  public isPerformanceAcceptable(): boolean {
    const metrics = this.getMetrics();
    
    // Check FPS
    if (metrics.averageFps < this.thresholds.minAcceptableFps) {
      return false;
    }

    // Check frame time
    if (metrics.averageFrameTime > this.thresholds.maxFrameTime) {
      return false;
    }

    // Check memory (if available)
    if (metrics.memoryUsed && metrics.memoryUsed > this.thresholds.maxMemoryMB) {
      return false;
    }

    return true;
  }

  /**
   * Get performance issues and warnings
   */
  public getIssues(): string[] {
    const issues: string[] = [];
    const metrics = this.getMetrics();

    if (metrics.averageFps < this.thresholds.minAcceptableFps) {
      issues.push(`Low FPS: ${metrics.averageFps.toFixed(1)} (target: ${this.thresholds.targetFps})`);
    }

    if (metrics.minFps < 20) {
      issues.push(`FPS drops detected: minimum ${metrics.minFps.toFixed(1)} FPS`);
    }

    if (metrics.averageFrameTime > this.thresholds.maxFrameTime) {
      issues.push(`High frame time: ${metrics.averageFrameTime.toFixed(2)}ms (max: ${this.thresholds.maxFrameTime}ms)`);
    }

    if (metrics.memoryUsed && metrics.memoryUsed > this.thresholds.maxMemoryMB) {
      issues.push(`High memory usage: ${metrics.memoryUsed.toFixed(1)}MB (max: ${this.thresholds.maxMemoryMB}MB)`);
    }

    if (metrics.drawCalls > 100) {
      issues.push(`High draw calls: ${metrics.drawCalls} (consider batching geometry)`);
    }

    if (metrics.triangles > 100000) {
      issues.push(`High triangle count: ${metrics.triangles} (consider LOD or simplification)`);
    }

    return issues;
  }

  /**
   * Reset performance tracking
   */
  public reset(): void {
    this.frames = [];
    this.frameTimes = [];
    this.lastTime = performance.now();
    this.startTime = performance.now();
  }

  /**
   * Update thresholds
   */
  public setThresholds(thresholds: Partial<PerformanceThresholds>): void {
    this.thresholds = { ...this.thresholds, ...thresholds };
  }

  /**
   * Generate performance report
   */
  public generateReport(): string {
    const metrics = this.getMetrics();
    const stats = this.getStats();
    const issues = this.getIssues();
    const durationSeconds = stats.duration / 1000;

    let report = '=== Performance Report ===\n\n';
    
    report += `Duration: ${durationSeconds.toFixed(1)}s\n\n`;
    
    report += '--- Frame Rate ---\n';
    report += `Current FPS: ${metrics.fps.toFixed(1)}\n`;
    report += `Average FPS: ${metrics.averageFps.toFixed(1)}\n`;
    report += `Min FPS: ${metrics.minFps.toFixed(1)}\n`;
    report += `Max FPS: ${metrics.maxFps.toFixed(1)}\n\n`;
    
    report += '--- Frame Time ---\n';
    report += `Current: ${metrics.frameTime.toFixed(2)}ms\n`;
    report += `Average: ${metrics.averageFrameTime.toFixed(2)}ms\n\n`;
    
    if (metrics.memoryUsed !== undefined) {
      report += '--- Memory ---\n';
      report += `Used: ${metrics.memoryUsed.toFixed(1)}MB\n`;
      report += `Total: ${metrics.memoryTotal?.toFixed(1)}MB\n\n`;
    }
    
    report += '--- Renderer Info ---\n';
    report += `Draw Calls: ${metrics.drawCalls}\n`;
    report += `Triangles: ${metrics.triangles}\n`;
    report += `Geometries: ${metrics.geometries}\n`;
    report += `Textures: ${metrics.textures}\n`;
    report += `Programs: ${metrics.programs}\n\n`;
    
    if (issues.length > 0) {
      report += '--- Issues Detected ---\n';
      issues.forEach(issue => {
        report += `⚠️  ${issue}\n`;
      });
    } else {
      report += '✅ No performance issues detected\n';
    }

    return report;
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Create a simple FPS counter overlay
 */
export function createFPSCounter(): HTMLDivElement {
  const counter = document.createElement('div');
  counter.style.position = 'fixed';
  counter.style.top = '10px';
  counter.style.right = '10px';
  counter.style.background = 'rgba(0, 0, 0, 0.7)';
  counter.style.color = '#00ff00';
  counter.style.padding = '10px';
  counter.style.fontFamily = 'monospace';
  counter.style.fontSize = '14px';
  counter.style.zIndex = '10000';
  counter.style.borderRadius = '5px';
  counter.textContent = 'FPS: 0';
  
  document.body.appendChild(counter);
  return counter;
}

/**
 * Update FPS counter display
 */
export function updateFPSCounter(
  counter: HTMLDivElement,
  metrics: PerformanceMetrics
): void {
  const fpsColor = metrics.fps >= 55 ? '#00ff00' : 
                   metrics.fps >= 30 ? '#ffaa00' : 
                   '#ff0000';
  
  counter.style.color = fpsColor;
  counter.innerHTML = `
    <strong>Performance</strong><br>
    FPS: ${metrics.fps.toFixed(1)}<br>
    Avg: ${metrics.averageFps.toFixed(1)}<br>
    Frame: ${metrics.frameTime.toFixed(2)}ms<br>
    ${metrics.memoryUsed ? `Mem: ${metrics.memoryUsed.toFixed(1)}MB<br>` : ''}
    Calls: ${metrics.drawCalls}<br>
    Tris: ${metrics.triangles}
  `;
}

/**
 * Log performance metrics to console
 */
export function logPerformanceMetrics(metrics: PerformanceMetrics): void {
  console.group('Performance Metrics');
  console.log(`FPS: ${metrics.fps.toFixed(1)} (avg: ${metrics.averageFps.toFixed(1)})`);
  console.log(`Frame Time: ${metrics.frameTime.toFixed(2)}ms (avg: ${metrics.averageFrameTime.toFixed(2)}ms)`);
  if (metrics.memoryUsed) {
    console.log(`Memory: ${metrics.memoryUsed.toFixed(1)}MB / ${metrics.memoryTotal?.toFixed(1)}MB`);
  }
  console.log(`Draw Calls: ${metrics.drawCalls}`);
  console.log(`Triangles: ${metrics.triangles}`);
  console.groupEnd();
}

/**
 * Test performance over a duration
 */
export async function runPerformanceTest(
  monitor: PerformanceMonitor,
  durationMs: number = 10000
): Promise<PerformanceMetrics> {
  monitor.reset();
  
  return new Promise((resolve) => {
    setTimeout(() => {
      const metrics = monitor.getMetrics();
      resolve(metrics);
    }, durationMs);
  });
}

/**
 * Detect browser and device capabilities
 */
export function detectCapabilities() {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  
  if (!gl) {
    return {
      webgl: false,
      webgl2: false,
      maxTextureSize: 0,
      maxVertexUniforms: 0,
      devicePixelRatio: window.devicePixelRatio || 1,
    };
  }

  const isWebGL2 = gl instanceof WebGL2RenderingContext;
  
  return {
    webgl: true,
    webgl2: isWebGL2,
    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
    maxVertexUniforms: gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS),
    maxFragmentUniforms: gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_VECTORS),
    maxVaryingVectors: gl.getParameter(gl.MAX_VARYING_VECTORS),
    maxVertexAttributes: gl.getParameter(gl.MAX_VERTEX_ATTRIBS),
    devicePixelRatio: window.devicePixelRatio || 1,
    vendor: gl.getParameter(gl.VENDOR),
    renderer: gl.getParameter(gl.RENDERER),
  };
}

/**
 * Optimize renderer settings based on performance
 */
export function optimizeRendererSettings(
  renderer: THREE.WebGLRenderer,
  targetFps: number = 60
): void {
  const currentFps = 60; // Would come from monitor
  
  if (currentFps < targetFps) {
    // Reduce quality for better performance
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.shadowMap.enabled = false;
  } else {
    // Use full quality
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  }
}

/**
 * Memory cleanup utility
 */
export function disposeObject(object: THREE.Object3D): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      if (child.geometry) {
        child.geometry.dispose();
      }
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(material => material.dispose());
        } else {
          child.material.dispose();
        }
      }
    }
  });
}

/**
 * Get scene complexity metrics
 */
export function getSceneComplexity(scene: THREE.Scene): {
  objects: number;
  vertices: number;
  faces: number;
  lights: number;
  materials: number;
} {
  let objects = 0;
  let vertices = 0;
  let faces = 0;
  let lights = 0;
  const materials = new Set<THREE.Material>();

  scene.traverse((child) => {
    objects++;

    if (child instanceof THREE.Mesh && child.geometry) {
      const geometry = child.geometry;
      
      if (geometry.attributes.position) {
        vertices += geometry.attributes.position.count;
      }
      
      if (geometry.index) {
        faces += geometry.index.count / 3;
      } else if (geometry.attributes.position) {
        faces += geometry.attributes.position.count / 3;
      }

      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(mat => materials.add(mat));
        } else {
          materials.add(child.material);
        }
      }
    }

    if (child instanceof THREE.Light) {
      lights++;
    }
  });

  return {
    objects,
    vertices,
    faces,
    lights,
    materials: materials.size,
  };
}
