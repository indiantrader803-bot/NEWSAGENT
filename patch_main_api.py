with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """    elif path_only == "/api/news":"""

replacement = """    elif path_only == "/api/momentum/start":
        try:
            from momentum_engine import engine
            engine.start()
            response_body = json.dumps({"status": "Started"})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/momentum/stop":
        try:
            from momentum_engine import engine
            engine.stop()
            response_body = json.dumps({"status": "Stopped"})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/momentum/live":
        try:
            from momentum_engine import engine
            trades = list(engine.active_trades.values())
            
            import sqlite3
            conn = sqlite3.connect("momentum_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, event, message, timestamp FROM strategy_logs ORDER BY id DESC LIMIT 10")
            logs = [{"symbol": r[0], "event": r[1], "message": r[2], "timestamp": r[3]} for r in cursor.fetchall()]
            conn.close()
            
            response_body = json.dumps({"active_trades": trades, "recent_logs": logs, "engine_active": engine.active})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/news":"""

if target in content:
    content = content.replace(target, replacement)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched main.py")
else:
    print("Target not found")
