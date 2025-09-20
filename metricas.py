import glob
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from github import Github

# Caminho base
BASE_DIR = "results"

# Função para calcular estatísticas
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
        "Comentarios_total": df["locComment"].sum()
    }

# Coleta métricas do CK
resumos = []
for class_csv in glob.glob(os.path.join(BASE_DIR, "*class.csv")):
    repo = os.path.basename(class_csv).replace("class.csv", "")
    df_class = pd.read_csv(class_csv)
    resumo = resumo_metricas(df_class, repo)
    resumos.append(resumo)

df_final = pd.DataFrame(resumos)

# GitHub API
# Crie um token em https://github.com/settings/tokens e coloque aqui
g = Github("SEU_TOKEN")

def get_repo_info(repo_fullname):
    repo = g.get_repo(repo_fullname)
    created = repo.created_at
    idade = (datetime.now() - created).days / 365
    return {
        "estrelas": repo.stargazers_count,
        "releases": repo.get_releases().totalCount,
        "idade_anos": round(idade, 2)
    }

# Gráficos de correlação
# sns.pairplot(df_final[["CBO_media", "DIT_media", "LCOM_media", "estrelas", "releases", "idade_anos"]])
# plt.show()

# Exporta resultado
df_final.to_csv("resultado_final.csv", index=False)
