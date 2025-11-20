import axios from 'axios';

// Configuración base de axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========== PRODUCTS ==========

export const getProducts = async (params = {}) => {
  const response = await api.get('/products/', { params });
  return response.data;
};

export const getProduct = async (id) => {
  const response = await api.get(`/products/${id}/`);
  return response.data;
};

export const searchProducts = async (query) => {
  const response = await api.get('/products/search/', {
    params: { q: query },
  });
  return response.data;
};

export const getProductAlternatives = async (id) => {
  const response = await api.get(`/products/${id}/alternatives/`);
  return response.data;
};

export const scanBarcode = async (barcode) => {
  const response = await api.post('/products/scan/', { barcode });
  return response.data;
};

// ========== SHOPPING LISTS ==========

export const getShoppingLists = async () => {
  const response = await api.get('/shopping-lists/');
  return response.data;
};

export const getShoppingList = async (id) => {
  const response = await api.get(`/shopping-lists/${id}/`);
  return response.data;
};

export const createShoppingList = async (data) => {
  const response = await api.post('/shopping-lists/', data);
  return response.data;
};

export const addItemToList = async (listId, productId, quantity) => {
  const response = await api.post(`/shopping-lists/${listId}/add-item/`, {
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const removeItemFromList = async (listId, itemId) => {
  const response = await api.delete(`/shopping-lists/${listId}/remove-item/`, {
    data: { item_id: itemId },
  });
  return response.data;
};

export const optimizeShoppingList = async (items, budget) => {
  const response = await api.post('/shopping-lists/optimize/', {
    items,
    budget,
  });
  return response.data;
};

// ========== STATS ==========

export const getStats = async () => {
  const response = await api.get('/stats/summary/');
  return response.data;
};

export default api;