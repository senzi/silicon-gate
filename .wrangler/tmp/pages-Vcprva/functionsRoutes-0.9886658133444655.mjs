import { onRequestPost as __api_verify_js_onRequestPost } from "D:\\My_Project\\silicon-gate\\functions\\api\\verify.js"

export const routes = [
    {
      routePath: "/api/verify",
      mountPath: "/api",
      method: "POST",
      middlewares: [],
      modules: [__api_verify_js_onRequestPost],
    },
  ]