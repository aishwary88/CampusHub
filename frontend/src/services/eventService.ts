import api from './api';

export const eventService = {
  getAllEvents: async () => {
    const response = await api.get('/api/events');
    return response.data;
  },

  getEventById: async (id: string) => {
    const response = await api.get(`/api/events/${id}`);
    return response.data;
  },

  createEvent: async (eventData: any) => {
    const response = await api.post('/api/events', eventData);
    return response.data;
  },

  updateEvent: async (id: string, eventData: any) => {
    const response = await api.put(`/api/events/${id}`, eventData);
    return response.data;
  },

  deleteEvent: async (id: string) => {
    const response = await api.delete(`/api/events/${id}`);
    return response.data;
  },

  rsvpEvent: async (id: string) => {
    const response = await api.post(`/api/events/${id}/rsvp`);
    return response.data;
  },

  cancelRsvp: async (id: string) => {
    const response = await api.delete(`/api/events/${id}/rsvp`);
    return response.data;
  },
};

export default eventService;
