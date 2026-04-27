export type CadastroCarreira = {
  nome: string
  data_nascimento: string
  data_ingresso: string
  tem_tempo_clt_averbado: boolean
}

export type ResumoCarreira = CadastroCarreira & {
  data_25_anos_carreira: string
  idade_na_data_25_anos_carreira: number
  possui_idade_minima_na_data_25_anos_carreira: boolean
  data_idade_minima_aposentadoria: string
  data_prevista_aposentadoria: string
  grau_aos_45_anos: string
  nivel_aos_45_anos: number
  grau_na_aposentadoria: string
  nivel_na_aposentadoria: number
}

export const CADASTRO_CARREIRA_INICIAL: CadastroCarreira = {
  nome: "Maria",
  data_nascimento: "1980-01-01",
  data_ingresso: "2010-01-01",
  tem_tempo_clt_averbado: true,
}

