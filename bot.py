
from bot_info import Application
from config import token_group, token_my

if __name__ == '__main__':
    app = Application(token_group, token_my)
    app.run()
