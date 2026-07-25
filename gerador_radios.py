import requests
import json
import unicodedata
import time

def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.upper()
    limpo = "".join([c for c in texto if c.isalnum() or c.isspace()])
    return limpo.strip()[:20]

def gerar_lista(sigla_pais, genero, limite=15):
    nome_arquivo = f"{sigla_pais.lower()}_{genero}.json"
    
    # Usando o endpoint raiz recomendado com o filtro correto por código de país
    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "countrycode": sigla_pais, # Sigla exata (BR, US, AR, etc.)
        "tag": genero,
        "limit": limite,
        "order": "votes",
        "reverse": "true",
        "hidebroken": "true"
    }

    # Cabeçalho obrigatório exigido pela documentação do Radio Browser para evitar bloqueio
    headers = {
        'User-Agent': 'FabaoSistemasRadioRadio/1.0'
    }

    try:
        resposta = requests.get(url, params=parametros, headers=headers, timeout=8)
        
        if resposta.status_code == 200:
            radios_brutas = resposta.json()
            lista_limpa = []
            
            for r in radios_brutas:
                nome_limpo = limpar_nome(r['name'])
                url_audio = r['url_resolved']
                if nome_limpo and url_audio:
                    lista_limpa.append({"n": nome_limpo, "u": url_audio})

            if lista_limpa:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(lista_limpa, f, ensure_ascii=True, separators=(',', ':'))
                print(f"✅ {nome_arquivo} salvo ({len(lista_limpa)} rádios)")
            else:
                print(f"⚠️ Vazio para {sigla_pais} - {genero}")
        else:
            print(f"❌ Erro HTTP {resposta.status_code} em {sigla_pais} - {genero}")
            
    except Exception as e:
        print(f"❌ Timeout/Erro em {sigla_pais} - {genero}")

# --- LISTA FOCO (Os principais países de alta demanda para o seu produto) ---
paises_foco = [
    "BR", "AR", "UY", "CL", "CO", "MX", "US", "CA", 
    "GB", "FR", "DE", "IT", "ES", "PT", "JP", "KR"
]

# --- GÊNEROS ESSENCIAIS ---
generos_foco = [
    "pop", "rock", "jazz", "classical", "news", 
    "electronic", "hiphop", "country", "80s", "latin"
]

if __name__ == "__main__":
    print("Iniciando varredura otimizada Fabão Sistemas...\n")
    
    for sigla in paises_foco:
        print(f"\n--- País: {sigla} ---")
        for genero in generos_foco:
            gerar_lista(sigla, genero, limite=15)
            # Pausa segura de 1 segundo para o servidor não banir o IP do GitHub
            time.sleep(1.0)
            
    print("\n🎉 Varredura otimizada finalizada com sucesso!")
