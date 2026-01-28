# 🌙 Bianca Bot - Telegram + IA

Bot de companhia virtual com personalidade enigmática, integrado com Claude AI (Anthropic) e sistema de assinatura premium.

## ✨ Funcionalidades

### 🤖 IA Conversacional
- Personalidade única e enigmática (Bianca, 24 anos, de Ribeirão Preto)
- Respostas contextuais usando Claude AI (Anthropic)
- Memória de conversas (últimas 15 mensagens)
- Detecção de humor do usuário (triste, feliz, flertando, etc.)

### 💰 Sistema de Monetização
- **Usuários Grátis**: 10 mensagens por dia
- **Premium**: Mensagens ilimitadas por R$ 14,99/7 dias
- Gatilhos inteligentes de conversão
- Paywall para conteúdo exclusivo

### 🎯 Engajamento Automático
- Boas-vindas personalizadas
- Re-engajamento de usuários inativos (3 níveis)
- Mensagens de bom dia/boa noite automáticas
- Sistema de "ciúmes" para usuários que voltam

### 📊 Gestão de Usuários
- Banco de dados JSON local
- Tracking de mensagens e status premium
- Histórico de conversas
- Reset automático de contadores diários

## 🚀 Instalação

### 1. Requisitos
- Python 3.8 ou superior
- Conta no Telegram
- Conta na Anthropic (para API do Claude)

### 2. Clone ou Baixe os Arquivos

```bash
# Estrutura de arquivos:
bianca-bot/
├── main.py                 # Inicializador principal
├── bianca_bot.py          # Lógica principal do bot
├── config.py              # Configurações e mensagens
├── reengagement.py        # Sistema de re-engajamento
├── requirements.txt       # Dependências
├── .env.example          # Template de variáveis de ambiente
└── README.md             # Este arquivo
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Credenciais

#### a) Crie seu Bot no Telegram
1. Abra o Telegram e fale com [@BotFather](https://t.me/BotFather)
2. Envie `/newbot`
3. Escolha um nome e username para o bot
4. Copie o **token** fornecido

#### b) Obtenha a API Key da Anthropic
1. Acesse [console.anthropic.com](https://console.anthropic.com/)
2. Crie uma conta ou faça login
3. Vá em "API Keys" e crie uma nova chave
4. Copie a chave API

#### c) Configure o arquivo .env
```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env e adicione suas credenciais:
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
PIX_KEY=seupix@email.com
```

### 5. Execute o Bot

```bash
# Bot principal
python main.py

# Sistema de re-engajamento (em outra janela/terminal)
python reengagement.py
```

## 📱 Como Usar

### Comandos Disponíveis

- `/start` - Inicia conversa com Bianca
- `/premium` - Informações sobre assinatura premium
- `/ativar` - Ativa premium (apenas para teste)

### Fluxo do Usuário

1. **Primeira Conversa**
   - Usuário inicia com `/start`
   - Bianca se apresenta de forma misteriosa
   - Pergunta sobre intenções do usuário

2. **Conversação Grátis**
   - Até 10 mensagens por dia
   - Avisos quando restarem poucas mensagens
   - IA responde com personalidade enigmática

3. **Limite Atingido**
   - Mensagem de paywall com oferta premium
   - Informações sobre benefícios
   - Instruções de pagamento via PIX

4. **Usuário Premium**
   - Mensagens ilimitadas
   - Acesso a "conteúdo exclusivo"
   - Respostas mais íntimas e personalizadas

## 🔧 Configurações

Edite `config.py` para personalizar:

```python
CONFIG = {
    "nome_bot": "Bianca",
    "limite_diario_gratis": 10,    # Mensagens grátis por dia
    "dias_premium": 7,              # Duração da assinatura
    "preco_premium": "R$ 14,99",    # Preço
    "max_memoria": 15,              # Mensagens mantidas em contexto
}
```

## 🎭 Personalidade da Bianca

A Bianca foi projetada para ser:
- **Enigmática**: Não entrega tudo de cara
- **Misteriosa**: Usa pausas dramáticas ("...")
- **Artística**: Curte música indie, tatuagens
- **Provocadora**: Mas sempre elegante
- **Intensa**: Quando gosta, gosta de verdade

### Emojis Favoritos
🌙 ✨ 🖤 🔮 💫

### Tom de Voz
- Respostas curtas (1-3 frases)
- Máximo 25 palavras
- Usa "hm...", "então...", "interessante..."
- Gírias sutis: "tô ligada", "faz sentido"

## 💳 Sistema de Pagamento

### Fluxo de Pagamento
1. Usuário demonstra interesse em premium
2. Bot envia informações e chave PIX
3. Usuário realiza pagamento
4. Envia comprovante para o admin
5. Admin ativa premium com `/ativar` (ou automaticamente com webhook)

### Implementação de Webhook (Opcional)
Para automação completa, integre com:
- **Mercado Pago API**
- **Pagar.me**
- **Asaas**
- Ou outro gateway que suporte PIX

## 🔄 Sistema de Re-engajamento

### Níveis de Inatividade
- **2 horas**: "Ei... sumiu 🌙"
- **24 horas**: "Um dia inteiro... senti falta 🖤"
- **72 horas**: "3 dias... 💫 Pensei que a gente tinha algo."
- **Última tentativa**: Pausa envios

### Mensagens Automáticas
- **Bom dia** (7h-9h): Para usuários ativos
- **Boa noite** (22h-23h): Para quem conversou hoje
- **Reset diário**: Meia-noite (00h)

## 📊 Dados do Usuário

Armazenados em `users_data.json`:

```json
{
  "user_id": {
    "is_premium": false,
    "premium_until": null,
    "messages_today": 5,
    "total_messages": 127,
    "conversation_history": [...],
    "user_name": "João",
    "last_message": "2025-01-27T15:30:00",
    "reengagement_count": 0
  }
}
```

## ⚠️ Avisos Importantes

### Ética e Legalidade
- ✅ Este é um bot de entretenimento/companhia virtual
- ⚠️ Deixe claro que é uma IA, não uma pessoa real
- ⚠️ Nunca prometa encontros presenciais
- ⚠️ Respeite leis locais sobre conteúdo adulto
- ⚠️ Implemente verificação de idade se necessário

### Segurança
- Nunca compartilhe suas credenciais (tokens, API keys)
- Use `.env` para variáveis sensíveis
- Adicione `.env` ao `.gitignore` se usar Git
- Faça backups regulares de `users_data.json`

### Custos
- **Telegram**: Grátis
- **Anthropic API**: Pago por uso (veja preços em console.anthropic.com)
- Monitore uso da API para evitar custos inesperados

## 🛠️ Troubleshooting

### Bot não responde
```bash
# Verifique se o token está correto
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_TOKEN'))"

# Teste conexão com Telegram
curl https://api.telegram.org/bot<SEU_TOKEN>/getMe
```

### Erro na API Anthropic
- Verifique saldo de créditos
- Confirme que a chave API está ativa
- Veja logs de erro para detalhes

### Mensagens não são salvas
- Verifique permissões de escrita na pasta
- Confirme que `users_data.json` existe

## 📈 Próximas Melhorias

- [ ] Dashboard web para administração
- [ ] Integração com gateway de pagamento
- [ ] Análise de métricas (conversão, retenção)
- [ ] Múltiplas personalidades/bots
- [ ] Sistema de referral/afiliados
- [ ] Conteúdo multimídia (fotos, áudios)

## 📄 Licença

Este código é fornecido como exemplo educacional. Use com responsabilidade.

## 🤝 Suporte

Para dúvidas ou problemas:
1. Revise este README
2. Verifique logs de erro
3. Consulte documentação oficial:
   - [python-telegram-bot](https://docs.python-telegram-bot.org/)
   - [Anthropic API](https://docs.anthropic.com/)

---

Desenvolvido com 🌙 para demonstração de bots conversacionais com IA
