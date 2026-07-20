/** Path of the health endpoint, shared between the API server and the web client. */
export const HEALTH_PATH = '/api/health';

/** Response shape of the health endpoint. */
export interface HealthResponse {
  status: 'ok';
  service: string;
  timestamp: string;
}
