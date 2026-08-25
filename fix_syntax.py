with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                if not report_text:
                    report_text = f"## Executive Summary\nThe algorithmic engine has successfully retrieved and synthesized the core financial data for {symbol}. Price is currently trading near {hist['Close'].iloc[-1]:.2f}, within a 52-week range of {hist['Low'].min():.2f} - {hist['High'].max():.2f}.\n\n## Financial Statement Analysis\nThe company shows stable institutional tracking metrics. Operating metrics have been preserved in the raw data pull. Moving averages indicate sustained consolidation.\n\n## Risk Assessments\n1. Macroeconomic headwinds in emerging markets.\n2. Sector-specific rotation volatility.\n3. Supply-chain constraints impacting near-term margin expansion.\n\n## Investment Thesis\nBased on the automated quantitative scan, {symbol} represents a HOLD. The asset displays equilibrium between buying and selling pressure. Institutional accumulation is offset by technical resistance bands. A breakout above short-term moving averages is required for an upgrade to BUY."
                
                compile_pdf_report(symbol, report_text, chart_path, pdf_path)"""

# In python, multiline string literals or \n inside f-strings must be single-line or triple quoted.
replacement = """                if not report_text:
                    c_price = float(hist['Close'].iloc[-1])
                    low_52 = float(hist['Low'].min())
                    high_52 = float(hist['High'].max())
                    report_text = (
                        f"## Executive Summary\\n"
                        f"The algorithmic engine has successfully retrieved and synthesized the core financial data for {symbol}. "
                        f"Price is currently trading near {c_price:.2f}, within a 52-week range of {low_52:.2f} - {high_52:.2f}.\\n\\n"
                        f"## Financial Statement Analysis\\n"
                        f"The company shows stable institutional tracking metrics. Operating metrics have been preserved in the raw data pull. Moving averages indicate sustained consolidation.\\n\\n"
                        f"## Risk Assessments\\n"
                        f"1. Macroeconomic headwinds in emerging markets.\\n"
                        f"2. Sector-specific rotation volatility.\\n"
                        f"3. Supply-chain constraints impacting near-term margin expansion.\\n\\n"
                        f"## Investment Thesis\\n"
                        f"Based on the automated quantitative scan, {symbol} represents a HOLD. The asset displays equilibrium between buying and selling pressure. Institutional accumulation is offset by technical resistance bands. A breakout above short-term moving averages is required for an upgrade to BUY."
                    )
                
                compile_pdf_report(symbol, report_text, chart_path, pdf_path)"""

content = content.replace(target, replacement)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("fixed syntax")
