Autotrade & Broker Credentials
===============================

Overview
--------
This project supports automated trading through pluggable broker adapters. To keep you safe by default, all adapters simulate (paper) orders unless you explicitly enable live trading and provide credentials.

How to provide credentials
--------------------------
- Create or edit a local `.env` file in the project root.
- Add the provider-specific environment variables listed in `.env.example` (DELTA_API_KEY, DELTA_API_SECRET, COINSWITCH_API_KEY, MT5_ACCOUNT, etc.).
- Keep live API keys secret and never commit them to Git.

Enable autotrading
------------------
1. In `.env`, set `AUTOTRADE_ENABLED=1` to enable the autotrader.
2. Choose your broker via `BROKER_PROVIDER` (e.g. `delta`, `coinswitch`, `mt5`, or `dummy`).
3. Use `AUTOTRADE_MODE=paper` to run simulated orders, or `AUTOTRADE_MODE=live` to attempt live execution (ensure credentials and safety checks are configured).

Safety recommendations
----------------------
- Start in paper mode (`BROKER_PROVIDER=dummy`, `AUTOTRADE_ENABLED=0` or `AUTOTRADE_MODE=paper`) until you're confident.
- Set `MAX_UNITS_PER_TRADE` to limit trade size.
- Implement and verify daily loss limits and position sizing before enabling live trading.

Adapter behavior
----------------
- `brokers/delta.py`, `brokers/coinswitch.py`, and `brokers/mt5.py` are skeleton adapters that simulate orders by default and log them to local files:
  - `autotrade_delta.log`, `autotrade_coinswitch.log`, `autotrade_mt5.log`.
- When credentials are present, adapters will expose `live_credentials_present` in simulated responses. Full live implementations require adding API calls and handling authentication details.

Live mode status
----------------
Each adapter accepts an explicit env-var to request live execution in addition to `AUTOTRADE_MODE=live`:

- `DELTA_LIVE=1` enables Delta live request handling
- `COINSWITCH_LIVE=1` enables Coinswitch live request handling

Currently the adapters include scaffolding and will record when live was requested; implementing the full signed REST calls requires adding provider-specific request signing and order schemas. I can implement the full REST flows next if you provide API docs or test keys.

Leverage
--------
You can set `LEVERAGE` in your `.env` in formats like `1:5` or `5`. The adapter will parse this and include a `leverage` field in trade requests. Example:

LEVERAGE=1:5

This is applied to the trade request so broker adapters can convert units into lots or notional values appropriately. Default is `1:1` (no leverage).

If you want, I can implement a full Delta/Coinswitch/MT5 live adapter next — tell me which broker to prioritize and whether you will provide test API keys or want paper-only first.
