# 🎙️ NewsVoice

Pipeline em Python que lê notícias da CNN, traduz do inglês para o português e gera narrações em áudio nos dois idiomas usando o [Kokoro TTS](https://github.com/hexgrad/kokoro), tudo salvo em um banco SQLite local.

## ✨ Funcionalidades

- Lê o feed RSS da CNN (seção *World*)
- Extrai o texto completo de cada artigo
- Traduz título e texto para português (Google Translate via `deep-translator`)
- Salva título, texto e link, em inglês e português, em um banco SQLite
- Gera dois áudios `.wav` por notícia (inglês e português) com o Kokoro TTS
- Tratamento de erro por notícia: se uma falhar, as demais continuam

## ⚙️ Como funciona

```
Feed RSS da CNN
      │
      ▼
Extração do artigo (newspaper)
      │
      ▼
Tradução EN → PT (deep-translator)
      │
      ├──► Salva no SQLite (noticias_cnn.db)
      │
      ▼
Narração com Kokoro TTS
      │
      ▼
audio_<id>_EN_kokoro.wav  +  audio_<id>_PT_kokoro.wav
```

## 📋 Requisitos

- Python 3.10 ou superior
- [espeak-ng](https://github.com/espeak-ng/espeak-ng) instalado no sistema (usado pelo Kokoro)
- Conexão com a internet (feed RSS, download dos artigos e tradução)

## 🚀 Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/newsvoice.git
   cd newsvoice
   ```

2. (Opcional) Crie um ambiente virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install feedparser newspaper3k lxml_html_clean deep-translator kokoro soundfile numpy
   ```

4. Instale o `espeak-ng`:

   - **Windows:** baixe o instalador `.msi` na página de releases do projeto
   - **Ubuntu/Debian:** `sudo apt install espeak-ng`
   - **macOS:** `brew install espeak-ng`

> Na primeira execução, o Kokoro baixa os modelos de voz automaticamente, então ela pode demorar mais.

## ▶️ Uso

Execute o script:

```bash
python main.py
```

> Ajuste o nome `main.py` para o nome real do seu arquivo.

Por padrão, o script processa as **3 primeiras notícias** do feed. Para mudar a quantidade, edite o final do arquivo:

```python
if __name__ == "__main__":
    quantidade = 3  # altere aqui
    coletar_traduzir_e_narrar(quantidade)
```

## 🔧 Configuração

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `VOZ_EN` | `af_sky` | Voz em inglês (opções: `af_bella`, `af_sky`) |
| `VOZ_PT` | `pm_santa` | Voz em português (opções: `pm_santa`, `pm_alex`, `pf_dora`) |
| `url_rss` | CNN World | Endereço do feed RSS usado como fonte |

## 📁 Saída gerada

```
.
├── noticias_cnn.db              # banco SQLite com as notícias
├── audio_1_EN_kokoro.wav        # narração em inglês da notícia 1
├── audio_1_PT_kokoro.wav        # narração em português da notícia 1
├── audio_2_EN_kokoro.wav
├── audio_2_PT_kokoro.wav
└── ...
```

### Estrutura da tabela `noticias`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | Identificador (usado no nome dos áudios) |
| `titulo_en` | TEXT | Título original em inglês |
| `texto_en` | TEXT | Texto original completo |
| `titulo_pt` | TEXT | Título traduzido |
| `texto_pt` | TEXT | Texto traduzido |
| `link` | TEXT | Link da notícia original |

## ⚠️ Limitações conhecidas

- O texto é truncado em 4.900 caracteres antes da tradução (limite do Google Translate), podendo cortar no meio de uma frase
- O banco guarda o texto em inglês completo, mas a tradução cobre apenas os primeiros 4.900 caracteres
- Rodar o script novamente insere as mesmas notícias outra vez (não há checagem de duplicatas)
- Alguns sites bloqueiam o download automático e, nesse caso, a notícia é ignorada
- O feed `rss.cnn.com` pode retornar poucas entradas ou conteúdo desatualizado
- Os arquivos `.wav` não são comprimidos e podem ocupar bastante espaço

## 🗺️ Próximos passos

- [ ] Evitar notícias duplicadas (checar o `link` no banco)
- [ ] Dividir o texto por frases em vez de cortar por caracteres
- [ ] Gravar o caminho dos áudios no banco de dados
- [ ] Exportar em MP3 para reduzir o tamanho dos arquivos
- [ ] Agendar a execução diária
- [ ] Criar uma interface simples para ouvir as notícias

## 🛠️ Tecnologias

- [feedparser](https://github.com/kurtmckee/feedparser): leitura do feed RSS
- [newspaper3k](https://github.com/codelucas/newspaper): extração de artigos
- [deep-translator](https://github.com/nidhaloff/deep-translator): tradução
- [Kokoro TTS](https://github.com/hexgrad/kokoro): síntese de voz
- [SQLite](https://www.sqlite.org/): armazenamento local

## 📄 Licença

Defina a licença do projeto (por exemplo, MIT).

> Este projeto é de uso pessoal e educacional. O conteúdo das notícias pertence à CNN e aos respectivos autores.
