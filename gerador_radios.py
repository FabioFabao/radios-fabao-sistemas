import requests
import json
import unicodedata
import os
import time

# Função que arranca acentos e limpa o nome para o LCD não travar
def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.upper()
    limpo = "".join([c for c in texto if c.isalnum() or c.isspace()])
    return limpo.strip()[:20]

def gerar_lista(sigla_pais, nome_pais, genero, limite=20):
    # Salva usando a sigla do país para economizar RAM no ESP32 (ex: br_rock.json, us_jazz.json)
    nome_arquivo = f"{sigla_pais.lower()}_{genero}.json"
    
    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "country": nome_pais,
        "tag": genero,
        "limit": limite,
        "order": "votes",
        "reverse": "true",
        "hidebroken": "true"
    }

    try:
        resposta = requests.get(url, params=parametros, timeout=10)
        
        if resposta.status_code == 200:
            radios_brutas = resposta.json()
            lista_limpa = []
            
            for r in radios_brutas:
                nome_limpo = limpar_nome(r['name'])
                url_audio = r['url_resolved']
                
                # Só adiciona se o nome não ficou vazio
                if nome_limpo:
                    lista_limpa.append({"n": nome_limpo, "u": url_audio})

            # Se encontrou rádios online para essa combinação, cria o arquivo
            if lista_limpa:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(lista_limpa, f, ensure_ascii=True, separators=(',', ':'))
                print(f"✅ {nome_arquivo} salvo ({len(lista_limpa)} rádios)")
            else:
                print(f"⚠️ Nenhuma rádio encontrada para {nome_pais} - {genero}")
                
        else:
            print(f"❌ Erro na API (Cod: {resposta.status_code}) para {nome_pais} - {genero}")
            
    except Exception as e:
        print(f"❌ Falha de conexão ao buscar {nome_pais} - {genero}")

# --- MATRIZ GLOBAL DE PAÍSES (31 Países) ---
paises = {
    # América do Sul e Central
    "BR": "Brazil", "AR": "Argentina", "UY": "Uruguay", "CL": "Chile", 
    "CO": "Colombia", "PE": "Peru", "VE": "Venezuela", "MX": "Mexico",
    # América do Norte
    "US": "United States", "CA": "Canada",
    # Europa
    "GB": "United Kingdom", "FR": "France", "DE": "Germany", "IT": "Italy", 
    "ES": "Spain", "PT": "Portugal", "NL": "Netherlands", "SE": "Sweden", 
    "CH": "Switzerland", "AT": "Austria", "BE": "Belgium", "IE": "Ireland",
    "GR": "Greece", "PL": "Poland", "RU": "Russia",
    # Ásia, Oceania e África
    "JP": "Japan", "KR": "South Korea", "CN": "China", 
    "IN": "India", "AU": "Australia", "ZA": "South Africa"
}

# --- MATRIZ DE GÊNEROS (16 Gêneros) ---
generos = [
    "pop", "rock", "jazz", "classical", "news", "sports", 
    "electronic", "dance", "hiphop", "reggae", "blues", 
    "country", "80s", "90s", "talk", "latin"
]

if __name__ == "__main__":
    print("Iniciando varredura global das rádios Fabão Sistemas...\n")
    
    total_arquivos = 0
    
    for sigla, pais in paises.items():
        print(f"\n--- Processando: {pais} ---")
        for genero in generos:
            gerar_lista(sigla, pais, genero, limite=20)
            total_arquivos += 1
            
            # Trava de segurança obrigatória: 0.5s de pausa
            # Evita que a API do Radio Browser bloqueie o robô por ataque de DDoS (muitos acessos por segundo)
            time.sleep(0.5) 
            
    print(f"\n🎉 Varredura completa! O robô tentou gerar {total_arquivos} arquivos.")
