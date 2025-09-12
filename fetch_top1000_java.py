import os, sys, time, csv
import requests
from datetime import datetime

TOKEN = ""
if not TOKEN:
    print("Defina a variável de ambiente GITHUB_TOKEN com seu personal access token")
    sys.exit(1)

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
PER_PAGE = 100
OUT = "top1000_java.csv"

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "full_name","stars","html_url","created_at","updated_at","size","language",
        "age_years","num_releases"
    ])

    for page in range(1, 11):  # 10 pages x 100 = 1000
        q = "language:java"
        url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={PER_PAGE}&page={page}"
        print(f"GET {url}")
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print("Erro na API:", r.status_code, r.text)
            sys.exit(1)
        data = r.json()
        items = data.get("items", [])
        if not items:
            print("Nenhum item retornado na página", page)
            break

        for it in items:
            # Calcular idade em anos
            created_at = it.get("created_at")
            created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            age_years = round((datetime.utcnow() - created_date).days / 365.25, 2)

            # Pegar número de releases
            releases_url = it.get("releases_url").replace("{/id}", "")
            r_rel = requests.get(releases_url, headers=HEADERS)
            num_releases = len(r_rel.json()) if r_rel.status_code == 200 else 0

            writer.writerow([
                it.get("full_name"),
                it.get("stargazers_count"),
                it.get("html_url"),
                it.get("created_at"),
                it.get("updated_at"),
                it.get("size"),
                it.get("language"),
                age_years,
                num_releases
            ])

        # Evitar limite de rate limit
        time.sleep(1.0)

print("Arquivo gerado:", OUT)