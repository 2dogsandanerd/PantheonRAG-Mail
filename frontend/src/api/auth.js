
import client from './client';

const TOKEN_KEY = 'pantheonmail_token';
const REFRESH_TOKEN_KEY = 'pantheonmail_refresh_token';
const USER_KEY = 'pantheonmail_user';

export const authService = {
  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, refresh_token } = response.data;
    this.setTokens(access_token, refresh_token);
    return response.data;
  },

  async register(username, email, password) {
    const response = await client.post('/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  async getMe() {
    const response = await client.get('/auth/me');
    return response.data;
  },

  async refreshToken() {
    const refresh_token = this.getRefreshToken();
    if (!refresh_token) {
      throw new Error('No refresh token');
    }

    const response = await client.post('/auth/refresh', null, {
      params: { refresh_token },
    });

    const { access_token, refresh_token: new_refresh_token } = response.data;
    this.setTokens(access_token, new_refresh_token);
    return response.data;
  },

  setTokens(accessToken, refreshToken) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  logout() {
    this.clearTokens();
  },
};

client.interceptors.request.use((config) => {
  const token = authService.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await authService.refreshToken();
        const token = authService.getToken();
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return client(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear tokens and let the app handle the logout
        authService.logout();
        // Don't reload - let the App component handle the auth state change
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default authService;
