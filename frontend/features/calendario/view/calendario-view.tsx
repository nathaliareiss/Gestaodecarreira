"use client"

import dayGridPlugin from "@fullcalendar/daygrid"
import interactionPlugin from "@fullcalendar/interaction"
import FullCalendar from "@fullcalendar/react"
import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react"

import { ApiResponseError } from "@/shared/api/client"
import { useLanguage } from "@/shared/i18n/language-provider"
import type {
  TipoEscalaTrabalho,
  VacationPeriod,
  WorkCalendarEvent,
  WorkCalendarOverride,
  WorkSchedule,
} from "../model/calendario.model"
import {
  criarEscalaTrabalho,
  criarExcecaoCalendario,
  criarFerias,
  listarEscalasTrabalho,
  listarEventosCalendario,
  listarExcecoesCalendario,
  listarFerias,
} from "../model/calendario.repository"

type CalendarioViewProps = {
  modoDemo: boolean
}

type IntervaloCalendario = {
  start: string
  end: string
}

type Labels = {
  title: string
  subtitle: string
  scheduleTitle: string
  vacationTitle: string
  overrideTitle: string
  currentSchedule: string
  activeSchedule: string
  noSchedules: string
  noVacations: string
  noOverrides: string
  scheduleName: string
  scheduleType: string
  anchorDate: string
  weekdays: string
  customPattern: string
  note: string
  activateNow: string
  saveSchedule: string
  saving: string
  vacationLabel: string
  vacationStart: string
  vacationEnd: string
  saveVacation: string
  overrideDate: string
  overrideMode: string
  overrideWork: string
  overrideOff: string
  overrideReason: string
  saveOverride: string
  calendarTitle: string
  calendarSubtitle: string
  loading: string
  refreshError: string
  demoOnly: string
  work: string
  off: string
  vacation: string
  holiday: string
  exception: string
  today: string
  month: string
  dayNames: string[]
  scheduleOptions: Record<TipoEscalaTrabalho, string>
  patternHint: string
}

const WEEKDAY_OPTIONS = [
  { value: 0, pt: "Seg", en: "Mon" },
  { value: 1, pt: "Ter", en: "Tue" },
  { value: 2, pt: "Qua", en: "Wed" },
  { value: 3, pt: "Qui", en: "Thu" },
  { value: 4, pt: "Sex", en: "Fri" },
  { value: 5, pt: "Sab", en: "Sat" },
  { value: 6, pt: "Dom", en: "Sun" },
] as const

function hojeISO() {
  return new Date().toISOString().slice(0, 10)
}

function deslocarDataISO(dataISO: string, dias: number) {
  const data = new Date(`${dataISO}T00:00:00Z`)
  data.setUTCDate(data.getUTCDate() + dias)
  return data.toISOString().slice(0, 10)
}

function intervaloMesAtual(): IntervaloCalendario {
  const hoje = new Date()
  const inicio = new Date(Date.UTC(hoje.getUTCFullYear(), hoje.getUTCMonth(), 1))
  const fim = new Date(Date.UTC(hoje.getUTCFullYear(), hoje.getUTCMonth() + 1, 0))
  return {
    start: inicio.toISOString().slice(0, 10),
    end: fim.toISOString().slice(0, 10),
  }
}

function formatarErro(error: unknown, fallback: string) {
  if (error instanceof ApiResponseError) {
    return error.message
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message
  }

  return fallback
}

function parsePadraoPersonalizado(valor: string) {
  return valor
    .split(/[,\s]+/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
    .map((item) => {
      if (item === "1") {
        return true
      }
      if (item === "0") {
        return false
      }
      throw new Error("Use apenas 1 para trabalho e 0 para folga no padrao personalizado.")
    })
}

function formatarDataISO(valor: string, language: "pt-BR" | "en") {
  if (!valor) {
    return "-"
  }

  const data = new Date(`${valor}T00:00:00Z`)
  return new Intl.DateTimeFormat(language === "en" ? "en-US" : "pt-BR", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(data)
}

function formatarDiasSemana(workingWeekdays: number[], labels: Labels) {
  if (workingWeekdays.length === 0) {
    return "-"
  }

  const map = new Map(WEEKDAY_OPTIONS.map((item) => [item.value, labels.dayNames[item.value] ?? String(item.value)]))
  return workingWeekdays.map((item) => map.get(item) ?? String(item)).join(", ")
}

function labelsPorIdioma(language: "pt-BR" | "en"): Labels {
  if (language === "en") {
    return {
      title: "Work calendar",
      subtitle: "Manage your work rotation, vacations, manual exceptions, and monthly visibility in one place.",
      scheduleTitle: "Work schedule",
      vacationTitle: "Vacations",
      overrideTitle: "Manual exceptions",
      currentSchedule: "Saved schedules",
      activeSchedule: "Active",
      noSchedules: "No schedule saved yet.",
      noVacations: "No vacations saved yet.",
      noOverrides: "No manual exceptions saved yet.",
      scheduleName: "Schedule name",
      scheduleType: "Rotation type",
      anchorDate: "Anchor date",
      weekdays: "Working weekdays",
      customPattern: "Custom pattern",
      note: "Notes",
      activateNow: "Set as active schedule",
      saveSchedule: "Save schedule",
      saving: "Saving...",
      vacationLabel: "Vacation title",
      vacationStart: "Start date",
      vacationEnd: "End date",
      saveVacation: "Save vacation",
      overrideDate: "Exception date",
      overrideMode: "Override type",
      overrideWork: "Working day",
      overrideOff: "Day off",
      overrideReason: "Reason",
      saveOverride: "Save exception",
      calendarTitle: "Calendar",
      calendarSubtitle: "Colors separate work days, days off, vacations, holidays, and manual changes.",
      loading: "Loading calendar data...",
      refreshError: "We could not load the calendar right now.",
      demoOnly: "Demo mode keeps this module read-only.",
      work: "Shift",
      off: "Day off",
      vacation: "Vacation",
      holiday: "Holiday",
      exception: "Exception",
      today: "Today",
      month: "Month",
      dayNames: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      scheduleOptions: {
        "12x36": "12x36",
        "24x72": "24x72",
        "5x2": "5x2",
        custom: "Custom",
      },
      patternHint: "Use 1 for work and 0 for day off. Example: 1, 0, 1, 0",
    }
  }

  return {
    title: "Calendario de trabalho",
    subtitle: "Gerencie sua escala, ferias, excecoes manuais e a visao mensal em um unico lugar.",
    scheduleTitle: "Escala de trabalho",
    vacationTitle: "Ferias",
    overrideTitle: "Excecoes manuais",
    currentSchedule: "Escalas salvas",
    activeSchedule: "Ativa",
    noSchedules: "Nenhuma escala cadastrada ainda.",
    noVacations: "Nenhum periodo de ferias cadastrado ainda.",
    noOverrides: "Nenhuma excecao manual cadastrada ainda.",
    scheduleName: "Nome da escala",
    scheduleType: "Tipo de escala",
    anchorDate: "Data base",
    weekdays: "Dias de trabalho",
    customPattern: "Padrao personalizado",
    note: "Observacoes",
    activateNow: "Definir como escala ativa",
    saveSchedule: "Salvar escala",
    saving: "Salvando...",
    vacationLabel: "Titulo das ferias",
    vacationStart: "Inicio",
    vacationEnd: "Fim",
    saveVacation: "Salvar ferias",
    overrideDate: "Data da excecao",
    overrideMode: "Tipo de excecao",
    overrideWork: "Marcar como plantao",
    overrideOff: "Marcar como folga",
    overrideReason: "Motivo",
    saveOverride: "Salvar excecao",
    calendarTitle: "Calendario",
    calendarSubtitle: "As cores separam plantao, folga, ferias, feriado e ajustes manuais.",
    loading: "Carregando dados do calendario...",
    refreshError: "Nao foi possivel carregar o calendario agora.",
    demoOnly: "No modo demonstracao, este modulo fica somente para leitura.",
    work: "Plantao",
    off: "Folga",
    vacation: "Ferias",
    holiday: "Feriado",
    exception: "Excecao",
    today: "Hoje",
    month: "Mes",
    dayNames: ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"],
    scheduleOptions: {
      "12x36": "12x36",
      "24x72": "24x72",
      "5x2": "5x2",
      custom: "Personalizada",
    },
    patternHint: "Use 1 para trabalho e 0 para folga. Exemplo: 1, 0, 1, 0",
  }
}

export function CalendarioView({ modoDemo }: CalendarioViewProps) {
  const { language } = useLanguage()
  const labels = useMemo(() => labelsPorIdioma(language), [language])
  const [intervalo, setIntervalo] = useState<IntervaloCalendario>(() => intervaloMesAtual())
  const [escalas, setEscalas] = useState<WorkSchedule[]>([])
  const [ferias, setFerias] = useState<VacationPeriod[]>([])
  const [excecoes, setExcecoes] = useState<WorkCalendarOverride[]>([])
  const [eventos, setEventos] = useState<WorkCalendarEvent[]>([])
  const [carregandoDados, setCarregandoDados] = useState(false)
  const [carregandoEventos, setCarregandoEventos] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [salvando, setSalvando] = useState<"schedule" | "vacation" | "override" | null>(null)

  const [nomeEscala, setNomeEscala] = useState("Escala principal")
  const [tipoEscala, setTipoEscala] = useState<TipoEscalaTrabalho>("12x36")
  const [dataBase, setDataBase] = useState(hojeISO())
  const [diasTrabalho, setDiasTrabalho] = useState<number[]>([0, 1, 2, 3, 4])
  const [padraoPersonalizado, setPadraoPersonalizado] = useState("1, 0")
  const [observacaoEscala, setObservacaoEscala] = useState("")
  const [escalaAtiva, setEscalaAtiva] = useState(true)

  const [tituloFerias, setTituloFerias] = useState(language === "en" ? "Vacation" : "Ferias")
  const [inicioFerias, setInicioFerias] = useState(hojeISO())
  const [fimFerias, setFimFerias] = useState(deslocarDataISO(hojeISO(), 7))
  const [observacaoFerias, setObservacaoFerias] = useState("")

  const [dataExcecao, setDataExcecao] = useState(hojeISO())
  const [excecaoTrabalha, setExcecaoTrabalha] = useState(true)
  const [tituloExcecao, setTituloExcecao] = useState(language === "en" ? "Manual change" : "Ajuste manual")
  const [observacaoExcecao, setObservacaoExcecao] = useState("")

  const carregarCadastros = useCallback(async () => {
    if (modoDemo) {
      setEscalas([])
      setFerias([])
      setExcecoes([])
      return
    }

    setCarregandoDados(true)
    setErro(null)

    try {
      const [escalasResposta, feriasResposta, excecoesResposta] = await Promise.all([
        listarEscalasTrabalho(),
        listarFerias(),
        listarExcecoesCalendario(),
      ])
      setEscalas(escalasResposta)
      setFerias(feriasResposta)
      setExcecoes(excecoesResposta)
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setCarregandoDados(false)
    }
  }, [labels.refreshError, modoDemo])

  const carregarEventos = useCallback(async () => {
    if (modoDemo) {
      setEventos([])
      return
    }

    setCarregandoEventos(true)
    setErro(null)

    try {
      const resposta = await listarEventosCalendario(intervalo.start, intervalo.end)
      setEventos(resposta)
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setCarregandoEventos(false)
    }
  }, [intervalo.end, intervalo.start, labels.refreshError, modoDemo])

  useEffect(() => {
    void carregarCadastros()
  }, [carregarCadastros])

  useEffect(() => {
    void carregarEventos()
  }, [carregarEventos])

  useEffect(() => {
    setTituloFerias(language === "en" ? "Vacation" : "Ferias")
    setTituloExcecao(language === "en" ? "Manual change" : "Ajuste manual")
  }, [language])

  const escalaAtual = useMemo(
    () => escalas.find((item) => item.is_active) ?? null,
    [escalas],
  )

  const eventosCalendario = useMemo(
    () =>
      eventos.map((item) => ({
        id: item.id,
        title: item.title,
        start: item.start,
        end: item.end,
        allDay: item.all_day,
        backgroundColor: item.color,
        borderColor: item.color,
        textColor: item.text_color,
        classNames: [`calendar-event--${item.category}`],
      })),
    [eventos],
  )

  async function submitEscala(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (modoDemo) {
      return
    }

    setSalvando("schedule")
    setErro(null)

    try {
      const customPattern = tipoEscala === "custom" ? parsePadraoPersonalizado(padraoPersonalizado) : []
      const workingWeekdays = tipoEscala === "5x2" ? diasTrabalho.slice().sort((a, b) => a - b) : []

      await criarEscalaTrabalho({
        name: nomeEscala.trim(),
        schedule_type: tipoEscala,
        anchor_date: dataBase,
        working_weekdays: workingWeekdays,
        custom_pattern: customPattern,
        note: observacaoEscala.trim() || null,
        is_active: escalaAtiva,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
      if (tipoEscala === "custom") {
        setPadraoPersonalizado("1, 0")
      }
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setSalvando(null)
    }
  }

  async function submitFerias(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (modoDemo) {
      return
    }

    setSalvando("vacation")
    setErro(null)

    try {
      await criarFerias({
        title: tituloFerias.trim(),
        start_date: inicioFerias,
        end_date: fimFerias,
        note: observacaoFerias.trim() || null,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
      setObservacaoFerias("")
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setSalvando(null)
    }
  }

  async function submitExcecao(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (modoDemo) {
      return
    }

    setSalvando("override")
    setErro(null)

    try {
      await criarExcecaoCalendario({
        override_date: dataExcecao,
        is_working_day: excecaoTrabalha,
        title: tituloExcecao.trim(),
        note: observacaoExcecao.trim() || null,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
      setObservacaoExcecao("")
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setSalvando(null)
    }
  }

  function alternarDiaTrabalho(valor: number) {
    setDiasTrabalho((atual) =>
      atual.includes(valor) ? atual.filter((item) => item !== valor) : [...atual, valor].sort((a, b) => a - b),
    )
  }

  return (
    <section className="calendar-shell">
      <div className="analysis-header__title analysis-header__title--compact">
        <p className="eyebrow eyebrow--title">{labels.title}</p>
        <h3>{labels.title}</h3>
        <p className="analysis-header__subtitle">{labels.subtitle}</p>
      </div>

      {modoDemo ? <p className="helper">{labels.demoOnly}</p> : null}
      {erro ? <p className="error-box">{erro}</p> : null}

      <div className="calendar-grid">
        <section className="calendar-panel">
          <div className="calendar-panel__header">
            <div>
              <p className="eyebrow">{labels.scheduleTitle}</p>
              <h4>{labels.scheduleTitle}</h4>
            </div>
            {escalaAtual ? <span className="status-pill">{labels.activeSchedule}</span> : null}
          </div>

          <form className="calendar-form" onSubmit={submitEscala}>
            <label className="field">
              <span>{labels.scheduleName}</span>
              <input
                type="text"
                value={nomeEscala}
                onChange={(event) => setNomeEscala(event.target.value)}
                disabled={modoDemo}
                required
              />
            </label>

            <div className="field-grid">
              <label className="field">
                <span>{labels.scheduleType}</span>
                <select
                  value={tipoEscala}
                  onChange={(event) => setTipoEscala(event.target.value as TipoEscalaTrabalho)}
                  disabled={modoDemo}
                >
                  <option value="12x36">{labels.scheduleOptions["12x36"]}</option>
                  <option value="24x72">{labels.scheduleOptions["24x72"]}</option>
                  <option value="5x2">{labels.scheduleOptions["5x2"]}</option>
                  <option value="custom">{labels.scheduleOptions.custom}</option>
                </select>
              </label>

              <label className="field">
                <span>{labels.anchorDate}</span>
                <input
                  type="date"
                  value={dataBase}
                  onChange={(event) => setDataBase(event.target.value)}
                  disabled={modoDemo}
                  required
                />
              </label>
            </div>

            {tipoEscala === "5x2" ? (
              <div className="field">
                <span>{labels.weekdays}</span>
                <div className="calendar-form__weekday-grid">
                  {WEEKDAY_OPTIONS.map((item) => (
                    <label className="calendar-form__weekday" key={item.value}>
                      <input
                        type="checkbox"
                        checked={diasTrabalho.includes(item.value)}
                        onChange={() => alternarDiaTrabalho(item.value)}
                        disabled={modoDemo}
                      />
                      <span>{labels.dayNames[item.value]}</span>
                    </label>
                  ))}
                </div>
              </div>
            ) : null}

            {tipoEscala === "custom" ? (
              <label className="field">
                <span>{labels.customPattern}</span>
                <input
                  type="text"
                  value={padraoPersonalizado}
                  onChange={(event) => setPadraoPersonalizado(event.target.value)}
                  placeholder="1, 0, 1, 0"
                  disabled={modoDemo}
                  required
                />
                <p className="helper calendar-pattern-hint">{labels.patternHint}</p>
              </label>
            ) : null}

            <label className="field">
              <span>{labels.note}</span>
              <input
                type="text"
                value={observacaoEscala}
                onChange={(event) => setObservacaoEscala(event.target.value)}
                disabled={modoDemo}
              />
            </label>

            <label className="calendar-form__toggle">
              <input
                type="checkbox"
                checked={escalaAtiva}
                onChange={(event) => setEscalaAtiva(event.target.checked)}
                disabled={modoDemo}
              />
              <span>{labels.activateNow}</span>
            </label>

            <button className="primary-button" type="submit" disabled={modoDemo || salvando === "schedule"}>
              {salvando === "schedule" ? labels.saving : labels.saveSchedule}
            </button>
          </form>

          <div className="calendar-summary">
            <p className="calendar-summary__title">{labels.currentSchedule}</p>
            {escalas.length === 0 ? (
              <p className="helper">{carregandoDados ? labels.loading : labels.noSchedules}</p>
            ) : (
              <ul className="calendar-chip-list">
                {escalas.map((item) => (
                  <li
                    className={item.is_active ? "calendar-chip calendar-chip--active" : "calendar-chip"}
                    key={item.id}
                  >
                    <strong>{item.name}</strong>
                    <span>
                      {labels.scheduleOptions[item.schedule_type]}
                      {item.schedule_type === "5x2"
                        ? ` - ${formatarDiasSemana(item.working_weekdays, labels)}`
                        : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="calendar-panel">
          <div className="calendar-panel__header">
            <div>
              <p className="eyebrow">{labels.vacationTitle}</p>
              <h4>{labels.vacationTitle}</h4>
            </div>
          </div>

          <form className="calendar-form" onSubmit={submitFerias}>
            <label className="field">
              <span>{labels.vacationLabel}</span>
              <input
                type="text"
                value={tituloFerias}
                onChange={(event) => setTituloFerias(event.target.value)}
                disabled={modoDemo}
                required
              />
            </label>

            <div className="field-grid">
              <label className="field">
                <span>{labels.vacationStart}</span>
                <input
                  type="date"
                  value={inicioFerias}
                  onChange={(event) => setInicioFerias(event.target.value)}
                  disabled={modoDemo}
                  required
                />
              </label>

              <label className="field">
                <span>{labels.vacationEnd}</span>
                <input
                  type="date"
                  value={fimFerias}
                  onChange={(event) => setFimFerias(event.target.value)}
                  disabled={modoDemo}
                  required
                />
              </label>
            </div>

            <label className="field">
              <span>{labels.note}</span>
              <input
                type="text"
                value={observacaoFerias}
                onChange={(event) => setObservacaoFerias(event.target.value)}
                disabled={modoDemo}
              />
            </label>

            <button className="primary-button" type="submit" disabled={modoDemo || salvando === "vacation"}>
              {salvando === "vacation" ? labels.saving : labels.saveVacation}
            </button>
          </form>

          <div className="calendar-summary">
            {ferias.length === 0 ? (
              <p className="helper">{carregandoDados ? labels.loading : labels.noVacations}</p>
            ) : (
              <ul className="calendar-summary-list">
                {ferias.map((item) => (
                  <li className="calendar-summary-item" key={item.id}>
                    <strong>{item.title}</strong>
                    <span>{`${formatarDataISO(item.start_date, language)} - ${formatarDataISO(item.end_date, language)}`}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="calendar-panel">
          <div className="calendar-panel__header">
            <div>
              <p className="eyebrow">{labels.overrideTitle}</p>
              <h4>{labels.overrideTitle}</h4>
            </div>
          </div>

          <form className="calendar-form" onSubmit={submitExcecao}>
            <label className="field">
              <span>{labels.overrideDate}</span>
              <input
                type="date"
                value={dataExcecao}
                onChange={(event) => setDataExcecao(event.target.value)}
                disabled={modoDemo}
                required
              />
            </label>

            <label className="field">
              <span>{labels.overrideMode}</span>
              <select
                value={excecaoTrabalha ? "work" : "off"}
                onChange={(event) => setExcecaoTrabalha(event.target.value === "work")}
                disabled={modoDemo}
              >
                <option value="work">{labels.overrideWork}</option>
                <option value="off">{labels.overrideOff}</option>
              </select>
            </label>

            <label className="field">
              <span>{labels.overrideReason}</span>
              <input
                type="text"
                value={tituloExcecao}
                onChange={(event) => setTituloExcecao(event.target.value)}
                disabled={modoDemo}
                required
              />
            </label>

            <label className="field">
              <span>{labels.note}</span>
              <input
                type="text"
                value={observacaoExcecao}
                onChange={(event) => setObservacaoExcecao(event.target.value)}
                disabled={modoDemo}
              />
            </label>

            <button className="primary-button" type="submit" disabled={modoDemo || salvando === "override"}>
              {salvando === "override" ? labels.saving : labels.saveOverride}
            </button>
          </form>

          <div className="calendar-summary">
            {excecoes.length === 0 ? (
              <p className="helper">{carregandoDados ? labels.loading : labels.noOverrides}</p>
            ) : (
              <ul className="calendar-summary-list">
                {excecoes.map((item) => (
                  <li className="calendar-summary-item" key={item.id}>
                    <strong>{item.title}</strong>
                    <span>{`${formatarDataISO(item.override_date, language)} - ${item.is_working_day ? labels.work : labels.off}`}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>

      <section className="calendar-panel calendar-panel--wide">
        <div className="calendar-panel__header">
          <div>
            <p className="eyebrow">{labels.calendarTitle}</p>
            <h4>{labels.calendarTitle}</h4>
            <p className="analysis-header__subtitle">{labels.calendarSubtitle}</p>
          </div>
          <div className="calendar-legend">
            {[
              { label: labels.work, color: "#14b8a6" },
              { label: labels.off, color: "#94a3b8" },
              { label: labels.vacation, color: "#f59e0b" },
              { label: labels.holiday, color: "#ef4444" },
              { label: labels.exception, color: "#8b5cf6" },
            ].map((item) => (
              <span className="calendar-legend__item" key={item.label}>
                <span className="calendar-legend__swatch" style={{ backgroundColor: item.color }} />
                {item.label}
              </span>
            ))}
          </div>
        </div>

        {carregandoEventos ? <p className="helper">{labels.loading}</p> : null}

        <div className="calendar-view">
          <FullCalendar
            plugins={[dayGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            height="auto"
            events={eventosCalendario}
            buttonText={{
              today: labels.today,
            }}
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "",
            }}
            datesSet={(arg) => {
              const inicio = arg.start.toISOString().slice(0, 10)
              const fimExclusivo = new Date(arg.end)
              fimExclusivo.setUTCDate(fimExclusivo.getUTCDate() - 1)
              const fim = fimExclusivo.toISOString().slice(0, 10)
              setIntervalo((atual) => (atual.start === inicio && atual.end === fim ? atual : { start: inicio, end: fim }))
            }}
            eventDisplay="block"
            dayMaxEvents={3}
            fixedWeekCount={false}
          />
        </div>
      </section>
    </section>
  )
}
