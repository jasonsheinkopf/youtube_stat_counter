import googleapiclient.discovery
import googleapiclient.errors
import pygame
import os
from video_stats import Video
from moviepy.editor import VideoFileClip
import pyglet
import random
import datetime
import pytz
import colorsys


# How many seconds between stat checks
wait_time = 60

# Set timezone
timezone = pytz.timezone('Asia/Tokyo')
# Time when awake hours begins
wake_hour = 8
sleep_hour = 21

# Your personal API key and channel ID
API_KEY = 'AIzaSyDzq_TFOT8qNbSHrbMz1Y_F5mpKrUXOq3s'
CHANNEL_ID = 'UCPAtrpdvJTHjy0c19zlWBGw'

# List to store video objects
video_list = []
api_calls = 0

def get_video_view_counts(channel_id, api_key):
    'Fetches video details and view counts for videos in a channel'
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
    global video_list, api_calls

    try:
        # Get the list of uploaded videos for the channel
        playlist_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        api_calls += 1

        # Extract the uploads playlist ID
        uploads_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve the videos from the uploads playlist
        videos_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50
        ).execute()
        api_calls += 1

        # Prepare a list of video IDs
        video_ids = [item['snippet']['resourceId']['videoId'] for item in videos_response['items']]

        # Fetch video statistics using batch request
        video_statistics_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()
        api_calls += 1

        # Flag to keep track of whether video object already created
        video_exists = False
        
        # Combine video details and view counts into video_data list
        for item in video_statistics_response['items']:
            video_id = item['id']
            video_title = item['snippet']['title']
            view_count = int(item['statistics']['viewCount'])
            
            # Iterate through list of video objects
            for video in video_list:
                # Check if video object has already been added to list
                if video.title == video_title:
                    # Set prev views to current for next cycle
                    video.prev_views = video.current_views          

                    # Update current views
                    video.current_views = view_count
                    
                    # # For debugging make first video get more counts DELETE LATER
                    # if video_list.index(video) == 0:
                    #     video.current_views += api_calls

                    # Update views added
                    video.views_added = video.current_views - video.prev_views

                    # Update today views
                    video.today_views = video.current_views - video.views_at_wake

                    # Set flag to True indicating video was found
                    video_exists = True
                    break

            # If video object is not yet in list
            if not video_exists:
                # Create new video object
                new_video = Video(title=video_title, current_views=view_count)
                # Append it to the list
                video_list.append(new_video)
                print(f"Video {video_title} added")
        
        # Count API calls
        print(f"Api calls: {api_calls}")
        return video_list
    
    except googleapiclient.errors.HttpError as e:
        print(f"an error occurred: {e}")

def get_subscribers_count(channel_id, api_key):
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    try:
        # Get the channel details
        channel_response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()

        # Extract the subscriber count from the response
        subscriber_count = int(channel_response['items'][0]['statistics']['subscriberCount'])

        return subscriber_count

    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

def wake_sleep():
    # Get current time
    current_time = datetime.datetime.now(timezone)

    # Turn off sounds during sleep hours
    if wake_hour <= current_time.hour < sleep_hour:
        # pygame.mixer.unpause()
        is_sleep = False
        print(f"{current_time} | Wake Hours: Yay!")
    else:
        # pygame.mixer.pause()
        is_sleep = True
        print(f"{current_time} | Sleep Hours: shhhh!")

    return is_sleep

def get_rainbow_color():
    # Get the elapsed time in milliseconds
    elapsed_time = pygame.time.get_ticks()
    
    # Adjust the hue value (range 0.0 to 1.0) based on elapsed time
    hue = (elapsed_time % 1000) / 1000.0  # Change 10000 to control the speed of the color cycling

    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    
    # Scale RGB values from (0.0 to 1.0) to (0 to 255)
    red = int(rgb[0] * 255)
    green = int(rgb[1] * 255)
    blue = int(rgb[2] * 255)
    
    # Return the color as a tuple
    return red, green, blue

# Set starting postion of pygame window
screen_x = 0
screen_y = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (screen_x, screen_y)

# Initialize Pygame
pygame.init()

# Set up the window
width, height = 320, 480  # Set the window size according to your touch screen
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Akiya Quest Stats")

# View audio dir
view_aud_dir = 'media/view_sounds'

# Initialize an empty list to store paths
view_aud_list = []

# Iterate through all files and directories in the folder
for root, dirs, files in os.walk(view_aud_dir):
    for file in files:
        # Get the absolute path of each file
        file_path = os.path.join(root, file)
        view_aud_list.append(file_path)

# Create sub audio and video object
sub_vid_path = "./media/pon_chorus.mp4"
sub_aud_path = "./media/pon_chorus.mp3"
sub_vid = VideoFileClip(sub_vid_path)

# Set video location and scale factor
video_x, video_y = 180, 85
sub_vid_sf = 0.13

# Resize video
aspect_ratio = sub_vid.w / sub_vid.h
new_sub_vid_w = int(sub_vid.w * sub_vid_sf)
new_sub_vid_h = int(sub_vid.h * sub_vid_sf)
sub_vid = sub_vid.resize((new_sub_vid_w, new_sub_vid_h))

# Set bool to false
video_playing = False

# Load logo
logo_sf = 0.07
logo = pygame.image.load('media/images/akiya_quest_logo.png')

# Calculate the new dimensions of the resized image
new_logo_w = int(logo.get_width() * logo_sf)
new_logo_h = int(logo.get_height() * logo_sf)

# Resize the image while preserving the aspect ratio
resized_logo = pygame.transform.scale(logo, (new_logo_w, new_logo_h))

# Load channel title image
title_sf = 0.13
title = pygame.image.load('media/images/akiya_quest_title.png')

# Calculate the new dimensions of the resized image
new_title_w = int(title.get_width() * title_sf)
new_title_h = int(title.get_height() * title_sf)

# Resize the image while preserving the aspect ratio
resized_title = pygame.transform.scale(title, (new_title_w, new_title_h))

# Load night background image
night_backdrop = pygame.image.load('media/images/night_backdrop.jpeg')

# Calculate the scale factor to fit the screen
sf_w = width / night_backdrop.get_width()
sf_h = height / night_backdrop.get_height()

# Choose the larger scale factor to maintain aspect ratio
night_backdrop_sf = max(sf_w, sf_h)

# Calculate the new dimensions of the resized image
new_night_backdrop_w = int(night_backdrop.get_width() * night_backdrop_sf)
new_night_backdrop_h = int(night_backdrop.get_height() * night_backdrop_sf)

# Resize the image while preserving the aspect ratio
resized_night_backdrop = pygame.transform.scale(night_backdrop, (new_night_backdrop_w, new_night_backdrop_h))

# Set the alpha transparency (opacity) of the image (0 to 255)
alpha_value = 40  # Adjust this value to set the desired transparency
resized_night_backdrop.set_alpha(alpha_value)

# Load day background image
day_backdrop = pygame.image.load('media/images/day_backdrop.jpeg')

# Calculate the scale factor to fit the screen
sf_w = width / day_backdrop.get_width()
sf_h = height / day_backdrop.get_height()

# Choose the larger scale factor to maintain aspect ratio
day_backdrop_sf = max(sf_w, sf_h)

# Calculate the new dimensions of the resized image
new_day_backdrop_w = int(day_backdrop.get_width() * day_backdrop_sf)
new_day_backdrop_h = int(day_backdrop.get_height() * day_backdrop_sf)

# Resize the image while preserving the aspect ratio
resized_day_backdrop = pygame.transform.scale(day_backdrop, (new_day_backdrop_w, new_day_backdrop_h))

# Set the alpha transparency (opacity) of the image (0 to 255)
alpha_value = 40  # Adjust this value to set the desired transparency
resized_day_backdrop.set_alpha(alpha_value)

# Load the custom font
font_path = 'Nexa-Heavy.ttf'
# font_path = 'MAGIMTOS.ttf'
# font_path = 'Quebab-Shadow-ffp.ttf'
font_size = 14
font_color = (0, 0, 0)
font = pygame.font.Font(font_path, font_size)

# Create a clock object
clock = pygame.time.Clock()
time_since_last_check = 0

# Initialize subscriber count
subscriber_count = get_subscribers_count(CHANNEL_ID, API_KEY)
prev_subscriber_count = subscriber_count

# Initialize view counts
video_view_counts = get_video_view_counts(CHANNEL_ID, API_KEY)

# Set wake views to current views when first starting code
for video in video_list:
    video.views_at_wake = video.current_views

# Bool to track sleep hours
is_sleep = wake_sleep()

# Run the game loop
running = True
while running:
    # Cycle through colors based on ticks
    rainbow_color = get_rainbow_color()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Check time elapsed since last stat update
    time_since_last_check += clock.tick()

    # Initialize total_new_views
    total_new_views = 0

    # Record beginning of day views at wake hour
    current_time = datetime.datetime.now(timezone)
    if current_time.hour == wake_hour and current_time.minute == 0 and current_time.second == 0:
        for video in video_view_counts:
            video.wake_views = video.current_views

    # Check if it's time to check new stats
    if time_since_last_check >= wait_time * 1000 and video_playing == False:
        time_since_last_check = 0

         # Handle wake sleep
        is_sleep = wake_sleep()
       
        # Get video view counts
        video_view_counts = get_video_view_counts(CHANNEL_ID, API_KEY)

        # Get subscribers count
        subscriber_count = get_subscribers_count(CHANNEL_ID, API_KEY)

        # Count total new views for all videos since api call
        for video in video_view_counts:
            total_new_views += video.views_added
      
        # Check if there are any new views
        if total_new_views > 0:
            # Randomly select a sound effect from the dir
            view_sound_object = pygame.mixer.Sound(random.choice(view_aud_list))
            duration = int(view_sound_object.get_length() * 1000)
            view_sound_object.set_volume(.3)
            view_sound_object.play(maxtime=duration) if not is_sleep else None
            pygame.time.delay(1000)

    # Clear the window
    window.fill((255, 255, 255))  # Set the background color to white

    # Blit the appropriate backdrop
    window.blit(resized_night_backdrop, (0, 0)) if is_sleep else window.blit(resized_day_backdrop, (0, 0))    

    # Center the resized images on the screen
    window.blit(resized_logo, (15, 15))
    window.blit(resized_title, (125, 25))
    
    # Render the subscriber text
    subscriber_font = rainbow_color if subscriber_count - prev_subscriber_count > 0 else font_color
    text_subscribers = font.render(f"{subscriber_count} subscribers", True, subscriber_font)  # Set the text color to black
    window.blit(text_subscribers, (160, 60))  # Adjust the position of the text according to your layout

    # Enable underline for the font
    font.set_underline(True)

    # Set text positions
    day_view_x = 20
    views_x = 80
    title_x = 135
    headings_y = 160
    text_spacing = 20

    # Render the today heading
    views_heading = font.render(f"Today", True, font_color)  # Set the text color to black
    window.blit(views_heading, (day_view_x, headings_y - text_spacing))  # Adjust the position of the text according to your layout

    # Render the views heading
    views_heading = font.render(f"Views", True, font_color)  # Set the text color to black
    window.blit(views_heading, (views_x, headings_y - text_spacing))  # Adjust the position of the text according to your layout

    # Render the title heading
    title_heading = font.render(f"Title", True, font_color)  # Set the text color to black
    window.blit(title_heading, (title_x, headings_y - text_spacing))  # Adjust the position of the text according to your layout

    # Enable underline for the font
    font.set_underline(False)

    # Reorder video view counts by most views
    video_view_counts = sorted(video_view_counts, key=lambda video: video.current_views, reverse=True)

    # Render video text
    for i, video in enumerate(video_view_counts):
        video_title = video.title.title()
        # Remove unnecessary prefix
        if "#" in video_title:
            video_title = video_title.split("#")[0]
        if "-" in video_title:
            video_title = video_title.split("-")[0]
        # Limit title characters
        video_title = video_title[:22]
        # Print video count to screen
        count_text = font.render(str(video.current_views), True, font_color)
        window.blit(count_text, (views_x, headings_y + text_spacing * i))
        # Print title to screen
        title_text = font.render(video_title, True, font_color)
        window.blit(title_text, (title_x, headings_y + text_spacing * i))
        # Check for new views since last update
        if video.views_added > 0 and video.prev_views != 0:
            # Display day views in rainbow if recently updated
            added_text = font.render("+" + str(video.today_views), True, rainbow_color)
            print(f"Video: {video.title} | Prev: {video.prev_views} | Cur: {video.prev_views} | Add: {video.views_added}")
            # pygame.time.delay(5000)
        else:
            # Else in font color
            added_text = font.render("+" + str(video.today_views), True, font_color)
        window.blit(added_text, (day_view_x, headings_y + text_spacing * i))

    # Print counts every 5 seconds for debugging
    if pygame.time.get_ticks() % 5000 == 0:
        for video in video_view_counts:
            print(video.current_views, video.title)
        print() 

    # Play video if new subscribers
    if subscriber_count > prev_subscriber_count and not video_playing:   # change to >
        sub_aud_object = pygame.mixer.Sound(sub_aud_path)
        sub_aud_dur = int(sub_aud_object.get_length() * 1000)
        sub_aud_object.set_volume(0.4)
        sub_aud_object.play(maxtime=sub_aud_dur) if not is_sleep else None
        video_playing = True
        video_start_time = pygame.time.get_ticks() / 1000
    # Handle case if subscribers are lost
    elif subscriber_count < prev_subscriber_count:
        prev_subscriber_count = subscriber_count

    # Check if the video is still playing
    if video_playing:
        elapsed_time = pygame.time.get_ticks() / 1000 - video_start_time
        # Handle tick count error
        sub_vid_frame_count = int(sub_vid.fps * sub_vid.duration)
        if elapsed_time > sub_vid_frame_count:
            elapsed_time = 0
        frame = sub_vid.get_frame(elapsed_time)
        pygame_frame = pygame.image.fromstring(frame.tobytes(), sub_vid.size, 'RGB')
        window.blit(pygame_frame, (video_x, video_y))

        # Check if the video has finished playing
        if elapsed_time >= sub_vid.duration:
            video_playing = False
            # pygame.mixer.music.stop()
            sub_vid.close()
            prev_subscriber_count = subscriber_count

    # Update the display
    pygame.display.flip()

    # print(f"Sub: {subscriber_count} | PrevSub: {prev_subscriber_count}")

# Quit Pygame
pygame.quit()
