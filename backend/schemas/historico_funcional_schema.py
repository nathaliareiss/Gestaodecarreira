from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SexoServidor = Literal["feminino", "masculino"]
FeriasTipo = Literal["regular", "premium"]
CategoriaPrevidenciaria = Literal["geral", "professor", "seguranca", "saude_exposicao"]


class HistoricoFuncionalUploadRequest(BaseModel):
    usuario_id: int | None = None
    arquivo_nome: str = Field(min_length=1)
    arquivo_storage_path: str = Field(min_length=1)
    armazenamento_origem: Literal["local"] = "local"
    data_nascimento: date
    sexo: SexoServidor
    categoria_previdenciaria: CategoriaPrevidenciaria = "geral"
    anos_clt_averbados: int = Field(default=0, ge=0, le=10)
    afastamentos_arquivo_nome: str | None = None
    afastamentos_storage_path: str | None = None
    afastamentos_armazenamento_origem: Literal["local"] | None = None
    ferias_arquivo_nome: str | None = None
    ferias_storage_path: str | None = None
    ferias_armazenamento_origem: Literal["local"] | None = None
    ferias_arquivo_nomes: list[str] = Field(default_factory=list)
    ferias_storage_paths: list[str] = Field(default_factory=list)


class AfastamentosUploadRequest(BaseModel):
    arquivo_nome: str = Field(min_length=1)
    arquivo_storage_path: str = Field(min_length=1)
    armazenamento_origem: Literal["local"] = "local"


class FeriasUploadRequest(BaseModel):
    arquivo_nome: str = Field(min_length=1)
    arquivo_storage_path: str = Field(min_length=1)
    armazenamento_origem: Literal["local"] = "local"
    arquivo_nomes: list[str] = Field(default_factory=list)
    arquivo_storage_paths: list[str] = Field(default_factory=list)


class HistoricoFuncionalEventoResponse(BaseModel):
    tipo: Literal["nomeacao", "progressao", "promocao", "substituicao"]
    descricao: str
    cargo: str
    simbolo: str
    nivel: str
    grau: str
    data_publicacao: date
    data_efetiva: date
    data_prevista: date | None
    status: Literal["cumprindo", "atrasado", "nao_aplicavel", "estagio_probatorio"]
    atraso_dias: int


class HistoricoFuncionalResumoGraficoResponse(BaseModel):
    tempo_trabalhado_dias: int
    tempo_restante_dias: int
    percentual_trabalhado: float
    percentual_restante: float
    eventos_totais: int
    eventos_por_status: dict[str, int]
    eventos_por_tipo: dict[str, int]


class HistoricoFuncionalResumoAposentadoriaResponse(BaseModel):
    tempo_restante_dias: int
    idade_na_aposentadoria_anos: int
    idade_por_tempo_servico_anos: int
    idade_minima_governo_anos: int
    data_por_tempo_servico: date
    data_por_idade_minima: date
    data_prevista: date
    nivel_previsto: str
    grau_previsto: str
    observacao: str


class AfastamentoPeriodoResponse(BaseModel):
    tipo: Literal[
        "aguardando_resultado_conclusivo_de_exame_pericial",
        "licenca_para_tratamento_de_saude",
    ]
    data_inicio: date
    data_fim: date
    total_dias: int
    legislacao: str | None = None
    publicacao: date | None = None
    mes_ano_afastamento: str = ""
    dias_restantes_ate_pericia: int = 0


class AfastamentoResumoResponse(BaseModel):
    periodos_totais: int
    dias_totais: int
    dias_por_tipo: dict[str, int]
    periodos_por_tipo: dict[str, int]


class FeriasPeriodoResponse(BaseModel):
    tipo: FeriasTipo
    data_inicio: date
    data_fim: date
    dias_contabilizados: int
    dias_corridos: int
    regra_contagem: Literal["dias_uteis", "dias_corridos"]
    observacao: str | None = None


class FeriasResumoResponse(BaseModel):
    periodos_totais: int
    dias_totais_usados: int
    dias_por_tipo: dict[str, int]
    periodos_por_tipo: dict[str, int]
    proxima_ferias_inicio: date | None = None
    proxima_ferias_fim: date | None = None
    proxima_ferias_tipo: FeriasTipo | None = None


class HistoricoFuncionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    historico_id: int
    usuario_id: int | None
    arquivo_nome: str
    nome: str
    masp: str
    cpf: str | None
    data_emissao: date | None
    data_nascimento: date
    sexo: SexoServidor | None = None
    categoria_previdenciaria: CategoriaPrevidenciaria | None = None
    data_posse: date
    data_exercicio: date
    cargo_atual: str
    simbolo_atual: str
    nivel_atual: str
    grau_atual: str
    tempo_clt_averbado_anos: int
    tempo_clt_creditado_anos: int
    data_aposentadoria_por_carreira: date
    data_aposentadoria_por_idade: date
    data_aposentadoria_prevista: date
    dias_trabalhados: int
    dias_totais_ate_aposentadoria: int
    percentual_trabalhado: float
    percentual_restante: float
    proxima_progressao_prevista: date
    proxima_promocao_prevista: date
    resumo_grafico: HistoricoFuncionalResumoGraficoResponse
    resumo_aposentadoria: HistoricoFuncionalResumoAposentadoriaResponse | None = None
    afastamentos_arquivo_nome: str | None = None
    afastamentos_resumo: AfastamentoResumoResponse | None = None
    afastamentos: list[AfastamentoPeriodoResponse] = Field(default_factory=list)
    ferias_arquivo_nome: str | None = None
    ferias_resumo: FeriasResumoResponse | None = None
    ferias: list[FeriasPeriodoResponse] = Field(default_factory=list)
    eventos: list[HistoricoFuncionalEventoResponse]
    armazenamento_origem: Literal["local"] = "local"
    processamento_origem: Literal["fila", "direto"] = "direto"
