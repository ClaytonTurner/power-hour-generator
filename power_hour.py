import os
import subprocess


def timestamp_convert_to_seconds(timestamp):
    minutes = int(timestamp[0:timestamp.rfind(":")])
    seconds = int(timestamp[timestamp.rfind(":") + 1:])
    return ((minutes * 60000) + (seconds * 1000)) / 1000


# open power hour text file
song_file = open("songs.txt", "r")

# download beep
print("Downloading beep...")
subprocess.call("youtube-dl --quiet -f mp4 -o beep_full.mp4 "
                + song_file.readline(), shell=True)

# Cut beep video
beepStart = timestamp_convert_to_seconds(song_file.readline())
beepEnd = timestamp_convert_to_seconds(song_file.readline())
beepLength = beepEnd - beepStart

# Convert beep to transport stream for intersplicing later
subprocess.call("ffmpeg -ss " + str(beepStart) + " -i beep_full.mp4" +
                        " -t " + str(beepLength) + " -vcodec libx264 -acodec aac -strict experimental -r 24 -async 1 -y beep.mp4")
subprocess.call("ffmpeg -i beep.mp4 -vf scale=1280:720,setdar=16:9 beep.ts"
                , shell=True)

# Now that we have the transport stream, let's remove the spliced and original beep
os.remove("beep_full.mp4")
os.remove("beep.mp4")

# TODO: Create a GUI to manage this as people may want differing song amounts/lengths/other customization
# Default: 60 songs of 1 minute a piece
# concat_vid_string holds the final string of transport streams to be passed to ffmpeg's concat protocol tool
songLength = 60
duration = "01:00"
concat_vid_string = "concat:"
for i in range(1, songLength + 1):
    link = song_file.readline()

    # This if is to prevent errors happening from extra blank lines
    if link:
        curSong = str(i)

        # Read the start time and convert
        start_time = song_file.readline().strip()
        start = timestamp_convert_to_seconds(start_time)

        # Download the full video that we want to split up and create transport stream just like above
        # TODO: We could extract this process into a function cleanly, but it's not bad as is
        print("Downloading song " + curSong + " of 60...")
        subprocess.call("youtube-dl --quiet -f mp4 -o " + curSong + "_full.mp4 " + link, shell=True)
        subprocess.call("ffmpeg " +
                        " -ss " + str(start_time) + " -i " + curSong + "_full.mp4 " +
                        " -t " + duration + " -vcodec libx264 -acodec aac -strict experimental -r 24 -async 1 -y " + curSong + ".mp4")
        os.remove(curSong + "_full.mp4")

        subprocess.call("ffmpeg -i " + curSong + ".mp4 -vf scale=1280:720,setdar=16:9 " + curSong + ".ts"
                        , shell=True)
        os.remove(curSong+".mp4")

        # Add our transport stream to the list and follow it with the interspliced beep
        concat_vid_string += curSong + ".ts|beep.ts|"


# Close the song file since we are done reading it
song_file.close()

# Use the ffmpeg Protocol method
# [:-9] is so we remove that last beep off the end
# TODO: When GUI'd up, do custom naming/location saving
subprocess.call("ffmpeg -i \"" + concat_vid_string[:-9] + "\"  -c copy -s 1280:720 powerhour.mp4")


# Remove temp files TODO: put in a temp folder and just remove the folder and reference through it
for root, dirs, files in os.walk(os.getcwd()):
    for currentFile in files:
        if any(currentFile.lower().endswith(ext) for ext in ["ts"]):
                os.remove(os.path.join(root, currentFile))
