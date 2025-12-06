const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  async request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include',
    });

    if (!response.ok) {
      let errorMessage = 'Request failed';
      try {
        const error = await response.json();
        errorMessage = error.error || error.message || errorMessage;
      } catch (e) {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return response;
  }

  auth = {
    login: (credentials) => this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

    signup: (userData) => this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

    logout: (userId) => this.request('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ userId }),
    }),

    getUser: () => this.request('/auth/user'),

    checkUsername: (username) => this.request(`/auth/check/username/${encodeURIComponent(username)}`),

    checkEmail: (email) => this.request(`/auth/check/email/${encodeURIComponent(email)}`),

    createUser: (userData) => this.request('/auth/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

    getUserByUsername: (username) => this.request(`/auth/users/by-username/${encodeURIComponent(username)}`),
  };

  angels = {
    getAll: () => this.request('/angels'),

    getById: (id) => this.request(`/angels/${id}`),

    getBySeries: (seriesId) => this.request(`/angels/series/${seriesId}`),

    getProfilePics: () => this.request('/angels/profile-pictures'),
  };

  users = {
    getProfile: (userId) => this.request(`/api/users/${userId}`),

    updateProfile: (userId, data) => this.request(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  };

  collections = {
    getByUser: (userId) => this.request(`/api/users/${userId}/collections`),

    upsert: (userId, data) => this.request(`/api/users/${userId}/collections`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    delete: (userId, angelId) => this.request(`/api/users/${userId}/collections/${angelId}`, {
      method: 'DELETE',
    }),
  };

  export = {
    getUserData: (userId, format = 'json') =>
      this.request(`/api/export/users/${userId}?format=${format}`),

    getStatus: (userId) => this.request(`/api/export/users/${userId}/status`),
  };
}

export default new ApiClient();
