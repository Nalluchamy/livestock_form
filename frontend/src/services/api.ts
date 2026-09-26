import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Attach Authorization header if access token exists
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('elhgs_access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Automatic token refresh interceptor on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('elhgs_refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
          const newAccessToken = res.data.access_token;
          const newRefreshToken = res.data.refresh_token;

          localStorage.setItem('elhgs_access_token', newAccessToken);
          if (newRefreshToken) {
            localStorage.setItem('elhgs_refresh_token', newRefreshToken);
          }

          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        } catch (refreshErr) {
          // Token refresh failed - clean storage
          localStorage.removeItem('elhgs_access_token');
          localStorage.removeItem('elhgs_refresh_token');
          localStorage.removeItem('elhgs_user');
          window.dispatchEvent(new Event('elhgs_session_expired'));
        }
      }
    }
    return Promise.reject(error);
  }
);
