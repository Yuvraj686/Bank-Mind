// API base fetch wrapper with JWT auth header

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getToken() {
  return localStorage.getItem('bankmind_token');
}

async function request(method, path, body = null, opts = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...opts.headers,
  };

  const config = {
    method,
    headers,
    ...(body ? { body: JSON.stringify(body) } : {}),
  };

  const res = await fetch(`${BASE_URL}${path}`, config);

  if (res.status === 401) {
    localStorage.removeItem('bankmind_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get:    (path, opts) => request('GET',    path, null, opts),
  post:   (path, body, opts) => request('POST',   path, body, opts),
  put:    (path, body, opts) => request('PUT',    path, body, opts),
  patch:  (path, body, opts) => request('PATCH',  path, body, opts),
  delete: (path, opts) => request('DELETE', path, null, opts),
};

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
};

// ── Customers ─────────────────────────────────────────────────────────────
export const customersApi = {
  list:            (stage) => api.get(`/customers${stage ? `?stage=${stage}` : ''}`),
  get:             (id) => api.get(`/customers/${id}`),
  create:          (data) => api.post('/customers', data),
  updateStage:     (id, stage, reason) => api.put(`/customers/${id}/stage`, { stage, reason }),
  getConversations:(id) => api.get(`/customers/${id}/conversations`),
};

// ── Dashboard ─────────────────────────────────────────────────────────────
export const dashboardApi = {
  kpis:         () => api.get('/dashboard/kpis'),
  pipeline:     () => api.get('/dashboard/pipeline'),
  activityFeed: () => api.get('/dashboard/activity-feed'),
};

// ── Agents ────────────────────────────────────────────────────────────────
export const agentsApi = {
  run:      (customerId) => api.post(`/agents/run/${customerId}`),
  logs:     (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api.get(`/agents/logs${q ? `?${q}` : ''}`);
  },
  logsForCustomer: (customerId) => api.get(`/agents/logs/${customerId}`),
  override: (logId, data) => api.patch(`/agents/logs/${logId}/override`, data),
};

// ── Demo ─────────────────────────────────────────────────────────────────
export const demoApi = {
  seed:  () => api.post('/demo/seed'),
  run:   () => api.post('/demo/run'),
  reset: () => api.post('/demo/reset'),
  state: () => api.get('/demo/state'),
};
