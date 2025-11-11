/**
 * Application configuration
 * Centralized access to environment variables
 */

interface AppConfig {
  apiUrl: string;
  maxFileSize: number;
  allowedFormats: string[];
  appName: string;
  appVersion: string;
  isDebug: boolean;
}

/**
 * Parse allowed formats from environment variable
 */
function parseAllowedFormats(formats: string | undefined): string[] {
  if (!formats) {
    return ['video/mp4', 'video/avi', 'video/mov', 'video/x-matroska'];
  }
  return formats.split(',').map(format => format.trim());
}

/**
 * Get application configuration from environment variables
 */
export function getConfig(): AppConfig {
  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    maxFileSize: parseInt(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || '104857600', 10),
    allowedFormats: parseAllowedFormats(process.env.NEXT_PUBLIC_ALLOWED_FORMATS),
    appName: process.env.NEXT_PUBLIC_APP_NAME || 'Chin',
    appVersion: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    isDebug: process.env.NEXT_PUBLIC_DEBUG === 'true',
  };
}

/**
 * Validate configuration on app start
 */
export function validateConfig(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  const config = getConfig();

  if (!config.apiUrl) {
    errors.push('API URL is not configured');
  }

  if (config.maxFileSize <= 0) {
    errors.push('Invalid max file size');
  }

  if (config.allowedFormats.length === 0) {
    errors.push('No allowed video formats configured');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Format file size to human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Export config instance
export const config = getConfig();
