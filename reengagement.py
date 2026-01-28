"""
Sistema de Re-engajamento Automático
Envia mensagens para usuários inativos
"""

import asyncio
import random
from datetime import datetime, timedelta
from telegram import Bot
from config import *
import json
import os


class ReengagementSystem:
    """Sistema para recuperar usuários inativos"""
    
    def __init__(self, telegram_token: str, users_file: str = "users_data.json"):
        self.bot = Bot(token=telegram_token)
        self.users_file = users_file
    
    def _load_users(self):
        """Carrega usuários do arquivo"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_users(self, users):
        """Salva usuários no arquivo"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def _get_inactive_hours(self, last_message_iso: str) -> float:
        """Calcula quantas horas o usuário está inativo"""
        last_message = datetime.fromisoformat(last_message_iso)
        now = datetime.now()
        delta = now - last_message
        return delta.total_seconds() / 3600
    
    async def check_and_reengage(self):
        """Verifica e reenvia mensagens para usuários inativos"""
        users = self._load_users()
        
        for user_id, user_data in users.items():
            # Pula se nunca conversou
            if not user_data.get("last_message"):
                continue
            
            # Calcula inatividade
            inactive_hours = self._get_inactive_hours(user_data["last_message"])
            
            # Verifica último reengajamento
            last_reeng = user_data.get("last_reengagement")
            if last_reeng:
                hours_since_reeng = self._get_inactive_hours(last_reeng)
                # Não enviar se já enviou nas últimas 12h
                if hours_since_reeng < 12:
                    continue
            
            # Contador de tentativas
            reeng_count = user_data.get("reengagement_count", 0)
            
            # Nível 1: 2 horas inativo
            if inactive_hours >= CONFIG["tempo_reengajamento"]["nivel_1"] and reeng_count == 0:
                await self._send_reengagement(user_id, REENGAGEMENT_1, users)
            
            # Nível 2: 24 horas inativo
            elif inactive_hours >= CONFIG["tempo_reengajamento"]["nivel_2"] and reeng_count == 1:
                await self._send_reengagement(user_id, REENGAGEMENT_2, users)
            
            # Nível 3: 72 horas inativo
            elif inactive_hours >= CONFIG["tempo_reengajamento"]["nivel_3"] and reeng_count == 2:
                await self._send_reengagement(user_id, REENGAGEMENT_3, users)
            
            # Última tentativa antes de pausar
            elif reeng_count == 3:
                await self._send_reengagement(user_id, LAST_ATTEMPT, users, is_last=True)
    
    async def _send_reengagement(self, user_id: str, messages: list, users: dict, is_last: bool = False):
        """Envia mensagem de reengajamento"""
        try:
            message = random.choice(messages)
            await self.bot.send_message(chat_id=int(user_id), text=message)
            
            # Atualiza dados
            users[user_id]["last_reengagement"] = datetime.now().isoformat()
            
            if is_last:
                users[user_id]["reengagement_count"] = 0  # Reset
                users[user_id]["paused"] = True
            else:
                users[user_id]["reengagement_count"] = users[user_id].get("reengagement_count", 0) + 1
            
            self._save_users(users)
            
            print(f"✉️ Reengajamento enviado para {user_id}")
        except Exception as e:
            print(f"Erro ao enviar para {user_id}: {e}")
    
    async def send_morning_messages(self):
        """Envia mensagens de bom dia para usuários ativos"""
        users = self._load_users()
        now = datetime.now()
        
        # Apenas entre 7h e 9h
        if not (7 <= now.hour < 9):
            return
        
        for user_id, user_data in users.items():
            # Pula se não está ativo ou já recebeu hoje
            if not user_data.get("last_message"):
                continue
            
            last_msg_date = datetime.fromisoformat(user_data["last_message"]).date()
            
            # Apenas se conversou nas últimas 48h
            if (now.date() - last_msg_date).days > 2:
                continue
            
            # Verifica se já enviou hoje
            last_morning = user_data.get("last_morning_message")
            if last_morning:
                if datetime.fromisoformat(last_morning).date() == now.date():
                    continue
            
            try:
                # Escolhe mensagem baseado no status
                is_premium = user_data.get("is_premium", False)
                messages_used = user_data.get("messages_today", 0)
                limit = CONFIG["limite_diario_gratis"]
                
                if is_premium:
                    message = random.choice(MORNING_VIP)
                elif messages_used >= limit:
                    message = random.choice(MORNING_LOCKED)
                else:
                    message = random.choice(MORNING_FREE)
                
                await self.bot.send_message(chat_id=int(user_id), text=message)
                
                users[user_id]["last_morning_message"] = now.isoformat()
                self._save_users(users)
                
                print(f"🌅 Bom dia enviado para {user_id}")
                
                # Aguarda para não sobrecarregar
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Erro ao enviar bom dia para {user_id}: {e}")
    
    async def send_night_messages(self):
        """Envia mensagens de boa noite"""
        users = self._load_users()
        now = datetime.now()
        
        # Apenas entre 22h e 23h
        if not (22 <= now.hour < 23):
            return
        
        for user_id, user_data in users.items():
            if not user_data.get("last_message"):
                continue
            
            last_msg_date = datetime.fromisoformat(user_data["last_message"]).date()
            
            # Apenas se conversou hoje
            if last_msg_date != now.date():
                continue
            
            # Verifica se já enviou hoje
            last_night = user_data.get("last_night_message")
            if last_night:
                if datetime.fromisoformat(last_night).date() == now.date():
                    continue
            
            try:
                is_premium = user_data.get("is_premium", False)
                messages_used = user_data.get("messages_today", 0)
                limit = CONFIG["limite_diario_gratis"]
                
                if is_premium:
                    message = random.choice(NIGHT_VIP)
                elif messages_used >= limit:
                    message = random.choice(NIGHT_LOCKED)
                else:
                    message = random.choice(NIGHT_FREE)
                
                await self.bot.send_message(chat_id=int(user_id), text=message)
                
                users[user_id]["last_night_message"] = now.isoformat()
                self._save_users(users)
                
                print(f"🌙 Boa noite enviado para {user_id}")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Erro ao enviar boa noite para {user_id}: {e}")
    
    async def reset_daily_counters(self):
        """Reseta contadores diários à meia-noite"""
        users = self._load_users()
        now = datetime.now()
        
        # Apenas à meia-noite
        if now.hour != 0:
            return
        
        for user_id in users:
            users[user_id]["messages_today"] = 0
            users[user_id]["warned_low_messages"] = False
        
        self._save_users(users)
        print("🔄 Contadores diários resetados")
    
    async def run_scheduler(self):
        """Executa verificações periódicas"""
        print("⏰ Scheduler de reengajamento iniciado...")
        
        while True:
            try:
                # Verifica reengajamento a cada hora
                await self.check_and_reengage()
                
                # Verifica mensagens de horário
                await self.send_morning_messages()
                await self.send_night_messages()
                await self.reset_daily_counters()
                
                # Aguarda 1 hora
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"Erro no scheduler: {e}")
                await asyncio.sleep(60)


# ================= EXECUÇÃO =================

if __name__ == "__main__":
    TELEGRAM_TOKEN = "SEU_TOKEN_DO_TELEGRAM"
    
    scheduler = ReengagementSystem(TELEGRAM_TOKEN)
    asyncio.run(scheduler.run_scheduler())
