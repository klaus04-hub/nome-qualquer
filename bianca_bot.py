"""
Bianca Bot - Telegram + IA
Bot de Companhia Virtual com Sistema de Assinatura
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# Imports do Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configuração da API da Anthropic (Claude)
import anthropic

# ================= CONFIGURAÇÕES =================
from config import *

# ================= CLASSE DE GERENCIAMENTO DE USUÁRIOS =================

class UserManager:
    """Gerencia dados dos usuários"""
    
    def __init__(self):
        self.users_file = "users_data.json"
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Carrega dados dos usuários do arquivo"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Salva dados dos usuários no arquivo"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def get_user(self, user_id: str) -> Dict:
        """Retorna dados do usuário"""
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "is_premium": False,
                "premium_until": None,
                "messages_today": 0,
                "total_messages": 0,
                "last_message": None,
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "user_name": None,
                "reengagement_count": 0,
                "last_reengagement": None,
                "warned_low_messages": False,
                "interests": [],
                "mood_detected": None
            }
            self._save_users()
        return self.users[user_id]
    
    def update_user(self, user_id: str, data: Dict):
        """Atualiza dados do usuário"""
        user = self.get_user(user_id)
        user.update(data)
        self._save_users()
    
    def add_message_to_history(self, user_id: str, role: str, content: str):
        """Adiciona mensagem ao histórico"""
        user = self.get_user(user_id)
        user["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantém apenas as últimas N mensagens
        if len(user["conversation_history"]) > CONFIG["max_memoria"] * 2:
            user["conversation_history"] = user["conversation_history"][-CONFIG["max_memoria"] * 2:]
        
        self._save_users()
    
    def increment_messages(self, user_id: str) -> int:
        """Incrementa contador de mensagens e retorna total do dia"""
        user = self.get_user(user_id)
        user["messages_today"] += 1
        user["total_messages"] += 1
        user["last_message"] = datetime.now().isoformat()
        self._save_users()
        return user["messages_today"]
    
    def reset_daily_messages(self, user_id: str):
        """Reseta contador diário de mensagens"""
        user = self.get_user(user_id)
        user["messages_today"] = 0
        user["warned_low_messages"] = False
        self._save_users()
    
    def set_premium(self, user_id: str, days: int = 7):
        """Define usuário como premium"""
        user = self.get_user(user_id)
        user["is_premium"] = True
        user["premium_until"] = (datetime.now() + timedelta(days=days)).isoformat()
        user["messages_today"] = 0  # Reset contador
        self._save_users()
    
    def check_premium_expired(self, user_id: str) -> bool:
        """Verifica se premium expirou"""
        user = self.get_user(user_id)
        if user["is_premium"] and user["premium_until"]:
            if datetime.fromisoformat(user["premium_until"]) < datetime.now():
                user["is_premium"] = False
                self._save_users()
                return True
        return False


# ================= CLASSE DO BOT =================

class BiancaBot:
    """Bot principal com IA"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str):
        self.telegram_token = telegram_token
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.user_manager = UserManager()
    
    def _get_periodo_dia(self) -> tuple:
        """Retorna período do dia e contexto"""
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            return "manhã", "Início do dia, energia renovada"
        elif 12 <= hora < 18:
            return "tarde", "Metade do dia, momento de pausa"
        elif 18 <= hora < 23:
            return "noite", "Fim do dia, hora de relaxar"
        else:
            return "madrugada", "Horas silenciosas, momento íntimo"
    
    def _detect_mood(self, message: str) -> Optional[str]:
        """Detecta humor do usuário baseado em keywords"""
        message_lower = message.lower()
        
        for mood, keywords in MOOD_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return mood
        return None
    
    def _check_premium_triggers(self, message: str) -> bool:
        """Verifica se mensagem contém gatilhos de interesse em premium"""
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in PREMIUM_TRIGGER_WORDS)
    
    def _check_hot_keywords(self, message: str) -> bool:
        """Verifica se mensagem contém keywords quentes (paywall)"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in HOT_KEYWORDS)
    
    def _build_system_prompt(self, user_id: str) -> str:
        """Constrói o prompt do sistema com contexto do usuário"""
        user = self.user_manager.get_user(user_id)
        periodo, contexto = self._get_periodo_dia()
        
        status_usuario = "Premium ✨" if user["is_premium"] else f"Grátis ({user['messages_today']}/{CONFIG['limite_diario_gratis']} msgs)"
        
        prompt = PERSONA_PROMPT.format(
            periodo=periodo,
            contexto_horario=contexto,
            status_usuario=status_usuario
        )
        
        # Adiciona detecção de humor se houver
        if user.get("mood_detected"):
            prompt += MOOD_RESPONSES.get(user["mood_detected"], "")
        
        return prompt
    
    async def _get_ai_response(self, user_id: str, user_message: str) -> str:
        """Obtém resposta da IA (Claude)"""
        user = self.user_manager.get_user(user_id)
        
        # Constrói histórico de mensagens para contexto
        messages = []
        for msg in user["conversation_history"][-10:]:  # Últimas 10 mensagens
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Adiciona mensagem atual
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Chama API da Anthropic
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,  # Respostas curtas
                system=self._build_system_prompt(user_id),
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Erro na API: {e}")
            return "Hm... tive um problema aqui. Me manda de novo? 🌙"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /start"""
        user_id = str(update.effective_user.id)
        user = self.user_manager.get_user(user_id)
        
        # Verifica se é primeira vez
        if user["total_messages"] == 0:
            await update.message.reply_text(WELCOME_MESSAGE)
            
            # Aguarda um pouco e envia pergunta de abertura
            await asyncio.sleep(2)
            
            keyboard = [
                [InlineKeyboardButton("🌙 Conversar de verdade", callback_data="opener_conversar")],
                [InlineKeyboardButton("🔥 Algo mais intenso", callback_data="opener_intenso")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                OPENER_QUESTION,
                reply_markup=reply_markup
            )
        else:
            # Usuário retornando
            if user["is_premium"]:
                await update.message.reply_text(f"Oi de novo, especial... 🌙\n\nSenti sua falta ✨")
            else:
                await update.message.reply_text(f"Oi... voltou! 💫\n\nComo você tá?")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para botões inline"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        
        if query.data == "opener_conversar":
            await query.message.reply_text(OPENER_CONVERSAR)
        elif query.data == "opener_intenso":
            await query.message.reply_text(OPENER_INTENSO)
        elif query.data == "premium_info":
            await self.send_premium_info(query.message, user_id)
    
    async def send_premium_info(self, message, user_id: str):
        """Envia informações sobre premium"""
        keyboard = [
            [InlineKeyboardButton("💳 Quero ser Premium", url=f"https://t.me/{CONFIG['nome_bot'].lower()}_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            VIP_INTEREST_RESPONSE,
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principal de mensagens"""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        user = self.user_manager.get_user(user_id)
        
        # Verifica se premium expirou
        if self.user_manager.check_premium_expired(user_id):
            await update.message.reply_text(
                "Ei... seu premium expirou 🌙\n\nVoltamos ao limite de mensagens... mas a gente pode voltar a ser ilimitado ✨"
            )
        
        # Verifica limites para usuários grátis
        if not user["is_premium"]:
            messages_count = self.user_manager.increment_messages(user_id)
            
            # Aviso quando estiver perto do limite
            if messages_count == CONFIG["limite_diario_gratis"] - 3 and not user.get("warned_low_messages"):
                await update.message.reply_text(LOW_MESSAGES_WARNING)
                self.user_manager.update_user(user_id, {"warned_low_messages": True})
            
            # Limite atingido
            if messages_count > CONFIG["limite_diario_gratis"]:
                keyboard = [
                    [InlineKeyboardButton("✨ Virar Premium", callback_data="premium_info")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    LIMIT_MESSAGE,
                    reply_markup=reply_markup
                )
                return
        
        # Detecta humor
        mood = self._detect_mood(user_message)
        if mood:
            self.user_manager.update_user(user_id, {"mood_detected": mood})
        
        # Verifica interesse em premium
        if self._check_premium_triggers(user_message):
            await self.send_premium_info(update.message, user_id)
            return
        
        # Verifica keywords quentes (paywall inteligente)
        if self._check_hot_keywords(user_message) and not user["is_premium"]:
            await update.message.reply_text(PHOTO_BLOCK_MESSAGE)
            
            keyboard = [
                [InlineKeyboardButton("🌙 Ver conteúdo exclusivo", callback_data="premium_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Quer desbloquear tudo?",
                reply_markup=reply_markup
            )
            return
        
        # Salva mensagem do usuário no histórico
        self.user_manager.add_message_to_history(user_id, "user", user_message)
        
        # Obtém resposta da IA
        await update.message.chat.send_action("typing")
        ai_response = await self._get_ai_response(user_id, user_message)
        
        # Salva resposta da IA no histórico
        self.user_manager.add_message_to_history(user_id, "assistant", ai_response)
        
        # Envia resposta
        await update.message.reply_text(ai_response)
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comando /premium"""
        user_id = str(update.effective_user.id)
        await self.send_premium_info(update.message, user_id)
    
    async def activate_premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para ativar premium (admin only)"""
        # Apenas para demonstração - em produção, verificar comprovante de pagamento
        user_id = str(update.effective_user.id)
        
        self.user_manager.set_premium(user_id, CONFIG["dias_premium"])
        
        await update.message.reply_text(PREMIUM_WELCOME)
    
    def run(self):
        """Inicia o bot"""
        app = Application.builder().token(self.telegram_token).build()
        
        # Handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("premium", self.premium_command))
        app.add_handler(CommandHandler("ativar", self.activate_premium_command))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("🌙 Bianca Bot iniciada...")
        app.run_polling()


# ================= EXECUÇÃO =================

if __name__ == "__main__":
    # Configurar tokens (usar variáveis de ambiente em produção)
    TELEGRAM_TOKEN = "8524075669:AAFWYS7ntdyWgn5csp_Eu5nC-oR9D5ivYg4"
    ANTHROPIC_API_KEY = "SUA_CHAVE_API_ANTHROPIC"
    
    bot = BiancaBot(TELEGRAM_TOKEN, ANTHROPIC_API_KEY)
    bot.run()
