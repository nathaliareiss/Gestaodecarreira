from backend.storage.local_storage import (
    StorageError,
    baixar_pdf_storage,
    gerar_caminho_storage_afastamentos,
    gerar_caminho_storage_ferias,
    gerar_caminho_storage_historico,
    enviar_pdf_para_storage,
    obter_origem_storage,
    remover_arquivo_storage,
)

__all__ = [
    "StorageError",
    "baixar_pdf_storage",
    "gerar_caminho_storage_afastamentos",
    "gerar_caminho_storage_ferias",
    "gerar_caminho_storage_historico",
    "enviar_pdf_para_storage",
    "obter_origem_storage",
    "remover_arquivo_storage",
]
