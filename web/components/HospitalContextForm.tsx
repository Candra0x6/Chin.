/**
 * HospitalContextForm Component
 * Collects hospital context data for analysis
 * Includes comprehensive logging for debugging
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface HospitalContext {
  staffing: {
    total_nurses: number;
    total_doctors: number;
    available_nurses: number;
    available_doctors: number;
    shift_type: 'Day' | 'Night' | 'Evening';
  };
  resources: {
    total_beds: number;
    occupied_beds: number;
    available_beds: number;
    critical_care_beds: number;
    general_beds: number;
    observation_beds: number;
  };
  area_sqm: number;
  location_name: string;
}

export interface HospitalContextFormProps {
  onSubmit: (context: HospitalContext) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function HospitalContextForm({
  onSubmit,
  onCancel,
  isLoading = false,
}: HospitalContextFormProps): React.ReactElement {
  const [formData, setFormData] = useState<HospitalContext>({
    staffing: {
      total_nurses: 10,
      total_doctors: 5,
      available_nurses: 8,
      available_doctors: 4,
      shift_type: 'Day',
    },
    resources: {
      total_beds: 50,
      occupied_beds: 35,
      available_beds: 15,
      critical_care_beds: 10,
      general_beds: 30,
      observation_beds: 10,
    },
    area_sqm: 500,
    location_name: 'Emergency Room',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    staffing: true,
    resources: false,
    general: false,
  });

  const logDebug = (message: string, data?: Record<string, unknown> | string | number | HospitalContext): void => {
    const timestamp = new Date().toISOString();
    console.log(`[HospitalContextForm] ${timestamp} - ${message}`, data || '');
  };

  const logValidation = (field: string, value: number | string, isValid: boolean): void => {
    const timestamp = new Date().toISOString();
    console.log(
      `[HospitalContextForm] ${timestamp} - VALIDATION: ${field} = ${value} (${isValid ? '✓' : '✗'})`
    );
  };

  /**
   * Validate form data
   */
  const validateForm = useCallback((): boolean => {
    logDebug('Starting form validation', formData);
    const newErrors: Record<string, string> = {};

    // Staffing validation
    if (formData.staffing.total_nurses < 1) {
      newErrors.total_nurses = 'Total nurses must be at least 1';
      logValidation('total_nurses', formData.staffing.total_nurses, false);
    }
    if (formData.staffing.available_nurses > formData.staffing.total_nurses) {
      newErrors.available_nurses =
        'Available nurses cannot exceed total nurses';
      logValidation('available_nurses', formData.staffing.available_nurses, false);
    }
    if (formData.staffing.total_doctors < 1) {
      newErrors.total_doctors = 'Total doctors must be at least 1';
      logValidation('total_doctors', formData.staffing.total_doctors, false);
    }
    if (formData.staffing.available_doctors > formData.staffing.total_doctors) {
      newErrors.available_doctors =
        'Available doctors cannot exceed total doctors';
      logValidation('available_doctors', formData.staffing.available_doctors, false);
    }

    // Resources validation
    if (formData.resources.total_beds < 1) {
      newErrors.total_beds = 'Total beds must be at least 1';
      logValidation('total_beds', formData.resources.total_beds, false);
    }
    if (formData.resources.occupied_beds > formData.resources.total_beds) {
      newErrors.occupied_beds = 'Occupied beds cannot exceed total beds';
      logValidation('occupied_beds', formData.resources.occupied_beds, false);
    }
    if (formData.resources.available_beds < 0) {
      newErrors.available_beds = 'Available beds cannot be negative';
      logValidation('available_beds', formData.resources.available_beds, false);
    }
    if (
      formData.resources.critical_care_beds +
        formData.resources.general_beds +
        formData.resources.observation_beds !==
      formData.resources.total_beds
    ) {
      newErrors.bed_distribution =
        'Sum of bed types must equal total beds';
      logValidation(
        'bed_distribution',
        `${formData.resources.critical_care_beds} + ${formData.resources.general_beds} + ${formData.resources.observation_beds} != ${formData.resources.total_beds}`,
        false
      );
    }

    // General validation
    if (formData.area_sqm < 1) {
      newErrors.area_sqm = 'Area must be at least 1 sqm';
      logValidation('area_sqm', formData.area_sqm, false);
    }
    if (!formData.location_name.trim()) {
      newErrors.location_name = 'Location name is required';
      logValidation('location_name', formData.location_name, false);
    }

    setErrors(newErrors);
    const isValid = Object.keys(newErrors).length === 0;
    logDebug(`Form validation result: ${isValid ? 'VALID ✓' : 'INVALID ✗'}`, {
      errorCount: Object.keys(newErrors).length,
      errors: newErrors,
    });
    return isValid;
  }, [formData]);

  /**
   * Handle number input with validation
   */
  const handleNumberChange = useCallback(
    (
      section: keyof HospitalContext,
      field: string,
      value: string
    ) => {
      const numValue = parseInt(value) || 0;
      logDebug(`Number input changed: ${section}.${field}`, {
        stringValue: value,
        numericValue: numValue,
      });

      setFormData((prev) => {
        const updated = { ...prev };
        if (section === 'staffing') {
          const staffingField = field as keyof typeof prev.staffing;
          updated.staffing[staffingField] = numValue as never;
        } else if (section === 'resources') {
          const resourceField = field as keyof typeof prev.resources;
          updated.resources[resourceField] = numValue as never;
        } else if (section === 'area_sqm') {
          updated.area_sqm = numValue;
        }

        // Auto-calculate available beds
        if (section === 'resources') {
          const occupied = updated.resources.occupied_beds;
          const total = updated.resources.total_beds;
          updated.resources.available_beds = Math.max(0, total - occupied);
          logDebug('Auto-calculated available_beds', {
            total,
            occupied,
            available: updated.resources.available_beds,
          });
        }

        return updated;
      });

      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    },
    []
  );

  /**
   * Handle text input
   */
  const handleTextChange = useCallback(
    (field: string, value: string) => {
      logDebug(`Text input changed: ${field}`, { value });
      setFormData((prev) => ({
        ...prev,
        location_name: value,
      }));
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    },
    []
  );

  /**
   * Handle shift type change
   */
  const handleShiftChange = useCallback(
    (value: 'Day' | 'Night' | 'Evening') => {
      logDebug('Shift type changed', { newShift: value });
      setFormData((prev) => ({
        ...prev,
        staffing: {
          ...prev.staffing,
          shift_type: value,
        },
      }));
    },
    []
  );

  /**
   * Toggle section expansion
   */
  const toggleExpanded = useCallback((section: string) => {
    logDebug(`Toggle section expanded: ${section}`);
    setExpanded((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      logDebug('Form submission started');

      if (!validateForm()) {
        logDebug('Form validation failed - submission cancelled');
        return;
      }

      logDebug('Form validation passed - submitting', formData);
      console.log('[HospitalContextForm] Final submission data:', JSON.stringify(formData, null, 2));
      onSubmit(formData);
    },
    [formData, validateForm, onSubmit]
  );

  /**
   * Handle cancel
   */
  const handleCancel = useCallback(() => {
    logDebug('Form cancelled by user');
    onCancel();
  }, [onCancel]);

  return (
    <div className="w-full max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          🏥 Hospital Context Information
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
          Provide hospital staffing and resource information for enhanced analysis
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Staffing Section */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <button
            type="button"
            onClick={() => toggleExpanded('staffing')}
            className="w-full px-6 py-4 bg-linear-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
          >
            <span className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              👨‍⚕️ Staffing Information
            </span>
            <span className={`text-gray-500 transition-transform ${expanded.staffing ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>

          {expanded.staffing && (
            <div className="p-6 space-y-4">
              {/* Shift Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Shift Type
                </label>
                <select
                  value={formData.staffing.shift_type}
                  onChange={(e) =>
                    handleShiftChange(e.target.value as 'Day' | 'Night' | 'Evening')
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Day">Day Shift</option>
                  <option value="Night">Night Shift</option>
                  <option value="Evening">Evening Shift</option>
                </select>
              </div>

              {/* Nurses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Total Nurses
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.staffing.total_nurses}
                    onChange={(e) =>
                      handleNumberChange('staffing', 'total_nurses', e.target.value)
                    }
                    className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.total_nurses
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.total_nurses && (
                    <p className="text-red-500 text-sm mt-1">{errors.total_nurses}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Available Nurses
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.staffing.available_nurses}
                    onChange={(e) =>
                      handleNumberChange('staffing', 'available_nurses', e.target.value)
                    }
                    className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.available_nurses
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.available_nurses && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.available_nurses}
                    </p>
                  )}
                </div>
              </div>

              {/* Doctors */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Total Doctors
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.staffing.total_doctors}
                    onChange={(e) =>
                      handleNumberChange('staffing', 'total_doctors', e.target.value)
                    }
                    className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.total_doctors
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.total_doctors && (
                    <p className="text-red-500 text-sm mt-1">{errors.total_doctors}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Available Doctors
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.staffing.available_doctors}
                    onChange={(e) =>
                      handleNumberChange('staffing', 'available_doctors', e.target.value)
                    }
                    className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.available_doctors
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.available_doctors && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.available_doctors}
                    </p>
                  )}
                </div>
              </div>

              {/* Staffing Summary */}
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  💡 Shift: <span className="font-semibold">{formData.staffing.shift_type}</span>
                  {' | '}
                  Nurses: <span className="font-semibold">
                    {formData.staffing.available_nurses}/{formData.staffing.total_nurses}
                  </span>
                  {' | '}
                  Doctors: <span className="font-semibold">
                    {formData.staffing.available_doctors}/{formData.staffing.total_doctors}
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Resources Section */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <button
            type="button"
            onClick={() => toggleExpanded('resources')}
            className="w-full px-6 py-4 bg-linear-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between hover:bg-emerald-100 dark:hover:bg-emerald-900/30 transition-colors"
          >
            <span className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              🛏️ Resources & Beds
            </span>
            <span className={`text-gray-500 transition-transform ${expanded.resources ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>

          {expanded.resources && (
            <div className="p-6 space-y-4">
              {/* Total Beds */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Total Beds
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.resources.total_beds}
                  onChange={(e) =>
                    handleNumberChange('resources', 'total_beds', e.target.value)
                  }
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent ${
                    errors.total_beds
                      ? 'border-red-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {errors.total_beds && (
                  <p className="text-red-500 text-sm mt-1">{errors.total_beds}</p>
                )}
              </div>

              {/* Occupied & Available */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Occupied Beds
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.resources.occupied_beds}
                    onChange={(e) =>
                      handleNumberChange('resources', 'occupied_beds', e.target.value)
                    }
                    className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent ${
                      errors.occupied_beds
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  />
                  {errors.occupied_beds && (
                    <p className="text-red-500 text-sm mt-1">{errors.occupied_beds}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Available Beds (Auto-calculated)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.resources.available_beds}
                    readOnly
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-600 text-gray-900 dark:text-white opacity-75"
                  />
                </div>
              </div>

              {/* Bed Distribution */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Critical Care Beds
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.resources.critical_care_beds}
                    onChange={(e) =>
                      handleNumberChange('resources', 'critical_care_beds', e.target.value)
                    }
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    General Beds
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.resources.general_beds}
                    onChange={(e) =>
                      handleNumberChange('resources', 'general_beds', e.target.value)
                    }
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Observation Beds
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.resources.observation_beds}
                    onChange={(e) =>
                      handleNumberChange('resources', 'observation_beds', e.target.value)
                    }
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  />
                </div>
              </div>

              {errors.bed_distribution && (
                <p className="text-red-500 text-sm">{errors.bed_distribution}</p>
              )}

              {/* Resources Summary */}
              <div className="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <p className="text-sm text-emerald-800 dark:text-emerald-200">
                  💡 Total: <span className="font-semibold">{formData.resources.total_beds}</span> beds
                  {' | '}
                  Occupied: <span className="font-semibold">{formData.resources.occupied_beds}</span>
                  {' | '}
                  Available: <span className="font-semibold">{formData.resources.available_beds}</span>
                  {' | '}
                  Distribution: <span className="font-semibold">
                    {formData.resources.critical_care_beds} critical + {formData.resources.general_beds} general + {formData.resources.observation_beds} observation
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* General Information Section */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <button
            type="button"
            onClick={() => toggleExpanded('general')}
            className="w-full px-6 py-4 bg-linear-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
          >
            <span className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              📍 General Information
            </span>
            <span className={`text-gray-500 transition-transform ${expanded.general ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>

          {expanded.general && (
            <div className="p-6 space-y-4">
              {/* Location Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location Name
                </label>
                <input
                  type="text"
                  value={formData.location_name}
                  onChange={(e) => handleTextChange('location_name', e.target.value)}
                  placeholder="e.g., Emergency Room, ICU"
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                    errors.location_name
                      ? 'border-red-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {errors.location_name && (
                  <p className="text-red-500 text-sm mt-1">{errors.location_name}</p>
                )}
              </div>

              {/* Area */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Area (Square Meters)
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.area_sqm}
                  onChange={(e) =>
                    handleNumberChange('area_sqm', '', e.target.value)
                  }
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                    errors.area_sqm
                      ? 'border-red-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {errors.area_sqm && (
                  <p className="text-red-500 text-sm mt-1">{errors.area_sqm}</p>
                )}
              </div>

              {/* General Summary */}
              <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <p className="text-sm text-purple-800 dark:text-purple-200">
                  💡 Location: <span className="font-semibold">{formData.location_name}</span>
                  {' | '}
                  Area: <span className="font-semibold">{formData.area_sqm} sqm</span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isLoading}
            className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 px-6 py-3 bg-linear-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                ✓ Continue with Analysis
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default HospitalContextForm;
