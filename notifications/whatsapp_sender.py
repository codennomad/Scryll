import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger


class WhatsAppNotifier:
    def __init__(self):
        try:
            logger.info("🔄 Inicializando WhatsAppNotifier...")

            self.dir_path = os.getcwd()
            profile_path = os.path.join(self.dir_path, "profile", "wpp")
            os.makedirs(profile_path, exist_ok=True)

            options = webdriver.ChromeOptions()
            options.add_argument(f"user-data-dir={profile_path}")
            self.webdriver = webdriver.Chrome(options=options)

            self.webdriver.get("https://web.whatsapp.com")

            logger.info("🕒 Aguarde escaneamento do QR Code (45s)")
            sleep(45)

        except Exception as e:
            logger.exception("🔥 Erro ao iniciar WhatsAppNotifier")
            raise e

    def send_message(self, contact_name: str, message: str):
        try:
            logger.info(f"✉️ Enviando mensagem para {contact_name}")

            # Clica na barra de pesquisa
            search_btn = WebDriverWait(self.webdriver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Pesquisar ou começar uma nova conversa"]'))
            )
            search_btn.click()

            # Campo de texto da pesquisa
            search_input = self.webdriver.find_element(By.XPATH, '//div[@title="Pesquisar..."]')
            search_input.clear()
            search_input.send_keys(contact_name)
            sleep(2)

            # Seleciona o contato
            contact = self.webdriver.find_element(By.XPATH, f'//span[@title="{contact_name}"]')
            contact.click()

            # Campo de mensagem
            msg_box = WebDriverWait(self.webdriver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Mensagem"]'))
            )
            msg_box.click()
            msg_box.send_keys(message)
            msg_box.send_keys('\n')

            logger.info("✅ Mensagem enviada com sucesso!")

        except Exception as e:
            logger.exception("❌ Erro ao enviar mensagem no WhatsApp")
            raise e


# Instância global (singleton)
notifier = WhatsAppNotifier()

def notify(message: str, contact: str = "Gabriel"):
    try:
        notifier.send_message(contact, message)
    except Exception:
        logger.warning("⚠️ Falha ao enviar notificação via WhatsApp")
