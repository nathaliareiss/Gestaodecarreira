import { obterApiBaseUrl } from "@/shared/config/api"

const METODOS_PERMITIDOS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

function montarUrlBackend(caminhos: string[], urlOrigem: URL) {
  const urlBackend = new URL(obterApiBaseUrl())
  urlBackend.pathname = `/api/${caminhos.join("/")}`
  urlBackend.search = urlOrigem.search
  return urlBackend
}

async function encaminharRequisicao(
  request: Request,
  params: { path?: string[] },
): Promise<Response> {
  const caminhos = params.path ?? []
  const urlBackend = montarUrlBackend(caminhos, new URL(request.url))
  const headers = new Headers(request.headers)

  headers.delete("host")
  headers.delete("content-length")
  headers.delete("connection")
  headers.delete("accept-encoding")

  const temCorpo = !["GET", "HEAD"].includes(request.method)
  const corpo = temCorpo ? await request.arrayBuffer() : undefined

  const respostaBackend = await fetch(urlBackend, {
    method: request.method,
    headers,
    body: corpo,
    cache: "no-store",
    redirect: "manual",
  })

  return new Response(respostaBackend.body, {
    status: respostaBackend.status,
    statusText: respostaBackend.statusText,
    headers: respostaBackend.headers,
  })
}

export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      Allow: METODOS_PERMITIDOS.join(", "),
    },
  })
}

export async function GET(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  return encaminharRequisicao(request, await context.params)
}

export async function POST(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  return encaminharRequisicao(request, await context.params)
}

export async function PUT(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  return encaminharRequisicao(request, await context.params)
}

export async function PATCH(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  return encaminharRequisicao(request, await context.params)
}

export async function DELETE(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  return encaminharRequisicao(request, await context.params)
}
