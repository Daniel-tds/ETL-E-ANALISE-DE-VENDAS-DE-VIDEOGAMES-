import pandas as pd

df = pd.read_csv("vgsales.csv")

relatorio = []

relatorio.append({"verificacao": "Total de registros", "quantidade": len(df), "percentual": ""})

for col in df.columns:
    n = df[col].isnull().sum()
    if n > 0:
        relatorio.append({
            "verificacao": f"Nulos em '{col}'",
            "quantidade": n,
            "percentual": f"{100*n/len(df):.1f}%"
        })

duplicatas = df.duplicated(subset=["Name", "Platform", "Year"]).sum()
relatorio.append({"verificacao": "Lançamentos duplicados", "quantidade": duplicatas, "percentual": f"{100*duplicatas/len(df):.1f}%"})

sem_vendas = (df[["NA_Sales","EU_Sales","JP_Sales","Other_Sales"]].fillna(0).sum(axis=1) == 0).sum()
relatorio.append({"verificacao": "Registros sem vendas", "quantidade": sem_vendas, "percentual": f"{100*sem_vendas/len(df):.1f}%"})

pd.DataFrame(relatorio).to_csv("qualidade_dados.csv", index=False)
print("[OK] Relatório salvo em qualidade_dados.csv")