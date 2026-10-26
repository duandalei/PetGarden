export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

interface ErrorBody {
  error?: { code?: string; message?: string }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, init)
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', '连接中断，请检查服务是否运行。')
  }
  if (res.status === 204) {
    return undefined as T
  }
  const data = (await res.json().catch(() => null)) as (ErrorBody & T) | null
  if (!res.ok) {
    const code = data?.error?.code ?? 'UNKNOWN'
    const message = data?.error?.message ?? '请求失败，请稍后再试。'
    throw new ApiError(res.status, code, message)
  }
  return data as T
}

function jsonInit(method: string, body?: unknown): RequestInit {
  return {
    method,
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) => request<T>(path, jsonInit('POST', body)),
  patch: <T>(path: string, body?: unknown) => request<T>(path, jsonInit('PATCH', body)),
  delete: <T>(path: string, body?: unknown) => request<T>(path, jsonInit('DELETE', body)),
}