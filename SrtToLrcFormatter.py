import os
from os import walk
from pathlib import Path


def formatDirectorySrtFilesToLrc(directory):
    try:
        audio_dir = directory
        overwrite = False
        count_formats = 0

        file_list = []
        if os.path.isdir(audio_dir):
            file_list = next(walk(audio_dir))[2]
            srt_list = [x for x in file_list if x.endswith('.srt')]
            lrc_list = [x for x in file_list if x.endswith('.lrc')]
            for srt_file in srt_list:
                file_name = srt_file[:-4]
                if file_name + '.lrc' not in lrc_list or overwrite:
                    new_file_start_time_lines = []
                    new_file_text_lines = []
                    count_formats += 1
                    with open(audio_dir + '/' + srt_file, 'r', encoding='utf-8') as file:
                        file_lines = file.readlines()
                    if len(file_lines) > 0:
                        # load
                        lrc_start_string = ''
                        for i, line in enumerate(file_lines):
                            line = line.rstrip()

                            if ' --> ' in line:
                                start_time = line.split(' --> ')[0]
                                start_time_sep = start_time.split(':')
                                second_sep = start_time_sep[2].split(',')
                                start_hour = start_time_sep[0]
                                start_minute = start_time_sep[1]
                                start_second = second_sep[0]
                                start_msecond = second_sep[1]

                                lrc_start_string = f'[{str(int(start_hour) * 60 + int(start_minute)).rjust(2, "0")}:' \
                                                f'{start_second}.{start_msecond[:2]}]'
                            else:
                                if lrc_start_string != '':
                                    new_file_start_time_lines.append(lrc_start_string)
                                    new_file_text_lines.append(line)
                                lrc_start_string = ''
                        # save
                        with open(audio_dir + '/' + file_name + '.lrc', 'w', encoding='utf-8') as file:
                            for i, new_line in enumerate(new_file_start_time_lines):
                                if i + 1 < len(new_file_start_time_lines):
                                    file.write(new_line + new_file_text_lines[i] + '\n')
                                else:
                                    file.write(new_line + new_file_text_lines[i])
                        if False:
                            with open(audio_dir + '/' + file_name + '.text', 'w', encoding='utf-8') as file:
                                for i, new_line in enumerate(new_file_text_lines):
                                    if i + 1 < len(new_file_start_time_lines):
                                        file.write(new_line + '\n')
                                    else:
                                        file.write(new_line)
        print(f'{count_formats} .srt files formated to .lrc')
        return True
    except (BaseException, ) as e:
        print(e)
        return False


if __name__ == '__main__':
    main()
