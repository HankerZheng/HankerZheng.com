import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or '53cr37_k3Y'

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True

class TestingConfig(Config):
	Testing = True

class ProductionConfig(Config):
	pass

config = {
	'development': 	DevelopmentConfig,
	'testing':		TestingConfig,
	'production':	ProductionConfig,
	'default':		DevelopmentConfig
}
