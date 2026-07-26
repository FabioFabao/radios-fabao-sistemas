import requests
import json
import unicodedata
import time

def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.upper()
    limpo = "".join([c for c in texto if c.isalnum() or c.isspace()])
    return limpo.strip()[:20]

# O "Sniper": Função que busca apenas a sua rádio favorita para atualizar o link
def buscar_radio_vip(sigla_pais, nome_busca):
    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "countrycode": sigla_pais,
        "name": nome_busca,
        "limit": 1,          # Só precisa achar 1 (a oficial)
        "hidebroken": "true" # Garante que o link está vivo hoje
    }
    headers = {'User-Agent': 'FabaoSistemasRadioRadio/3.0'}
    
    try:
        resposta = requests.get(url, params=parametros, headers=headers, timeout=5)
        if resposta.status_code == 200:
            radios = resposta.json()
            if radios:
                r = radios[0]
                nome_limpo = limpar_nome(r['name'])
                # Se o nome limpado ficar vazio, forçamos o nome da busca
                if not nome_limpo: 
                    nome_limpo = limpar_nome(nome_busca)
                return {"n": nome_limpo, "u": r['url_resolved']}
    except Exception:
        pass
    return None # Retorna vazio se der erro ou a rádio estiver fora do ar

def gerar_top150_pais(sigla_pais, limite=150):
    nome_arquivo = f"{sigla_pais.lower()}_top150.json"
    lista_final = []

    # --- A MÁGICA VIP ACONTECE AQUI ---
    # Se for Brasil, busca a 80 FM primeiro
    if sigla_pais == "BR":
        vip = buscar_radio_vip("BR", "80 FM")
        if vip:
            lista_final.append(vip)
            print("⭐ Rádio VIP '80 FM' garantida no topo absoluto do Brasil!")
    
    # Se for Chile, busca a Festiva primeiro
    if sigla_pais == "CL":
        vip = buscar_radio_vip("CL", "Festiva")
        if vip:
            lista_final.append(vip)
            print("⭐ Rádio VIP 'Festiva FM' garantida no topo absoluto do Chile!")

    # --- AGORA BUSCA AS TOP 150 ---
    url = "https://de1.api.radio-browser.info/json/stations/search"
    parametros = {
        "countrycode": sigla_pais,
        "limit": limite,
        "order": "clickcount",
        "reverse": "true",
        "hidebroken": "true"
    }
    headers = {'User-Agent': 'FabaoSistemasRadioRadio/3.0'}

    try:
        resposta = requests.get(url, params=parametros, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            radios_brutas = resposta.json()
            
            for r in radios_brutas:
                nome_limpo = limpar_nome(r['name'])
                url_audio = r['url_resolved']
                
                if nome_limpo and url_audio:
                    item = {"n": nome_limpo, "u": url_audio}
                    # Trava de segurança: Evita duplicar a rádio VIP se ela já for uma das top 150
                    if item not in lista_final:
                        lista_final.append(item)

            if lista_final:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(lista_final, f, ensure_ascii=True, separators=(',', ':'))
                print(f"✅ {nome_arquivo} salvo com sucesso ({len(lista_final)} rádios)")
            else:
                print(f"⚠️ Nenhuma rádio encontrada para a sigla {sigla_pais}")
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
    print("Iniciando varredura Fabão Sistemas: VIPs e Top 150 Global...\n")
    
    for sigla in paises_50:
        print(f"\n--- País: {sigla} ---")
        gerar_top150_pais(sigla, limite=150)
        time.sleep(1.0)
        
    print("\n🎉 Varredura finalizada com perfeição!")
