import { apiClient } from 'services/api';

export interface Fir {
  ROWID: string;
  fir_number: string;
  crime_id: string;
  station_id: string;
  officer_id: string;
  description: string;
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
  CREATEDTIME: string;
  MODIFIEDTIME: string;
}

export interface FirCreate {
  fir_number: string;
  crime_id: string;
  station_id: string;
  officer_id: string;
  description: string;
  status?: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
}

export interface FirUpdate {
  fir_number?: string;
  crime_id?: string;
  station_id?: string;
  officer_id?: string;
  description?: string;
  status?: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
}

export interface FirFilters {
  limit?: number;
  offset?: number;
  fir_number?: string;
  district_id?: string;
  station_id?: string;
  officer_id?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

export const firsApi = {
  list: (filters?: FirFilters) =>
    apiClient.get<Fir[]>('/firs', { params: filters }),

  getById: (id: string) =>
    apiClient.get<Fir>(`/firs/${id}`),

  create: (data: FirCreate) =>
    apiClient.post<Fir>('/firs', data),

  update: (id: string, data: FirUpdate) =>
    apiClient.put<Fir>(`/firs/${id}`, data),

  delete: (id: string) =>
    apiClient.delete(`/firs/${id}`),
};
