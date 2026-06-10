from __future__ import annotations

import logging

from backend.logger import StructuredFormatter


def test_structured_formatter_mascara_campos_sensiveis() -> None:
    record = logging.LogRecord(
        name="app",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Teste",
        args=(),
        exc_info=None,
    )
    record.email = "maria@example.com"
    record.cpf = "123.456.789-00"
    record.file_hash = "6b86b273ff34fce19d6b804eff5a3f5747ada4ea"
    record.status = "ok"

    formatter = StructuredFormatter("%(message)s")
    resultado = formatter.format(record)

    assert "maria@example.com" not in resultado
    assert "123.456.789-00" not in resultado
    assert "6b86b273ff34fce19d6b804eff5a3f5747ada4ea" not in resultado
    assert "m***@example.com" in resultado
    assert "***.***.***-**" in resultado
    assert "[redacted-secret]" in resultado
    assert "status=ok" in resultado
