from gevent import monkey
from app import *

monkey.patch_all()


application = create_app()
