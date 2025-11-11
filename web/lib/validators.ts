/**
 * Validation utilities for file uploads and form data
 */

import { config } from './config';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate video file before upload
 */
export function validateVideoFile(file: File): ValidationResult {
  // Check file exists
  if (!file) {
    return {
      isValid: false,
      error: 'No file selected',
    };
  }

  // Check file type
  const isValidType = config.allowedFormats.some(format => 
    file.type === format || file.name.toLowerCase().endsWith(format.split('/')[1])
  );

  if (!isValidType) {
    return {
      isValid: false,
      error: `Invalid file type. Allowed formats: ${config.allowedFormats.map(f => f.split('/')[1].toUpperCase()).join(', ')}`,
    };
  }

  // Check file size
  if (file.size > config.maxFileSize) {
    const maxSizeMB = Math.round(config.maxFileSize / (1024 * 1024));
    const fileSizeMB = Math.round(file.size / (1024 * 1024));
    return {
      isValid: false,
      error: `File size (${fileSizeMB}MB) exceeds maximum allowed size (${maxSizeMB}MB)`,
    };
  }

  // Check file size is not zero
  if (file.size === 0) {
    return {
      isValid: false,
      error: 'File is empty',
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Validate analysis ID format (UUID)
 */
export function validateAnalysisId(id: string): ValidationResult {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  
  if (!id) {
    return {
      isValid: false,
      error: 'Analysis ID is required',
    };
  }

  if (!uuidRegex.test(id)) {
    return {
      isValid: false,
      error: 'Invalid analysis ID format',
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Validate chat message
 */
export function validateChatMessage(message: string): ValidationResult {
  if (!message || message.trim().length === 0) {
    return {
      isValid: false,
      error: 'Message cannot be empty',
    };
  }

  if (message.length > 1000) {
    return {
      isValid: false,
      error: 'Message is too long (maximum 1000 characters)',
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Sanitize user input to prevent XSS
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Format bytes to human-readable size
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
}

/**
 * Check if file is a video based on extension
 */
export function isVideoFile(filename: string): boolean {
  const videoExtensions = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'];
  const extension = getFileExtension(filename);
  return videoExtensions.includes(extension);
}
