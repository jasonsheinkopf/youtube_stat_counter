# YouTube Stat Counter
YouTube Stat Counter is graphical displays that fetches stats by API and shows a channel's current view and subscriber counts.
- Vidoes in descending order ranked by total views
- Video title hashtags removed for display
- Includes daily views per video
- Current subscriber count
- Plays user-defined sound on new views
- Plays user-defined video on new subscriber 
- Day / night mode for silent operation
- Wallpaper matched day / night mode

# Demo
<img src="https://github.com/jasonsheinkopf/youtube_stat_counter/blob/main/readme_images/Youtube%20Counter%20Demo.gif" alt="Your GIF" width="250">

# How It Works
- Makes an API call to YouTube at regular intervals
- Parses stats for all videos in channel
- Strips hastags from titles and truncates names
- Sorts in descending order and display lifetime views
- Displays new views since beginning of day (or when program started running)
- Plays random cat sound when if new views are detected
- Plays video if new subscribers are detected

# Installation
## 1. Clone the Repository
```bash
git clone https://github.com/jasonsheinkopf/youtube_stat_counter.git
```
## 2. Create virtual environment from .yml
```bash
conda env create -f environment.yml
```
## 3 Activate virtual environment
```base
conda activate youtubestats
```
## 4. Create new file named .env in root directory, add these lines of code
```GOOGLE_API_KEY = 'GOOGLE_API_KEY'``` ```YOUTUBE_CHANNEL_ID = 'YOUTUBE_CHANNEL_ID'```
Replace strings with your info.  
[How to get a Google API key](https://support.google.com/googleapi/answer/6158862?hl=en)  
[How to find your YouTube Channel ID](https://support.google.com/youtube/answer/3250431?hl=en)
## 5. Customize View Sounds
Add or replace audio.wav viles to view_sounds folder.  
Sound played is selected randomly from files in that folder.
## 6. Customize Video
Replace subscriber_vid.mp4  
Replace subscriber_audio.wav (audio only file from video)
## 7. Customize images
## 8. Set timezone, wake_hour, sleep_hour, wait_time
## 9. If you have one, run on a Raspberry Pi



