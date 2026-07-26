import requests
import json
import unicodedata
import time

def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.upper()
    limpo = "".join([c for c in texto if c.isalnum() or c.isspace()])
    return limpo.strip()[:20]

def gerar_top150_pais(sigla_pais, limite=150):
    nome_arquivo = f"{sigla_pais.lower()}_top150.json"
    lista_final = []
    
    # O SEGREDO CONTRA REPETIÇÕES: Guardar o que já passou pelo crivo
    nomes_vistos = set()
    urls_vistas = set()

    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "countrycode": sigla_pais,
        "countryexact": "true", 
        "limit": 500,           # Puxa 500 cruas para ter mais material limpo
        "order": "votes",       
        "reverse": "true",
        "hidebroken": "true"
    }
    
    headers = {'User-Agent': 'FabaoSistemasRadio/6.0'}

    try:
        resposta = requests.get(url, params=parametros, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            radios_brutas = resposta.json()
            
            for r in radios_brutas:
                if r.get('countrycode', '').upper() == sigla_pais:
                    nome_limpo = limpar_nome(r['name'])
                    url_audio = r['url_resolved']
                    
                    # Trava 3: Guilhotina dupla (Nome único E Link único)
                    if nome_limpo and url_audio:
                        if nome_limpo not in nomes_vistos and url_audio not in urls_vistas:
                            
                            lista_final.append({"n": nome_limpo, "u": url_audio})
                            nomes_vistos.add(nome_limpo)
                            urls_vistas.add(url_audio)
                            
                            # Para de adicionar assim que bater a meta
                            if len(lista_final) == limite:
                                break

            if lista_final:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(lista_final, f, ensure_ascii=True, separators=(',', ':'))
                print(f"✅ {nome_arquivo} salvo: {len(lista_final)} rádios ÚNICAS.")
            else:
                print(f"⚠️ Nenhuma rádio validada para a sigla {sigla_pais}")
        else:
            print(f"❌ Erro HTTP {resposta.status_code} no país {sigla_pais}")
            
    except Exception as e:
        print(f"❌ Timeout/Erro de conexão no país {sigla_pais}")

# --- MATRIZ DOS 50 PAÍSES ---
paises_50 = [
    "BR", "AR", "UY", "CL", "CO", "PE", "VE", "EC", "PY", "BO",
    "US", "CA", "MX", "CU", "CR", "PA", "DO", "JM", "SV", "GT",
    "GB", "FR", "DE", "IT", "ES", "PT", "NL", "SE", "CH", "AT", "BE", "IE", "GR", "PL", "RU",
    "JP", "KR", "CN", "IN", "ID", "PH", "TH", "VN",
    "AU", "NZ", "ZA", "EG", "NG", "KE", "MA"
]

if __name__ == "__main__":
    print("Iniciando varredura Fabão Sistemas: Filtro Anti-Repetição Absoluto...\n")
    
    for sigla in paises_50:
        print(f"\n--- País: {sigla} ---")
        gerar_top150_pais(sigla, limite=150)
        time.sleep(1.0)
        
    print("\n🎉 Varredura finalizada com sucesso. Zero duplicatas!")
