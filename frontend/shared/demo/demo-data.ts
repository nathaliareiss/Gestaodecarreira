import type { FinanceiroContrachequeResumo, FinanceiroEvolucaoSalarialResponse } from "@/features/financeiro/model/financeiro.model"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

export const DEMO_USUARIO: UsuarioConta = {
  id: 101,
  nome: "Maria Helena Alves",
  apelido: "Mari",
  email: "maria.helena@exemplo.com",
  data_exercicio: "2010-02-15",
  login: "maria.helena",
  senha_cadastrada: true,
  email_confirmado: true,
  criado_em: "2025-01-10T13:20:00.000Z",
  confirmado_em: "2025-01-10T13:25:00.000Z",
}

export const DEMO_HISTORICO: HistoricoFuncionalAnalise = {
  historico_id: 9001,
  usuario_id: DEMO_USUARIO.id,
  arquivo_nome: "historico-funcional-exemplo.pdf",
  nome: DEMO_USUARIO.nome,
  masp: "1234567-8",
  cpf: "123.456.789-00",
  data_emissao: "2025-03-15",
  data_nascimento: "1988-08-12",
  data_posse: "2010-02-01",
  data_exercicio: "2010-02-15",
  cargo_atual: "Analista de Gestão",
  simbolo_atual: "AG-12",
  nivel_atual: "III",
  grau_atual: "B",
  tempo_clt_averbado_anos: 2,
  tempo_clt_creditado_anos: 14,
  data_aposentadoria_por_carreira: "2038-02-01",
  data_aposentadoria_por_idade: "2048-08-12",
  data_aposentadoria_prevista: "2038-02-01",
  dias_trabalhados: 5480,
  dias_totais_ate_aposentadoria: 10950,
  percentual_trabalhado: 50.1,
  percentual_restante: 49.9,
  proxima_progressao_prevista: "2026-09-01",
  proxima_promocao_prevista: "2027-03-01",
  resumo_grafico: {
    tempo_trabalhado_dias: 5480,
    tempo_restante_dias: 5470,
    percentual_trabalhado: 50.1,
    percentual_restante: 49.9,
    eventos_totais: 5,
    eventos_por_status: {
      cumprindo: 2,
      atrasado: 1,
      nao_aplicavel: 1,
      estagio_probatorio: 1,
    },
    eventos_por_tipo: {
      nomeacao: 1,
      progressao: 2,
      promocao: 1,
      substituicao: 1,
    },
  },
  afastamentos_arquivo_nome: "afastamentos-exemplo.pdf",
  afastamentos_resumo: {
    periodos_totais: 2,
    dias_totais: 54,
    dias_por_tipo: {
      aguardando_resultado_conclusivo_de_exame_pericial: 18,
      licenca_para_tratamento_de_saude: 36,
    },
    periodos_por_tipo: {
      aguardando_resultado_conclusivo_de_exame_pericial: 1,
      licenca_para_tratamento_de_saude: 1,
    },
  },
  afastamentos: [
    {
      tipo: "licenca_para_tratamento_de_saude",
      data_inicio: "2024-03-04",
      data_fim: "2024-03-26",
      total_dias: 23,
      legislacao: "Lei 869/1952",
      publicacao: "1952-09-05",
      mes_ano_afastamento: "03/2024",
      dias_restantes_ate_pericia: 0,
    },
    {
      tipo: "aguardando_resultado_conclusivo_de_exame_pericial",
      data_inicio: "2025-06-10",
      data_fim: "2025-06-27",
      total_dias: 18,
      legislacao: "Decreto 48.384/2022",
      publicacao: "2022-11-03",
      mes_ano_afastamento: "06/2025",
      dias_restantes_ate_pericia: 3,
    },
  ],
  eventos: [
    {
      tipo: "nomeacao",
      descricao: "Nomeação inicial para a carreira.",
      cargo: "Analista de Gestão",
      simbolo: "AG-08",
      nivel: "I",
      grau: "A",
      data_publicacao: "2010-02-01",
      data_efetiva: "2010-02-15",
      data_prevista: null,
      status: "nao_aplicavel",
      atraso_dias: 0,
    },
    {
      tipo: "progressao",
      descricao: "Primeira progressão concluída dentro do prazo.",
      cargo: "Analista de Gestão",
      simbolo: "AG-10",
      nivel: "II",
      grau: "A",
      data_publicacao: "2012-07-10",
      data_efetiva: "2012-08-01",
      data_prevista: "2012-08-01",
      status: "cumprindo",
      atraso_dias: 0,
    },
    {
      tipo: "promocao",
      descricao: "Promoção com pequeno atraso administrativo.",
      cargo: "Analista de Gestão",
      simbolo: "AG-11",
      nivel: "II",
      grau: "B",
      data_publicacao: "2015-09-18",
      data_efetiva: "2015-10-06",
      data_prevista: "2015-09-20",
      status: "atrasado",
      atraso_dias: 16,
    },
    {
      tipo: "substituicao",
      descricao: "Atuação temporária em coordenação de equipe.",
      cargo: "Analista de Gestão",
      simbolo: "AG-11",
      nivel: "III",
      grau: "A",
      data_publicacao: "2020-01-06",
      data_efetiva: "2020-02-03",
      data_prevista: null,
      status: "nao_aplicavel",
      atraso_dias: 0,
    },
    {
      tipo: "progressao",
      descricao: "Progressão atual projetada dentro do cronograma.",
      cargo: "Analista de Gestão",
      simbolo: "AG-12",
      nivel: "III",
      grau: "B",
      data_publicacao: "2026-08-15",
      data_efetiva: "2026-09-01",
      data_prevista: "2026-09-01",
      status: "cumprindo",
      atraso_dias: 0,
    },
  ],
  armazenamento_origem: "local",
  processamento_origem: "direto",
}

type DemoFinanceiroAno = {
  ano: number
  salario_base: number
  bruto_total: number
  liquido: number
  descontos: number
  composicao_vantagens: Record<string, number>
  composicao_descontos: Record<string, number>
}

const DEMO_FINANCEIRO_ANOS: DemoFinanceiroAno[] = [
  {
    ano: 2010,
    salario_base: 2380.0,
    bruto_total: 2510.0,
    liquido: 1993.0,
    descontos: 517.0,
    composicao_vantagens: {
      salario_base: 2380.0,
      outros_vantagens: 130.0,
    },
    composicao_descontos: {
      previdencia: 290.0,
      irrf: 78.0,
      saude: 78.0,
      emprestimo: 71.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2011,
    salario_base: 2470.0,
    bruto_total: 2600.0,
    liquido: 2065.0,
    descontos: 535.0,
    composicao_vantagens: {
      salario_base: 2470.0,
      outros_vantagens: 130.0,
    },
    composicao_descontos: {
      previdencia: 300.0,
      irrf: 85.0,
      saude: 80.0,
      emprestimo: 70.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2012,
    salario_base: 2620.0,
    bruto_total: 2750.0,
    liquido: 2184.0,
    descontos: 566.0,
    composicao_vantagens: {
      salario_base: 2620.0,
      outros_vantagens: 130.0,
    },
    composicao_descontos: {
      previdencia: 315.0,
      irrf: 92.0,
      saude: 85.0,
      emprestimo: 74.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2013,
    salario_base: 2740.0,
    bruto_total: 2875.0,
    liquido: 2285.0,
    descontos: 590.0,
    composicao_vantagens: {
      salario_base: 2740.0,
      outros_vantagens: 135.0,
    },
    composicao_descontos: {
      previdencia: 330.0,
      irrf: 97.0,
      saude: 89.0,
      emprestimo: 74.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2014,
    salario_base: 2930.0,
    bruto_total: 3050.0,
    liquido: 2424.0,
    descontos: 626.0,
    composicao_vantagens: {
      salario_base: 2930.0,
      outros_vantagens: 120.0,
    },
    composicao_descontos: {
      previdencia: 346.0,
      irrf: 104.0,
      saude: 96.0,
      emprestimo: 80.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2015,
    salario_base: 3563.86,
    bruto_total: 3563.86,
    liquido: 2798.25,
    descontos: 765.61,
    composicao_vantagens: {
      salario_base: 3563.86,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 392.02,
      irrf: 140.75,
      saude: 114.04,
      emprestimo: 0.0,
      outros_descontos: 118.8,
    },
  },
  {
    ano: 2016,
    salario_base: 3563.86,
    bruto_total: 3690.0,
    liquido: 2900.0,
    descontos: 790.0,
    composicao_vantagens: {
      salario_base: 3563.86,
      outros_vantagens: 126.14,
    },
    composicao_descontos: {
      previdencia: 403.0,
      irrf: 148.0,
      saude: 120.0,
      emprestimo: 119.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2017,
    salario_base: 3695.0,
    bruto_total: 3845.0,
    liquido: 3023.0,
    descontos: 822.0,
    composicao_vantagens: {
      salario_base: 3695.0,
      ade: 100.0,
      alimentacao: 50.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 415.0,
      irrf: 154.0,
      saude: 125.0,
      emprestimo: 128.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2018,
    salario_base: 3845.0,
    bruto_total: 4025.0,
    liquido: 3169.0,
    descontos: 856.0,
    composicao_vantagens: {
      salario_base: 3845.0,
      ade: 115.0,
      alimentacao: 65.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 430.0,
      irrf: 160.0,
      saude: 132.0,
      emprestimo: 134.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2019,
    salario_base: 3845.0,
    bruto_total: 4130.0,
    liquido: 3252.0,
    descontos: 878.0,
    composicao_vantagens: {
      salario_base: 3845.0,
      ade: 165.0,
      alimentacao: 120.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 440.0,
      irrf: 165.0,
      saude: 138.0,
      emprestimo: 135.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2020,
    salario_base: 4210.0,
    bruto_total: 4490.0,
    liquido: 3534.0,
    descontos: 956.0,
    composicao_vantagens: {
      salario_base: 4210.0,
      ade: 180.0,
      alimentacao: 100.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 480.0,
      irrf: 175.0,
      saude: 150.0,
      emprestimo: 151.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2021,
    salario_base: 4445.0,
    bruto_total: 4780.0,
    liquido: 3762.0,
    descontos: 1018.0,
    composicao_vantagens: {
      salario_base: 4445.0,
      ade: 220.0,
      alimentacao: 115.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 510.0,
      irrf: 185.0,
      saude: 160.0,
      emprestimo: 163.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2022,
    salario_base: 4735.0,
    bruto_total: 5140.0,
    liquido: 4046.0,
    descontos: 1094.0,
    composicao_vantagens: {
      salario_base: 4735.0,
      ade: 280.0,
      alimentacao: 125.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 548.0,
      irrf: 200.0,
      saude: 175.0,
      emprestimo: 171.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2023,
    salario_base: 5025.0,
    bruto_total: 5550.0,
    liquido: 4370.0,
    descontos: 1180.0,
    composicao_vantagens: {
      salario_base: 5025.0,
      ade: 350.0,
      alimentacao: 175.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 588.0,
      irrf: 214.0,
      saude: 190.0,
      emprestimo: 188.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2024,
    salario_base: 5370.0,
    bruto_total: 6090.0,
    liquido: 4795.0,
    descontos: 1295.0,
    composicao_vantagens: {
      salario_base: 5370.0,
      ade: 420.0,
      alimentacao: 300.0,
      outros_vantagens: 0.0,
    },
    composicao_descontos: {
      previdencia: 644.0,
      irrf: 228.0,
      saude: 209.0,
      emprestimo: 214.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2025,
    salario_base: 5820.0,
    bruto_total: 7190.0,
    liquido: 5665.0,
    descontos: 1525.0,
    composicao_vantagens: {
      salario_base: 5820.0,
      ade: 520.0,
      alimentacao: 650.0,
      outros_vantagens: 200.0,
    },
    composicao_descontos: {
      previdencia: 740.0,
      irrf: 262.0,
      saude: 238.0,
      emprestimo: 285.0,
      outros_descontos: 0.0,
    },
  },
  {
    ano: 2026,
    salario_base: 6416.46,
    bruto_total: 10617.09,
    liquido: 8312.63,
    descontos: 2304.46,
    composicao_vantagens: {
      salario_base: 6416.46,
      ade: 674.53,
      adicional_noturno: 10.13,
      alimentacao: 823.82,
      abono_vestimenta: 115.18,
      outros_vantagens: 2576.97,
    },
    composicao_descontos: {
      previdencia: 892.02,
      irrf: 873.84,
      emprestimo: 360.19,
      saude: 178.41,
      outros_descontos: 0.0,
    },
  },
]

function arredondar(valor: number): number {
  return Number(valor.toFixed(2))
}

function calcularVariacaoPercentual(valorAnterior: number, valorAtual: number): number | null {
  if (valorAnterior <= 0) {
    return null
  }

  return arredondar(((valorAtual - valorAnterior) / valorAnterior) * 100)
}

const DEMO_FINANCEIRO_SERIE = DEMO_FINANCEIRO_ANOS.map((item, indice) => {
  const variacao = indice === 0 ? null : calcularVariacaoPercentual(DEMO_FINANCEIRO_ANOS[indice - 1].salario_base, item.salario_base)
  const crescimentoRelevante = variacao === null ? true : Math.abs(variacao) >= 1

  return {
    ano: item.ano,
    salario_base_referencia_anual: item.salario_base,
    bruto_total_referencia_anual: item.bruto_total,
    liquido_referencia_anual: item.liquido,
    descontos_referencia_anual: item.descontos,
    vantagens_adicionais_referencia_anual: arredondar(item.bruto_total - item.salario_base),
    composicao_vantagens_referencia_anual: item.composicao_vantagens,
    composicao_descontos_referencia_anual: item.composicao_descontos,
    quantidade_contracheques: 1,
    variacao_percentual_salario_base_ano_a_ano: variacao,
    crescimento_relevante: crescimentoRelevante,
  }
})

const DEMO_FINANCEIRO_ANOS_SEM_CRESCIMENTO_RELEVANTE = DEMO_FINANCEIRO_SERIE
  .filter((item) => item.variacao_percentual_salario_base_ano_a_ano !== null)
  .filter((item) => !item.crescimento_relevante)
  .map((item) => item.ano)

export const DEMO_FINANCEIRO_EVOLUCAO: FinanceiroEvolucaoSalarialResponse = {
  batch_id: null,
  ano_inicial: DEMO_FINANCEIRO_SERIE[0].ano,
  ano_final: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].ano,
  salario_base_inicial_referencia: DEMO_FINANCEIRO_SERIE[0].salario_base_referencia_anual,
  salario_base_final_referencia: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].salario_base_referencia_anual,
  bruto_total_inicial_referencia: DEMO_FINANCEIRO_SERIE[0].bruto_total_referencia_anual,
  bruto_total_final_referencia: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].bruto_total_referencia_anual,
  liquido_inicial_referencia: DEMO_FINANCEIRO_SERIE[0].liquido_referencia_anual,
  liquido_final_referencia: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].liquido_referencia_anual,
  descontos_inicial_referencia: DEMO_FINANCEIRO_SERIE[0].descontos_referencia_anual,
  descontos_final_referencia: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].descontos_referencia_anual,
  vantagens_adicionais_inicial_referencia: DEMO_FINANCEIRO_SERIE[0].vantagens_adicionais_referencia_anual,
  vantagens_adicionais_final_referencia: DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].vantagens_adicionais_referencia_anual,
  variacao_acumulada_salario_base_percentual: calcularVariacaoPercentual(
    DEMO_FINANCEIRO_SERIE[0].salario_base_referencia_anual,
    DEMO_FINANCEIRO_SERIE[DEMO_FINANCEIRO_SERIE.length - 1].salario_base_referencia_anual,
  ),
  anos_sem_crescimento_relevante: DEMO_FINANCEIRO_ANOS_SEM_CRESCIMENTO_RELEVANTE,
  series: DEMO_FINANCEIRO_SERIE,
}

export const DEMO_FINANCEIRO_CONTRACHEQUES: FinanceiroContrachequeResumo[] = DEMO_FINANCEIRO_SERIE.map((item) => ({
  id: 10000 + item.ano,
  competencia: `12/${item.ano}`,
  ano: item.ano,
  mes: 12,
  salario_base: item.salario_base_referencia_anual,
  bruto_total: item.bruto_total_referencia_anual,
  liquido: item.liquido_referencia_anual,
  descontos: item.descontos_referencia_anual,
}))
