import api from './api';

export const postService = {
  getAllPosts: async () => {
    const response = await api.get('/api/posts');
    return response.data;
  },

  getPostById: async (id: string) => {
    const response = await api.get(`/api/posts/${id}`);
    return response.data;
  },

  createPost: async (postData: any) => {
    const response = await api.post('/api/posts', postData);
    return response.data;
  },

  updatePost: async (id: string, postData: any) => {
    const response = await api.put(`/api/posts/${id}`, postData);
    return response.data;
  },

  deletePost: async (id: string) => {
    const response = await api.delete(`/api/posts/${id}`);
    return response.data;
  },
};

export default postService;
