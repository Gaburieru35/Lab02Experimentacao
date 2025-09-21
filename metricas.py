import glob
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from github import Auth, Github

BASE_DIR = "results"

TOKEN = ""

# Função para calcular estatísticas do CK
def resumo_metricas(df, repo_name):
    return {
        "repo": repo_name,
        "CBO_media": df["cbo"].mean(),
        "CBO_mediana": df["cbo"].median(),
        "CBO_std": df["cbo"].std(),
        "DIT_media": df["dit"].mean(),
        "DIT_mediana": df["dit"].median(),
        "DIT_std": df["dit"].std(),
        "LCOM_media": df["lcom"].mean(),
        "LCOM_mediana": df["lcom"].median(),
        "LCOM_std": df["lcom"].std(),
        "LOC_total": df["loc"].sum(),
    }

resumos = []
for class_csv in glob.glob(os.path.join(BASE_DIR, "*class.csv")):
    repo = os.path.basename(class_csv).replace("class.csv", "")
    df_class = pd.read_csv(class_csv)
    resumo = resumo_metricas(df_class, repo)
    resumos.append(resumo)

df_final = pd.DataFrame(resumos)

# Se tiver token, coleta infos do GitHub (online)
if TOKEN:
    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)

    def get_repo_info(repo_fullname):
        repo = g.get_repo(repo_fullname)
        created = repo.created_at
        idade = (datetime.now() - created).days / 365
        return {
            "estrelas": repo.stargazers_count,
            "releases": repo.get_releases().totalCount,
            "idade_anos": round(idade, 2),
        }

    infos = []
    for repo_name in df_final["repo"]:
        try:
            info = get_repo_info(repo_name)
        except Exception as e:
            print(f"Erro ao coletar {repo_name}: {e}")
            info = {"estrelas": None, "releases": None, "idade_anos": None}
        infos.append(info)

    df_infos = pd.DataFrame(infos)
    df_final = pd.concat([df_final, df_infos], axis=1)

df_final.to_csv("resultado_final.csv", index=False)
print("Resultado salvo em resultado_final.csv")

cols_corr = ["CBO_media", "DIT_media", "LCOM_media", "LOC_total"]
if {"estrelas", "releases", "idade_anos"}.issubset(df_final.columns):
    cols_corr += ["estrelas", "releases", "idade_anos"]

sns.pairplot(df_final[cols_corr].dropna())
plt.savefig("correlacoes.png")
print("Gráfico salvo em correlacoes.png")
