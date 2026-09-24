import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState({
    username: 'commander',
    full_name: 'Dr. Rajesh Sharma',
    role: 'Expedition Commander',
    email: 'rajesh.sharma@ncpor.gov.in',
    station: 'Maitri-II Main Station',
    permissions: ['PLAN_EXPEDITION', 'DISPATCH_SAR', 'APPROVE_ROUTES', 'OVERRIDE_SAFETY', 'MANAGE_FLEET']
  });

  const [availableRoles, setAvailableRoles] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available roles from backend
    const fetchRoles = async () => {
      try {
        const res = await axios.get(`${BASE_URL}/auth/roles`);
        if (res.data && Array.isArray(res.data)) {
          setAvailableRoles(res.data);
        }
      } catch (err) {
        console.warn('Failed to fetch roles list:', err);
      }
    };
    fetchRoles();
  }, []);

  const switchRole = async (username) => {
    setLoading(true);
    try {
      const res = await axios.post(`${BASE_URL}/auth/login`, {
        username,
        password: 'polar2026'
      });
      if (res.data?.user) {
        setCurrentUser(res.data.user);
        localStorage.setItem('polarsync_token', res.data.access_token);
      }
    } catch (err) {
      console.error('Role switch failed:', err);
      // Fallback locally
      const found = availableRoles.find(r => r.username === username);
      if (found) setCurrentUser(found);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ currentUser, availableRoles, switchRole, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
