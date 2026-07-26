import requests
import json
import unicodedata
import time

def limpar_nome(texto):
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    # Deixa tudo maiúsculo
    texto = texto.upper()
    # Remove tudo que não for letra, número ou espaço
    limpo = "".join([c for c in texto if c.isalnum() or c.isspace()])
    # Limita o tamanho para o LCD do ESP32 (ex: 20 caracteres)
    return limpo.strip()[:20]

def gerar_top100_pais(sigla_pais, limite=100):
    # O arquivo será salvo como br_top100.json, us_top100.json, etc.
    nome_arquivo = f"{sigla_pais.lower()}_top100.json"
    
    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "countrycode": sigla_pais,
        "limit": limite,
        "order": "clickcount", # O segredo: ordena pelas mais ouvidas no mundo real
        "reverse": "true",
        "hidebroken": "true"   # Oculta links quebrados
    }

    # Cabeçalho para não ser bloqueado
    headers = {
        'User-Agent': 'FabaoSistemasRadioRadio/2.0'
    }

    try:
        resposta = requests.get(url, params=parametros, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            radios_brutas = resposta.json()
            lista_limpa = []
            
            for r in radios_brutas:
                nome_limpo = limpar_nome(r['name'])
                url_audio = r['url_resolved']
                
                # Só adiciona se tiver nome e link válidos
                if nome_limpo and url_audio:
                    lista_limpa.append({"n": nome_limpo, "u": url_audio})

            if lista_limpa:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(lista_limpa, f, ensure_ascii=True, separators=(',', ':'))
                print(f"✅ {nome_arquivo} salvo com sucesso ({len(lista_limpa)} rádios reais)")
            else:
                print(f"⚠️ Nenhuma rádio encontrada para a sigla {sigla_pais}")
        else:
            print(f"❌ Erro HTTP {resposta.status_code} no país {sigla_pais}")
            
    except Exception as e:
        print(f"❌ Timeout/Erro de conexão no país {sigla_pais}")

# --- MATRIZ DE 50 PAÍSES ESTRATÉGICOS ---
paises_50 = [
    # América do Sul (10)
    "BR", "AR", "UY", "CL", "CO", "PE", "VE", "EC", "PY", "BO",
    # América do Norte e Central (10)
    "US", "CA", "MX", "CU", "CR", "PA", "DO", "JM", "SV", "GT",
    # Europa (15)
    "GB", "FR", "DE", "IT", "ES", "PT", "NL", "SE", "CH", "AT", "BE", "IE", "GR", "PL", "RU",
    # Ásia (8)
    "JP", "KR", "CN", "IN", "ID", "PH", "TH", "VN",
    # Oceania e África (7)
    "AU", "NZ", "ZA", "EG", "NG", "KE", "MA"
]

if __name__ == "__main__":
    print("Iniciando varredura Fabão Sistemas: Top 100 Global em 50 Países...\n")
    
    for sigla in paises_50:
        print(f"\n--- País: {sigla} ---")
        gerar_top100_pais(sigla, limite=100)
        
        # Pausa cirúrgica de 1 segundo para poupar o servidor
        time.sleep(1.0)
        
    print("\n🎉 Varredura Top 100 Global finalizada com perfeição!")
