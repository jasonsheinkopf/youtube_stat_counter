import googleapiclient.discovery
import googleapiclient.errors
import pygame
import os
from video_stats import Video

# Your personal API key and channel ID
API_KEY = 'AIzaSyDzq_TFOT8qNbSHrbMz1Y_F5mpKrUXOq3s'
CHANNEL_ID = 'UCPAtrpdvJTHjy0c19zlWBGw'

def get_video_view_counts(channel_id, api_key):
    'Creates a list of video objects from youtube channel'
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
    video_list = []

    try:
        # Get the list of uploaded videos for the channel
        playlist_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        # Extract the uploads playlist ID
        uploads_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve the videos from the uploads playlist
        videos_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50
        ).execute()

        # Iterate over the videos and fetch their view counts
        for item in videos_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            video_response = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()

            # Extract the view count from the response
            view_count = int(video_response['items'][0]['statistics']['viewCount'])
            # video_list.append({video_title: view_count})

            # Flag to keep track of whether video has already been created
            video_exists = False
            # Iterate through list of video objects
            for video in video_list:
                # If the video object already exists
                if video.title == video_title:
                    # Count how many views added
                    video.views_added = video.current_views - video.prev_views
                    # Set previous views to current for next api call
                    video.prev_views = video.current_views
                    # Set flag to True to indicated video was found
                    video_found = True
                    break
            # If the video_title is not found anywhere in the list
            if not video_exists:
                # Create new video object
                new_video = Video(title=video_title, current_views=view_count)
                # Append it to the list
                video_list.append(new_video)

        return video_list

    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

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

# Get initial subscribers count
subscriber_count = get_subscribers_count(CHANNEL_ID, API_KEY)
prev_subscriber_count = subscriber_count

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

# Load logo
logo_sf = 0.07
logo = pygame.image.load('akiya_quest_logo.png')

# Calculate the new dimensions of the resized image
new_logo_w = int(logo.get_width() * logo_sf)
new_logo_h = int(logo.get_height() * logo_sf)

# Resize the image while preserving the aspect ratio
resized_logo = pygame.transform.scale(logo, (new_logo_w, new_logo_h))

# Load title
title_sf = 0.13
title = pygame.image.load('akiya_quest_title.png')

# Calculate the new dimensions of the resized image
new_title_w = int(title.get_width() * title_sf)
new_title_h = int(title.get_height() * title_sf)

# Resize the image while preserving the aspect ratio
resized_title = pygame.transform.scale(title, (new_title_w, new_title_h))

# Load the custom font 'Fujimaru-Regular.ttf'
font_path = 'Nexa-Heavy.ttf'
font_size = 14
font_color = (0, 0, 0)
font = pygame.font.Font(font_path, font_size)

# How many seconds between stat checks
wait_time = 60

# Create a clock object
clock = pygame.time.Clock()
time_since_last_check = 0

# Run the game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Check time elapsed since last stat update
    time_since_last_check += clock.tick()

    # Get initial view and subscriber counts
    video_view_counts = get_video_view_counts(CHANNEL_ID, API_KEY)
    subscriber_count = get_subscribers_count(CHANNEL_ID, API_KEY)

    # Check if it's time to check new stats
    if time_since_last_check >= wait_time * 1000:
        time_since_last_check = 0

        # Get video view counts
        video_view_counts = get_video_view_counts(CHANNEL_ID, API_KEY)

        # Get subscribers count
        subscriber_count = get_subscribers_count(CHANNEL_ID, API_KEY)
        if subscriber_count > prev_subscriber_count:
            print("Play subscriber animation")

        # Count new views for each video
        [video.count_new_views() for video in video_view_counts]

    # Clear the window
    window.fill((255, 255, 255))  # Set the background color to white

    # Center the resized images on the screen
    window.blit(resized_logo, (15, 15))
    window.blit(resized_title, (125, 25))
    
    # Render the subscriber text
    text_subscribers = font.render(f"Subscribers  {subscriber_count}", True, font_color)  # Set the text color to black
    window.blit(text_subscribers, (160, 60))  # Adjust the position of the text according to your layout

    # Enable underline for the font
    font.set_underline(True)

    # Render the views heading
    views_heading = font.render(f"VIEWS", True, font_color)  # Set the text color to black
    window.blit(views_heading, (40, 120))  # Adjust the position of the text according to your layout

    # Render the title heading
    title_heading = font.render(f"TITLE", True, font_color)  # Set the text color to black
    window.blit(title_heading, (125, 120))  # Adjust the position of the text according to your layout

    # Enable underline for the font
    font.set_underline(False)

    # Reorder video view counts by most views
    video_view_counts = sorted(video_view_counts, key=lambda video: video.current_views, reverse=True)
    
    # Render video text
    for i, video in enumerate(video_view_counts):
        video_title = video.title
        # Remove unnecessary prefix
        if "#" in video_title:
            video_title = video_title.split("#")[0]
        if "-" in video_title:
            video_title = video_title.split("-")[0]
        view_count = video.current_views
        count_text = font.render(str(view_count), True, font_color)
        window.blit(count_text, (40, 150 + 20 * i))
        video_text = font.render(video_title, True, font_color)
        window.blit(video_text, (125, 150 + 20 * i))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
