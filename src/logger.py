import logging, datetime

class Logger(object):

  def __init__(self, user_login, log_file_path=None):
    self.user_login = user_login
    self.log_file_path = log_file_path
    self.log_file_exists = False

  def log(self, log_text):
    if self.log_file_path is None:
      try:
        print(log_text)
      except UnicodeEncodeError:
        print('Log text unicode error.')
    else:
      if not self.log_file_exists:
        self.log_file_exists = True
        now_time = datetime.datetime.now()
        self.log_full_path = '%s%s_%s.log' % (self.log_file_path,
                   self.user_login,
                   now_time.strftime("%d.%m.%Y_%H:%M"))
        formatter = logging.Formatter('%(asctime)s - %(name)s '
              '- %(message)s')
        self.logger = logging.getLogger(self.user_login)
        self.hdrl = logging.FileHandler(self.log_full_path, mode='w')
        self.hdrl.setFormatter(formatter)
        self.logger.setLevel(level=logging.INFO)
        self.logger.addHandler(self.hdrl)
      try:
        self.logger.info(log_text)
      except UnicodeEncodeError:
        print('Log text unicode error.')
