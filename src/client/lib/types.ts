export interface TokenResponse {
  access_token: string
  token_type: string
  scope: string
}

export interface MessageResponse {
  message: string
}

export interface LoginChallengeResponse {
  requires_2fa: true
  challenge_token: string
  challenge_type: 'totp'
}

export type LoginResponse = TokenResponse | LoginChallengeResponse

export type OAuthProviderName = 'GITHUB' | 'GOOGLE'

export interface OAuthProviderInfo {
  provider: OAuthProviderName
  label: string
}

export interface OAuthProvidersResponse {
  providers: OAuthProviderInfo[]
}

export interface OAuthTicketExchangePayload {
  ticket: string
}

export interface OAuthAuthorizeMetadata {
  client_id: string
  client_name: string
  redirect_uri: string
  permissions: OAuthPermission[]
  state: string | null
}

export interface OAuthPermission {
  scope: string
  title: string
  description: string
}

export interface OAuthAuthorizeConfirmPayload {
  response_type: string
  client_id: string
  redirect_uri: string
  scope: string
  state?: string | null
  code_challenge: string
  code_challenge_method: string
  approve: boolean
}

export interface OAuthAuthorizeResult {
  redirect_url: string
}

export interface OAuthDeviceAuthorizationMetadata {
  client_id: string
  client_name: string
  user_code: string
  permissions: OAuthPermission[]
  expires_at: string
}

export interface OAuthDeviceAuthorizationConfirmPayload {
  user_code: string
  approve: boolean
}

export interface OAuthDeviceAuthorizationResult {
  status: 'approved' | 'denied'
}

export interface AuthTokens {
  accessToken: string
}

export type UserRole = 'user' | 'admin'

export type UserStatus = 'active' | 'inactive'

export interface UserProfile {
  id: number
  username: string
  email: string
  name: string | null
  role: UserRole
  status: UserStatus
}

export interface LoginPayload {
  username: string
  password: string
  turnstile_token?: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface VerificationCodePayload {
  email: string
  turnstile_token?: string
}

export interface RegisterWithCodePayload {
  username: string
  email: string
  password: string
  code: string
  turnstile_token?: string
}

export interface UpdateProfilePayload {
  username?: string | null
  name?: string | null
}

export interface PasswordResetLinkPayload {
  email: string
  turnstile_token?: string
}

export interface PasswordResetWithTokenPayload {
  token: string
  new_password: string
}

export interface EmailChangeCodePayload {
  email: string
}

export interface EmailChangeConfirmPayload {
  email: string
  code: string
}

export interface PasswordChangeConfirmPayload {
  token: string
  new_password: string
}

export interface AdminUser {
  id: number
  username: string
  email: string
  name: string | null
  role: UserRole
  status: UserStatus
  scope_overrides: string[] | null
  effective_scopes: string[]
  available_scopes: string[]
  created_at: string
}

export interface AdminUserCreatePayload {
  username: string
  email: string
  name?: string | null
  role?: UserRole
  status?: UserStatus
  password: string
}

export interface AdminUserUpdatePayload {
  username?: string | null
  email?: string | null
  name?: string | null
  role?: UserRole
  status?: UserStatus
  password?: string | null
}

export interface AdminUserScopesUpdatePayload {
  scopes: string[]
}

export type ScopeCategory = 'normal' | 'sensitive' | 'dangerous'

export interface AdminScope {
  id: number
  scope: string
  title: string
  description: string
  category: ScopeCategory
  created_at: string
  updated_at: string
}

export interface AdminScopeUpdatePayload {
  category: ScopeCategory
}

export interface DailyQuestion {
  id: number
  content: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface DailyQuestionPayload {
  content: string
  is_active: boolean
  sort_order: number
}

export interface DailyQuestionUpdatePayload {
  content?: string
  is_active?: boolean
  sort_order?: number
}

export interface JournalEntryPayload {
  question_id: number
  content: string
}

export interface AttachmentMatch {
  word: string
  start: number
  end: number
}

export interface JournalEntry {
  id: number
  user_id: number
  question_id: number
  question_content: string
  content: string
  created_at: string
  updated_at: string
  attachment_matches: AttachmentMatch[]
  relief_count: number
  has_relief_feedback: boolean
}

export interface ReliefFeedback {
  entry_id: number
  relief_count: number
  has_relief_feedback: boolean
}

export interface ItemPayload {
  name: string
}

export interface Item {
  id: number
  name: string
}

export type AsyncTaskStatus = 'pending' | 'running' | 'completed' | 'failed'

export type AsyncTaskLogLevel = 'info' | 'warning' | 'error'

export interface AsyncTaskPayload {
  name: string
  total_count: number
  fail_every: number
  delay_ms: number
}

export interface AsyncTaskLog {
  id: number
  sequence: number
  level: AsyncTaskLogLevel
  message: string
  created_at: string
}

export interface AsyncTask {
  id: number
  name: string
  status: AsyncTaskStatus
  total_count: number
  processed_count: number
  success_count: number
  failure_count: number
  progress_percent: number
  fail_every: number
  delay_ms: number
  last_message: string | null
  requested_by_user_id: number | null
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface AsyncTaskDetail extends AsyncTask {
  logs: AsyncTaskLog[]
}
