import yaml, requests, random, time, datetime, json, sys
from string import Template
from logger import Logger
from session import Session
from URL import URL

requests.packages.urllib3.disable_warnings()

class Instabot(object):

  def __init__(self, config_path, log_file_path=None):
    start_time = datetime.datetime.now()

    config = yaml.safe_load(open(config_path, "r"))
    username, password, remove_count, wanted_followers = (
      config['CREDENTIALS']['USERNAME'],
      config['CREDENTIALS']['PASSWORD'],
      config['REMOVE_FOLLOWERS_COUNT'],
      config['KEEP_FOLLOWERS'],
    )
    self.init_bot_config()

    self.logger = Logger(username, log_file_path)
    self.logger.log('Instabot v0.1 started at: %s' % (start_time.strftime("%d.%m.%Y %H:%M")))
    self.logger.log('Instabot v0.1 will remove at most ' + str(remove_count) + ' followers')

    self.session = Session(username, password, self.logger)
    self.session.login()
    
    self.run(username, wanted_followers, remove_count)

    self.session.logout()

    end_time = datetime.datetime.now()
    self.logger.log('Instabot v0.1 stopped at: %s' % (end_time.strftime("%d.%m.%Y %H:%M")))
    self.logger.log('Instabot v0.1 took ' + str(end_time-start_time) + ' in total')

  def init_bot_config(self):
    self.config = {
      'request': {
        'wait': {
          'min': 15,
          'max': 45,
        },
      },
      'confirm_data': False,
      'fast': False,
    }

  def run(self, username, wanted_followers, remove_count):
    unwanted_followers = self.get_unwanted_followers(username, wanted_followers, remove_count)
    
    unfollow_count = 0
    perseverance = 1
    patience = 3

    while len(unwanted_followers):
      if not self.session.login_status:
        self.session.login()

      follower = unwanted_followers.pop()
      status = self.unfollow(follower)

      if status == 200:
        perseverance = 1
        unfollow_count += 1
        self.logger.log('#' + str(unfollow_count) + ' - Unfollowed ' + follower.name)

      elif status >= 400 and status <= 499:
        self.logger.log('Failed to unfollow user: ' + follower.name + ' with status ' + str(status) + '. Failed attempt #' + str(perseverance))
        perseverance += 1

        unwanted_followers.append(follower)

        if perseverance > patience: # the bot knows when patience is more important then perseverance
          wait = random.randint(45,75) * 60
          self.logger.log('Instagram might have flagged the bot. Going idle for '+ str(int(wait/60)) +' minutes.')
          time.sleep(wait)

      else:
        self.logger.log('Unexpected status code: ' + status)

      # sleep after one unfollow
      self.sleep()

  def get_unwanted_followers(self, username, wanted_followers, remove_count):
    wanted_set = set(wanted_followers)
    unwanted = set()
    keep = set()
    
    user_id = self.get_user_id(username)
    batch_size = 50
    has_next_page = True
    scroll_hash = ''

    while has_next_page and len(unwanted) < remove_count:
      followers_url = self.get_followers_url(user_id, batch_size, scroll_hash)
      followers, has_next_page, scroll_hash = self.get_followers_data(followers_url)

      for follower in followers:
        if follower.name in wanted_set:
          keep.add(follower.name)
        elif len(unwanted) < remove_count:
          unwanted.add(follower)

      print('Loaded ' + str(len(unwanted)) + ' unwanted followers...')

      time.sleep(2)

    self.logger.log('Please confirm the information below:')
    self.logger.log('List of followers that should be kept:' + str(list(keep)))
    self.logger.log('List of followers to be removed:' + str([ follower.name for follower in unwanted]))
    self.confirm_data()

    return list(unwanted)

  def get_user_id(self, username):
    data = self.get_profile_page_data(URL.profile % (username))
    return data['entry_data']['ProfilePage'][0]['graphql']['user']['id']

  def get_profile_page_data(self, url):
    html = self.get_html(url)
    return self.get_data_from_html(html)

  def get_html(self, url):
    self.logger.log('Fetching ' + url)
    response = self.session.get(url)
    html = response.text
    self.sleep(False)
    return html

  def get_data_from_html(self, html):
    try:
      finder_start = '<script type="text/javascript">window._sharedData = '
      finder_end = ';</script>'
      data_start = html.find(finder_start)
      data_end = html.find(finder_end, data_start + 1)
      json_str = html[data_start + len(finder_start):data_end]
      data = json.loads(json_str)
      return data
    except json.decoder.JSONDecodeError as e:
      self.logger.log('Error parsing json string: ' + str(e))

  def get_followers_url(self, user_id, batch_size=50, scroll_hash=''):
    base_url = 'https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables='
    variables_template = '{"id":"$user_id","include_reel":false,"fetch_mutual":false,"first":$first,"after":"$after"}'
    variables = Template(variables_template).substitute(user_id=user_id, first=batch_size, after=scroll_hash)
    return base_url + variables

  def get_followers_data(self, url):
    response = self.session.get(url, False)
    data = json.loads(response.text)

    followers = list()
    for node in data['data']['user']['edge_followed_by']['edges']:
      name = node['node']['username']
      follower_id = node['node']['id']
      followers.append(Follower(name, follower_id))

    has_next_page = data['data']['user']['edge_followed_by']['page_info']['has_next_page']
    after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']

    return (followers, has_next_page, after)

  def confirm_data(self):
    if not self.config['confirm_data']:
      return

    answer = None
    confirmed = False
    text = "Should the bot proceed? [y/n]"

    while True:
      answer = input(text)

      if answer == "y":
        if confirmed:
          return

        confirmed = True
        text = "Are you sure? [y/n]"

      elif answer == "n":
        raise Exception("Instabot v0.1 aborted")

  def sleep(self, continuous_request=True):
    if self.config['fast']:
      wait = 1
    elif continuous_request and random.randint(1, 100) < 5:
      # sleep longer after 5% of cycles (from 7min to 15 min)
      wait = random.randint(7, 15) * 60
      self.logger.log('Coffee time! Will be back in ' + str(int(wait/60)) + ' minutes...')
    else:
      wait = random.randint(self.config['request']['wait']['min'], self.config['request']['wait']['max'])
    
    time.sleep(wait)

  def unfollow(self, follower):
    block_url = (URL.block % follower.id)
    block_response = self.session.post(block_url)

    if block_response.status_code != 200:
      self.logger.log('Blocking follower ' + follower.name + 'failed with status ' + str(block_response.status_code))
      return block_response.status_code

    self.sleep()
    unblock_url = (URL.unblock % follower.id)
    unblock_response = self.session.post(unblock_url)

    if unblock_response.status_code != 200:
      self.logger.log('Unblocking follower ' + follower.name + 'failed with status ' + str(unblock_response.status_code))
      return unblock_response.status_code

    return 200


class Follower(object):
  def __init__(self, name, follower_id):
    self.name = name
    self.id = follower_id


if __name__ == "__main__":
  try:
    Instabot('config/config.yml', sys.argv[1])
  except IndexError:
    Instabot('config/config.yml')
