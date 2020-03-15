echo "Shutting down InstaBot..."
kill $(ps aux | grep instabot | grep -v "grep" | awk '{print $2}')