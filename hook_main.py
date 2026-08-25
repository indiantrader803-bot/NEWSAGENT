import re

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# We need to add the route `/api/smc-matrix`
route_code = """
    elif path_only == "/api/smc-matrix":
        try:
            symbols_param = query_params.get("symbols", ["^NSEI, XAUUSD=X, EURUSD=X"])[0]
            symbols_list = [s.strip() for s in symbols_param.split(",") if s.strip()]
            
            import smc_matrix
            results = smc_matrix.scan_smc(symbols_list)
            response_body = json.dumps(results)
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"
"""

if "/api/smc-matrix" not in main_code:
    # Insert right before `/api/signals`
    main_code = main_code.replace('    if path_only == "/api/signals":', route_code + '\n    if path_only == "/api/signals":')

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
