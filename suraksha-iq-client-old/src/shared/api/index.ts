export { default as apiClient, setAuthHandlers, parseProblemDetail } from './client';
export type { ApiError, AxiosRequestConfig } from './client';
export {
  buildCursorParams,
  createAbortSignal,
  parseProblemDetail as parseApiProblemDetail,
} from './pagination';
export type {
  ProblemDetail,
  PaginatedResponse,
  CursorPaginationParams,
} from './pagination';

export { authApi } from './authApi';
export { hotspotsApi } from './hotspotsApi';
export type { Hotspot } from './hotspotsApi';
export { trendsApi } from './trendsApi';
export type { TrendPoint } from './trendsApi';
export { anomaliesApi } from './anomaliesApi';
export type { Anomaly } from './anomaliesApi';
export { repeatOffendersApi } from './repeatOffendersApi';
export type { RepeatOffender } from './repeatOffendersApi';
export { networkApi } from './networkApi';
export type { NetworkGraph, NetworkNode, NetworkEdge } from './networkApi';
export { riskScoringApi } from './riskScoringApi';
export type { RiskScore } from './riskScoringApi';
export { alertsApi } from './alertsApi';
export type { AlertRecord } from './alertsApi';
export { casesApi } from './casesApi';
export type { CaseRecord } from './casesApi';
export { districtsApi } from './districtsApi';
export type { DistrictSummary } from './districtsApi';
export { reportsApi } from './reportsApi';
export type { Report } from './reportsApi';
export { adminApi } from './adminApi';
export type { AdminUser, AlertRule } from './adminApi';
export { dashboardApi } from './dashboardApi';
export type { DashboardSummary, DashboardMetric } from './dashboardApi';
