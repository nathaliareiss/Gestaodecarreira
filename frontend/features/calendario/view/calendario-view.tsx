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
  WorkSchedule,
} from "../model/calendario.model"
import {
  criarEscalaTrabalho,
  criarFerias,
  listarEscalasTrabalho,
  listarEventosCalendario,
  listarFerias,
} from "../model/calendario.repository"

type CalendarioViewProps = {
  modoDemo: boolean
}

type IntervaloCalendario = {
  start: string
  end: string
}

type CidadeOption = {
  state: string
  city: string
  label: string
}

const CITY_OPTIONS: CidadeOption[] = [
  { state: "MG", city: "Belo Horizonte", label: "Belo Horizonte - MG" },
  { state: "MG", city: "Contagem", label: "Contagem - MG" },
  { state: "MG", city: "Betim", label: "Betim - MG" },
  { state: "MG", city: "Uberlandia", label: "Uberlandia - MG" },
  { state: "MG", city: "Juiz de Fora", label: "Juiz de Fora - MG" },
  { state: "SP", city: "Sao Paulo", label: "Sao Paulo - SP" },
  { state: "RJ", city: "Rio de Janeiro", label: "Rio de Janeiro - RJ" },
]

const WEEKDAY_OPTIONS = [
  { value: 0, label: "Seg" },
  { value: 1, label: "Ter" },
  { value: 2, label: "Qua" },
  { value: 3, label: "Qui" },
  { value: 4, label: "Sex" },
  { value: 5, label: "Sab" },
  { value: 6, label: "Dom" },
] as const

function hojeISO() {
  return new Date().toISOString().slice(0, 10)
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

function formatarDiasSemana(workingWeekdays: number[]) {
  if (workingWeekdays.length === 0) {
    return "-"
  }

  const map = new Map<number, string>(WEEKDAY_OPTIONS.map((item) => [item.value, item.label]))
  return workingWeekdays.map((item) => map.get(item) ?? String(item)).join(", ")
}

function calendarioEventClass(category: WorkCalendarEvent["category"]) {
  return `calendar-event--${category}`
}

export function CalendarioView({ modoDemo }: CalendarioViewProps) {
  const { language } = useLanguage()
  const labels = useMemo(
    () => ({
      title: language === "en" ? "Work schedule" : "Escala",
      subtitle:
        language === "en"
          ? "Manage shifts, regular vacation, premium vacation, and holidays in the same calendar."
          : "Gerencie plantoes, ferias regulamentares, ferias-premio e feriados no mesmo calendario.",
      scheduleTitle: language === "en" ? "Shift schedule" : "Escala de plantao",
      city: language === "en" ? "City for local holidays" : "Cidade dos feriados municipais",
      regularVacation: language === "en" ? "Regular vacation" : "Ferias regulamentares",
      premiumVacation: language === "en" ? "Premium vacation" : "Ferias-premio",
      loading: language === "en" ? "Loading..." : "Carregando...",
      save: language === "en" ? "Save" : "Salvar",
      saving: language === "en" ? "Saving..." : "Salvando...",
      refreshError:
        language === "en"
          ? "We could not load the schedule right now."
          : "Nao foi possivel carregar a escala agora.",
      demoOnly:
        language === "en"
          ? "Demo mode keeps this module read-only."
          : "No modo demonstracao, este modulo fica somente para leitura.",
      noSchedules: language === "en" ? "No schedule saved yet." : "Nenhuma escala cadastrada ainda.",
      noVacations: language === "en" ? "No vacation saved yet." : "Nenhuma ferias cadastrada ainda.",
      active: language === "en" ? "Active" : "Ativa",
      work: language === "en" ? "Shift" : "Plantao",
      off: language === "en" ? "Day off" : "Folga",
      vacation: language === "en" ? "Regular vacation" : "Ferias regulamentares",
      premium: language === "en" ? "Premium vacation" : "Ferias-premio",
      holiday: language === "en" ? "Holiday" : "Feriado",
      today: language === "en" ? "Today" : "Hoje",
    }),
    [language],
  )

  const [intervalo, setIntervalo] = useState<IntervaloCalendario>(() => intervaloMesAtual())
  const [escalas, setEscalas] = useState<WorkSchedule[]>([])
  const [ferias, setFerias] = useState<VacationPeriod[]>([])
  const [eventos, setEventos] = useState<WorkCalendarEvent[]>([])
  const [carregandoDados, setCarregandoDados] = useState(false)
  const [carregandoEventos, setCarregandoEventos] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [salvando, setSalvando] = useState<"schedule" | "regular" | "premium" | null>(null)

  const [nomeEscala, setNomeEscala] = useState("Escala principal")
  const [tipoEscala, setTipoEscala] = useState<TipoEscalaTrabalho>("12x36")
  const [dataBase, setDataBase] = useState(hojeISO())
  const [cidadeSelecionada, setCidadeSelecionada] = useState("MG|Belo Horizonte")
  const [diasTrabalho, setDiasTrabalho] = useState<number[]>([0, 1, 2, 3, 4])
  const [padraoPersonalizado, setPadraoPersonalizado] = useState("1, 0")
  const [observacaoEscala, setObservacaoEscala] = useState("")

  const [inicioFeriasRegular, setInicioFeriasRegular] = useState(hojeISO())
  const [diasFeriasRegular, setDiasFeriasRegular] = useState(15)
  const [observacaoFeriasRegular, setObservacaoFeriasRegular] = useState("")

  const [inicioFeriasPremio, setInicioFeriasPremio] = useState(hojeISO())
  const [diasFeriasPremio, setDiasFeriasPremio] = useState(30)
  const [observacaoFeriasPremio, setObservacaoFeriasPremio] = useState("")

  const carregarCadastros = useCallback(async () => {
    if (modoDemo) {
      setEscalas([])
      setFerias([])
      return
    }

    setCarregandoDados(true)
    setErro(null)

    try {
      const [escalasResposta, feriasResposta] = await Promise.all([
        listarEscalasTrabalho(),
        listarFerias(),
      ])
      setEscalas(escalasResposta)
      setFerias(feriasResposta)
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
      setEventos(await listarEventosCalendario(intervalo.start, intervalo.end))
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

  const escalaAtual = useMemo(
    () => escalas.find((item) => item.is_active) ?? null,
    [escalas],
  )

  const feriasRegulares = useMemo(
    () => ferias.filter((item) => item.vacation_type !== "premium"),
    [ferias],
  )

  const feriasPremio = useMemo(
    () => ferias.filter((item) => item.vacation_type === "premium"),
    [ferias],
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
        classNames: [calendarioEventClass(item.category)],
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
      const [stateCode, cityName] = cidadeSelecionada.split("|")
      await criarEscalaTrabalho({
        name: nomeEscala.trim(),
        schedule_type: tipoEscala,
        anchor_date: dataBase,
        state_code: stateCode || null,
        city_name: cityName || null,
        working_weekdays: tipoEscala === "5x2" ? diasTrabalho.slice().sort((a, b) => a - b) : [],
        custom_pattern: tipoEscala === "custom" ? parsePadraoPersonalizado(padraoPersonalizado) : [],
        note: observacaoEscala.trim() || null,
        is_active: true,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setSalvando(null)
    }
  }

  async function submitFeriasRegular(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (modoDemo) {
      return
    }

    setSalvando("regular")
    setErro(null)

    try {
      await criarFerias({
        title: "Ferias regulamentares",
        vacation_type: "regular",
        start_date: inicioFeriasRegular,
        requested_days: diasFeriasRegular,
        note: observacaoFeriasRegular.trim() || null,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
      setObservacaoFeriasRegular("")
    } catch (error) {
      setErro(formatarErro(error, labels.refreshError))
    } finally {
      setSalvando(null)
    }
  }

  async function submitFeriasPremio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (modoDemo) {
      return
    }

    setSalvando("premium")
    setErro(null)

    try {
      await criarFerias({
        title: "Ferias-premio",
        vacation_type: "premium",
        start_date: inicioFeriasPremio,
        requested_days: diasFeriasPremio,
        note: observacaoFeriasPremio.trim() || null,
      })

      await Promise.all([carregarCadastros(), carregarEventos()])
      setObservacaoFeriasPremio("")
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
            {escalaAtual ? <span className="status-pill">{labels.active}</span> : null}
          </div>

          <form className="calendar-form" onSubmit={submitEscala}>
            <label className="field">
              <span>Nome da escala</span>
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
                <span>Tipo de escala</span>
                <select
                  value={tipoEscala}
                  onChange={(event) => setTipoEscala(event.target.value as TipoEscalaTrabalho)}
                  disabled={modoDemo}
                >
                  <option value="12x36">12x36</option>
                  <option value="24x72">24x72</option>
                  <option value="5x2">5x2</option>
                  <option value="custom">Personalizada</option>
                </select>
              </label>

              <label className="field">
                <span>Data base</span>
                <input
                  type="date"
                  value={dataBase}
                  onChange={(event) => setDataBase(event.target.value)}
                  disabled={modoDemo}
                  required
                />
              </label>
            </div>

            <label className="field">
              <span>{labels.city}</span>
              <select
                value={cidadeSelecionada}
                onChange={(event) => setCidadeSelecionada(event.target.value)}
                disabled={modoDemo}
              >
                {CITY_OPTIONS.map((item) => (
                  <option key={`${item.state}-${item.city}`} value={`${item.state}|${item.city}`}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>

            {tipoEscala === "5x2" ? (
              <div className="field">
                <span>Dias de trabalho</span>
                <div className="calendar-form__weekday-grid">
                  {WEEKDAY_OPTIONS.map((item) => (
                    <label className="calendar-form__weekday" key={item.value}>
                      <input
                        type="checkbox"
                        checked={diasTrabalho.includes(item.value)}
                        onChange={() => alternarDiaTrabalho(item.value)}
                        disabled={modoDemo}
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ) : null}

            {tipoEscala === "custom" ? (
              <label className="field">
                <span>Padrao personalizado</span>
                <input
                  type="text"
                  value={padraoPersonalizado}
                  onChange={(event) => setPadraoPersonalizado(event.target.value)}
                  placeholder="1, 0, 1, 0"
                  disabled={modoDemo}
                  required
                />
                <p className="helper calendar-pattern-hint">
                  Use 1 para trabalho e 0 para folga.
                </p>
              </label>
            ) : null}

            <label className="field">
              <span>Observacoes</span>
              <input
                type="text"
                value={observacaoEscala}
                onChange={(event) => setObservacaoEscala(event.target.value)}
                disabled={modoDemo}
              />
            </label>

            <button className="primary-button" type="submit" disabled={modoDemo || salvando === "schedule"}>
              {salvando === "schedule" ? labels.saving : labels.save}
            </button>
          </form>

          <div className="calendar-summary">
            {escalas.length === 0 ? (
              <p className="helper">{carregandoDados ? labels.loading : labels.noSchedules}</p>
            ) : (
              <ul className="calendar-chip-list">
                {escalas.map((item) => (
                  <li className={item.is_active ? "calendar-chip calendar-chip--active" : "calendar-chip"} key={item.id}>
                    <strong>{item.name}</strong>
                    <span>
                      {item.schedule_type}
                      {item.schedule_type === "5x2" ? ` - ${formatarDiasSemana(item.working_weekdays)}` : ""}
                      {item.city_name ? ` - ${item.city_name}/${item.state_code ?? ""}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <VacationCard
          title={labels.regularVacation}
          description="Periodo de 10 ou 15 dias uteis."
          startDate={inicioFeriasRegular}
          days={diasFeriasRegular}
          dayOptions={[10, 15]}
          note={observacaoFeriasRegular}
          saving={salvando === "regular"}
          disabled={modoDemo}
          vacations={feriasRegulares}
          emptyLabel={labels.noVacations}
          loadingLabel={carregandoDados ? labels.loading : null}
          language={language}
          onStartDateChange={setInicioFeriasRegular}
          onDaysChange={setDiasFeriasRegular}
          onNoteChange={setObservacaoFeriasRegular}
          onSubmit={submitFeriasRegular}
        />

        <VacationCard
          title={labels.premiumVacation}
          description="Opcional. Contagem em dias corridos."
          startDate={inicioFeriasPremio}
          days={diasFeriasPremio}
          dayOptions={[15, 30, 45, 60, 90]}
          note={observacaoFeriasPremio}
          saving={salvando === "premium"}
          disabled={modoDemo}
          vacations={feriasPremio}
          emptyLabel="Preencha somente se tiver direito a ferias-premio."
          loadingLabel={carregandoDados ? labels.loading : null}
          language={language}
          onStartDateChange={setInicioFeriasPremio}
          onDaysChange={setDiasFeriasPremio}
          onNoteChange={setObservacaoFeriasPremio}
          onSubmit={submitFeriasPremio}
        />
      </div>

      <section className="calendar-panel calendar-panel--wide">
        <div className="calendar-panel__header">
          <div>
            <p className="eyebrow">{labels.title}</p>
            <h4>{labels.title}</h4>
            <p className="analysis-header__subtitle">
              Plantoes, folgas, ferias e feriados nacionais/estaduais/municipais aparecem juntos.
            </p>
          </div>
          <div className="calendar-legend">
            {[
              { label: labels.work, color: "#14b8a6" },
              { label: labels.off, color: "#94a3b8" },
              { label: labels.vacation, color: "#f59e0b" },
              { label: labels.premium, color: "#38bdf8" },
              { label: labels.holiday, color: "#ef4444" },
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
            buttonText={{ today: labels.today }}
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

type VacationCardProps = {
  title: string
  description: string
  startDate: string
  days: number
  dayOptions: number[]
  note: string
  saving: boolean
  disabled: boolean
  vacations: VacationPeriod[]
  emptyLabel: string
  loadingLabel: string | null
  language: "pt-BR" | "en"
  onStartDateChange: (value: string) => void
  onDaysChange: (value: number) => void
  onNoteChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

function VacationCard({
  title,
  description,
  startDate,
  days,
  dayOptions,
  note,
  saving,
  disabled,
  vacations,
  emptyLabel,
  loadingLabel,
  language,
  onStartDateChange,
  onDaysChange,
  onNoteChange,
  onSubmit,
}: VacationCardProps) {
  return (
    <section className="calendar-panel">
      <div className="calendar-panel__header">
        <div>
          <p className="eyebrow">{title}</p>
          <h4>{title}</h4>
          <p className="helper">{description}</p>
        </div>
      </div>

      <form className="calendar-form" onSubmit={onSubmit}>
        <div className="field-grid">
          <label className="field">
            <span>Inicio</span>
            <input
              type="date"
              value={startDate}
              onChange={(event) => onStartDateChange(event.target.value)}
              disabled={disabled}
              required
            />
          </label>

          <label className="field">
            <span>Dias</span>
            <select
              value={days}
              onChange={(event) => onDaysChange(Number(event.target.value))}
              disabled={disabled}
            >
              {dayOptions.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="field">
          <span>Observacoes</span>
          <input
            type="text"
            value={note}
            onChange={(event) => onNoteChange(event.target.value)}
            disabled={disabled}
          />
        </label>

        <button className="primary-button" type="submit" disabled={disabled || saving}>
          {saving ? "Salvando..." : "Salvar"}
        </button>
      </form>

      <div className="calendar-summary">
        {vacations.length === 0 ? (
          <p className="helper">{loadingLabel ?? emptyLabel}</p>
        ) : (
          <ul className="calendar-summary-list">
            {vacations.map((item) => (
              <li className="calendar-summary-item" key={item.id}>
                <strong>{item.title}</strong>
                <span>
                  {`${formatarDataISO(item.start_date, language)} - ${formatarDataISO(item.end_date, language)}`}
                </span>
                <span>{`${item.counted_days ?? item.requested_days ?? "-"} dias`}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
