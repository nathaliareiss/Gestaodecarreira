import { apiFetch, parseApiResponse } from "@/shared/api/client"

import type {
  TipoEscalaTrabalho,
  VacationPeriod,
  WorkCalendarEvent,
  WorkCalendarOverride,
  WorkSchedule,
} from "./calendario.model"

type WorkSchedulePayload = {
  name: string
  schedule_type: TipoEscalaTrabalho
  anchor_date: string
  working_weekdays: number[]
  custom_pattern: boolean[]
  note: string | null
  is_active: boolean
}

type VacationPayload = {
  title: string
  start_date: string
  end_date: string
  note: string | null
}

type CalendarOverridePayload = {
  override_date: string
  is_working_day: boolean
  title: string
  note: string | null
}

function numeroSeguro(valor: unknown, padrao = 0) {
  const numero = typeof valor === "number" ? valor : Number(valor)
  return Number.isFinite(numero) ? numero : padrao
}

function stringSegura(valor: unknown, padrao = "") {
  return typeof valor === "string" ? valor : padrao
}

function booleanoSeguro(valor: unknown, padrao = false) {
  return typeof valor === "boolean" ? valor : padrao
}

function listaDeNumerosSegura(valor: unknown) {
  if (!Array.isArray(valor)) {
    return []
  }

  return valor
    .map((item) => Number(item))
    .filter((item) => Number.isInteger(item) && item >= 0)
}

function listaDeBooleanosSegura(valor: unknown) {
  if (!Array.isArray(valor)) {
    return []
  }

  return valor.map((item) => Boolean(item))
}

function categoriaSegura(valor: unknown): WorkCalendarEvent["category"] {
  switch (valor) {
    case "work":
    case "off":
    case "vacation":
    case "holiday":
    case "exception":
      return valor
    default:
      return "off"
  }
}

function tipoEscalaSeguro(valor: unknown): TipoEscalaTrabalho {
  switch (valor) {
    case "12x36":
    case "24x72":
    case "5x2":
    case "custom":
      return valor
    default:
      return "5x2"
  }
}

function normalizarEscala(resposta: Partial<WorkSchedule> | null | undefined): WorkSchedule {
  return {
    id: numeroSeguro(resposta?.id),
    user_id: numeroSeguro(resposta?.user_id),
    name: stringSegura(resposta?.name),
    schedule_type: tipoEscalaSeguro(resposta?.schedule_type),
    anchor_date: stringSegura(resposta?.anchor_date),
    working_weekdays: listaDeNumerosSegura(resposta?.working_weekdays),
    custom_pattern: listaDeBooleanosSegura(resposta?.custom_pattern),
    note: typeof resposta?.note === "string" ? resposta.note : null,
    is_active: booleanoSeguro(resposta?.is_active, true),
    created_at: stringSegura(resposta?.created_at),
    updated_at: stringSegura(resposta?.updated_at),
  }
}

function normalizarFerias(resposta: Partial<VacationPeriod> | null | undefined): VacationPeriod {
  return {
    id: numeroSeguro(resposta?.id),
    user_id: numeroSeguro(resposta?.user_id),
    title: stringSegura(resposta?.title),
    start_date: stringSegura(resposta?.start_date),
    end_date: stringSegura(resposta?.end_date),
    note: typeof resposta?.note === "string" ? resposta.note : null,
    created_at: stringSegura(resposta?.created_at),
    updated_at: stringSegura(resposta?.updated_at),
  }
}

function normalizarExcecao(
  resposta: Partial<WorkCalendarOverride> | null | undefined,
): WorkCalendarOverride {
  return {
    id: numeroSeguro(resposta?.id),
    user_id: numeroSeguro(resposta?.user_id),
    override_date: stringSegura(resposta?.override_date),
    is_working_day: booleanoSeguro(resposta?.is_working_day),
    title: stringSegura(resposta?.title),
    note: typeof resposta?.note === "string" ? resposta.note : null,
    created_at: stringSegura(resposta?.created_at),
    updated_at: stringSegura(resposta?.updated_at),
  }
}

function normalizarEvento(resposta: Partial<WorkCalendarEvent> | null | undefined): WorkCalendarEvent {
  return {
    id: stringSegura(resposta?.id),
    title: stringSegura(resposta?.title),
    start: stringSegura(resposta?.start),
    end: stringSegura(resposta?.end),
    all_day: booleanoSeguro(resposta?.all_day, true),
    category: categoriaSegura(resposta?.category),
    color: stringSegura(resposta?.color, "#94a3b8"),
    text_color: stringSegura(resposta?.text_color, "#08111d"),
    source: stringSegura(resposta?.source),
    is_working_day: booleanoSeguro(resposta?.is_working_day),
  }
}

export async function criarEscalaTrabalho(payload: WorkSchedulePayload): Promise<WorkSchedule> {
  const response = await apiFetch("/api/work-schedules", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  const dados = await parseApiResponse<Partial<WorkSchedule> | null>(
    response,
    "Nao foi possivel salvar a escala de trabalho.",
  )

  return normalizarEscala(dados)
}

export async function listarEscalasTrabalho(): Promise<WorkSchedule[]> {
  const response = await apiFetch("/api/work-schedules", {
    method: "GET",
  })

  const dados = await parseApiResponse<Array<Partial<WorkSchedule>> | null>(
    response,
    "Nao foi possivel carregar as escalas de trabalho.",
  )

  return Array.isArray(dados) ? dados.map((item) => normalizarEscala(item)) : []
}

export async function criarFerias(payload: VacationPayload): Promise<VacationPeriod> {
  const response = await apiFetch("/api/vacations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  const dados = await parseApiResponse<Partial<VacationPeriod> | null>(
    response,
    "Nao foi possivel salvar as ferias.",
  )

  return normalizarFerias(dados)
}

export async function listarFerias(): Promise<VacationPeriod[]> {
  const response = await apiFetch("/api/vacations", {
    method: "GET",
  })

  const dados = await parseApiResponse<Array<Partial<VacationPeriod>> | null>(
    response,
    "Nao foi possivel carregar os periodos de ferias.",
  )

  return Array.isArray(dados) ? dados.map((item) => normalizarFerias(item)) : []
}

export async function criarExcecaoCalendario(
  payload: CalendarOverridePayload,
): Promise<WorkCalendarOverride> {
  const response = await apiFetch("/api/calendar-overrides", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  const dados = await parseApiResponse<Partial<WorkCalendarOverride> | null>(
    response,
    "Nao foi possivel salvar a excecao manual.",
  )

  return normalizarExcecao(dados)
}

export async function listarExcecoesCalendario(): Promise<WorkCalendarOverride[]> {
  const response = await apiFetch("/api/calendar-overrides", {
    method: "GET",
  })

  const dados = await parseApiResponse<Array<Partial<WorkCalendarOverride>> | null>(
    response,
    "Nao foi possivel carregar as excecoes do calendario.",
  )

  return Array.isArray(dados) ? dados.map((item) => normalizarExcecao(item)) : []
}

export async function listarEventosCalendario(
  start: string,
  end: string,
): Promise<WorkCalendarEvent[]> {
  const response = await apiFetch(`/api/calendar/events?start=${start}&end=${end}`, {
    method: "GET",
  })

  const dados = await parseApiResponse<Array<Partial<WorkCalendarEvent>> | null>(
    response,
    "Nao foi possivel carregar os eventos do calendario.",
  )

  return Array.isArray(dados) ? dados.map((item) => normalizarEvento(item)) : []
}
