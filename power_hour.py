import os
import shutil
import subprocess
import sys


def timestamp_convert_to_seconds(timestamp):
    minutes = int(timestamp[0:timestamp.rfind(":")])
    seconds = int(timestamp[timestamp.rfind(":") + 1:])
    return ((minutes * 60000) + (seconds * 1000)) / 1000


def setup_temp_folder(temp_dir, orig_dir):
    # Create temporary file directory
    print("Removing temp folder if exists then (re)creating it for a clean run.")
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(os.path.join(orig_dir, temp_dir))
        os.makedirs(temp_dir)
    except OSError as e:
        error_description = "This is due to a temp directory being created while this app\n" \
                            "is attempting to create the directory, but the directory did\n" \
                            "not exist whenever we checked for it. Exiting..."
        print("Error: {e}".format(e=str(e)), error_description)
        sys.exit(0)


def download_beep(song_file):
    print("Downloading beep...")
    subprocess.call("youtube-dl --quiet -f mp4 -o beep_full.mp4 "
                    + song_file.readline(), shell=True)

    # Cut beep video
    beep_start = timestamp_convert_to_seconds(song_file.readline())
    beep_end = timestamp_convert_to_seconds(song_file.readline())
    beep_length = beep_end - beep_start

    # Convert beep to transport stream for inter-splicing later
    subprocess.call("ffmpeg -ss {beep_start} -i beep_full.mp4"
                    " -t {beep_length} -vcodec libx264 -acodec aac "
                    "-strict experimental -r 24 -async 1 -y beep.mp4"
                    .format(beep_start=str(beep_start), beep_length=str(beep_length)), shell=True)
    subprocess.call("ffmpeg -i beep.mp4 -vf scale=1280:720,setdar=16:9 beep.ts", shell=True)


def download_and_create_video_string(song_length, song_file, duration, fade_frame_count, fade_length):
    # TODO: Create a GUI to manage this as people may want differing song amounts/lengths/other customization
    # Default: 60 songs of 1 minute a piece - declared above
    # concat_vid_string holds the final string of transport streams to be passed to ffmpeg's concat protocol tool
    concat_vid_string = "concat:"
    for i in range(1, song_length + 1):
        # TODO: This for loop could probably be broken up a bit into functions
        link = song_file.readline()

        # This if is to prevent errors happening from extra blank lines
        if link:
            current_song = str(i)

            # Read the start time and convert
            start_time = song_file.readline().strip()
            start = timestamp_convert_to_seconds(start_time)

            # Download the full video that we want to split up and create transport stream just like above
            # TODO: We could extract this process into a function cleanly, but it's not bad as is
            # TODO: Try/Except youtube-dl somehow since it occasionally has download errors
            print("Downloading song {current_song} of 60...".format(current_song=current_song))
            subprocess.call("youtube-dl --quiet -f mp4 -o {current_song}_full.mp4 {link}"
                            .format(current_song=current_song, link=link),
                            shell=True)


            # TODO: Add frames per second using ffprobe here
            # TODO: Optimize this call as it scans the whole video for this as is
            # print("Determining frames per second for fade conversion")
            #ffprobe_out = subprocess.Popen("ffprobe -select_streams v -show_streams " + current_song + "_full.mp4"
            #                               , stdout=subprocess.PIPE)
            # This includes fade out - we figured out fading out cheapens the effect but let's leave the code here
            #   for the time being so we can add it to customization options later
            # subprocess.call("ffmpeg " +
            #                 " -ss " + str(start_time) + " -i " + current_song + "_full.mp4 " +
            #                 " -t " + duration + " -vcodec libx264 -acodec aac -strict experimental -r 24 -async 1 -y " +
            #                 "-vf fade=in:0:" + str(fade_frame_count) +
            #                 ",fade=out:" + str(fade_out_start) + ":" + str(fade_frame_count) +
            #                 " -af afade=in:st=0:d=" + str(fade_length) +
            #                 ",afade=out:st=" + str(song_length - fade_length) + ":d=" + str(fade_length) +
            #                 " " + current_song + ".mp4")

            # Don't specify -t flag if last song so we can fully play it out
            duration_string = " -t {duration}".format(duration=duration) if i < song_length else ""
            call_string = "ffmpeg -ss {start_time} -i {current_song}_full.mp4{duration_string} -vcodec libx264 -acodec " \
                          "aac -strict experimental -r 24 -async 1 -y -vf fade=in:0:{fade_frame_count} -af " \
                          "afade=in:st=0:d={fade_length} {current_song}.mp4"\
                .format(start_time=str(start_time),
                        current_song=current_song,
                        duration_string=duration_string,
                        fade_frame_count=str(fade_frame_count),
                        fade_length=str(fade_length),
                        )
            subprocess.call(call_string, shell=True)

            subprocess.call("ffmpeg -i {current_song}.mp4 -vf scale=1280:720,setdar=16:9 {current_song}.ts"
                            .format(current_song=current_song,
                                    ),
                            shell=True)

            # Add our transport stream to the list and follow it with the interspliced beep
            concat_vid_string += "{current_song}.ts|beep.ts|".format(current_song=current_song)
        return concat_vid_string


def execute():
    # Variable declarations - also adds easy insertion/extraction into GUI later
    # TODO: All these top level options should be configurable at invocation time
    song_file_name = "songs.txt"  # Use in GUI
    orig_dir = os.getcwd()
    temp_dir = "temp"
    power_hour_name = "power_hour"  # We add the .mp4 later # Use in GUI
    duration = "01:00"
    song_length = 60

    # Variables for fading
    # If fade_length is zero, then we should remove the filters to speed the process up
    fade_length = 2  # In seconds # Use in GUI
    frames_per_second = 24  # This is an assumption based on tests # Fade out var (not currently used)
    frames_per_video = frames_per_second * song_length
    fade_out_start = frames_per_video - frames_per_second * fade_length  # Fade out var (not currently used)
    fade_frame_count = frames_per_video - fade_out_start  # Fade out var (not currently used)

    # open power hour text file
    song_file = open(song_file_name, "r")

    setup_temp_folder(temp_dir, orig_dir)
    os.chdir(temp_dir)
    download_beep(song_file)
    vid_string = download_and_create_video_string(song_length, song_file, duration, fade_frame_count, fade_length)

    # Close the song file since we are done reading it
    song_file.close()

    # Use the ffmpeg Protocol method
    # [:-9] is so we remove that last beep off the end
    # TODO: When GUI'd up, move power hours to a Power_Hours folder (currently in gitignore)
    subprocess.call("ffmpeg -i \"" + vid_string[:-9] + "\"  -c copy -s 1280:720 " + power_hour_name + ".mp4", shell=True)

    shutil.move(os.path.join(os.getcwd(), power_hour_name) + ".mp4",
                os.path.join(orig_dir, power_hour_name) + ".mp4")

    os.chdir(orig_dir)
    shutil.rmtree(os.path.join(orig_dir, temp_dir))


if __name__ == "__main__":
    execute()
