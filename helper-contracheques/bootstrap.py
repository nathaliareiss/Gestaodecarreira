from __future__ import annotations

import time


def main() -> int:
    inicio = time.perf_counter()
    print("Iniciando assistente...", flush=True)
    print("Carregando navegador automático...", flush=True)

    import main as helper_main

    print(f"[tempo] bootstrap_import={time.perf_counter() - inicio:.2f}s", flush=True)
    return helper_main.main()


if __name__ == "__main__":
    raise SystemExit(main())
