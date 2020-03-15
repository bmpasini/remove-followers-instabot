ROOT_PATH=/home/bmpasini/remove-followers-instabot

LOG_PATH=$ROOT_PATH/logs/
BOT_PATH=$ROOT_PATH/src/instabot.py

PYTHON_PATH=/usr/bin/python3

mkdir -p $LOG_PATH && cd $ROOT_PATH

echo "Saving log to $LOG_PATH"

$PYTHON_PATH -u $BOT_PATH $LOG_PATH &