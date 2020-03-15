import requests, random, time
from URL import URL

TEST_MODE = False

class Session(object):

  accept_language = 'en-US,en;q=0.8,pt-br,pt;q=0.6,'
  user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36')

  def __init__(self, username, password, logger=None):
    self.user_login = username.lower()
    self.user_password = password
    self.session = requests.Session()
    self.logger = logger
    self.login_status = False

  def __del__(self):
    if self.login_status:
      self.logout()

  def login(self):
    self.log('User: %s --> Login attempt...' % (self.user_login))
    self.init_headers()
    
    login_response = self.attempt_login()

    if not self.is_login_successful(login_response):
      return

    self.set_client_token(login_response)
    self.log('User: %s --> Successful login!' % (self.user_login))

  def init_headers(self):
    self.session.cookies.update ({
      'sessionid' : ''    , 'mid'        : '', 'ig_pr' : '1',
      'ig_vw'     : '1920', 'csrftoken'  : '',
      's_network' : ''    , 'ds_user_id' : ''
    })
    self.session.headers.update ({
      'Accept-Encoding'  : 'gzip, deflate',
      'Accept-Language'  : self.accept_language,
      'Connection'       : 'keep-alive',
      'Content-Length'   : '0',
      'Host'             : 'www.instagram.com',
      'Origin'           : 'https://www.instagram.com',
      'Referer'          : 'https://www.instagram.com/',
      'User-Agent'       : self.user_agent,
      'X-Instagram-AJAX' : '1',
      'X-Requested-With' : 'XMLHttpRequest'
    })

  def sleep(self):
    if TEST_MODE:
      time.sleep(1)
    else:
      time.sleep(random.randint(2,5))

  def attempt_login(self):
    self.login_post = {
      'username' : self.user_login,
      'password' : self.user_password
    }
    res = self.session.get(URL.root)
    self.sleep()
    self.session.headers.update({'X-CSRFToken' : res.cookies['csrftoken']})
    login_response = self.session.post(URL.login, data=self.login_post, allow_redirects=True)
    self.sleep()
    return login_response

  def is_login_successful(self, login_response):
    if login_response.status_code != 200:
      self.log('Wrong username or password.')
      return False

    response = self.session.get(URL.root)
    finder = response.text.find(self.user_login)

    if finder == -1:
      self.log('Wrong username or password.')
      return False

    return True

  def set_client_token(self, login_response):
    self.session.headers.update({'X-CSRFToken' : login_response.cookies['csrftoken']})
    self.csrftoken = login_response.cookies['csrftoken']
    self.login_status = True

  def logout(self):
    try:
      logout_post = {'csrfmiddlewaretoken' : self.csrftoken}
      logout = self.session.post(URL.logout, data=logout_post)
      self.log("Successful logout!")
      self.login_status = False
    except:
      self.log("Error: Unsuccessful logout.")

  def get(self, url, log_result=True):
    response = self.session.get(url)
    if log_result:
      self.log("GET request to: " + url + " - Status: " + str(response.status_code))
    return response

  def post(self, url):
    response = self.session.post(url)
    self.log("POST request to: " + url + " - Status: " + str(response.status_code))
    return response

  def log(self, text):
    if self.logger:
      self.logger.log(text)
    else:
      print(text)
