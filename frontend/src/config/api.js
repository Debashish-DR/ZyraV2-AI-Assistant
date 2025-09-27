import axios from 'axios';

// API configuration - Use your exact backend URL
const API_BASE_URL = 'https://zyra-backend-f7qj.onrender.com';

// Create axios instance with configuration
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000, // Increased timeout for better reliability
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor to add auth token and log requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Log request for debugging
        console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            headers: config.headers
        });
        
        return config;
    },
    (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
    (response) => {
        // Log successful response
        console.log(`✅ API Response: ${response.status} ${response.config.url}`, response.data);
        return response;
    },
    (error) => {
        // Log error response
        console.error('❌ API Error Response:', {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
        });
        
        if (error.response?.status === 401) {
            console.log('🔐 Unauthorized - Clearing tokens');
            localStorage.removeItem('token');
            localStorage.removeItem('email');
            // Redirect to login page
            if (window.location.pathname !== '/') {
                window.location.href = '/';
            }
        }
        
        return Promise.reject(error);
    }
);

export default api;