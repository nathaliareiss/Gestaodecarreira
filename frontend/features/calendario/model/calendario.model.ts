export type TipoEscalaTrabalho = "12x36" | "24x72" | "5x2" | "custom"
export type TipoFerias = "regular" | "premium"

export type WorkSchedule = {
  id: number
  user_id: number
  name: string
  schedule_type: TipoEscalaTrabalho
  anchor_date: string
  state_code: string | null
  city_name: string | null
  working_weekdays: number[]
  custom_pattern: boolean[]
  note: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type VacationPeriod = {
  id: number
  user_id: number
  title: string
  vacation_type: TipoFerias
  start_date: string
  end_date: string
  requested_days: number | null
  counted_days: number | null
  note: string | null
  created_at: string
  updated_at: string
}

export type WorkCalendarOverride = {
  id: number
  user_id: number
  override_date: string
  is_working_day: boolean
  title: string
  note: string | null
  created_at: string
  updated_at: string
}

export type WorkCalendarEventCategory =
  | "work"
  | "off"
  | "vacation"
  | "premium_vacation"
  | "holiday"
  | "exception"

export type WorkCalendarEvent = {
  id: string
  title: string
  start: string
  end: string
  all_day: boolean
  category: WorkCalendarEventCategory
  color: string
  text_color: string
  source: string
  is_working_day: boolean
}
