from flask import Flask
try:
    import pymysql
except ImportError:
    pymysql.install_as_MySQLdb()

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
# app.config.from_object('config')
# connection = pymysql.connect(host='localhost',
#                              port=3306,
#                              user='root',
#                              password='aapi2020',
#                              db='AAPI_DB')


import routes