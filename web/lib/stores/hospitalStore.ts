import { create } from 'zustand';

export interface HospitalMetricsState {
  // Analysis Metrics
  peakCount: number;
  
  // Hospital Context Data
  availableBeds: number;
  availableNurses: number;
  
  // Actions
  setPeakCount: (count: number) => void;
  setAvailableBeds: (beds: number) => void;
  setAvailableNurses: (nurses: number) => void;
  
  // Update all metrics at once
  updateMetrics: (data: {
    peakCount?: number;
    availableBeds?: number;
    availableNurses?: number;
  }) => void;
  
  // Reset to default values
  reset: () => void;
}

const initialState = {
  peakCount: 0,
  availableBeds: 0,
  availableNurses: 0,
};

export const useHospitalStore = create<HospitalMetricsState>((set) => ({
  ...initialState,
  
  setPeakCount: (count: number) => set({ peakCount: count }),
  
  setAvailableBeds: (beds: number) => set({ availableBeds: beds }),
  
  setAvailableNurses: (nurses: number) => set({ availableNurses: nurses }),
  
  updateMetrics: (data) =>
    set((state) => ({
      peakCount: data.peakCount !== undefined ? data.peakCount : state.peakCount,
      availableBeds: data.availableBeds !== undefined ? data.availableBeds : state.availableBeds,
      availableNurses: data.availableNurses !== undefined ? data.availableNurses : state.availableNurses,
    })),
  
  reset: () => set(initialState),
}));
