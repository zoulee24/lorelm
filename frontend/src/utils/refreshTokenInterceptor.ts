import useUserStore from "@/store/user";
import request from "./request";
import type { JwtToken } from "@/schemas/base";
import { ElMessage } from "element-plus";

type RequestQueueItem = {
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
  config: RequestInfo & { _retry?: boolean, url: string };
};

let isRefreshing = false;
let failedRequestsQueue: RequestQueueItem[] = [];


const refresh_token = () => {
  const user_store = useUserStore();
  return request.post<JwtToken>('/auth/token/refresh', { 
    token: `${user_store.token!.token_type} ${user_store.token!.refresh_token}` 
  }).then(rsp => (user_store.setToken(rsp))).catch(() => {
    ElMessage.warning('登录信息已失效，请重新登录！')
    user_store.logout()
  })
}


// 重新发送原始请求
async function retryOriginalRequest(
  originalConfig: RequestInit & { _retry?: boolean, url: string }
): Promise<any> {
  const user_store = useUserStore();
  const headers = new Headers(originalConfig?.headers);
  if (user_store.isLogined) {
    headers.set(user_store.token!.token_type ?? 'Authorization', user_store.token!.refresh_token);
  }

  const retryConfig = {
    ...originalConfig,
    headers,
  };

  return fetch(retryConfig.url, retryConfig);
}


(function () {
  const originalFetch = window.fetch;

  window.fetch = async function (input: string | URL | globalThis.Request, init?: RequestInit): Promise<Response> {
    const headers = new Headers(init?.headers);

    if (input.toString().startsWith(import.meta.env.VITE_API_BASE_URL)) {
      const user_store = useUserStore();
      if (user_store.isLogined && !headers.has('Authorization')) {
        headers.set('Authorization', `${user_store.token!.token_type} ${user_store.token!.access_token}`);
      }
    }
    const config = {
      ...init,
      headers,
      url: input instanceof Request ? input.url : input.toString(),
    } as RequestInfo & { _retry?: boolean, url: string };

    try {
      const response = await originalFetch(input, {
        ...init,
        headers,
      });
      // 成功则直接返回
      if (response.status !== 401) {
        return response;
      }
      // 如果是 token 失效，进入刷新流程
      if (!config._retry) {
        config._retry = true;

        const retryPromise = new Promise<Response>((resolve, reject) => {
          failedRequestsQueue.push({
            resolve,
            reject,
            config,
          });
        });

        if (!isRefreshing) {
          isRefreshing = true;

          try {
            await refresh_token();
            isRefreshing = false;

            // 重放队列中的请求
            failedRequestsQueue.forEach(({ resolve, config }) => {
              retryOriginalRequest(config).then(resolve);
            });

            failedRequestsQueue = [];
          } catch (error) {
            isRefreshing = false;
            failedRequestsQueue.forEach(({ reject }) => {
              reject(error);
            });
            failedRequestsQueue = [];
            throw error;
          }
        }

        return retryPromise;
      }

      return response;

    } catch (err) {
      console.error('Fetch error:', err);
      throw err;
    }
  }

})();