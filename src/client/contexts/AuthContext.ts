import { createContext } from 'react'
import type {
  EmailChangeCodePayload,
  EmailChangeConfirmPayload,
  LoginResponse,
  LoginPayload,
  MessageResponse,
  OAuthTicketExchangePayload,
  PasswordChangeConfirmPayload,
  PasswordResetLinkPayload,
  PasswordResetWithTokenPayload,
  RegisterWithCodePayload,
  UpdateProfilePayload,
  UserProfile,
  VerificationCodePayload,
} from '../lib/types'

export interface AuthContextValue {
  user: UserProfile | null
  loading: boolean
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<LoginResponse>
  exchangeOAuthTicket: (payload: OAuthTicketExchangePayload) => Promise<LoginResponse>
  register: (payload: RegisterWithCodePayload) => Promise<UserProfile>
  registerWithCode: (payload: RegisterWithCodePayload) => Promise<UserProfile>
  sendVerificationCode: (payload: VerificationCodePayload) => Promise<{ message: string }>
  sendPasswordResetLink: (payload: PasswordResetLinkPayload) => Promise<{ message: string }>
  resetPasswordWithToken: (payload: PasswordResetWithTokenPayload) => Promise<{ message: string }>
  sendEmailChangeCode: (payload: EmailChangeCodePayload) => Promise<{ message: string }>
  confirmEmailChange: (payload: EmailChangeConfirmPayload) => Promise<UserProfile>
  sendPasswordChangeLink: () => Promise<{ message: string }>
  confirmPasswordChange: (payload: PasswordChangeConfirmPayload) => Promise<{ message: string }>
  refreshProfile: () => Promise<UserProfile | null>
  logout: () => Promise<void>
  logoutAllDevices: () => Promise<MessageResponse>
  update: (payload: UpdateProfilePayload) => Promise<UserProfile>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export { AuthContext }
