import sqlite3
import feedparser
import os
import numpy as np
import soundfile as sf
from newspaper import Article
from deep_translator import GoogleTranslator
from kokoro import KPipeline

# --- Configurações das Vozes do Kokoro ---
# Inglês (lang_code='a'): af_bella, af_sky
VOZ_EN = 'af_sky' 

# Português (lang_code='p'): pm_santa, pm_alex, pf_dora
VOZ_PT = 'pm_santa'  

def inicializar_base_dados():
    """Cria a base de dados SQLite e a tabela, se não existirem."""
    conn = sqlite3.connect('noticias_cnn.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_en TEXT,
            texto_en TEXT,
            titulo_pt TEXT,
            texto_pt TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    return conn

def gerar_audio_kokoro(texto, pipeline, voz, arquivo_saida):
    """Gera áudio usando Kokoro TTS e junta todas as frases em um único arquivo .wav"""
    print(f"Gerando áudio ({arquivo_saida}) com a voz {voz}...")
    try:
        # O Kokoro quebra textos longos em pedaços e gera áudio para cada um
        generator = pipeline(texto, voice=voz, speed=1)
        
        pedacos_de_audio = []
        for gs, ps, audio in generator:
            if audio is not None:
                pedacos_de_audio.append(audio)
        
        if pedacos_de_audio:
            # Junta todos os pedaços num áudio só usando numpy
            audio_completo = np.concatenate(pedacos_de_audio)
            
            # Salva o arquivo final
            sf.write(arquivo_saida, audio_completo, 24000)
            print(f" -> SUCESSO! Áudio salvo: {arquivo_saida}")
        else:
            print(" -> ERRO: O modelo Kokoro não retornou nenhum áudio.")
            
    except Exception as e:
        print(f" -> ERRO no Kokoro: {e}")

def coletar_traduzir_e_narrar(n_noticias):
    # 1. Preparar a Base de Dados e Tradutor
    conn = inicializar_base_dados()
    cursor = conn.cursor()
    tradutor = GoogleTranslator(source='auto', target='pt')
    
    # 2. Iniciar as Pipelines do Kokoro (Isso pode levar alguns segundos)
    print("Carregando modelos Kokoro na memória (Aguarde)...")
    pipeline_en = KPipeline(lang_code='a') # 'a' para American English
    pipeline_pt = KPipeline(lang_code='p') # 'p' para Português
    print("Modelos carregados!\n")
    
    url_rss = "http://rss.cnn.com/rss/edition_world.rss"
    print(f"Lendo o feed RSS: {url_rss}")
    feed = feedparser.parse(url_rss)
    
    entradas = feed.entries[:n_noticias]
    
    for i, entrada in enumerate(entradas, 1):
        titulo_en = entrada.title
        link_rss = entrada.link
        
        print(f"\n[{i}/{len(entradas)}] Processando: {titulo_en}")
        
        try:
            # 3. Extrair o texto original (Inglês)
            artigo = Article(link_rss)
            artigo.download()
            artigo.parse()
            texto_en = artigo.text
            
            texto_en_truncado = texto_en[:4900] if len(texto_en) > 4900 else texto_en
            
            if not texto_en_truncado.strip():
                print(" -> Artigo vazio ou bloqueado, pulando...")
                continue

            # 4. Traduzir para Português
            print(" -> Traduzindo para português...")
            titulo_pt = tradutor.translate(titulo_en)
            texto_pt = tradutor.translate(texto_en_truncado)
            
            # 5. Salvar no SQLite
            cursor.execute('''
                INSERT INTO noticias (titulo_en, texto_en, titulo_pt, texto_pt, link)
                VALUES (?, ?, ?, ?, ?)
            ''', (titulo_en, texto_en, titulo_pt, texto_pt, link_rss))
            conn.commit()
            print(" -> Salvo no banco de dados!")
            
            # 6. Gerar os Áudios com Kokoro
            id_noticia = cursor.lastrowid
            audio_en_nome = f"audio_{id_noticia}_EN_kokoro.wav"
            audio_pt_nome = f"audio_{id_noticia}_PT_kokoro.wav"
            
            # Removi o limite de [:1000] que tínhamos no Piper. 
            # Como o Kokoro lida bem com textos por pedaços no loop interno, 
            # ele pode narrar a notícia toda com mais tranquilidade.
            texto_fala_en = f"News Title: {titulo_en}. {texto_en_truncado}"
            texto_fala_pt = f"Título da notícia: {titulo_pt}. {texto_pt}"
            
            gerar_audio_kokoro(texto_fala_en, pipeline_en, VOZ_EN, audio_en_nome)
            gerar_audio_kokoro(texto_fala_pt, pipeline_pt, VOZ_PT, audio_pt_nome)
            
        except Exception as e:
            print(f" -> Ocorreu um erro ao processar: {e}")

    conn.close()
    print("\nProcesso concluído! Banco de dados e áudios gerados com Kokoro.")

if __name__ == "__main__":
    quantidade = 3
    coletar_traduzir_e_narrar(quantidade)