import { ElMessage } from 'element-plus'
import { ContentTypeEnum } from './request.types';


type METHODS = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

type RequestParams = {
  method?: METHODS;           // 请求方法，默认为 GET
  params?: object;            // 请求参数，默认为空对象
  body?: object | object[] | string;   // 请求体，默认为空对象
  token?: string;             // 令牌，默认为空字符串
  timeout?: number;           // 超时时间，单位：秒
  parse?: boolean;            // 是否解析响应体，默认为 true
  // stream?: boolean;           // 是否流式处理响应，默认为 false
  form?: FormData;               // 是否使用表单数据
  blob?: boolean;               // 是否返回文件流
  base_url?: string;
};

const success_code = 0;

interface SuccessResponse<T> {
  code: 0;
  message: string;
  data: T;
}

interface ErrorResponse {
  code: number;
  message: string;
  data: any;
}

export type ResponseInfo<T> = SuccessResponse<T> | ErrorResponse;

function buildQueryParams(params: Record<string, any>): string {
  return Object.keys(params).filter(key => (params[key] !== undefined && params[key] !== null))
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');
}

const buildRequestUrl = (url: string, params: Record<string, any> | null | undefined) =>
  params && Object.keys(params).length > 0 ? `${url}?${buildQueryParams(params!)}` : url;

const request = <T = any>(endpoint: string, params?: RequestParams) => new Promise<T>((resolve, reject) => {
  const timeout = (params?.timeout ?? 10) * 1000;
  const controller = new AbortController();
  const timer = setTimeout(() => {
    controller.abort();
  }, timeout);

  let url: string;
  if (endpoint.startsWith('http')) {
    url = endpoint;
  } else {
    url = (params?.base_url ?? import.meta.env.VITE_API_BASE_URL) + endpoint;
  }

  let content_type: string | null = null;
  if (!params?.form) {
    content_type = params?.body ? ContentTypeEnum.JSON : ContentTypeEnum.TEXT
  }

  const headers = new Headers();
  if (content_type) headers.append('Content-Type', content_type);
  if (params?.token) headers.append('Authorization', params.token);

  const body = params ? params.form ?? JSON.stringify(params.body) : null

  return fetch(buildRequestUrl(url, params?.params), {
    method: params?.method || 'GET',
    headers,
    body,
    signal: controller.signal,
  }).then(res => {
    if (res.ok) {
      if (params?.blob === true) {
        return res.blob()
      } else {
        if (params?.parse === false) resolve(res.body as T);
        else return res.json();
      }
    } else if (res.status === 401) {

    } else {
      ElMessage.error('请求失败');
      reject(res.body);
    }
  }).then((res: ResponseInfo<T> | Blob) => {
    // 判断是不是文件流
    if (res instanceof Blob) resolve(res as T)
    else if (res.code === success_code) resolve(res.data as T);
    else {
      ElMessage.error(res.message ?? '服务器异常！')
      return reject(res)
    }
  }).catch(reject).finally(() => clearTimeout(timer));
});

interface SteamResponse<T = string> {
  type: "message" | string;
  data: T;
}


async function* stream<T>(endpoint: string, params?: RequestParams): AsyncIterable<SteamResponse<T>> {
  const decoder = new TextDecoder('utf-8');
  try {
    const res = await request<ReadableStream<Uint8Array<ArrayBufferLike>>>(endpoint, { ...params, parse: false })
    const reader = res?.getReader();

    if (!reader) {
      throw new Error('流式响应不可用');
    }
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value);

      if (!buffer.endsWith('\n\n')) continue;

      const events = buffer.split('\n\n')
      buffer = events.pop() || '';

      for (const it of events) {
        const lines = it.split('\n')
        let event: string = 'message';
        let rsp_data: string = '';
        for (const line of lines) {
          if (line.startsWith('event:')) {
            event = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            // 支持多行数据
            rsp_data = line.slice(5).trim();
          }
        }
        yield {
          type: event,
          data: (params?.parse && rsp_data ? JSON.parse(rsp_data) : rsp_data) as T,
        }
      }
    }
  } catch (err) {
    console.error('流式请求出错:', err);
    throw err;
  }
  // }
}


// 封装 GET/POST/PUT/DELETE 方法
export default {
  get<T>(endpoint: string, config?: RequestParams): Promise<T> {
    return request(endpoint, { ...config, method: 'GET' })
  },
  post<T>(endpoint: string, config?: RequestParams): Promise<T> {
    return request(endpoint, { ...config, method: 'POST' })
  },
  put<T>(endpoint: string, config?: RequestParams): Promise<T> {
    return request(endpoint, { ...config, method: 'PUT' })
  },
  delete<T>(endpoint: string, config?: RequestParams): Promise<T> {
    return request(endpoint, { ...config, method: 'DELETE' })
  },
  patch<T>(endpoint: string, config?: RequestParams): Promise<T> {
    return request(endpoint, { ...config, method: 'PATCH' })
  },
  request,
  stream,
}