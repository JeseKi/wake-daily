import api from './api'
import type {
  OAuthAuthorizeConfirmPayload,
  OAuthAuthorizeMetadata,
  OAuthAuthorizeResult,
  OAuthDeviceAuthorizationConfirmPayload,
  OAuthDeviceAuthorizationMetadata,
  OAuthDeviceAuthorizationResult,
} from './types'

export async function fetchOAuthAuthorizeMetadata(params: URLSearchParams): Promise<OAuthAuthorizeMetadata> {
  const { data } = await api.get<OAuthAuthorizeMetadata>('/oauth-provider/authorize/metadata', {
    params: Object.fromEntries(params.entries()),
  })
  return data
}

export async function confirmOAuthAuthorize(
  payload: OAuthAuthorizeConfirmPayload,
): Promise<OAuthAuthorizeResult> {
  const { data } = await api.post<OAuthAuthorizeResult>('/oauth-provider/authorize', payload)
  return data
}

export async function fetchOAuthDeviceAuthorizationMetadata(
  userCode: string,
): Promise<OAuthDeviceAuthorizationMetadata> {
  const { data } = await api.get<OAuthDeviceAuthorizationMetadata>('/oauth-provider/device/metadata', {
    params: { user_code: userCode },
  })
  return data
}

export async function confirmOAuthDeviceAuthorization(
  payload: OAuthDeviceAuthorizationConfirmPayload,
): Promise<OAuthDeviceAuthorizationResult> {
  const { data } = await api.post<OAuthDeviceAuthorizationResult>('/oauth-provider/device/authorize', payload)
  return data
}
