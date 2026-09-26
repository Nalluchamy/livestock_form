import { apiClient } from './api';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: 'FARMER' | 'EXPERT_GRADER' | 'SENIOR_REVIEWER' | 'ADMIN';
  is_active: boolean;
  is_verified: boolean;
  created_at?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: UserProfile;
}

export async function loginUser(username_or_email: string, password: string): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', {
    username_or_email,
    password,
  });
  return response.data;
}

export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  return response.data;
}

export async function logoutUser(refreshToken?: string): Promise<void> {
  await apiClient.post('/auth/logout', {
    refresh_token: refreshToken,
  });
}

export async function getCurrentUserProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/auth/me');
  return response.data;
}

export async function registerUser(payload: {
  username: string;
  email: string;
  password: string;
  role?: string;
}): Promise<UserProfile> {
  const response = await apiClient.post<UserProfile>('/auth/register', payload);
  return response.data;
}

export async function requestPasswordReset(username_or_email: string): Promise<{ message: string; reset_token?: string }> {
  const response = await apiClient.post('/auth/forgot-password', {
    username_or_email,
  });
  return response.data;
}

export async function confirmPasswordReset(token: string, new_password: string): Promise<UserProfile> {
  const response = await apiClient.post<UserProfile>('/auth/reset-password', {
    token,
    new_password,
  });
  return response.data;
}
