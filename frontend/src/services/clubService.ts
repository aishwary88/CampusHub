import api from './api';

export const clubService = {
  getAllClubs: async () => {
    const response = await api.get('/api/clubs');
    return response.data;
  },

  getClubById: async (id: string) => {
    const response = await api.get(`/api/clubs/${id}`);
    return response.data;
  },

  createClub: async (clubData: any) => {
    const response = await api.post('/api/clubs', clubData);
    return response.data;
  },

  updateClub: async (id: string, clubData: any) => {
    const response = await api.put(`/api/clubs/${id}`, clubData);
    return response.data;
  },

  deleteClub: async (id: string) => {
    const response = await api.delete(`/api/clubs/${id}`);
    return response.data;
  },

  joinClub: async (id: string) => {
    const response = await api.post(`/api/clubs/${id}/join`);
    return response.data;
  },

  leaveClub: async (id: string) => {
    const response = await api.post(`/api/clubs/${id}/leave`);
    return response.data;
  },
};

export default clubService;
