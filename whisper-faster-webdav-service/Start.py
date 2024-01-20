import os
import sys
import pathlib
import schedule
import datetime
import time
from dotenv import load_dotenv

from faster_whisper import WhisperModel, download_model
import easywebdav

easywebdav.basestring = str
easywebdav.client.basestring = str
import urllib
import pysubs2
from SrtToLrcFormatter import formatDirectorySrtFilesToLrc

# set Workplace
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.getcwd())

# set directorys
audio_dir = 'audio'
upload_dir = 'upload'
whisper_model_dir = 'whisper_models'
transcribe_formats = ['.mp3', '.m4a', '.wav', '.ogg', '.3gp', '.aac', 'wma']
pathlib.Path(audio_dir).mkdir(parents=True, exist_ok=True)
pathlib.Path(upload_dir).mkdir(parents=True, exist_ok=True)
pathlib.Path(whisper_model_dir).mkdir(parents=True, exist_ok=True)


class WhisperFasterWebDAVService:
    def __init__(self):
        global audio_dir
        global upload_dir
        global whisper_model_dir
        self.audio_dir = audio_dir
        self.upload_dir = upload_dir
        self.whisper_model_dir = whisper_model_dir

        # webdav connection settings
        self.host = os.environ['W_DOMAIN']
        self.username = os.environ['W_USERNAME']
        self.password = os.environ['W_PASSWORD']
        self.root_path = os.environ['W_ROOT_PATH']
        self.root_path = self.root_path[:-1] if self.root_path[-1] == '/' else self.root_path
        try:
            self.whisper_model = os.environ['W_WHISPER_MODEL']
        except (BaseException,):
            self.whisper_model = 'large-v2'

    def run(self):
        print('starting service...')
        success = True
        # Upload all files in upload dir (leftovers)
        success = self.upload_srt_and_lrc_files(skip_files=[])

        if success:
            # download files which to be transcribed or formated to .lrc
            print('starting downloading files...')
            audio_files_whithout_srt, srt_files_without_lrc = self.download_audio_and_srt_files()
            print('done')
        if len(audio_files_whithout_srt) > 0:
            # transcribe audio files
            print(f'transcribe {len(audio_files_whithout_srt)} files')
            success = self.transcribe_directory_files()
            if success:
                print('successfully transcribed')
            else:
                print('error while transcription')
        else:
            print(f'no files for transcription found')

        if success:
            # format .srt files to .lrc
            print('formating .srt to .lrc...')
            success = formatDirectorySrtFilesToLrc(directory=self.audio_dir)
            if success:
                print('successfully formatted')
            else:
                print('error while formatting')

        if success:
            # move to upload directory
            file_list = next(os.walk(self.audio_dir))[2]
            for file in file_list:
                os.rename(f'{self.audio_dir}/{file}', f'{self.upload_dir}/{file}')

            # upload
            print('uploading files...')
            success = self.upload_srt_and_lrc_files(skip_files=srt_files_without_lrc)
            if success:
                print('successfully uploaded')
            else:
                print('error while uplading')

        print('service done')

    def download_audio_and_srt_files(self):
        # Download audio files, if no .srt file with same name exists - for transcribe
        # download .srt files, if audio exists with same name but no .lrc with same name - to format into .lrc files

        # a = urllib.parse.unquote(.name)
        try:
            webdav = easywebdav.connect(host=self.host, username=self.username, password=self.password,
                                        protocol='https')
            file_list = webdav.ls(self.root_path)

            audio_file_list = []
            srt_file_list = []
            lrc_file_list = []
            # check existant of lyrics files
            for file in file_list:
                if file.contenttype.strip() == '':
                    continue
                file_name = urllib.parse.unquote(file.name).split('/')[-1]
                if 'audio' in file.contenttype:
                    audio_file_list.append(file_name)
                elif file_name.endswith('srt'):
                    srt_file_list.append(file_name)
                elif file_name.endswith('lrc'):
                    lrc_file_list.append(file_name)

            audio_files_whithout_srt = []  # convert audio to srt list
            srt_files_without_lrc = []  # convert audio to lrc list
            for audio_file_name in audio_file_list:
                exists_srt = False
                for srt_file_name in srt_file_list:
                    if f'{audio_file_name[:-4]}.srt' == srt_file_name:
                        exists_srt = True
                        break
                if not exists_srt:
                    audio_files_whithout_srt.append(audio_file_name)
            for srt_file_name in srt_file_list:
                exists_audio_file = False
                for audio_file_name in audio_file_list:
                    if f'{audio_file_name[:-4]}.srt' == srt_file_name:
                        exists_audio_file = True
                        break
                if not exists_audio_file:
                    continue

                exists_lrc_file = False
                for lrc_file_name in lrc_file_list:
                    if f'{srt_file_name[:-4]}.lrc' == lrc_file_name:
                        exists_lrc_file = True
                        break

                if not exists_lrc_file:
                    srt_files_without_lrc.append(srt_file_name)

            # Download files
            for audio_file_name in audio_files_whithout_srt:
                print('Download ' + audio_file_name)
                # file = next(urllib.parse.unquote(file.name).split('/')[-1] for file in file_list if urllib.parse.unquote(file.name).split('/')[-1] == audio_file_name)
                webdav.download(self.root_path + '/' + audio_file_name, self.audio_dir + '/' + audio_file_name)
            for srt_file_name in srt_files_without_lrc:
                print('Download ' + srt_file_name)
                webdav.download(self.root_path + '/' + srt_file_name, self.audio_dir + '/' + srt_file_name)
            return (audio_files_whithout_srt, srt_files_without_lrc)
        except (BaseException,) as e:
            print(e)

        return ([], [])

    def transcribe_directory_files(self):
        try:
            global transcribe_formats
            file_list = next(os.walk(self.audio_dir))[2]
            audio_file_list = [x for x in file_list if x[-4:] in transcribe_formats]
            if len(audio_file_list) > 0:
                model_dir = download_model(self.whisper_model,
                                           output_dir=self.whisper_model_dir + '/' + self.whisper_model)
                model = WhisperModel(model_dir, device="cpu", compute_type="auto", cpu_threads=1)

            for file in audio_file_list:
                print('transcribe ' + file + '...')
                start = time.time()
                if file[-4:] not in transcribe_formats:
                    continue

                name = file[:-4]

                segments, info = model.transcribe(f'{self.audio_dir}/{file}',
                                                  temperature=0,
                                                  best_of=5,
                                                  beam_size=5,
                                                  patience=1,
                                                  length_penalty=1,
                                                  no_repeat_ngram_size=0,
                                                  prompt_reset_on_temperature=0.5,
                                                  compression_ratio_threshold=2.4,
                                                  log_prob_threshold=-1,
                                                  no_speech_threshold=0.6,
                                                  vad_filter=True,
                                                  vad_parameters=dict(
                                                      min_speech_duration_ms=350,
                                                      threshold=0.45,
                                                      min_silence_duration_ms=3200,
                                                      speech_pad_ms=900,
                                                      window_size_samples=1536
                                                  ),
                                                  language="de",
                                                  )

                results = []
                for segment in segments:
                    segment_dict = {'start': segment.start, 'end': segment.end, 'text': segment.text}
                    results.append(segment_dict)
                    print("[%.2fs -> %.2fs] %s" % (segment_dict['start'], segment_dict['end'], segment_dict['text']))

                subs = pysubs2.load_from_whisper(results)
                # save srt file
                subs.save(f'{self.audio_dir}/{name}.srt')

                # remove audio file
                os.remove(f'{self.audio_dir}/{file}')

                end = time.time()
                print(f'transcription of {file} finished in {timedelta(seconds=end - start)} (HH:mm:ss)')
            return True
        except (BaseException,) as e:
            print(e)
            return False

    def upload_srt_and_lrc_files(self, skip_files):
        global transcribe_formats
        try:
            file_list = next(os.walk(self.upload_dir))[2]
            upload_file_list = [x for x in file_list if
                                (x.endswith('.srt') and not x in skip_files) or x.endswith('.lrc')]
            print(upload_file_list)

            # skip if upload/ is empty
            if len(upload_file_list) == 0:
                return True

            webdav = easywebdav.connect(host=self.host, username=self.username, password=self.password,
                                        protocol='https')
            for file in file_list:
                # skip audio files
                if file[-4:] in transcribe_formats:
                    continue

                if file not in skip_files:
                    print('Upload ' + file)
                    webdav.upload(f'{self.upload_dir}/{file}', f'{self.root_path}/{file}')
                os.remove(f'{self.upload_dir}/{file}')
            return True
        except (BaseException,) as e:
            print(e)
            return False


if __name__ == '__main__':
    load_dotenv()
    service = WhisperFasterWebDAVService()

    try:
        runonstart = os.environ['W_RUN_ON_START']
        if runonstart:
            service.run()
    except (BaseException,):
        pass

    # add here schedules
    schedule.every().sunday.at("13:00").do(service.run)

    # everyday schedule
    schedule.every().day.at("22:00").do(service.run)

    print('Schedules are set and waiting for run')
    print('first schedule-run in: ' + str(schedule.idle_seconds()) + 's')
    while True:
        schedule.run_pending()
        time.sleep(60)
